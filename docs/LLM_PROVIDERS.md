# LLM Provider Configuration

The browser agent now supports multiple LLM providers through a centralized configuration system. You can easily switch between providers by setting environment variables.

## Supported Providers

- **OpenAI** - GPT-4 and other OpenAI models
- **Azure OpenAI** - Azure-hosted OpenAI models
- **Groq** - Fast inference with Llama and other models
- **Anthropic** - Claude models

## Configuration

### 1. Set Your Preferred Provider

Set the `LLM_PROVIDER` environment variable to choose your provider:

```bash
export LLM_PROVIDER=groq  # Options: openai, azure, groq, anthropic
```

### 2. Configure API Keys

Set the appropriate API key for your chosen provider:

#### OpenAI

```bash
export OPENAI_API_KEY=your_api_key_here
```

#### Azure OpenAI

```bash
export AZURE_OPENAI_API_KEY=your_api_key_here
export AZURE_ENDPOINT=https://your-resource-name.openai.azure.com/
```

#### Groq

```bash
export GROQ_API_KEY=your_api_key_here
```

#### Anthropic

```bash
export ANTHROPIC_API_KEY=your_api_key_here
```

### 3. Using .env File

Copy `.env.example` to `.env` and configure your settings:

```bash
cp .env.example .env
# Edit .env with your preferred provider and API keys
```

## Automatic Fallback

If your selected provider doesn't have an API key configured, the system will automatically:

1. Show available providers with configured API keys
2. Switch to the first available provider
3. Display a warning message

## Model Configuration

Each provider has default models and settings defined in `configurations/config.py`:

- **OpenAI**: gpt-4o
- **Azure**: gpt-4o
- **Groq**: meta-llama/llama-4-maverick-17b-128e-instruct
- **Anthropic**: claude-3-5-sonnet-20241022

You can customize these settings by modifying the `LLM_CONFIG` dictionary in the config file.

## Examples

### Switching Providers

```bash
# Use OpenAI
export LLM_PROVIDER=openai
export OPENAI_API_KEY=your_key

# Switch to Groq
export LLM_PROVIDER=groq
export GROQ_API_KEY=your_key

# Run the agent
python main.py
```

### Checking Configuration

```bash
python examples/provider_demo.py
```

This will show your current configuration and validate that everything is set up correctly.
