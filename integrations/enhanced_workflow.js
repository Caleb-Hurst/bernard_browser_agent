require('dotenv').config();
const { Octokit } = require("@octokit/rest");
const { OpenAI } = require("openai");
const { spawn } = require('child_process');
const path = require('path');

// Get target repository from environment or default to First-Workflow
const targetRepo = process.env.TARGET_REPO || "Caleb-Hurst/First-Workflow";
const [owner, repo] = targetRepo.split('/');
const label = "needs-test";

const octokit = new Octokit({ auth: process.env.GITHUB_TOKEN });
const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

// Path to browser agent project (current directory when running in CI)
const BROWSER_AGENT_PATH = process.cwd();

async function findAssociatedPRNumber(issueNumber) {
  const timeline = await octokit.issues.listEventsForTimeline({
    owner,
    repo,
    issue_number: issueNumber,
    per_page: 100
  });

  for (const event of timeline.data) {
    if (
      event.event === "cross-referenced" &&
      event.source &&
      event.source.pull_request
    ) {
      if (event.source.pull_request.number) {
        return event.source.pull_request.number;
      }
      if (event.source.issue && event.source.issue.pull_request) {
        return event.source.issue.number;
      }
    }
  }

  const prs = await octokit.pulls.list({
    owner,
    repo,
    state: "open",
    per_page: 100
  });

  for (const pr of prs.data) {
    if (pr.body && pr.body.includes(`#${issueNumber}`)) {
      return pr.number;
    }
  }

  const comments = await octokit.issues.listComments({
    owner,
    repo,
    issue_number: issueNumber,
    per_page: 50
  });

  for (const comment of comments.data) {
    const numberMatch = comment.body.match(/#(\d+)/);
    if (numberMatch) {
      const possibleNumber = numberMatch[1];
      try {
        const pr = await octokit.pulls.get({ owner, repo, pull_number: possibleNumber });
        if (pr) return possibleNumber;
      } catch (err) {}
    }
  }
  // No PR found
  return null;
}

async function generateTestScenario(issueTitle, issueBody, prAnalysis = null) {
  const systemPrompt = `You are an expert QA test scenario generator. Create a detailed browser automation test scenario based on the given issue and PR information.

IMPORTANT: Generate a specific, actionable test scenario that can be executed by a browser automation agent. Include:
1. The specific URL to test (use realistic URLs based on the issue context)
2. Step-by-step actions to perform
3. Expected outcomes to verify
4. Specific elements to interact with

Keep the scenario focused and executable. If the issue lacks specific URLs or context, make reasonable assumptions about a typical web application.`;

  const userPrompt = `Issue Title: ${issueTitle}
Issue Body: ${issueBody}
${prAnalysis ? `PR Analysis: ${prAnalysis}` : ''}

Generate a comprehensive browser test scenario for this issue.`;

  try {
    const response = await openai.chat.completions.create({
      model: "gpt-4o",
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: userPrompt }
      ],
      max_tokens: 500
    });

    return response.choices[0].message.content;
  } catch (error) {
    console.error("Failed to generate test scenario:", error);
    return `Test the functionality described in: ${issueTitle}. Navigate to the relevant page and verify the expected behavior works correctly.`;
  }
}

async function executeBrowserTest(testScenario) {
  return new Promise((resolve, reject) => {
    console.log("🤖 Executing browser automation test...");

    const pythonScript = path.join(BROWSER_AGENT_PATH, 'integrations', 'github_integration.py');
    const pythonProcess = spawn('uv', ['run', 'python', pythonScript, testScenario], {
      cwd: BROWSER_AGENT_PATH,
      env: {
        ...process.env,
        HEADLESS: "true", // Run in headless mode for CI
        TIMEOUT: "180",   // 3 minute timeout
        PATH: `${process.env.HOME}/.local/bin:${process.env.PATH}` // Ensure uv is in PATH
      }
    });

    let stdout = '';
    let stderr = '';

    pythonProcess.stdout.on('data', (data) => {
      stdout += data.toString();
      console.log(`[Browser Agent] ${data.toString().trim()}`);
    });

    pythonProcess.stderr.on('data', (data) => {
      stderr += data.toString();
      console.error(`[Browser Agent Error] ${data.toString().trim()}`);
    });

    pythonProcess.on('close', (code) => {
      if (code === 0) {
        console.log("✅ Browser test completed successfully");
        resolve({
          success: true,
          output: stdout,
          exitCode: code
        });
      } else {
        console.log(`❌ Browser test failed with exit code ${code}`);
        resolve({
          success: false,
          output: stdout,
          error: stderr,
          exitCode: code
        });
      }
    });

    pythonProcess.on('error', (error) => {
      console.error(`Failed to start browser test: ${error.message}`);
      reject(error);
    });
  });
}

