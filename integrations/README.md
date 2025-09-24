# GitHub Actions Browser Agent Integration

This integration connects your existing GitHub Actions workflow with the Browser Agent to automatically test issues labeled with `needs-test`.

## 🚀 What This Does

1. **Scans Issues**: Monitors issues with the `needs-test` label
2. **Analyzes Content**: Uses LLM to understand the issue and associated PR
3. **Generates Test Scenarios**: Creates browser automation test scripts
4. **Executes Tests**: Runs the browser agent to actually test the functionality
5. **Reports Results**: Posts comprehensive test results back to the issue

## 📋 Setup Instructions

### 1. Self-Hosted Runner Setup

Since browser testing requires a GUI environment, you'll need a self-hosted GitHub Actions runner:

```bash
# On your Mac (where the browser agent works)
cd /path/to/your/runner/directory

# Download and configure GitHub Actions runner
# (Follow GitHub's self-hosted runner setup instructions)

# Make sure the runner has access to:
# - Chrome browser
# - Python 3.11+
# - Node.js 18+
# - Your API keys
```

### 2. Environment Variables

Set these secrets in your GitHub repository settings:

```bash
GITHUB_TOKEN          # Already available in Actions
OPENAI_API_KEY        # For LLM analysis
GROQ_API_KEY          # Alternative LLM provider
ANTHROPIC_API_KEY     # Alternative LLM provider
```

### 3. Repository Setup

1. Copy the integration files to your workflow repository:
   ```bash
   # In your First-Workflow repository
   mkdir -p integrations
   cp /path/to/bernard_browser_agent/integrations/* integrations/
   cp integrations/browser-testing.yml .github/workflows/
   ```

2. Update the workflow file paths in `enhanced_workflow.js`:
   ```javascript
   // Update this line to point to your browser agent location
   const BROWSER_AGENT_PATH = process.env.BROWSER_AGENT_PATH || "/path/to/bernard_browser_agent";
   ```

3. Install Node.js dependencies:
   ```bash
   npm install child_process path
   ```

## 🧪 Testing the Integration

Test locally before deploying:

```bash
# Set your API keys
export GROQ_API_KEY="your_key_here"
export OPENAI_API_KEY="your_key_here"

# Run the test suite
cd /path/to/bernard_browser_agent
python integrations/test_integration.py
```

## 🔧 Usage

### Automatic Triggering
- Add the `needs-test` label to any issue
- The workflow will automatically run browser tests
- Results are posted as a comment on the issue

### Manual Triggering
- Go to Actions → Browser Agent Testing → Run workflow
- Optionally specify an issue number or custom test scenario

## 📊 What You Get

The workflow posts a comprehensive comment with:

- **📋 Issue Analysis**: LLM summary of the issue
- **🔄 PR Analysis**: Code changes summary (if PR exists)
- **🧪 Test Scenario**: Generated automation script
- **✅/❌ Test Results**: Pass/fail status with detailed output

## 🔍 Example Output

```markdown
## 📋 Issue Analysis
The user reports that login form validation is not working properly...

## 🔄 Associated PR (#123) Summary
This PR adds client-side email validation to the login form...

## 🧪 Generated Test Scenario
Navigate to /login, enter invalid email 'notanemail', click submit, verify validation error appears...

## ✅ Browser Test Results
**Status:** PASSED ✅
**Test Output:**
Successfully navigated to login page
Entered invalid email: notanemail
Clicked submit button
✅ Validation error message appeared: "Please enter a valid email address"
Test completed successfully!
```

## 🛠 Customization

### Test Scenario Customization
Edit the `generateTestScenario()` function in `enhanced_workflow.js` to customize how test scenarios are generated based on your application structure.

### Browser Configuration
Modify `github_integration.py` to adjust:
- Headless vs. headed mode
- Timeout settings
- Browser options
- Screenshot capture

### LLM Providers
The integration supports multiple LLM providers (OpenAI, Groq, Anthropic). Configure your preferred provider in the browser agent's `.env` file.

## 🚦 Workflow Triggers

- **Issue Labeled**: Automatically runs when `needs-test` label is added
- **Manual Dispatch**: Can be triggered manually with custom parameters
- **Scheduled**: Can be set to run on a schedule (add to YAML)

## 📁 File Structure

```
integrations/
├── github_integration.py      # Browser agent wrapper
├── enhanced_workflow.js       # Enhanced workflow script
├── test_integration.py        # Local testing script
└── browser-testing.yml        # GitHub Actions workflow

.github/workflows/
└── browser-testing.yml        # GitHub Actions workflow (copy here)
```

## 🎯 Next Steps

1. **Set up self-hosted runner** on your Mac
2. **Configure API keys** in GitHub repository secrets
3. **Test locally** with the test script
4. **Deploy the workflow** to your repository
5. **Add `needs-test` label** to an issue to try it out!

## 🐛 Troubleshooting

- **Browser won't start**: Ensure Chrome is installed and accessible
- **Test timeout**: Increase timeout in environment variables
- **API errors**: Check that API keys are correctly set
- **Python errors**: Ensure all dependencies are installed with `uv sync`

## 💡 Tips

- Start with simple test scenarios to verify the integration works
- Use headless mode in CI for faster execution
- Monitor GitHub Actions logs for detailed debugging information
- Consider adding screenshot capture for failed tests
