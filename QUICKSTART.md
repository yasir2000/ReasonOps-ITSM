# AI Agents Quick Reference Guide

> 🚀 **Quick start guide for ReasonOps AI Agents** - Get up and running in 5 minutes!

## Table of Contents
- [Quick Start](#quick-start)
- [CLI Commands](#cli-commands)
- [API Endpoints](#api-endpoints)
- [SDK Usage](#sdk-usage)
- [Web UI](#web-ui)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

## Quick Start

### 1. Install Ollama (Recommended for local LLMs)

```bash
# macOS/Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# Download from https://ollama.com/download
```

### 2. Pull a Model

```bash
ollama pull llama2
# or
ollama pull mistral
```

### 3. Configure Providers

Create `config/llm_providers.json`:

```json
{
  "providers": {
    "ollama": {
      "base_url": "http://localhost:11434",
      "default_model": "llama2",
      "enabled": true
    }
  },
  "fallback_chain": ["ollama", "mock"],
  "default_provider": "ollama"
}
```

### 4. Start Services

```bash
# Terminal 1: Backend
cd api
uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd webapp
npm run dev
```

### 5. Run Your First Agent!

**Via CLI:**
```bash
python python-framework/cli.py agents:run incident_analysis '{"incident_id": "INC-001", "description": "Server not responding"}'
```

**Via Web UI:**
- Navigate to http://localhost:5173/agents
- Select "Incident Analysis" agent
- Enter context and click "Execute Agent"

---

## CLI Commands

### Run Agent
Execute an AI agent with context:

```bash
python cli.py agents:run <agent_type> '<context_json>'

# Examples:
python cli.py agents:run incident_analysis '{"incident_id": "INC-001"}'
python cli.py agents:run root_cause '{"incident_id": "INC-001"}'
python cli.py agents:run knowledge_base '{"query": "how to restart apache"}'
```

### List Agent Decisions
View decision history:

```bash
python cli.py agents:list-decisions

# With filters:
python cli.py agents:list-decisions --agent-type incident_analysis
python cli.py agents:list-decisions --limit 10
```

### Configure LLM Provider
Set active LLM provider:

```bash
python cli.py agents:configure-llm <provider_name>

# Examples:
python cli.py agents:configure-llm ollama
python cli.py agents:configure-llm openai
python cli.py agents:configure-llm anthropic
```

### Check Agent Health
Monitor agent and LLM provider health:

```bash
python cli.py agents:health

# Sample output:
# Provider: ollama - Status: healthy ✅
# Provider: openai - Status: unhealthy ❌
# Provider: mock - Status: healthy ✅
```

### List Available Providers
Show all configured LLM providers:

```bash
python cli.py agents:list-providers

# Sample output:
# Available LLM Providers:
# - ollama (active) - llama2
# - openai (inactive) - gpt-4
# - anthropic (inactive) - claude-3-sonnet
```

---

## API Endpoints

### POST /api/agents/run
Execute an AI agent:

```bash
curl -X POST http://localhost:8000/api/agents/run \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "incident_analysis",
    "context": {
      "incident_id": "INC-001",
      "description": "Server not responding",
      "priority": "high"
    },
    "llm_provider": "ollama"
  }'
```

**Response:**
```json
{
  "status": "success",
  "agent_type": "incident_analysis",
  "recommendations": [
    "Check server logs for errors",
    "Verify network connectivity",
    "Restart Apache service"
  ],
  "confidence": 0.87,
  "execution_time": 2.3
}
```

### GET /api/agents/decisions
Retrieve agent decision history:

```bash
curl http://localhost:8000/api/agents/decisions

# With filters:
curl "http://localhost:8000/api/agents/decisions?agent_type=incident_analysis&limit=10"
```

### POST /api/agents/configure-llm
Configure active LLM provider:

```bash
curl -X POST http://localhost:8000/api/agents/configure-llm \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "ollama",
    "model": "llama2"
  }'
```

### GET /api/agents/health
Check agent system health:

```bash
curl http://localhost:8000/api/agents/health
```

**Response:**
```json
{
  "status": "healthy",
  "providers": {
    "ollama": {
      "status": "healthy",
      "response_time": 0.12,
      "last_checked": "2025-01-15T10:30:00Z"
    },
    "openai": {
      "status": "unhealthy",
      "error": "Connection timeout",
      "last_checked": "2025-01-15T10:30:00Z"
    }
  }
}
```

### GET /api/agents/providers
List available LLM providers:

```bash
curl http://localhost:8000/api/agents/providers
```

---

## SDK Usage

### Initialize Client

```python
from reasonops_sdk import ReasonOpsClient

client = ReasonOpsClient(base_url="http://localhost:8000")
```

### Run Agent

```python
result = client.run_agents(
    agent_type="incident_analysis",
    context={
        "incident_id": "INC-001",
        "description": "Database connection timeout",
        "priority": "critical"
    }
)

print(f"Status: {result['status']}")
print(f"Recommendations: {result['recommendations']}")
```

### Get Agent Decisions

```python
decisions = client.get_agent_decisions(
    agent_type="incident_analysis",
    limit=10
)

for decision in decisions:
    print(f"Decision: {decision['id']}")
    print(f"Agent: {decision['agent_type']}")
    print(f"Outcome: {decision['outcome']}")
```

### Configure LLM Provider

```python
config_result = client.configure_llm_provider(
    provider="openai",
    model="gpt-4"
)

print(f"Provider configured: {config_result['provider']}")
```

### Check Health

```python
health = client.check_agent_health()

print(f"Overall status: {health['status']}")
for provider, status in health['providers'].items():
    print(f"{provider}: {status['status']}")
```

### List Providers

```python
providers = client.list_llm_providers()

for provider in providers:
    print(f"Provider: {provider['name']}")
    print(f"Status: {provider['status']}")
    print(f"Model: {provider['default_model']}")
```

### Complete Example

```python
from reasonops_sdk import ReasonOpsClient
import json

# Initialize
client = ReasonOpsClient(base_url="http://localhost:8000")

# Check health first
health = client.check_agent_health()
if health['status'] != 'healthy':
    print("Warning: Some providers are unhealthy")

# Run incident analysis
incident_context = {
    "incident_id": "INC-123",
    "description": "Web application returning 503 errors",
    "priority": "high",
    "affected_users": 150
}

result = client.run_agents(
    agent_type="incident_analysis",
    context=incident_context
)

# Display results
if result['status'] == 'success':
    print("✅ Analysis Complete")
    print("\nRecommendations:")
    for i, rec in enumerate(result['recommendations'], 1):
        print(f"{i}. {rec}")
    print(f"\nConfidence: {result['confidence']:.0%}")
else:
    print(f"❌ Analysis Failed: {result.get('error')}")

# View decision history
decisions = client.get_agent_decisions(limit=5)
print(f"\nRecent Decisions: {len(decisions)}")
```

---

## Web UI

### Accessing the Agent Dashboard

1. **Navigate** to http://localhost:5173/agents
2. **Configure Provider** in the "LLM Provider Configuration" section
3. **Check Health** - ensure providers show "✅ Healthy"
4. **Execute Agent** - select type, enter context, click "Execute Agent"
5. **View Results** - see recommendations, confidence, and execution time
6. **Review History** - check "Decision History" table for past executions

### Provider Configuration Panel

**Fields:**
- **Provider**: Select from dropdown (Ollama, OpenAI, Anthropic, etc.)
- **Model**: Enter model name (llama2, gpt-4, claude-3-sonnet)
- **Base URL**: Provider endpoint (default: http://localhost:11434 for Ollama)

**Actions:**
- Click "Configure Provider" to save
- Click "Refresh Health" to check status

### Agent Execution Panel

**Fields:**
- **Agent Type**: incident_analysis, root_cause, knowledge_base
- **Context (JSON)**: Provide agent-specific context

**Example Context:**
```json
{
  "incident_id": "INC-001",
  "description": "Server not responding",
  "priority": "high"
}
```

### Decision History

**Features:**
- View all past agent executions
- Filter by agent type
- Search by context
- Sort by timestamp
- Export to CSV

---

## Configuration

### LLM Provider Configuration File

`config/llm_providers.json`:

```json
{
  "providers": {
    "ollama": {
      "base_url": "http://localhost:11434",
      "default_model": "llama2",
      "timeout": 30,
      "enabled": true
    },
    "openai": {
      "api_key_env": "OPENAI_API_KEY",
      "default_model": "gpt-4",
      "organization_env": "OPENAI_ORG_ID",
      "timeout": 30,
      "enabled": false
    },
    "anthropic": {
      "api_key_env": "ANTHROPIC_API_KEY",
      "default_model": "claude-3-sonnet-20240229",
      "timeout": 30,
      "enabled": false
    }
  },
  "fallback_chain": ["ollama", "openai", "mock"],
  "default_provider": "ollama",
  "health_check_interval": 60,
  "max_retries": 3
}
```

### Environment Variables

Create `.env` file:

```bash
# OpenAI
OPENAI_API_KEY=sk-proj-...
OPENAI_ORG_ID=org-...

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Google
GOOGLE_API_KEY=AIza...

# Azure OpenAI
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=https://....openai.azure.com/

# HuggingFace
HUGGINGFACE_API_TOKEN=hf_...
```

### Agent-Specific Configuration

Each agent type supports different context parameters:

#### Incident Analysis Agent
```json
{
  "incident_id": "INC-001",
  "description": "Server not responding",
  "priority": "high|medium|low",
  "affected_users": 150,
  "category": "infrastructure"
}
```

#### Root Cause Analysis Agent
```json
{
  "incident_id": "INC-001",
  "symptoms": ["timeout", "503 errors"],
  "timeline": "2025-01-15T10:00:00Z",
  "related_changes": ["deploy-v1.2.3"]
}
```

#### Knowledge Base Agent
```json
{
  "query": "how to restart apache service",
  "category": "infrastructure",
  "limit": 5
}
```

---

## Troubleshooting

### Common Issues

#### 1. "Connection refused" when running agents

**Problem**: Ollama or API service not running

**Solution**:
```bash
# Check if Ollama is running
curl http://localhost:11434/api/version

# Start Ollama
ollama serve

# Check if API is running
curl http://localhost:8000/health
```

#### 2. "Model not found" error

**Problem**: Model not pulled in Ollama

**Solution**:
```bash
# List available models
ollama list

# Pull missing model
ollama pull llama2
ollama pull mistral
```

#### 3. "Provider unhealthy" status

**Problem**: LLM provider not responding

**Solution**:
```bash
# Check provider health
python cli.py agents:health

# Try fallback provider
python cli.py agents:configure-llm mock

# Check logs
tail -f logs/agent_orchestrator.log
```

#### 4. API key errors (OpenAI, Anthropic, etc.)

**Problem**: Missing or invalid API key

**Solution**:
```bash
# Check environment variables
echo $OPENAI_API_KEY

# Set in .env file
echo "OPENAI_API_KEY=sk-proj-..." >> .env

# Reload environment
source .env  # or restart terminal
```

#### 5. Slow agent execution

**Problem**: LLM provider is slow or timing out

**Solution**:
```json
// Increase timeout in config/llm_providers.json
{
  "providers": {
    "ollama": {
      "timeout": 60  // increased from 30
    }
  }
}
```

#### 6. "Agent type not found"

**Problem**: Invalid agent type specified

**Solution**:
```python
# Valid agent types:
# - incident_analysis
# - root_cause
# - knowledge_base

# Check available agents
python cli.py agents:list-providers
```

### Debug Mode

Enable verbose logging:

```bash
# Set environment variable
export REASONOPS_DEBUG=1

# Or in Python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Health Check

```bash
# Full system health check
python cli.py agents:health

# API health endpoint
curl http://localhost:8000/api/agents/health

# Check specific provider
curl http://localhost:11434/api/version  # Ollama
```

---

## Performance Tips

### 1. Use Local Models for Speed
- Ollama with llama2: ~2-5s response time
- OpenAI GPT-4: ~5-10s response time

### 2. Configure Timeouts
```json
{
  "providers": {
    "ollama": {
      "timeout": 30  // Balance between speed and reliability
    }
  }
}
```

### 3. Enable Caching
```python
# Cache LLM responses for repeated queries
from functools import lru_cache

@lru_cache(maxsize=100)
def get_llm_response(query: str) -> str:
    return llm.generate(query)
```

### 4. Use Streaming for Long Responses
```python
result = client.run_agents(
    agent_type="incident_analysis",
    context=context,
    stream=True  # Get results progressively
)
```

---

## Additional Resources

- 📖 **Full Documentation**: [README.md](README.md)
- 🚀 **Release Notes**: [RELEASE_NOTES.md](RELEASE_NOTES.md)
- 📝 **Changelog**: [CHANGELOG.md](CHANGELOG.md)
- 🤝 **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)
- 🔒 **Security**: [SECURITY.md](SECURITY.md)
- 🏷️ **Version Info**: [VERSION.md](VERSION.md)

---

**Need Help?**
- 🐛 [Report Issues](https://github.com/yasir2000/ReasonOps-ITSM/issues)
- 💬 [Ask Questions](https://github.com/yasir2000/ReasonOps-ITSM/discussions)
- 📧 Email: support@reasonops.io (if available)

**Happy Agent Building! 🤖✨**
