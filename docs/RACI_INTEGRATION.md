# RACI Model Integration for ReasonOps ITIL AI Agents

## Overview

The ReasonOps framework now includes comprehensive RACI (Responsible, Accountable, Consulted, Informed) model integration for intelligent ITIL/ITSM AI agent assignment and orchestration. This enhancement enables automatic assignment of AI agents to ITIL activities based on their defined roles and responsibilities.

## Key Features

### 🎯 Intelligent Agent Assignment
- **Automatic Role Assignment**: AI agents are automatically assigned to ITIL activities based on RACI definitions
- **Priority-based Selection**: When multiple agents are responsible, selection is based on priority and current workload
- **Conditional Assignments**: Support for conditional role assignments based on context (e.g., severity, escalation type)

### 🔄 Multi-Agent Collaboration
- **Responsible Agents**: Execute the actual work
- **Accountable Agents**: Provide oversight and sign-off
- **Consulted Agents**: Provide expert input and advice
- **Informed Agents**: Receive notifications and updates

### 📊 Audit Trail & Compliance
- **Complete Activity Tracking**: Every ITIL activity execution is tracked with full audit trail
- **RACI Compliance Validation**: Built-in validation ensures proper RACI matrix compliance
- **Accountability Records**: All agent decisions and sign-offs are recorded

## Architecture

### Core Components

1. **RACI Model (`raci_model.py`)**
   - Defines RACI assignments for ITIL activities
   - Validates matrix consistency
   - Supports export/import of RACI definitions

2. **RACI Orchestrator (`raci_orchestrator.py`)**
   - Manages agent assignment and execution
   - Handles multi-agent collaboration workflows
   - Provides workload balancing and escalation

3. **Enhanced Agent Crews (`itil_crewai_integration.py`)**
   - Extended with RACI-specific methods
   - Support for role-specific activity execution
   - Consultation and accountability capabilities

## RACI Matrix Definition

### Incident Management Example

| Activity | Service Desk Agent | Incident Analyst | Incident Manager | Technical Specialist |
|----------|-------------------|------------------|------------------|---------------------|
| Detection & Recording | R | - | A | - |
| Classification & Prioritization | - | R | A | C |
| Initial Diagnosis | R | A | - | C |
| Escalation | - | - | A | R |
| Resolution & Recovery | - | - | A | R |
| Closure | R | - | A | - |

**Legend**: R=Responsible, A=Accountable, C=Consulted, I=Informed

## Usage Examples

### 1. Basic Activity Execution

```python
from ai_agents.raci_orchestrator import create_raci_orchestrator

# Create RACI-enabled orchestrator
orchestrator = create_raci_orchestrator()

# Execute incident classification
context = {
    "incident_id": "INC-2025-001",
    "severity": "high",
    "description": "Database connection timeout",
    "affected_users": 1500
}

execution_id = orchestrator.execute_activity("inc_002", context)
print(f"Activity executed: {execution_id}")
```

### 2. Custom RACI Matrix

```python
from ai_agents.raci_model import RACIMatrix, ProcessActivity, RACIAssignment, AgentRole, RACIRole, ITILProcess

# Create custom RACI matrix
matrix = RACIMatrix()

# Define custom activity
activity = ProcessActivity(
    activity_id="custom_001",
    activity_name="Custom Security Review",
    process=ITILProcess.INFORMATION_SECURITY_MANAGEMENT,
    description="Review security implications of changes",
    raci_assignments=[
        RACIAssignment(AgentRole.SECURITY_ANALYST, RACIRole.RESPONSIBLE),
        RACIAssignment(AgentRole.SECURITY_MANAGER, RACIRole.ACCOUNTABLE),
        RACIAssignment(AgentRole.CHANGE_COORDINATOR, RACIRole.CONSULTED),
        RACIAssignment(AgentRole.SERVICE_OWNER, RACIRole.INFORMED),
    ]
)

matrix.add_activity(activity)

# Use custom matrix
orchestrator = create_raci_orchestrator(matrix)
```

### 3. Workload Monitoring

```python
# Get agent workload report
workload_report = orchestrator.get_agent_workload_report()
print(f"Agent Workloads:")
for agent, workload in workload_report["agents"].items():
    print(f"  {agent}: {workload['active_activities']} active, {workload['capacity_utilization']:.1%} utilized")

# Get RACI compliance report
compliance = orchestrator.get_raci_compliance_report()
print(f"RACI Compliance: {compliance['compliance_status']}")
```

## Configuration

### Environment Setup

1. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

2. **Initialize RACI Framework**:
```python
from ai_agents.raci_model import create_default_raci_matrix

# Create and validate default RACI matrix
matrix = create_default_raci_matrix()
issues = matrix.validate_matrix()
if not issues:
    print("✅ RACI Matrix validation passed")
```

### LLM Configuration

The RACI orchestrator supports multiple LLM providers through the existing multi-LLM framework:

```python
# Configure with Ollama (local)
orchestrator = create_raci_orchestrator()
orchestrator.configure_llm_provider(
    provider='ollama',
    model='llama2-7b',
    temperature=0.7
)

# Configure with OpenAI (cloud)
orchestrator.configure_llm_provider(
    provider='openai',
    model='gpt-4-turbo',
    api_key='your-api-key',
    temperature=0.7
)
```

