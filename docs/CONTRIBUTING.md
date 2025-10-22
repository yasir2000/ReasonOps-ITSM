# Contributing to ReasonOps ITSM

Thank you for your interest in contributing to ReasonOps ITSM! This document provides guidelines and instructions for contributing to the project.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Documentation](#documentation)
- [Community](#community)

## 🤝 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of:

- Age, body size, disability, ethnicity, gender identity and expression
- Level of experience, nationality, personal appearance, race, religion
- Sexual identity and orientation

### Our Standards

**Positive Behaviors:**
- ✅ Using welcoming and inclusive language
- ✅ Being respectful of differing viewpoints
- ✅ Gracefully accepting constructive criticism
- ✅ Focusing on what's best for the community
- ✅ Showing empathy towards others

**Unacceptable Behaviors:**
- ❌ Trolling, insulting/derogatory comments, personal or political attacks
- ❌ Public or private harassment
- ❌ Publishing others' private information without permission
- ❌ Other conduct which could reasonably be considered inappropriate

## 🚀 Getting Started

### Prerequisites

- **Python**: 3.9 or higher
- **Node.js**: 18 or higher
- **Git**: Latest version
- **VS Code** (recommended) or your preferred IDE

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:

```bash
git clone https://github.com/YOUR_USERNAME/ReasonOps-ITSM.git
cd ReasonOps-ITSM
```

3. Add upstream remote:

```bash
git remote add upstream https://github.com/yasir2000/ReasonOps-ITSM.git
```

4. Create a feature branch:

```bash
git checkout -b feature/your-feature-name
```

## 🛠️ Development Setup

### Backend Setup

1. **Create virtual environment:**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development tools
```

3. **Run backend:**

```bash
cd api
uvicorn main:app --reload --port 8000
```

### Frontend Setup

1. **Install dependencies:**

```bash
cd webapp
npm install
```

2. **Run development server:**

```bash
npm run dev
```

3. **Access the app:**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### AI Agents Setup (Optional)

1. **Install Ollama** (for local LLMs):

```bash
# On macOS/Linux
curl -fsSL https://ollama.com/install.sh | sh

# On Windows
# Download from https://ollama.com/download
```

2. **Pull models:**

```bash
ollama pull llama2
ollama pull mistral
```

3. **Configure providers** in `config/llm_providers.json`

## 🔧 Making Changes

### Branch Naming

Use descriptive branch names:

- `feature/add-incident-automation` - New features
- `fix/resolve-api-timeout` - Bug fixes
- `docs/update-readme` - Documentation
- `refactor/optimize-queries` - Code refactoring
- `test/add-integration-tests` - Test additions

### Development Workflow

1. **Sync with upstream:**

```bash
git fetch upstream
git rebase upstream/main
```

2. **Make your changes:**
   - Write clean, readable code
   - Follow existing patterns
   - Add comments for complex logic

3. **Test your changes:**

```bash
# Python tests
pytest tests/ -v

# Webapp tests
cd webapp && npm test

# Integration tests
pytest tests/integration/ -v
```

4. **Lint your code:**

```bash
# Python
black .
ruff check .

# TypeScript
cd webapp && npm run lint
```

## 📏 Coding Standards

### Python Style Guide

Follow **PEP 8** with these conventions:

```python
# Good: Clear function names, type hints
def calculate_sla_compliance(
    incidents: list[Incident],
    sla_threshold: float = 0.95
) -> SLAReport:
    """Calculate SLA compliance for incidents.
    
    Args:
        incidents: List of incidents to analyze
        sla_threshold: Minimum acceptable compliance (default: 0.95)
        
    Returns:
        SLAReport containing compliance metrics
    """
    compliant = [i for i in incidents if i.resolved_within_sla]
    compliance_rate = len(compliant) / len(incidents)
    
    return SLAReport(
        total_incidents=len(incidents),
        compliant_incidents=len(compliant),
        compliance_rate=compliance_rate,
        meets_threshold=compliance_rate >= sla_threshold
    )
```

**Key Points:**
- Use type hints for function parameters and return values
- Write docstrings for public functions (Google style)
- Max line length: 100 characters
- Use `black` for formatting
- Use `ruff` for linting

### TypeScript Style Guide

Follow **ESLint config** with these conventions:

```typescript
// Good: Typed props, clear component structure
interface AgentExecutionProps {
  agentType: string;
  context: Record<string, any>;
  onComplete?: (result: AgentResult) => void;
}

export const AgentExecution: React.FC<AgentExecutionProps> = ({
  agentType,
  context,
  onComplete
}) => {
  const [isRunning, setIsRunning] = useState(false);
  const [result, setResult] = useState<AgentResult | null>(null);
  
  const handleExecute = async () => {
    setIsRunning(true);
    try {
      const response = await fetch('/api/agents/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ agent_type: agentType, context })
      });
      
      const data = await response.json();
      setResult(data);
      onComplete?.(data);
    } catch (error) {
      console.error('Agent execution failed:', error);
    } finally {
      setIsRunning(false);
    }
  };
  
  return (
    <div className="agent-execution">
      <button onClick={handleExecute} disabled={isRunning}>
        {isRunning ? 'Running...' : 'Execute Agent'}
      </button>
      {result && <AgentResultView result={result} />}
    </div>
  );
};
```

**Key Points:**
- Use TypeScript for all new code
- Define interfaces for props and data structures
- Use functional components with hooks
- Prefer `const` over `let`, avoid `var`
- Use async/await over promises

### File Organization

```
project/
├── api/                    # FastAPI backend
│   ├── main.py            # Main API entry point
│   ├── routes/            # API route modules
│   └── models/            # Pydantic models
├── python-framework/       # Core ITSM framework
│   ├── ai_agents/         # AI agent implementations
│   ├── services/          # Business logic
│   └── models/            # Data models
├── webapp/                 # React frontend
│   ├── src/
│   │   ├── components/    # Reusable components
│   │   ├── pages/         # Page components
│   │   └── hooks/         # Custom hooks
│   └── public/            # Static assets
├── tests/                  # Python tests
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── fixtures/          # Test fixtures
└── docs/                   # Documentation
```

## 🧪 Testing

### Writing Tests

**Python Tests (pytest):**

```python
import pytest
from python_framework.ai_agents import AgentOrchestrator

@pytest.fixture
def orchestrator():
    """Create test orchestrator instance."""
    return AgentOrchestrator(
        llm_config_file="config/test_llm_providers.json"
    )

def test_incident_analysis_agent(orchestrator):
    """Test incident analysis agent execution."""
    context = {
        "incident_id": "INC-123",
        "description": "Server not responding",
        "priority": "high"
    }
    
    result = orchestrator.run_agent(
        agent_type="incident_analysis",
        context=context
    )
    
    assert result["status"] == "success"
    assert "recommendations" in result
    assert len(result["recommendations"]) > 0
```

**TypeScript Tests (Jest + React Testing Library):**

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { AgentsPage } from '../pages/AgentsPage';

describe('AgentsPage', () => {
  it('executes agent and displays results', async () => {
    render(<AgentsPage />);
    
    // Select agent type
    const agentSelect = screen.getByLabelText(/agent type/i);
    fireEvent.change(agentSelect, { target: { value: 'incident_analysis' } });
    
    // Enter context
    const contextInput = screen.getByLabelText(/context/i);
    fireEvent.change(contextInput, {
      target: { value: '{"incident_id": "INC-123"}' }
    });
    
    // Execute
    const executeButton = screen.getByRole('button', { name: /execute/i });
    fireEvent.click(executeButton);
    
    // Wait for results
    await waitFor(() => {
      expect(screen.getByText(/recommendations/i)).toBeInTheDocument();
    });
  });
});
```

### Test Coverage

Aim for **80%+ coverage** on new code:

```bash
# Python coverage
pytest --cov=python_framework --cov-report=html tests/

# TypeScript coverage
cd webapp && npm run test:coverage
```

### Running Tests

```bash
# All Python tests
pytest tests/ -v

# Specific test file
pytest tests/test_agents.py -v

# Specific test
pytest tests/test_agents.py::TestLLMRouter::test_health_check -v

# All webapp tests
cd webapp && npm test

# Watch mode
cd webapp && npm test -- --watch
```

## 📝 Commit Guidelines

### Conventional Commits

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**

```bash
# Feature
git commit -m "feat(agents): add knowledge base retrieval agent"

# Bug fix
git commit -m "fix(api): resolve timeout in incident creation endpoint"

# Documentation
git commit -m "docs(readme): update AI agent configuration section"

# Breaking change
git commit -m "feat(api)!: change incident API response format

BREAKING CHANGE: Incident API now returns ISO 8601 timestamps"
```

### Commit Best Practices

- ✅ Make atomic commits (one logical change per commit)
- ✅ Write clear, descriptive commit messages
- ✅ Reference issue numbers: `fix(api): resolve timeout (#123)`
- ✅ Explain *why*, not just *what*
- ❌ Don't commit commented-out code
- ❌ Don't commit sensitive data (API keys, passwords)

## 🔄 Pull Request Process

### Before Submitting

1. **Update from upstream:**

```bash
git fetch upstream
git rebase upstream/main
```

2. **Run full test suite:**

```bash
pytest tests/ -v && cd webapp && npm test
```

3. **Lint your code:**

```bash
black . && ruff check . && cd webapp && npm run lint
```

4. **Update documentation** if needed

### Creating a Pull Request

1. **Push to your fork:**

```bash
git push origin feature/your-feature-name
```

2. **Create PR on GitHub:**
   - Provide a clear title
   - Fill out the PR template
   - Reference related issues
   - Add screenshots for UI changes

3. **PR Template:**

```markdown
## Description
Brief description of changes

## Related Issues
Fixes #123

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] All tests pass
- [ ] Added new tests
- [ ] Manual testing completed

## Screenshots (if applicable)
[Add screenshots here]

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
```

### Review Process

1. **Automated checks** must pass (CI/CD)
2. **At least one maintainer** reviews your PR
3. Address review feedback promptly
4. Once approved, maintainers will merge

### After Merge

1. **Delete your branch:**

```bash
git branch -d feature/your-feature-name
git push origin --delete feature/your-feature-name
```

2. **Update your fork:**

```bash
git checkout main
git pull upstream main
git push origin main
```

## 📚 Documentation

### Inline Comments

```python
# Good: Explains WHY, not WHAT
# Use exponential backoff to avoid overwhelming the LLM provider
# when it's experiencing temporary issues
retry_delay = base_delay * (2 ** attempt)

# Bad: States the obvious
# Multiply base_delay by 2 to the power of attempt
retry_delay = base_delay * (2 ** attempt)
```

### README Updates

Update README.md when adding:
- New features or capabilities
- Configuration options
- Dependencies
- Breaking changes

### API Documentation

Document API endpoints with OpenAPI:

```python
@app.post("/api/agents/run", response_model=AgentResult)
async def run_agent(
    agent_type: str,
    context: dict,
) -> AgentResult:
    """Execute an AI agent with given context.
    
    Args:
        agent_type: Type of agent to run (incident_analysis, root_cause, etc.)
        context: Context dictionary with agent-specific parameters
        
    Returns:
        AgentResult with execution status and results
        
    Raises:
        HTTPException: If agent type is invalid or execution fails
        
    Example:
        ```json
        {
          "agent_type": "incident_analysis",
          "context": {
            "incident_id": "INC-123",
            "description": "Server not responding"
          }
        }
        ```
    """
    # Implementation
```

## 🌍 Community

### Getting Help

- 📖 Check the [documentation](README.md)
- 💬 Join [GitHub Discussions](https://github.com/yasir2000/ReasonOps-ITSM/discussions)
- 🐛 Search [existing issues](https://github.com/yasir2000/ReasonOps-ITSM/issues)
- ❓ Ask questions in discussions

### Reporting Bugs

Use the bug report template and include:
- Clear, descriptive title
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Logs or error messages
- Screenshots if applicable

### Requesting Features

Use the feature request template and include:
- Clear use case description
- Why this feature would be valuable
- Proposed implementation (optional)
- Alternatives considered

### Areas We Need Help

We especially welcome contributions in:

- 🐛 **Bug Fixes**: Check [good first issue](https://github.com/yasir2000/ReasonOps-ITSM/labels/good%20first%20issue) label
- 📝 **Documentation**: Improve guides, add examples
- 🧪 **Testing**: Increase coverage, add integration tests
- 🌐 **Internationalization**: Translate UI to other languages
- 🎨 **UI/UX**: Improve design and user experience
- 🤖 **AI Agents**: Add new agent types and capabilities
- 🔌 **Integrations**: Connect with other ITSM platforms
- ⚡ **Performance**: Optimize slow operations
- 🔒 **Security**: Identify and fix vulnerabilities

## 🎉 Recognition

Contributors are recognized in:
- [CONTRIBUTORS.md](CONTRIBUTORS.md)
- Release notes
- Annual contributor highlights

Thank you for contributing to ReasonOps ITSM! 🚀
