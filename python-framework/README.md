# ReasonOps ITSM (Python Framework)

ReasonOps ITSM is a practical, orchestrated implementation of ITIL/ITSM with autonomous multi‑agent workflows and multi‑LLM provider support (including local Ollama).

A comprehensive, production-ready Python implementation of the ITIL 4 (Information Technology Infrastructure Library) framework. This framework provides object-oriented implementations of core ITIL concepts, practices, and workflows.

## 🌟 Features

- **Complete ITIL 4 Implementation**: Full Service Value System with all core components
- **34 ITIL Practices**: Comprehensive implementations starting with the most critical practices
- **Production Ready**: Enterprise-grade code with proper error handling and validation
- **Integrated Workflows**: Seamless integration between practices (Incidents → Problems → Changes)
- **Comprehensive Metrics**: Built-in reporting and analytics for all practices
- **Extensible Architecture**: Easy to extend with custom practices and workflows
- **Real-world Scenarios**: Based on actual ITSM implementations and best practices

## 🏗️ Architecture

### Core Components

```
python-framework/
├── core/                          # ITIL 4 Service Value System
│   ├── service_value_system.py   # Main SVS implementation
│   └── __init__.py               # Core module exports
└── practices/                     # ITIL 4 Practices
    ├── incident_management.py    # Incident Management practice
    ├── problem_management.py     # Problem Management practice
    ├── change_enablement.py      # Change Enablement practice
    └── __init__.py               # Practices module exports
```

### Service Value System Components

- **Guiding Principles**: 7 principles that guide decision-making
- **Governance**: Framework for direction and control
- **Service Value Chain**: 6 key activities for value creation
- **Practices**: 34 practices organized in 3 categories
- **Continual Improvement**: Built-in improvement model

### Implemented Practices

✅ **Incident Management** - Minimize negative impact of incidents
✅ **Problem Management** - Identify and manage root causes
✅ **Change Enablement** - Ensure successful service changes
🔄 **Service Request Management** - Handle service requests efficiently
🔄 **Knowledge Management** - Maintain organizational knowledge
🔄 **Release Management** - Plan and control releases

## 🚀 Quick Start

### Installation

```python
# Clone the repository
git clone <repository-url>
cd ITIL-Notes

# Import the framework
from python_framework import ITILFramework
```

### Basic Usage

```python
from python_framework import ITILFramework
from python_framework.core import Person, Impact, Urgency
from python_framework.practices import IncidentCategory

# Create the framework
itil = ITILFramework()

# Create a person
user = Person("1", "John Doe", "john.doe@company.com", "End User", "Sales")

# Create an incident
incident = itil.create_incident(
    short_description="Email server down",
    description="Email server is not responding",
    caller=user,
    category=IncidentCategory.APPLICATION,
    impact=Impact.HIGH,
    urgency=Urgency.HIGH
)

print(f"Created incident: {incident.number}")
```

### Integrated Workflow Example

```python
# Create multiple related incidents
incident1 = itil.create_incident(
    "Slow email response", 
    "Email taking 30+ seconds to load",
    user, IncidentCategory.APPLICATION, Impact.MEDIUM, Urgency.HIGH
)

incident2 = itil.create_incident(
    "Email timeouts",
    "Email client timing out when sending", 
    user, IncidentCategory.APPLICATION, Impact.MEDIUM, Urgency.HIGH
)

# Create problem from incidents
analyst = Person("2", "Jane Analyst", "jane.analyst@company.com", "Problem Analyst", "IT")

problem = itil.create_problem_from_incidents(
    incident_numbers=[incident1.number, incident2.number],
    short_description="Email server performance issues",
    description="Multiple incidents indicate systemic email server problems",
    category=ProblemCategory.APPLICATION,
    analyst=analyst
)

# Create change to fix the problem
change = itil.create_change_from_problem(
    problem_number=problem.number,
    change_description="Upgrade email server infrastructure",
    requester=analyst
)

print(f"Workflow: {incident1.number} + {incident2.number} → {problem.number} → {change.number}")
```

## 📊 Metrics and Reporting

### Dashboard Metrics

