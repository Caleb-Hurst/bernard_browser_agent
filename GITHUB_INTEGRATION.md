# 🤖 Browser Agent GitHub Integration

This repository includes a complete GitHub Actions workflow that automatically tests issues using the Browser Agent.

## 🚀 Quick Start

### 1. Enable the Workflow

The workflow is ready to use! It will automatically trigger when:
- Issues are labeled with `needs-test`
- You manually trigger it from the Actions tab

### 2. Set up Self-Hosted Runner

Since browser testing requires a GUI environment, you need a self-hosted runner:

```bash
# On your Mac/Linux machine
cd ~/actions-runner

# Follow GitHub's instructions to download and configure the runner
# Make sure it has access to:
# - Chrome browser
# - Python 3.11+
# - Node.js 18+
```

### 3. Configure Repository Secrets

Go to **Settings → Secrets and variables → Actions** and add:

```
OPENAI_API_KEY     # For LLM analysis (required)
GROQ_API_KEY       # Alternative LLM provider (optional)
ANTHROPIC_API_KEY  # Alternative LLM provider (optional)
```

### 4. Test It!

1. **Create an issue** in this repository
2. **Add the `needs-test` label**
3. **Watch the magic happen!** ✨

## 🎯 How It Works

When an issue is labeled with `needs-test`:

1. **📋 Issue Analysis**: LLM analyzes the issue content
2. **🔄 PR Detection**: Finds and analyzes associated pull requests
3. **🧪 Test Generation**: Creates browser automation test scenarios
4. **🤖 Browser Testing**: Executes actual browser tests
5. **📝 Results**: Posts comprehensive results back to the issue

## 📊 Example Output

The workflow will post a comment like this:

```markdown
## 📋 Issue Analysis
The login form validation issue affects user authentication flow...

## 🔄 Associated PR (#123) Summary  
This PR adds client-side email validation using regex patterns...

## 🧪 Generated Test Scenario
Navigate to /login, enter invalid email formats, verify error messages...

## ✅ Browser Test Results
**Status:** PASSED ✅

**Test Output:**
✅ Successfully navigated to login page
✅ Entered invalid email: notanemail@
✅ Validation error appeared: "Please enter a valid email"
✅ Test completed successfully!
```

## 🛠 Advanced Usage

### Manual Testing

Run the workflow manually with custom scenarios:

1. Go to **Actions** → **Browser Agent Issue Testing**
2. Click **Run workflow**
3. Enter a custom test scenario or target specific issues

### Testing Other Repositories

You can use this workflow to test issues in other repositories:

```yaml
# In the manual workflow trigger
Target Repository: owner/repository-name
```

### Local Testing

Test the integration locally:

```bash
# Set your API keys
export OPENAI_API_KEY="your_key_here"

# Test browser integration
uv run python integrations/test_integration.py

# Test issue workflow (requires GitHub token)
export GITHUB_TOKEN="your_token_here"
node integrations/enhanced_workflow.js
```

## 🔧 Configuration

Edit `integrations/config.env` to customize:

- Target repositories
- Issue labels
- Timeout settings
- LLM providers
- Test behavior

## 📁 File Structure

```
.github/workflows/
└── browser-testing.yml          # GitHub Actions workflow

integrations/
├── github_integration.py        # Browser agent wrapper
├── enhanced_workflow.js         # Issue analysis & testing
├── test_integration.py          # Local testing script
├── config.env                   # Configuration
└── README.md                    # Integration docs

package.json                     # Node.js dependencies
```

## 🎭 Use Cases

Perfect for testing:
- **🔐 Login flows** - Authentication and validation
- **📝 Form submissions** - Data entry and validation
- **🔍 Search functionality** - Query processing and results
- **🛒 E-commerce flows** - Shopping cart and checkout
- **📱 UI interactions** - Buttons, modals, navigation
- **🔗 Link verification** - Navigation and routing

## 🐛 Troubleshooting

**Workflow not triggering?**
- Check that the issue has the `needs-test` label
- Verify the self-hosted runner is online
- Check repository secrets are configured

**Browser tests failing?**
- Ensure Chrome is installed on the runner
- Check if the target URLs are accessible
- Review the test timeout settings

**API errors?**
- Verify API keys are correctly set in repository secrets
- Check API key permissions and usage limits

## 💡 Pro Tips

1. **Start simple** - Test with basic scenarios first
2. **Use realistic URLs** - Point to actual staging/test environments  
3. **Be specific** - Detailed issue descriptions = better test scenarios
4. **Monitor usage** - Keep an eye on API costs and runner usage
5. **Iterate** - Refine test scenarios based on results

## 🎉 Ready to Go!

Your browser agent is now integrated with GitHub Actions and ready to automatically test your issues! 

Create an issue, add the `needs-test` label, and watch your automated QA assistant in action! 🚀