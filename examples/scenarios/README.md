# ReasonOps ITSM - End-to-End Scenarios

This directory contains complete, executable scenario demonstrations of ReasonOps ITSM with AI Agents.

## 🎯 Overview

Each scenario demonstrates a complete workflow from problem detection to resolution, showcasing:
- Real-world ITSM challenges
- AI-powered analysis and recommendations
- Automated response and remediation
- Complete audit trail and documentation

## 📚 Available Scenarios

### 1. Critical Production Outage (`scenario1_production_outage.py`)
**Situation:** Web application returning 503 errors, 5,000 users affected  
**Duration:** ~12 minutes resolution time  
**Demonstrates:**
- Automated incident creation
- AI-powered root cause analysis
- Emergency rollback procedures
- Service restoration verification
- Post-incident documentation
- Problem management integration

**Run it:**
```bash
python examples/scenarios/scenario1_production_outage.py
```

**Key Features:**
- ✅ 92% AI accuracy in root cause identification
- ✅ 12-minute end-to-end resolution
- ✅ SLA compliance demonstrated
- ✅ Complete incident lifecycle

### 2. Database Performance Degradation (`scenario2_database_performance.py`)
**Situation:** Database query response time increased by 400%  
**Duration:** ~47 minutes resolution time  
**Demonstrates:**
- Performance monitoring and alerts
- AI-powered performance analysis
- Knowledge base integration
- Change management for optimization
- Real-time performance monitoring
- Proactive optimization recommendations

**Run it:**
```bash
python examples/scenarios/scenario2_database_performance.py
```

**Key Features:**
- ✅ 89% AI confidence in diagnosis
- ✅ 95% performance improvement
- ✅ Zero-downtime optimization
- ✅ Proactive prevention suggestions

### 3. Security Incident Response (`scenario3_security_incident.py`)
**Situation:** Brute force attack - 500 failed login attempts  
**Duration:** ~15 minutes response time  
**Demonstrates:**
- Automated security threat detection
- AI-powered threat analysis
- Automated incident response
- Continuous attack monitoring
- Forensic analysis
- Security hardening recommendations

**Run it:**
```bash
python examples/scenarios/scenario3_security_incident.py
```

**Key Features:**
- ✅ 2-minute detection to mitigation
- ✅ 100% automated response
- ✅ Zero compromised accounts
- ✅ Complete forensic trail

## 🚀 Quick Start

### Prerequisites

1. **Backend API running:**
```bash
cd api
uvicorn main:app --reload --port 8000
```

2. **Ollama installed (optional but recommended):**
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull llama2
```

3. **Python dependencies:**
```bash
pip install -r requirements.txt
```

### Running Scenarios

**Individual scenario:**
```bash
python examples/scenarios/scenario1_production_outage.py
```

**Run all scenarios:**
```bash
cd examples/scenarios
for scenario in scenario*.py; do
    echo "Running $scenario..."
    python "$scenario"
    echo ""
done
```

**With verbose output:**
```bash
REASONOPS_DEBUG=1 python examples/scenarios/scenario1_production_outage.py
```

## 📖 Scenario Structure

Each scenario follows this pattern:

```python
#!/usr/bin/env python3
"""
Scenario N: Descriptive Title
Brief description of what this scenario demonstrates.
"""

# 1. Setup and initialization
# 2. Problem detection
# 3. AI analysis
# 4. Response/remediation
# 5. Verification
# 6. Documentation
# 7. Prevention/improvement
# 8. Summary report
```

## 🎓 Learning Paths

### For New Users
Start with:
1. `scenario1_production_outage.py` - Basic incident response
2. `scenario2_database_performance.py` - Performance optimization
3. Explore the web UI at http://localhost:5173/agents

### For Developers
Focus on:
1. Code structure in each scenario
2. SDK usage patterns
3. AI agent integration
4. Error handling patterns

### For Operations
Analyze:
1. SLA compliance tracking
2. Automated response workflows
3. Change management integration
4. Metrics and reporting

## 📊 Scenario Comparison

| Scenario | Type | AI Accuracy | Automation | Time Saved |
|----------|------|-------------|------------|------------|
| 1. Production Outage | Incident | 92% | 80% | ~20 min |
| 2. DB Performance | Problem | 89% | 70% | ~2 hours |
| 3. Security Attack | Security | 91% | 100% | ~30 min |

## 🛠️ Customization

### Modify Scenario Parameters

Edit the scenario file and change variables:

```python
# In scenario1_production_outage.py
incident_data = {
    "title": "YOUR CUSTOM TITLE",
    "priority": "high",  # Change to: low, medium, high, critical
    "affected_users": 1000,  # Change impact
    # ... modify other fields
}
```

### Create Custom Scenarios

1. Copy an existing scenario:
```bash
cp scenario1_production_outage.py scenario4_custom.py
```

2. Modify the workflow:
- Change incident type
- Add custom analysis steps
- Implement different resolution strategies
- Add custom metrics

3. Test your scenario:
```bash
python examples/scenarios/scenario4_custom.py
```

## 📝 Sample Output

### Scenario 1 Output:
```
======================================================================
  SCENARIO 1: Critical Production Outage
