# AI Agents Framework for ITIL - Installation Guide

## Overview

This guide explains how to set up and use AI agents with the ITIL framework using CrewAI for autonomous incident resolution and ITSM process automation.

## Prerequisites

### Required Python Packages

```bash
# Core CrewAI framework
pip install crewai

# LangChain for LLM integration
pip install langchain

# OpenAI for GPT models (or alternative LLM)
pip install openai

# Additional dependencies
pip install langchain-openai
pip install langchain-community
```

### Optional LLM Providers

```bash
# For local models
pip install ollama

# For Anthropic Claude
pip install anthropic

# For Google models
pip install langchain-google-genai

# For Azure OpenAI
pip install langchain-azure-openai
```

### Environment Setup

Create a `.env` file in your project root:

```env
# OpenAI API Key (if using OpenAI)
OPENAI_API_KEY=your_openai_api_key_here

# Or use other LLM providers
ANTHROPIC_API_KEY=your_anthropic_key_here
GOOGLE_API_KEY=your_google_key_here

# Agent configuration
AGENT_VERBOSE=true
AGENT_DEBUG=false
```

## Quick Start

### 1. Basic Setup

```python
from ai_agents import ITILAgentCrew
from integration.integration_manager import ITILIntegrationManager

# Initialize ITIL framework
itil_manager = ITILIntegrationManager()

# Create AI agent crew
agent_crew = ITILAgentCrew(itil_manager)

# Process an incident
incident_data = {
    "id": "INC-001",
    "title": "Email system slow",
    "description": "Users reporting slow email performance",
    "affected_users": 50,
    "urgency": "High",
    "impact": "Medium"
}

results = agent_crew.handle_incident(incident_data)
print(f"Resolution status: {results['status']}")
```

### 2. Custom Agent Configuration

```python
from crewai import Agent
from ai_agents import ITILAgentCrew, AgentRole

# Create custom agent crew with specific LLM
from langchain.llms import OpenAI

custom_llm = OpenAI(
    temperature=0.1,
    model_name="gpt-4"
)

agent_crew = ITILAgentCrew(
    itil_manager=itil_manager,
    llm_model=custom_llm
)
```

### 3. Adding Custom Tools

```python
from ai_agents import ITILAgentTool

class CustomMonitoringTool(ITILAgentTool):
    def __init__(self, itil_manager):
        super().__init__(
            name="system_monitoring",
            description="Monitor system health and performance",
            itil_manager=itil_manager
        )
    
    def _run(self, system_name: str) -> str:
        # Your custom monitoring logic
        return f"System {system_name} status: Healthy"

# Add to agent crew
agent_crew.tools["system_monitoring"] = CustomMonitoringTool(itil_manager)
```

## Agent Roles and Capabilities

### Available Agent Roles

1. **Incident Analyst**
   - Incident classification and prioritization
   - Initial triage and assessment
   - Escalation decisions

2. **Technical Specialist** 
   - Deep technical troubleshooting
   - Resolution plan implementation
   - System analysis and diagnostics

3. **Problem Analyst**
   - Pattern recognition in incidents
   - Root cause analysis
   - Trend analysis and reporting

4. **Knowledge Manager**
   - Knowledge base maintenance
   - Solution documentation
   - Best practices capture

### Agent Capabilities

```python
# Check agent capabilities
agent_status = agent_crew.get_agent_status()

for role, info in agent_status['agents'].items():
    print(f"{role}: {info['capabilities']}")
```

## Advanced Configuration

### 1. Custom LLM Integration

```python
# Using local Ollama model
from langchain.llms import Ollama

local_llm = Ollama(model="llama2")
agent_crew = ITILAgentCrew(itil_manager, llm_model=local_llm)

# Using Azure OpenAI
from langchain.llms import AzureOpenAI

azure_llm = AzureOpenAI(
    deployment_name="gpt-4",
    model_name="gpt-4"
)
agent_crew = ITILAgentCrew(itil_manager, llm_model=azure_llm)
```

### 2. Agent Memory and Learning

```python
from crewai.memory import LongTermMemory

# Configure agent memory
agent_crew.agents[AgentRole.INCIDENT_ANALYST].memory = LongTermMemory(
    storage_path="./agent_memory"
)
```

### 3. Agent Collaboration Patterns

```python
# Configure hierarchical process
from crewai import Process

incident_crew = Crew(
    agents=[analyst_agent, specialist_agent, problem_agent],
    tasks=[analysis_task, resolution_task, pattern_task],
    process=Process.hierarchical,  # Instead of sequential
    manager_llm=manager_llm
)
```

## Integration with ITIL Processes

### 1. Incident Management Integration

```python
# Automatic incident processing
def auto_process_incident(incident_data):
    # AI agents analyze and classify
    results = agent_crew.handle_incident(incident_data)
    
    # Update ITIL incident management system
    if results['status'] == 'completed':
        incident_mgmt = itil_manager.registry.get("incident_management")
        incident_mgmt.update_incident(
            incident_data['id'], 
            results['recommendations']
        )
    
    return results
```

### 2. Problem Management Integration

