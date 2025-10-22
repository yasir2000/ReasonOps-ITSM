# ReasonOps ITSM Version Information

## Current Release: v0.2.0
**Release Date:** January 2025
**Release Type:** Minor Release (Feature Addition)

## Component Versions

### Core Components
- **ReasonOps SDK**: 0.2.0
- **ReasonOps Web UI**: 0.2.0
- **ReasonOps API**: 0.2.0
- **Python Framework**: 0.2.0

### Runtime Requirements
- **Python**: >=3.9, <4.0
- **Node.js**: >=18.0.0
- **React**: ^18.3.1
- **FastAPI**: ^0.115.12

## Version History

### v0.2.0 - January 2025
**Major Features:**
- ✨ AI Agent Infrastructure with multi-LLM support
- 🔄 LLM Router with health monitoring and fallbacks
- 🌐 7 LLM Provider integrations (Ollama, OpenAI, Anthropic, Google, Azure, HuggingFace, Mock)
- 📡 5 new API endpoints for agent operations
- 💻 5 new CLI commands for agent management
- 🔧 5 new SDK methods for programmatic access
- 🎨 Complete Agent UI redesign with real-time monitoring
- 🧪 Comprehensive test suite (21 passing tests)

**Improvements:**
- Enhanced error handling in API layer
- Improved streaming support for LLM responses
- Better health monitoring across all components
- Increased test coverage to 80%+

**Bug Fixes:**
- Fixed async orchestrator initialization
- Resolved ModelType enum issues
- Fixed event bus attribute access
- Corrected test assertions for provider counts

**Documentation:**
- Added comprehensive AI Agent setup guide
- Created CHANGELOG.md and RELEASE_NOTES.md
- Updated README with badges, TOC, and examples
- Added CONTRIBUTING.md with detailed guidelines

**Breaking Changes:**
- None (backward compatible with v0.1.0)

### v0.1.0 - December 2024
**Initial Release:**
- 📊 Core ITSM framework (Incident, Problem, Change management)
- 🔧 Python SDK for ITSM operations
- 🌐 FastAPI REST API
- 💻 Basic CLI interface
- 🎨 React-based web UI
- 📈 SLA/SLO monitoring
- 🔒 Multi-tenant support
- 🧪 Initial test suite

## Compatibility Matrix

| Component | Python | Node.js | React | FastAPI |
|-----------|--------|---------|-------|---------|
| v0.2.0 | >=3.9 | >=18.0 | ^18.3 | ^0.115 |
| v0.1.0 | >=3.9 | >=16.0 | ^18.2 | ^0.100 |

## LLM Provider Support (v0.2.0)

| Provider | Status | Models | License |
|----------|--------|--------|---------|
| Ollama | ✅ Stable | llama2, mistral, etc. | MIT |
| OpenAI | ✅ Stable | gpt-4, gpt-3.5-turbo | Proprietary |
| Anthropic | ✅ Stable | claude-3, claude-2 | Proprietary |
| Google | ✅ Beta | gemini-pro | Proprietary |
| Azure OpenAI | ✅ Beta | gpt-4, gpt-35-turbo | Proprietary |
| HuggingFace | ⚠️ Experimental | Various | Various |
| Mock | ✅ Stable | mock-model | N/A |

## Upgrade Paths

### From v0.1.0 to v0.2.0

**No breaking changes** - fully backward compatible.

**Optional Enhancements:**
1. Install AI dependencies: `pip install openai anthropic google-generativeai`
2. Configure LLM providers: Copy `config/llm_providers.json.example`
3. Install Ollama for local LLMs (optional)
4. Explore new agent endpoints and CLI commands

**Migration Steps:**
```bash
# 1. Backup existing data
cp -r data/ data.backup/

# 2. Pull latest code
git pull origin main

# 3. Update Python dependencies
pip install -r requirements.txt

# 4. Update webapp dependencies
cd webapp && npm install

# 5. Run tests to verify
pytest tests/ -v
cd webapp && npm test

# 6. Restart services
# Backend
cd api && uvicorn main:app --reload

# Frontend
cd webapp && npm run dev
```

## Release Schedule

- **Major Releases** (x.0.0): Yearly - Breaking changes, major features
- **Minor Releases** (0.x.0): Quarterly - New features, backward compatible
- **Patch Releases** (0.0.x): Monthly - Bug fixes, security updates

## Planned Releases

### v0.3.0 (Planned: Q2 2025)
- Advanced agent orchestration with workflows
- Knowledge base integration
- Enhanced analytics and reporting
- Multi-language support (i18n)
- Advanced RBAC (Role-Based Access Control)

### v0.4.0 (Planned: Q3 2025)
- GraphQL API support
- Real-time collaboration features
- Mobile app (React Native)
- Advanced automation rules
- Integration marketplace

### v1.0.0 (Planned: Q4 2025)
- Production-ready enterprise features
- Certified security compliance
- Advanced multi-tenancy
- High-availability clustering
- Professional support options

## Support Policy

### Active Support
- **v0.2.x**: Full support (current)
- **v0.1.x**: Security updates until Q2 2025

### End of Life
- None yet

## Security Updates

See [SECURITY.md](SECURITY.md) for security policy and vulnerability reporting.

## Build Information

### Build Tools
- **Python Build**: hatchling >=1.25.0
- **TypeScript Build**: Vite ^5.4
- **Test Framework**: pytest + vitest

### CI/CD
- **GitHub Actions**: Automated testing on push/PR
- **Test Coverage**: 80%+ required for merge
- **Linting**: black, ruff (Python), ESLint (TypeScript)

## License

Apache License 2.0 - See [LICENSE](LICENSE) file

## Contact

- **Repository**: https://github.com/yasir2000/ReasonOps-ITSM
- **Issues**: https://github.com/yasir2000/ReasonOps-ITSM/issues
- **Discussions**: https://github.com/yasir2000/ReasonOps-ITSM/discussions

---

**Last Updated:** January 2025