## Predefined RACI Assignments

### Incident Management
- **Detection & Recording**: Service Desk Agent (R), Incident Manager (A)
- **Classification**: Incident Analyst (R), Incident Manager (A), Service Owner (C)
- **Investigation**: Service Desk Agent (R), Technical Specialist (R), Incident Analyst (A)
- **Escalation**: Escalation Manager (R), Incident Manager (A)
- **Resolution**: Technical Specialist (R), Incident Analyst (A)
- **Closure**: Service Desk Agent (R), Incident Manager (A), User Rep (C)

### Problem Management
- **Identification**: Problem Analyst (R), Problem Manager (A)
- **Investigation**: Problem Analyst (R), Technical Specialist (R), Problem Manager (A)
- **Workaround**: Technical Specialist (R), Problem Analyst (A)

### Change Enablement
- **Request Creation**: Change Coordinator (R), Change Manager (A)
- **Assessment**: Change Advisory Board (R), Change Manager (A)
- **Authorization**: Change Manager (A), Risk Analyst (C), Security Analyst (C)

### Service Desk
- **Contact Logging**: Service Desk Agent (R), Service Desk Supervisor (A)
- **Initial Resolution**: Service Desk Agent (R), Knowledge Manager (C)

## Event-Driven Automation

The RACI orchestrator automatically responds to ITIL events:

```python
# Incident created → Triggers incident detection activity
orchestrator.event_bus.publish("incident.created", {
    "incident_id": "INC-001",
    "severity": "high",
    "description": "Service outage"
})

# Problem identified → Triggers problem identification activity
orchestrator.event_bus.publish("problem.identified", {
    "problem_id": "PRB-001",
    "related_incidents": ["INC-001", "INC-002"]
})

# Change requested → Triggers change request creation
orchestrator.event_bus.publish("change.requested", {
    "change_id": "CHG-001",
    "change_type": "emergency"
})
```

## Integration with Existing Framework

### Framework Integration
The RACI model integrates seamlessly with existing ReasonOps components:

- **Integration Manager**: Provides practice access for agent tools
- **Event Bus**: Enables automatic activity triggering
- **JSON Storage**: Stores execution records and audit trail
- **Multi-LLM Provider**: Supports various LLM backends

### Web Interface Integration
The RACI orchestrator can be accessed through the web interface:

```typescript
// Frontend integration example
const response = await fetch('/api/agents/execute-activity', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    activity_id: 'inc_002',
    context: {
      incident_id: 'INC-001',
      severity: 'high'
    }
  })
});
```

## Benefits

### 🎯 **Intelligent Automation**
- Automatic agent assignment based on expertise and availability
- Reduced manual coordination overhead
- Consistent application of ITIL best practices

### 🔍 **Enhanced Accountability**
- Clear responsibility assignment for every activity
- Complete audit trail for compliance
- Quality control through accountability sign-offs

### ⚡ **Improved Efficiency**
- Parallel execution of independent activities
- Optimized workload distribution
- Faster incident and problem resolution

### 📈 **Better Compliance**
- Enforced RACI model compliance
- Automated validation of role assignments
- Consistent process execution

## Troubleshooting

### Common Issues

1. **Agent Assignment Failures**
   - Check RACI matrix validation: `matrix.validate_matrix()`
   - Ensure all required agent roles are initialized
   - Verify activity conditions are met

2. **LLM Provider Issues**
   - Check LLM provider health: `orchestrator.check_agent_health()`
   - Verify API keys and connectivity
   - Test with mock provider for debugging

3. **Activity Execution Errors**
   - Review execution logs in JSON storage
   - Check agent crew initialization
   - Validate activity context parameters

### Debug Mode

Enable debug logging for detailed troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

orchestrator = create_raci_orchestrator()
# Detailed logs will show agent assignment and execution steps
```

## Future Enhancements

### Planned Features
- **Machine Learning Integration**: Learn from past executions to optimize assignments
- **Advanced Workload Balancing**: Dynamic capacity management based on agent performance
- **Custom RACI Templates**: Industry-specific RACI templates (banking, healthcare, etc.)
- **Integration APIs**: RESTful APIs for external ITSM tool integration
- **Real-time Dashboards**: Live monitoring of agent activities and workloads

### Contributing

To extend the RACI model with new processes or agent roles:

1. **Add New Agent Roles**: Extend `AgentRole` enum in `raci_model.py`
2. **Define RACI Activities**: Add new `ProcessActivity` definitions
3. **Implement Agent Behaviors**: Add role-specific methods to `ITILAgentCrew`
4. **Update Documentation**: Document new assignments and capabilities

## References

- **YaSM RACI Matrix**: See `docs/YaSM-RACI-Matrix.pdf` for detailed role definitions
- **ITIL 4 Framework**: Official ITIL 4 guidance on practices and roles
- **ReasonOps Documentation**: See `docs/` for additional framework documentation

---

**Note**: This RACI integration transforms ReasonOps from a basic ITIL framework into an intelligent, self-organizing system of AI agents that can autonomously handle complex ITSM scenarios while maintaining proper governance and accountability.