```python
# Pattern-based problem creation
def check_for_problems():
    problem_analyst = agent_crew.agents[AgentRole.PROBLEM_ANALYST]
    
    # Get recent incidents
    recent_incidents = get_recent_incidents()
    
    # Analyze for patterns
    pattern_analysis = problem_analyst.analyze_patterns(recent_incidents)
    
    if pattern_analysis['create_problem']:
        create_problem_record(pattern_analysis)
```

### 3. Change Management Integration

```python
# AI-assisted change planning
def plan_change_request(problem_data):
    planning_tool = agent_crew.tools["resolution_planning"]
    
    change_plan = planning_tool._run(problem_data)
    
    # Create change request with AI recommendations
    change_mgmt = itil_manager.registry.get("change_enablement")
    change_request = change_mgmt.create_change_request(
        title=f"Resolve {problem_data['title']}",
        plan=change_plan
    )
    
    return change_request
```

## Monitoring and Observability

### 1. Agent Performance Metrics

```python
# Monitor agent performance
def get_agent_metrics():
    return {
        "incidents_processed": agent_crew.get_processed_count(),
        "resolution_accuracy": agent_crew.get_accuracy_score(),
        "average_processing_time": agent_crew.get_avg_processing_time(),
        "escalation_rate": agent_crew.get_escalation_rate()
    }
```

### 2. Agent Learning and Improvement

```python
# Feedback loop for agent improvement
def provide_feedback(incident_id, resolution_success, feedback):
    agent_crew.learn_from_feedback(
        incident_id=incident_id,
        success=resolution_success,
        feedback=feedback
    )
```

### 3. Integration Health Monitoring

```python
# Monitor integration health
def check_integration_health():
    health = itil_manager.get_integration_health()
    agent_status = agent_crew.get_agent_status()
    
    return {
        "itil_framework": health['validation_status'],
        "ai_agents": "active" if agent_status['total_agents'] > 0 else "inactive",
        "tools_available": len(agent_status['agents']),
        "overall_status": "healthy" if all_systems_operational() else "degraded"
    }
```

## Best Practices

### 1. Agent Design Principles

- **Single Responsibility**: Each agent should have a clear, focused role
- **Collaboration**: Agents should work together, not in isolation
- **Human Oversight**: Always include human approval for critical actions
- **Continuous Learning**: Implement feedback loops for improvement

### 2. Error Handling

```python
def safe_agent_execution(agent_func, *args, **kwargs):
    try:
        result = agent_func(*args, **kwargs)
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        return {"status": "error", "error": str(e)}
```

### 3. Security Considerations

- **API Key Management**: Use environment variables for API keys
- **Access Control**: Implement proper authentication and authorization
- **Audit Logging**: Log all agent actions for compliance
- **Data Privacy**: Ensure sensitive data is properly handled

### 4. Performance Optimization

- **Caching**: Cache frequent LLM responses
- **Batching**: Process multiple incidents together when possible
- **Resource Limits**: Set appropriate limits on agent execution time
- **Load Balancing**: Distribute work across multiple agent instances

## Troubleshooting

### Common Issues

1. **Agent Not Responding**
   ```python
   # Check agent status
   status = agent_crew.get_agent_status()
   if status['integration_status'] != 'connected':
       # Reconnect to ITIL framework
       agent_crew.reconnect()
   ```

2. **LLM Rate Limits**
   ```python
   # Implement retry logic with exponential backoff
   import time
   
   def retry_with_backoff(func, max_retries=3):
       for attempt in range(max_retries):
           try:
               return func()
           except RateLimitError:
               time.sleep(2 ** attempt)
       raise Exception("Max retries exceeded")
   ```

3. **Memory Issues**
   ```python
   # Clear agent memory periodically
   agent_crew.clear_memory()
   
   # Or implement memory rotation
   agent_crew.rotate_memory(keep_recent=100)
   ```

### Debugging

```python
# Enable verbose logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Test individual tools
tool = agent_crew.tools["incident_analysis"]
result = tool._run(test_incident_data)
print(f"Tool result: {result}")

# Test agent communication
agent_crew.test_agent_communication()
```

## Production Deployment

### 1. Docker Configuration

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "-m", "ai_agents.itil_crewai_integration"]
```

### 2. Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: itil-ai-agents
spec:
  replicas: 3
  selector:
    matchLabels:
      app: itil-ai-agents
  template:
    metadata:
      labels:
        app: itil-ai-agents
    spec:
      containers:
      - name: ai-agents
        image: itil-ai-agents:latest
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: openai-secret
              key: api-key
```

### 3. Monitoring Setup

```python
# Prometheus metrics
from prometheus_client import Counter, Histogram, Gauge

incidents_processed = Counter('itil_incidents_processed_total')
processing_time = Histogram('itil_incident_processing_seconds')
agents_active = Gauge('itil_agents_active')

def record_metrics(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        processing_time.observe(time.time() - start_time)
        incidents_processed.inc()
        return result
    return wrapper
```

## Support and Resources

- **Documentation**: Check the `ai_agents/` directory for detailed API docs
- **Examples**: See `examples/` directory for complete usage examples
- **Issues**: Report issues in the project repository
- **Community**: Join the ITIL AI Agents community for support

For advanced customization and enterprise features, refer to the full documentation in the project repository.