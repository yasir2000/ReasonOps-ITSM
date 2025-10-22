# Changelog

All notable changes to the ReasonOps ITSM project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-10-22

### 🤖 AI Agent Integration - Major Release

This release introduces comprehensive AI agent capabilities with multi-LLM provider support, including local deployment with Ollama.

#### Added

**LLM Infrastructure**
- Enhanced LLM router with health monitoring (`python-framework/ai_agents/llm_router.py`)
- Automatic health checks for all configured providers
- Intelligent fallback chain (Ollama → OpenAI → Mock)
- Streaming response support for real-time agent output
- Provider status tracking (healthy/degraded/unhealthy)
- Latency monitoring and error counting
- Connection pooling and rate limiting

**API Endpoints**
- `POST /api/agents/run` - Execute AI agent orchestration for events
- `GET /api/agents/decisions` - Retrieve agent decision history with filters
- `POST /api/agents/configure-llm` - Configure active LLM provider
- `GET /api/agents/health` - Check health of all LLM providers
- `GET /api/agents/providers` - List available providers and models

**CLI Commands**
- `agents:run` - Execute agent orchestration from command line
- `agents:list-decisions` - View agent decision history
- `agents:configure-llm` - Configure LLM provider settings
- `agents:health` - Check provider health status
- `agents:list-providers` - List available LLM providers and models

**SDK Methods** (`reasonops_sdk.ReasonOpsClient`)
- `run_agents()` - Execute agent orchestration
- `get_agent_decisions()` - Retrieve decision history
- `configure_llm_provider()` - Configure LLM settings
- `check_agent_health()` - Monitor provider health
- `list_llm_providers()` - List available options

**Web UI**
- Complete agent management dashboard (`webapp/src/pages/AgentsPage.tsx`)
- LLM provider configuration panel with dropdown selectors
- Real-time provider health monitoring with status indicators
- Agent execution panel for triggering workflows
- Decision history table with filtering and pagination
- Toast notifications for user feedback
- Support for multiple event types (incident, capacity_alert, outage, etc.)

**Testing**
- Comprehensive Python test suite (`tests/test_agents.py`)
  - LLM router tests (initialization, health checks, fallbacks)
  - Agent orchestration tests
  - SDK method tests
  - 13 passing tests, 2 skipped
- Complete webapp test suite (`webapp/src/__tests__/agents.test.tsx`)
  - UI component tests
  - Provider configuration tests
  - Decision history tests
  - 8 passing tests

**Documentation**
- AI Agent Setup section in README with Ollama quickstart
- SDK usage examples for all agent methods
- CLI command reference with examples
- API endpoint documentation with curl examples
- Architecture overview and configuration guide
- Multi-provider setup instructions

**LLM Provider Support**
- **Ollama** (local): llama2-7b, mistral-7b, codellama, llama2-13b
- **OpenAI** (cloud): gpt-4, gpt-4-turbo, gpt-3.5-turbo
- **Anthropic** (cloud): claude-3-opus, claude-3-sonnet, claude-3-haiku
- **Google** (cloud): gemini-pro, gemini-pro-vision
- **Azure OpenAI** (enterprise): gpt-4, gpt-35-turbo
- **HuggingFace** (custom): any model via API
- **Mock** (testing): mock-model for development

#### Changed
- Updated `api/main.py` with agent endpoints and lazy initialization
- Enhanced `reasonops_sdk/client.py` with 5 new agent methods
- Extended `python-framework/cli.py` with 5 new agent commands
- Upgraded `webapp/src/pages/AgentsPage.tsx` from basic to full-featured dashboard
- Added `pytest-asyncio` support in `pyproject.toml`

#### Fixed
- Async test support with pytest-asyncio configuration
- Provider health tracking for duplicate provider names
- Test assertions for variable provider counts
- UI test selectors for elements with duplicate text

### Technical Details

**Dependencies Added**
- `pytest-asyncio` for async test support

**Configuration**
- Added `asyncio_mode = "auto"` to pytest configuration
- Added `asyncio_default_fixture_loop_scope = "function"`

**Breaking Changes**
- None - all changes are additive

### Migration Guide

For users upgrading from 0.1.0:

1. **Install Ollama (optional, for local LLM)**:
   ```bash
   # Visit https://ollama.com/download
   ollama pull llama2:7b
   ollama serve
   ```

2. **Update dependencies**:
   ```bash
   pip install -r api/requirements.txt
   cd webapp && npm install
   ```

3. **Configure LLM provider** (choose one):
   ```python
   from reasonops_sdk import ReasonOpsClient
   
   client = ReasonOpsClient()
   
   # Option 1: Local with Ollama
   client.configure_llm_provider(provider='ollama', model='llama2-7b')
   
   # Option 2: Cloud with OpenAI
   client.configure_llm_provider(provider='openai', model='gpt-4', api_key='sk-...')
   ```

4. **Access new features**:
   - Web UI: http://localhost:5173/agents
   - API: http://localhost:8000/api/agents/*
   - CLI: `python -m cli agents:health`
   - SDK: See documentation above

## [0.1.0] - 2025-10-15

### Initial Release

#### Added
- Complete ITIL 4 framework implementation
- Python SDK (`reasonops-sdk`) with packaging and CI/CD
- FastAPI backend with ITSM endpoints
- React + TypeScript frontend with Vite
- Dashboard, SLM, Capacity, Financials, Agents, Exports pages
- Chart integration with react-chartjs-2
- Authentication scaffolding with role-based access
- Toast notification system
- Comprehensive test infrastructure (pytest, vitest)
- GitHub Actions workflows (SDK CI, Webapp CI)
- DevContainer configuration
- Apache 2.0 license
- Complete documentation in README

#### Initial Features
- Service catalog management
- SLM metrics tracking
- Capacity planning
- Financial operations (penalties, chargebacks)
- Monthly summary exports
- JSON-based storage with rollups
- Mock fallback for development

---

## Version History

- **0.2.0** (2025-10-22) - AI Agent Integration with Multi-LLM Support
- **0.1.0** (2025-10-15) - Initial Release

## Links

- [GitHub Repository](https://github.com/yasir2000/ReasonOps-ITSM)
- [Issue Tracker](https://github.com/yasir2000/ReasonOps-ITSM/issues)
- [Documentation](README.md)