async function run() {
  console.log(`🎯 Processing issues in: ${targetRepo}`);
  console.log(`🔍 Scanning for ALL issues with label "${label}"`);

  // Process all issues with "needs-test" label (exactly like First-Workflow)
  const issues = await octokit.issues.listForRepo({
    owner,
    repo,
    labels: label,
    state: "open",
    per_page: 100
  });

  if (!issues.data.length) {
    console.log(`📭 No issues found with label "${label}" in ${targetRepo}.`);
    return;
  }

  console.log(`📋 Found ${issues.data.length} issue(s) with "${label}" label to process`);

  for (const issue of issues.data) {
    const { number, title, body, labels } = issue;
    console.log(`\n🔍 Processing Issue #${number}: ${title}`);

    let prNumber = await findAssociatedPRNumber(number);

    const issuePrompt = `You are an expert GitHub issue analyst. Summarize the ticket below in clear language for QA:\nTitle: ${title}\nBody: ${body}\nLabels: ${labels.map(l => l.name).join(", ")}`;

    let commentBody = "";

    // Generate issue analysis
    try {
      const response = await openai.chat.completions.create({
        model: "gpt-4o",
        messages: [
          { role: "system", content: "You are an expert GitHub issue analyst. Summarize the ticket in clear language for QA." },
          { role: "user", content: issuePrompt }
        ],
        max_tokens: 300
      });
      const analysis = response.choices[0].message.content;
      commentBody += `## 📋 Issue Analysis\n\n${analysis}\n\n`;
    } catch (error) {
      commentBody += `Failed to generate issue analysis: ${error.message}\n\n`;
    }

    let prAnalysis = null;

    // Analyze associated PR if found
    if (prNumber) {
      try {
        const pr = await octokit.pulls.get({ owner, repo, pull_number: prNumber });
        const changedFiles = await octokit.pulls.listFiles({ owner, repo, pull_number: prNumber });

        const prTitle = pr.data.title;
        const prBody = pr.data.body;
        const filesList = changedFiles.data.map(f => f.filename).join(", ");

        const diffs = changedFiles.data
          .filter(f => f.patch)
          .map(f => `File: ${f.filename}\n${f.patch}`)
          .join('\n\n');

        const prPrompt = `A pull request (#${prNumber}) is associated with this issue. Here are the details:\nPR Title: ${prTitle}\nPR Body: ${prBody}\nFiles changed: ${filesList}\nCode changes:\n${diffs}\n\nSummarize what the code in this PR does for QA.`;

        const prResponse = await openai.chat.completions.create({
          model: "gpt-4o",
          messages: [
            { role: "system", content: "You are an expert code reviewer. Briefly summarize what the following pull request's code changes accomplish, in plain language for QA." },
            { role: "user", content: prPrompt }
          ],
          max_tokens: 400
        });

        prAnalysis = prResponse.choices[0].message.content;
        commentBody += `## 🔄 Associated PR (#${prNumber}) Summary\n\n${prAnalysis}\n\n`;
      } catch (error) {
        commentBody += `Failed to analyze associated PR (#${prNumber}): ${error.message}\n\n`;
      }
    } else {
      commentBody += `## 🔄 Associated PR\n\nNo associated pull request found for this issue.\n\n`;
    }

    // Generate and execute browser test
    try {
      console.log("🧪 Generating test scenario...");
      const testScenario = await generateTestScenario(title, body, prAnalysis);

      commentBody += `## 🧪 Generated Test Scenario\n\n\`\`\`\n${testScenario}\n\`\`\`\n\n`;

      console.log("🤖 Executing browser automation test...");
      const testResult = await executeBrowserTest(testScenario);

      if (testResult.success) {
        commentBody += `## ✅ Browser Test Results\n\n**Status:** PASSED ✅\n\n**Test Output:**\n\`\`\`\n${testResult.output.slice(-1000)}\n\`\`\`\n\n`;
      } else {
        commentBody += `## ❌ Browser Test Results\n\n**Status:** FAILED ❌\n\n**Error:**\n\`\`\`\n${testResult.error || 'Unknown error'}\n\`\`\`\n\n**Output:**\n\`\`\`\n${testResult.output.slice(-500)}\n\`\`\`\n\n`;
      }
    } catch (error) {
      console.error("Browser test execution failed:", error);
      commentBody += `## ❌ Browser Test Results\n\n**Status:** ERROR ❌\n\n**Error:** Failed to execute browser test: ${error.message}\n\n`;
    }

    // Post the comment (with cross-repo permission handling)
    try {
      await octokit.issues.createComment({
        owner,
        repo,
        issue_number: number,
        body: commentBody
      });
      console.log(`✅ Posted comprehensive analysis and test results on Issue #${number}`);
    } catch (error) {
      if (error.status === 403 && error.message.includes('Resource not accessible by integration')) {
        console.log(`⚠️  Cannot comment on cross-repo issue #${number} - insufficient permissions`);
        console.log(`📋 Test results for Issue #${number}:`);
        console.log('==========================================');
        console.log(commentBody);
        console.log('==========================================');
      } else {
        console.error(`❌ Failed to comment on issue #${number}:`, error);
      }
    }
  }
}

run().catch(console.error);
