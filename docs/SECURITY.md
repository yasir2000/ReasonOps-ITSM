# Security Policy

## Supported Versions

We release security updates for the following versions:

| Version | Supported          | Support Until |
| ------- | ------------------ | ------------- |
| 0.2.x   | ✅ Full support    | Current       |
| 0.1.x   | ⚠️ Security only   | Q2 2025       |
| < 0.1   | ❌ Not supported   | N/A           |

## Reporting a Vulnerability

**Please do NOT report security vulnerabilities through public GitHub issues.**

### Preferred Reporting Method

Email security reports to: **security@reasonops.io** (if available)

Or create a private security advisory on GitHub:
1. Go to https://github.com/yasir2000/ReasonOps-ITSM/security/advisories
2. Click "Report a vulnerability"
3. Fill out the form with details

### What to Include

Please include the following information:

- **Type of issue** (e.g., SQL injection, XSS, authentication bypass)
- **Full paths** of source file(s) related to the issue
- **Location** of affected source code (tag/branch/commit or direct URL)
- **Step-by-step instructions** to reproduce the issue
- **Proof-of-concept or exploit code** (if possible)
- **Impact** of the issue and potential exploit scenarios
- **Your contact information**

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 1 week
- **Fix Timeline**: Varies by severity
  - **Critical**: 7-14 days
  - **High**: 14-30 days
  - **Medium**: 30-60 days
  - **Low**: Next regular release

## Security Best Practices

### For Users

#### API Security
```python
# ✅ Good: Use environment variables for secrets
import os
from reasonops_sdk import ReasonOpsClient

client = ReasonOpsClient(
    base_url=os.getenv("REASONOPS_API_URL"),
    api_key=os.getenv("REASONOPS_API_KEY")
)

# ❌ Bad: Hardcoded credentials
client = ReasonOpsClient(
    base_url="http://localhost:8000",
    api_key="hardcoded-secret-key-123"
)
```

#### LLM Provider Configuration
```json
// ✅ Good: Store API keys in environment variables
{
  "providers": {
    "openai": {
      "api_key_env": "OPENAI_API_KEY",
      "organization_env": "OPENAI_ORG_ID"
    }
  }
}

// ❌ Bad: API keys in config files
{
  "providers": {
    "openai": {
      "api_key": "sk-proj-abc123...",
      "organization": "org-xyz789..."
    }
  }
}
```

#### Input Validation
```python
# ✅ Good: Validate and sanitize user input
from pydantic import BaseModel, validator

class IncidentCreate(BaseModel):
    title: str
    description: str
    
    @validator('title')
    def validate_title(cls, v):
        if len(v) > 200:
            raise ValueError('Title too long')
        # Sanitize HTML/script tags
        return v.replace('<', '&lt;').replace('>', '&gt;')

# ❌ Bad: Direct database queries with user input
cursor.execute(f"SELECT * FROM incidents WHERE title = '{user_input}'")
```

### For Developers

#### Authentication
- Use strong password hashing (bcrypt, argon2)
- Implement rate limiting on authentication endpoints
- Use secure session management
- Enable multi-factor authentication (MFA) where possible

#### Authorization
- Follow principle of least privilege
- Validate permissions on every request
- Use role-based access control (RBAC)
- Implement proper tenant isolation in multi-tenant scenarios

#### Data Protection
- Encrypt sensitive data at rest
- Use TLS/SSL for data in transit
- Implement proper key management
- Regular security audits of dependencies

#### Code Security
```python
# ✅ Good: Parameterized queries
from sqlalchemy import text

query = text("SELECT * FROM incidents WHERE id = :id")
result = session.execute(query, {"id": incident_id})

# ❌ Bad: String interpolation
query = f"SELECT * FROM incidents WHERE id = {incident_id}"
result = session.execute(query)
```

#### Dependency Management
```bash
# Check for vulnerabilities regularly
pip-audit

# Update dependencies
pip install --upgrade -r requirements.txt

# Lock dependency versions in production
pip freeze > requirements.lock
```

## Known Security Considerations

### AI Agent Security

#### Prompt Injection
**Risk**: Malicious users may attempt to inject commands into LLM prompts.

**Mitigation**:
- Input sanitization on all user-provided context
- System prompts with clear boundaries
- Output validation and filtering
- Rate limiting on agent execution