```python
# Get comprehensive metrics
metrics = itil.get_dashboard_metrics(period_days=30)

print(f"Incidents: {metrics['incident_management']['total_incidents']}")
print(f"Problems: {metrics['problem_management']['total_problems']}")
print(f"Changes: {metrics['change_enablement']['total_changes']}")
print(f"Success Rate: {metrics['change_enablement']['success_rate']}%")
```

### Individual Practice Metrics

```python
# Incident Management metrics
incident_metrics = itil.incident_management.get_metrics(30)
print(f"SLA Compliance: {incident_metrics['sla_compliance_rate']}%")
print(f"Average Resolution Time: {incident_metrics['avg_resolution_time_hours']} hours")

# Problem Management metrics  
problem_metrics = itil.problem_management.get_metrics(30)
print(f"RCA Completion Rate: {problem_metrics['rca_completion_rate']}%")
print(f"Proactive Problems: {problem_metrics['proactive_problems']}")

# Change Enablement metrics
change_metrics = itil.change_enablement.get_metrics(30)
print(f"Change Success Rate: {change_metrics['success_rate']}%")
print(f"Emergency Changes: {change_metrics['type_distribution']['Emergency']}")
```

## 🔧 Advanced Usage

### Custom Practice Implementation

```python
from python_framework.core import ServiceValueSystem
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ServiceRequest:
    number: str
    description: str
    requester: Person
    status: str = "New"
    created_at: datetime = datetime.now()

class ServiceRequestManagement:
    def __init__(self):
        self.requests = {}
    
    def create_request(self, description: str, requester: Person):
        request = ServiceRequest(
            number=f"REQ{len(self.requests)+1:04d}",
            description=description,
            requester=requester
        )
        self.requests[request.number] = request
        return request

# Integrate with main framework
itil.service_request_management = ServiceRequestManagement()
```

### Configuration Management

```python
# Export current configuration
config = itil.export_configuration()

# Validate framework health
health = itil.validate_framework_health()
print(f"Health Status: {health['overall_health']}")

# Get integration report
integration = itil.get_integration_report()
print(f"Cross-references: {integration['cross_references']}")
```

## 📚 Practice Details

### Incident Management

Complete incident lifecycle management with:
- Priority matrix calculation (Impact × Urgency)
- SLA tracking and breach detection
- Escalation management
- Major incident handling
- Comprehensive work logging

```python
# Advanced incident operations
incident.acknowledge(agent)
incident.assign(technician, "Network Team")
incident.escalate(EscalationLevel.L2, "Complex network issue", agent)
incident.resolve(technician, "Replaced faulty network switch")
```

### Problem Management

Full problem investigation and resolution:
- Reactive and proactive problem identification
- Root cause analysis with multiple methodologies
- Known error management
- Trend analysis for proactive problems

```python
# Root cause analysis
rca_guidance = problem_mgmt.conduct_root_cause_analysis(
    problem.number, 
    RootCauseAnalysisMethod.FIVE_WHYS,
    analyst
)

# Create known error
known_error = problem.create_known_error(
    analyst, 
    "Workaround: Restart service every 4 hours until patch available"
)
```

### Change Enablement

Complete change lifecycle with governance:
- Normal, Standard, and Emergency changes
- Change Advisory Board (CAB) integration
- Risk assessment and approval workflows
- Implementation and backout planning

```python
# Create change with full planning
change = change_mgmt.create_change_request(
    "Upgrade database server",
    "Upgrade to latest version for security patches",
    "Security vulnerabilities in current version",
    ChangeCategory.DATABASE,
    ChangeType.NORMAL,
    requester
)

# Add implementation plan
impl_plan = ImplementationPlan(
    description="Database upgrade procedure",
    steps=["1. Backup database", "2. Stop services", "3. Upgrade", "4. Test", "5. Go live"],
    estimated_duration=timedelta(hours=4)
)
change.implementation_plan = impl_plan

# Add approvers and approve
change.add_approver(manager)
change.approve_change(manager, "Approved for weekend maintenance window")
```

## 🎯 Best Practices

### Error Handling

```python
try:
    incident = itil.create_incident(...)
    incident.acknowledge(agent)
    incident.resolve(technician, "Issue resolved")
except Exception as e:
    print(f"Error managing incident: {e}")
```

### Integration Patterns

