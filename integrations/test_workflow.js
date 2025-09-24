#!/usr/bin/env node

/**
 * Test script to simulate the GitHub workflow locally
 * This helps verify the integration works before deploying to GitHub Actions
 */

require('dotenv').config();
const { Octokit } = require("@octokit/rest");
const { OpenAI } = require("openai");

// Mock issue data for testing
const mockIssue = {
  number: 999,
  title: "Login form validation not working properly",
  body: `## Problem Description

The login form doesn't show validation errors when users enter invalid email addresses.

## Steps to Reproduce

1. Navigate to the login page
2. Enter an invalid email like "notanemail"
3. Click the submit button
4. Expected: Validation error should appear
5. Actual: Form submits without showing any error

## Additional Context

This affects user experience and could lead to confusion. We need proper client-side validation.

## Test URL

You can test this at: https://www.google.com (as a demo - just check the search field validation)`,
  labels: [{ name: "needs-test" }, { name: "bug" }]
};

async function testIssueAnalysis() {
  console.log("🧪 Testing Issue Analysis and Test Generation");
  console.log("=" .repeat(60));
  
  if (!process.env.OPENAI_API_KEY) {
    console.log("❌ OPENAI_API_KEY not set. Skipping LLM testing.");
    return;
  }

  const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

  try {
    // Test issue analysis
    console.log("📋 Analyzing mock issue...");
    const issuePrompt = `You are an expert GitHub issue analyst. Summarize the ticket below in clear language for QA:\nTitle: ${mockIssue.title}\nBody: ${mockIssue.body}\nLabels: ${mockIssue.labels.map(l => l.name).join(", ")}`;

    const analysisResponse = await openai.chat.completions.create({
      model: "gpt-4o",
      messages: [
        { role: "system", content: "You are an expert GitHub issue analyst. Summarize the ticket in clear language for QA." },
        { role: "user", content: issuePrompt }
      ],
      max_tokens: 300
    });

    const analysis = analysisResponse.choices[0].message.content;
    console.log("✅ Issue Analysis:");
    console.log(analysis);

    // Test scenario generation
    console.log("\n🧪 Generating test scenario...");
    const scenarioPrompt = `You are an expert QA test scenario generator. Create a detailed browser automation test scenario based on the given issue.

IMPORTANT: Generate a specific, actionable test scenario that can be executed by a browser automation agent. Include:
1. The specific URL to test (use realistic URLs based on the issue context)
2. Step-by-step actions to perform
3. Expected outcomes to verify
4. Specific elements to interact with

Keep the scenario focused and executable.

Issue Title: ${mockIssue.title}
Issue Body: ${mockIssue.body}

Generate a comprehensive browser test scenario for this issue.`;

    const scenarioResponse = await openai.chat.completions.create({
      model: "gpt-4o",
      messages: [
        { role: "system", content: "You are an expert QA test scenario generator. Create detailed, executable browser automation test scenarios." },
        { role: "user", content: scenarioPrompt }
      ],
      max_tokens: 500
    });

    const testScenario = scenarioResponse.choices[0].message.content;
    console.log("✅ Generated Test Scenario:");
    console.log(testScenario);

    // Test browser execution (if requested)
    if (process.argv.includes('--run-browser')) {
      console.log("\n🤖 Executing browser test...");
      const { spawn } = require('child_process');
      
      return new Promise((resolve) => {
        const pythonProcess = spawn('uv', ['run', 'python', 'integrations/github_integration.py', testScenario], {
          stdio: 'inherit'
        });

        pythonProcess.on('close', (code) => {
          if (code === 0) {
            console.log("✅ Browser test completed successfully!");
          } else {
            console.log(`❌ Browser test failed with exit code ${code}`);
          }
          resolve();
        });
      });
    }

  } catch (error) {
    console.error("❌ Test failed:", error.message);
  }
}

async function testGitHubAPI() {
  console.log("\n🔍 Testing GitHub API Connection");
  console.log("=" .repeat(60));

  if (!process.env.GITHUB_TOKEN) {
    console.log("⚠️  GITHUB_TOKEN not set. Skipping GitHub API test.");
    return;
  }

  try {
    const octokit = new Octokit({ auth: process.env.GITHUB_TOKEN });
    
    // Test API connection
    const { data: user } = await octokit.rest.users.getAuthenticated();
    console.log(`✅ Connected to GitHub API as: ${user.login}`);

    // Test repository access
    const { data: repo } = await octokit.rest.repos.get({
      owner: 'Caleb-Hurst',
      repo: 'bernard_browser_agent'
    });
    console.log(`✅ Repository access confirmed: ${repo.full_name}`);

  } catch (error) {
    console.error("❌ GitHub API test failed:", error.message);
  }
}

async function main() {
  console.log("🚀 Browser Agent GitHub Integration Test Suite");
  console.log("=" .repeat(70));
  
  console.log(`
🔧 Test Configuration:
- OpenAI API Key: ${process.env.OPENAI_API_KEY ? '✅ Set' : '❌ Missing'}
- GitHub Token: ${process.env.GITHUB_TOKEN ? '✅ Set' : '❌ Missing'}
- Groq API Key: ${process.env.GROQ_API_KEY ? '✅ Set' : '❌ Missing'}
- Run Browser Test: ${process.argv.includes('--run-browser') ? '✅ Yes' : '❌ No (add --run-browser to enable)'}
`);

  await testGitHubAPI();
  await testIssueAnalysis();

  console.log("\n🎉 Test Suite Complete!");
  console.log("=" .repeat(70));
  console.log(`
💡 Next Steps:
1. Set up GitHub repository secrets (OPENAI_API_KEY, etc.)
2. Configure a self-hosted runner
3. Create an issue and add the 'needs-test' label
4. Watch the automated workflow in action!

📚 Full Documentation: GITHUB_INTEGRATION.md
  `);
}

if (require.main === module) {
  main().catch(console.error);
}