```python
# ✅ Good: Sanitize context before sending to LLM
def sanitize_context(context: dict) -> dict:
    """Remove potentially dangerous content from context."""
    safe_context = {}
    for key, value in context.items():
        if isinstance(value, str):
            # Remove common injection patterns
            value = value.replace("IGNORE PREVIOUS", "")
            value = value.replace("SYSTEM:", "")
        safe_context[key] = value
    return safe_context

context = sanitize_context(user_provided_context)
result = agent.execute(context)
```

#### Data Leakage
**Risk**: Sensitive data may be sent to external LLM providers.

**Mitigation**:
- Use local LLMs (Ollama) for sensitive data
- Implement data classification and filtering
- Audit logs for all LLM interactions
- Data anonymization before LLM processing

```python
# ✅ Good: Classify and filter sensitive data
def prepare_context_for_llm(incident: Incident) -> dict:
    """Prepare incident context, removing PII."""
    return {
        "incident_id": incident.id,
        "priority": incident.priority,
        "category": incident.category,
        # Exclude: user names, emails, IP addresses
        "description": anonymize_text(incident.description)
    }
```

#### Model Hallucination
**Risk**: LLMs may generate false information presented as fact.

**Mitigation**:
- Always validate LLM outputs
- Use retrieval-augmented generation (RAG)
- Implement confidence scoring
- Human-in-the-loop for critical decisions

```python
# ✅ Good: Validate LLM recommendations
def validate_recommendation(recommendation: str, incident: Incident) -> bool:
    """Validate that recommendation is safe and applicable."""
    # Check against known good patterns
    if not matches_incident_pattern(recommendation, incident):
        return False
    
    # Check for dangerous operations
    if contains_dangerous_operations(recommendation):
        return False
    
    return True

if validate_recommendation(llm_output, incident):
    apply_recommendation(llm_output)
else:
    flag_for_review(llm_output)
```

### API Security

#### Rate Limiting
Implemented on all endpoints to prevent abuse:
- Authentication: 5 requests/minute
- Agent execution: 10 requests/minute
- General API: 100 requests/minute

#### CORS Configuration
```python
# Production: Restrict origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

### Web Application Security

#### Content Security Policy
```html
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; 
               script-src 'self'; 
               style-src 'self' 'unsafe-inline'; 
               img-src 'self' data: https:;">
```

#### XSS Prevention
All user input is sanitized in React components:
```typescript
// React automatically escapes content
<div>{userInput}</div>

// ✅ Good: Use dangerouslySetInnerHTML sparingly with sanitization
import DOMPurify from 'dompurify';

<div dangerouslySetInnerHTML={{
  __html: DOMPurify.sanitize(htmlContent)
}} />
```

## Security Testing

### Automated Security Scans

```bash
# Python dependency scanning
pip-audit

# Python code security analysis
bandit -r python-framework/ api/

# Node.js dependency scanning
cd webapp && npm audit

# Fix vulnerabilities automatically
npm audit fix
```

### Manual Security Testing

Checklist for security review:
- [ ] Authentication mechanisms tested
- [ ] Authorization boundaries verified
- [ ] Input validation on all endpoints
- [ ] SQL injection tests passed
- [ ] XSS vulnerability tests passed
- [ ] CSRF protection verified
- [ ] Rate limiting functional
- [ ] Session management secure
- [ ] Dependencies up to date
- [ ] Security headers configured

## Compliance

### Data Privacy
- **GDPR**: Supports data export, deletion, and consent management
- **CCPA**: Provides user data access and deletion capabilities
- **SOC 2**: Working towards compliance (in progress)

### Logging and Auditing
- All authentication attempts logged
- Agent executions tracked with context
- API calls logged with user identity
- Sensitive data masked in logs

## Security Updates

Subscribe to security announcements:
- Watch this repository for security advisories
- Follow [@ReasonOps](https://twitter.com/reasonops) on Twitter (if available)
- Join our [Discord community](https://discord.gg/reasonops) (if available)

## Acknowledgments

We appreciate responsible disclosure and will acknowledge security researchers who report vulnerabilities:

- Your name will be listed in our security acknowledgments (with permission)
- CVE credit where applicable
- Swag/merch for significant findings (when available)

## Past Security Advisories

None yet - we're a new project! 🎉

---

**Last Updated:** January 2025

For questions about this security policy, contact: security@reasonops.io (or open a discussion on GitHub)