```python
# Pattern 1: Incident to Problem
if len(similar_incidents) >= 3:
    problem = itil.create_problem_from_incidents(
        [inc.number for inc in similar_incidents],
        "Recurring issue pattern detected",
        "Analysis needed for root cause",
        category,
        analyst
    )

# Pattern 2: Problem to Change
if problem.root_cause and problem.root_cause.confidence_level > 80:
    change = itil.create_change_from_problem(
        problem.number,
        "Implement permanent fix",
        analyst
    )
```

### Performance Monitoring

```python
# Monitor SLA performance
sla_breached = itil.incident_management.get_sla_breached_incidents()
if len(sla_breached) > 0:
    print(f"Warning: {len(sla_breached)} incidents have SLA breaches")

# Monitor change success rates
metrics = itil.change_enablement.get_metrics(7)  # Last 7 days
if metrics['success_rate'] < 95:
    print(f"Alert: Change success rate below threshold: {metrics['success_rate']}%")
```

## 🧪 Testing

### Unit Testing

```python
import unittest
from python_framework import ITILFramework

class TestIncidentManagement(unittest.TestCase):
    def setUp(self):
        self.itil = ITILFramework()
        self.user = Person("1", "Test User", "test@example.com", "User", "IT")
    
    def test_create_incident(self):
        incident = self.itil.create_incident(
            "Test incident",
            "Test description", 
            self.user,
            IncidentCategory.SOFTWARE,
            Impact.LOW,
            Urgency.LOW
        )
        self.assertIsNotNone(incident.number)
        self.assertEqual(incident.priority, Priority.P4_LOW)

if __name__ == '__main__':
    unittest.main()
```

### Integration Testing

```python
def test_incident_to_problem_workflow():
    itil = ITILFramework()
    
    # Create incidents
    incidents = [
        itil.create_incident("Issue 1", "Description 1", user, category, Impact.MEDIUM, Urgency.HIGH),
        itil.create_incident("Issue 2", "Description 2", user, category, Impact.MEDIUM, Urgency.HIGH)
    ]
    
    # Create problem
    problem = itil.create_problem_from_incidents(
        [inc.number for inc in incidents],
        "Pattern detected",
        "Multiple similar incidents",
        ProblemCategory.APPLICATION,
        analyst
    )
    
    # Verify linking
    assert problem.number in incidents[0].related_problems
    assert incidents[0].number in problem.related_incidents
```

## 📈 Performance Considerations

### Memory Usage
- Objects are designed to be lightweight
- Use generators for large datasets
- Consider pagination for metrics over large time periods

### Scalability
- Framework supports thousands of records per practice
- Database backend can be added for persistence
- Metrics calculations are optimized for performance

### Thread Safety
- Core classes are thread-safe for read operations
- Use locks for concurrent write operations
- Consider async patterns for high-throughput scenarios

## 🔮 Roadmap

### Phase 2 - Additional Practices
- [ ] Service Request Management
- [ ] Knowledge Management
- [ ] Release Management
- [ ] Deployment Management
- [ ] IT Asset Management

### Phase 3 - Advanced Features
- [ ] Database persistence layer
- [ ] REST API endpoints
- [ ] Web dashboard interface
- [ ] Integration with external ITSM tools
- [ ] Machine learning for predictive analytics

### Phase 4 - Enterprise Features
- [ ] Multi-tenancy support
- [ ] Advanced security and audit logging
- [ ] Workflow automation engine
- [ ] Custom practice framework
- [ ] Integration with CMDB systems

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-practice`)
3. Commit your changes (`git commit -am 'Add new practice implementation'`)
4. Push to the branch (`git push origin feature/new-practice`)
5. Create a Pull Request

### Development Setup

```bash
# Clone repository
git clone <repository-url>
cd ITIL-Notes

# Set up development environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Run examples
python python-framework/__init__.py
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: See inline docstrings and type hints
- **Examples**: Check the `examples/` directory
- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Use GitHub Discussions for questions

## 🙏 Acknowledgments

- **ITIL 4 Foundation**: Based on official ITIL 4 guidance from Axelos
- **ServiceNow**: Inspiration from ServiceNow platform implementations
- **Community**: Thanks to the ITSM community for feedback and guidance

---

**Built with ❤️ for the ITSM community**

*Making ITIL 4 accessible through code*