# Multi-LLM Provider Setup Guide

This guide helps you set up multi-LLM provider support for the ITIL AI Agents framework, enabling you to use different AI models from various providers including local Ollama models.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Core multi-LLM support
pip install openai anthropic google-generativeai ollama transformers torch requests aiohttp pyyaml

# Optional: For specific providers
pip install azure-openai  # Azure OpenAI
pip install huggingface_hub  # Hugging Face models
```

### 2. Set Environment Variables

Create a `.env` file or set environment variables:

```bash
# OpenAI
export OPENAI_API_KEY="your-openai-api-key"

# Anthropic Claude
export ANTHROPIC_API_KEY="your-anthropic-api-key"

# Google AI
export GOOGLE_API_KEY="your-google-api-key"

# Azure OpenAI (if using Azure)
export AZURE_OPENAI_API_KEY="your-azure-api-key"
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
```

### 3. Install and Setup Ollama (for local models)

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve

# Download models (in another terminal)
ollama pull llama2:7b      # Llama 2 7B
ollama pull llama2:13b     # Llama 2 13B (larger, more capable)
ollama pull mistral:7b     # Mistral 7B (good for technical tasks)
ollama pull codellama:7b   # Code Llama (specialized for code)
ollama pull neural-chat:7b # Neural Chat (conversational)

# Verify installation
ollama list
```

## 🔧 Configuration

### Option 1: Use Configuration File

Copy and edit the configuration file:

```bash
cp config/llm_providers.yaml config/my_llm_config.yaml
# Edit my_llm_config.yaml with your settings
```

### Option 2: Programmatic Configuration

```python
from ai_agents.multi_llm_provider import MultiLLMManager, LLMConfig, LLMProvider, ModelType

# Initialize manager
llm_manager = MultiLLMManager()

# Add OpenAI provider
openai_config = LLMConfig(
    provider=LLMProvider.OPENAI,
    model=ModelType.GPT_4,
    api_key="your-api-key",
    temperature=0.1,
    max_tokens=2000
)
llm_manager.add_provider("openai", openai_config)

# Add Ollama provider
ollama_config = LLMConfig(
    provider=LLMProvider.OLLAMA,
    model=ModelType.LLAMA_2_7B,
    api_base="http://localhost:11434",
    temperature=0.1,
    max_tokens=2000
)
llm_manager.add_provider("ollama", ollama_config)

# Set primary and fallback
llm_manager.set_primary_provider("openai")
llm_manager.add_fallback_provider("ollama")
```

## 🎯 Supported Providers

### Cloud Providers

| Provider | Models | API Key Required | Notes |
|----------|---------|------------------|-------|
| OpenAI | GPT-3.5, GPT-4, GPT-4-turbo | Yes | Most capable, higher cost |
| Anthropic | Claude 3 (Haiku, Sonnet, Opus) | Yes | Excellent for analysis |
| Google | Gemini Pro, Gemini Pro Vision | Yes | Good performance/cost ratio |
| Azure OpenAI | Same as OpenAI | Yes | Enterprise deployment |

### Local Providers

| Provider | Models | Requirements | Notes |
|----------|--------|--------------|-------|
| Ollama | Llama2, Mistral, CodeLlama, etc. | Ollama installed | Privacy-focused, no API costs |
| Hugging Face | Any compatible model | Transformers library | Open source models |

### Utility Providers

| Provider | Purpose | When to Use |
|----------|---------|-------------|
| Mock | Testing and fallback | Always available, no external dependencies |

## 📊 Provider Selection Strategy

### By Use Case

**Complex Incident Analysis:**
- Primary: GPT-4, Claude 3 Opus
- Fallback: Llama2 13B, GPT-3.5

**Quick Triage:**
- Primary: GPT-3.5, Llama2 7B
- Fallback: Mistral 7B, Mock

**Code Analysis:**
- Primary: CodeLlama, GPT-4
- Fallback: Mistral, GPT-3.5

**Documentation:**
- Primary: Claude 3, Gemini Pro
- Fallback: Llama2, GPT-3.5

**Privacy-Sensitive Tasks:**
- Primary: Ollama models (local)
- Fallback: Mock (no external calls)

### By Performance Requirements

**High Quality (Accuracy):**
1. GPT-4
2. Claude 3 Opus
3. Claude 3 Sonnet
4. Llama2 13B

**Fast Response:**
1. GPT-3.5 Turbo
2. Llama2 7B (local)
3. Mistral 7B (local)
4. Mock

**Cost Effective:**
1. Ollama models (local, free)
2. GPT-3.5 Turbo
3. Gemini Pro
4. Mock

## 🛠️ Integration with ITIL Agents

### Using with Agent Crew

```python
from ai_agents.itil_crewai_integration import ITILAgentCrew
from integration.integration_manager import ITILIntegrationManager

# Initialize with multi-LLM support
itil_manager = ITILIntegrationManager()
agent_crew = ITILAgentCrew(
    itil_manager=itil_manager,
    llm_config_file="config/my_llm_config.yaml"
)

# Check LLM status
print(agent_crew.get_llm_provider_info())

# Use specific provider for a task
response = await agent_crew.get_llm_response(
    prompt="Analyze this critical incident...",
    provider_name="openai_gpt4"
)
```