======================================================================

🚨 Simulating production incident response with AI agents
⏱️  Estimated runtime: 30 seconds

──────────────────────────────────────────────────────────────────────
STEP 1: Incident Detection & Creation
──────────────────────────────────────────────────────────────────────

📊 Monitoring Alert Received:
   - Service: web-app-prod
   - Error Rate: 98.5%
   - Status: All backends down
   - Impact: 5,000 users affected

Creating incident... ✓

✅ Incident Created: INC-2025-001
   Priority: CRITICAL
   Assigned: SRE On-Call Team
...
```

## 🔗 Integration Examples

### Use Scenarios in Testing

```python
# In your test suite
from examples.scenarios import scenario1_production_outage

def test_incident_response_workflow():
    # Run scenario and verify outcomes
    result = scenario1_production_outage.main()
    assert result.sla_met == True
    assert result.downtime_minutes < 15
```

### Extract Patterns for Your Code

```python
# Learn from scenario patterns
from reasonops_sdk import ReasonOpsClient

# Pattern from scenario1
def handle_production_incident(monitoring_data):
    client = ReasonOpsClient(base_url="http://localhost:8000")
    
    # Create incident
    incident = client.create_incident({
        "title": "...",
        "monitoring_data": monitoring_data
    })
    
    # AI analysis
    analysis = client.run_agents(
        agent_type="incident_analysis",
        context={"incident_id": incident['id']}
    )
    
    # Apply recommendations
    # ...
```

## 📚 Additional Resources

- **Full Documentation:** [README.md](../../README.md)
- **Quick Start Guide:** [QUICKSTART.md](../../docs/QUICKSTART.md)
- **Scenario Details:** [SCENARIOS.md](../../docs/SCENARIOS.md)
- **API Reference:** [README.md#api](../../README.md#-api)
- **SDK Guide:** [README.md#python-sdk](../../README.md#-python-sdk)

## 🤝 Contributing

Have a great scenario idea? Contribute it!

1. Create your scenario following the existing pattern
2. Add documentation
3. Test thoroughly
4. Submit a pull request

See [CONTRIBUTING.md](../../docs/CONTRIBUTING.md) for details.

## 💡 Tips & Tricks

### Speed Up Scenarios
```bash
# Skip delays for faster execution
SKIP_DELAYS=1 python examples/scenarios/scenario1_production_outage.py
```

### Debug Mode
```bash
# Enable verbose logging
export REASONOPS_DEBUG=1
python examples/scenarios/scenario1_production_outage.py
```

### Generate Reports
```bash
# Save output to file
python examples/scenarios/scenario1_production_outage.py > report.txt
```

## 🐛 Troubleshooting

**"Connection refused" error:**
- Ensure API is running: `cd api && uvicorn main:app --reload`
- Check API health: `curl http://localhost:8000/health`

**Slow execution:**
- This is normal - scenarios include realistic delays
- Use `SKIP_DELAYS=1` for faster runs (testing only)

**Import errors:**
- Ensure you're in the project root directory
- Install dependencies: `pip install -r requirements.txt`

## 📞 Support

- 🐛 [Report Issues](https://github.com/yasir2000/ReasonOps-ITSM/issues)
- 💬 [Ask Questions](https://github.com/yasir2000/ReasonOps-ITSM/discussions)
- 📖 [Read Docs](../../README.md)

---

**Built with ❤️ by the ReasonOps Team**

*Making ITSM accessible, intelligent, and open-source.*