### Direct LLM Manager Usage

```python
from ai_agents.multi_llm_provider import MultiLLMManager

# Initialize from config
manager = MultiLLMManager("config/my_llm_config.yaml")

# Get response with automatic fallback
response = await manager.generate_response(
    prompt="What are ITIL 4 guiding principles?",
    system_prompt="You are an ITIL expert."
)

# Use specific provider
response = await manager.generate_response(
    prompt="Analyze this incident pattern...",
    provider_name="claude"
)
```

## 🔍 Testing and Validation

### Run the Demo

```bash
cd python-framework/examples
python multi_llm_demo.py
```

The demo will:
- Test all configured providers
- Compare response times and quality
- Demonstrate fallback mechanisms
- Show integration with ITIL agents

### Validate Ollama Setup

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Test a model
curl http://localhost:11434/api/generate -d '{
  "model": "llama2:7b",
  "prompt": "What is ITIL?",
  "stream": false
}'
```

### Test Provider Configuration

```python
from ai_agents.multi_llm_provider import MultiLLMManager

manager = MultiLLMManager("config/my_llm_config.yaml")

# List available providers
print("Available providers:", manager.get_available_providers())

# Test each provider
for provider in manager.get_available_providers():
    try:
        response = await manager.generate_response(
            "Hello, are you working?",
            provider_name=provider
        )
        print(f"✅ {provider}: Working")
    except Exception as e:
        print(f"❌ {provider}: {e}")
```

## 🚨 Troubleshooting

### Common Issues

**"OpenAI API key not set"**
- Set the `OPENAI_API_KEY` environment variable
- Or use mock provider for testing

**"Connection to Ollama failed"**
- Check if Ollama is running: `ps aux | grep ollama`
- Start Ollama: `ollama serve`
- Verify connection: `curl http://localhost:11434/api/tags`

**"Model not found"**
- Download the model: `ollama pull llama2:7b`
- Check available models: `ollama list`

**"All providers failed"**
- Check internet connection for cloud providers
- Verify API keys are correct
- Ensure at least one provider is properly configured
- Mock provider should always work as fallback

### Performance Issues

**Slow responses with local models:**
- Use smaller models (7B instead of 13B)
- Ensure sufficient RAM (8GB+ for 7B models)
- Consider GPU acceleration if available

**High API costs:**
- Use GPT-3.5 instead of GPT-4 for simple tasks
- Implement request caching
- Use local models for development/testing

### Memory Issues

**Out of memory with Hugging Face models:**
- Use smaller models
- Enable model sharding
- Reduce max_tokens parameter

## 📈 Monitoring and Optimization

### Usage Tracking

```python
# Track provider usage
manager = MultiLLMManager("config/my_llm_config.yaml")

# After some requests
for provider_name in manager.get_available_providers():
    info = manager.get_provider_info(provider_name)
    print(f"{provider_name}: {info}")
```

### Cost Optimization

1. **Use appropriate models for tasks:**
   - GPT-3.5 for simple tasks
   - GPT-4 for complex analysis
   - Local models for development

2. **Implement caching:**
   - Cache frequent queries
   - Store common responses

3. **Set limits:**
   - max_tokens per request
   - Request rate limiting
   - Daily/monthly budgets

### Performance Tuning

1. **Response time optimization:**
   - Use local models for development
   - Implement request batching
   - Choose providers based on latency

2. **Quality vs. Speed tradeoffs:**
   - Fast models for triage
   - Powerful models for analysis
   - Automatic provider selection

## 🔐 Security Considerations

### API Key Management

- Store API keys in environment variables
- Never commit API keys to version control
- Use different keys for different environments
- Rotate keys regularly

### Local Model Security

- Ollama models run locally (more secure)
- No data sent to external services
- Suitable for sensitive ITIL data
- Consider network isolation

### Data Privacy

- Choose providers based on data sensitivity
- Use local models for confidential data
- Review provider privacy policies
- Implement data encryption in transit

## 🎯 Best Practices

### Provider Configuration

1. **Always configure multiple providers** for redundancy
2. **Set appropriate fallback chains** based on capability
3. **Use provider-specific strengths** (e.g., Claude for documentation)
4. **Monitor usage and costs** regularly

### Development Workflow

1. **Start with mock provider** for initial development
2. **Use local models** for extensive testing
3. **Add cloud providers** for production features
4. **Implement comprehensive error handling**

### Production Deployment

1. **Use configuration files** for easy management
2. **Implement monitoring** and alerting
3. **Set up automatic failover**
4. **Plan for cost management**

## 📚 Additional Resources

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [Google AI Documentation](https://ai.google.dev/)
- [Ollama Documentation](https://ollama.ai/docs)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers)

## 🆘 Support

For issues and questions:

1. Check the troubleshooting section above
2. Run the diagnostic demo: `python examples/multi_llm_demo.py`
3. Review configuration files for syntax errors
4. Test individual providers separately
5. Check logs for specific error messages

## 🚀 Next Steps

Once you have multi-LLM support working:

1. **Customize provider selection** for your specific ITIL processes
2. **Implement usage monitoring** and cost tracking
3. **Fine-tune model parameters** for optimal performance
4. **Integrate with your existing ITIL tools** and workflows
5. **Train team members** on the new capabilities