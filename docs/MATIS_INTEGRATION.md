# Matis Integration Guide

## Overview

Matis is a Rust-based IT automation platform that has been integrated into ReasonOps-ITSM as a core Task Force automation executor. This integration enables intelligent, autonomous execution of IT tasks and automation within the ITSM framework.

## Architecture

The Matis integration consists of several key components:

### MatisTaskExecutor Class

Located in `ai_agents/matis_task_executor.py`, this class provides:

- **Playbook Execution**: Execute YAML-based automation playbooks
- **SSH Task Execution**: Run tasks on remote systems via SSH
- **Simulation Mode**: Test automation logic without actual execution
- **History Tracking**: Maintain execution logs and results
- **Sample Playbook Generation**: Create incident response playbooks

### CLI Integration

The main CLI (`cli.py`) includes a `matis` subcommand with the following options:

- `validate`: Verify Matis installation and accessibility
- `execute`: Run automation playbooks
- `ssh`: Execute tasks on remote systems
- `simulate`: Test automation in simulation mode
- `history`: View execution history
- `sample`: Generate sample playbooks

### Orchestrator Integration

The `itil_multi_agent_orchestrator.py` includes Matis validation and can trigger autonomous task execution as part of collaborative AI agent workflows.

## Installation

### Prerequisites

1. **Rust Toolchain**: Install Rust from https://rustup.rs/
2. **Git**: Ensure git is available for submodule operations

### Setup Steps

1. **Add Matis Submodule**:
   ```bash
   cd /e/Code/ReasonOps-ITSM
   git submodule add https://github.com/yasir2000/Matis matis
   git submodule update --init --recursive
   ```

2. **Build Matis Binary**:
   ```bash
   cd matis
   cargo build --release
   ```

3. **Verify Installation**:
   ```bash
   cd python-framework
   python cli.py matis validate
   ```

## Usage

### CLI Commands

#### Validate Installation
```bash
python cli.py matis validate
```
Verifies that Matis is properly installed and accessible.

#### Execute Playbook
```bash
python cli.py matis execute --playbook /path/to/playbook.yaml --inventory /path/to/inventory.yaml
```
Executes an automation playbook against specified inventory.

#### SSH Task Execution
```bash
python cli.py matis ssh --host hostname --task "command to execute"
```
Runs a task on a remote system via SSH.

#### Simulation Mode
```bash
python cli.py matis simulate --playbook /path/to/playbook.yaml
```
Tests automation logic without actual execution.

#### View History
```bash
python cli.py matis history
```
Displays execution history and results.

#### Generate Sample Playbook
```bash
python cli.py matis sample --type incident-response --output /path/to/output.yaml
```
Creates a sample playbook for common scenarios.

### Python API

#### Basic Usage
```python
from ai_agents.matis_task_executor import MatisTaskExecutor

# Initialize executor
executor = MatisTaskExecutor()

# Validate installation
is_valid, message = executor.validate_matis()
print(f"Matis validation: {message}")

# Execute playbook
result = executor.execute_playbook(
    playbook_path="/path/to/playbook.yaml",
    inventory_path="/path/to/inventory.yaml"
)
print(f"Execution result: {result}")

# Simulate execution
simulation_result = executor.simulate_execution(
    playbook_path="/path/to/playbook.yaml"
)
print(f"Simulation result: {simulation_result}")
```

#### Advanced Usage with Orchestrator
```python
from ai_agents.itil_multi_agent_orchestrator import CollaborativeAgentsOrchestrator

# Initialize orchestrator
orchestrator = CollaborativeAgentsOrchestrator()

# Run demo with Matis integration
orchestrator.run_demo()
```

## Playbook Format

Matis uses YAML-based playbooks for automation. Here's an example incident response playbook:

```yaml
---
name: "Incident Response Automation"
description: "Automated response to system incidents"

tasks:
  - name: "Check system status"
    command: "systemctl status"
    hosts: "all"
    become: true

  - name: "Restart failed services"
    command: "systemctl restart {{ service_name }}"
    hosts: "webservers"
    become: true
    when: "service_status == 'failed'"

  - name: "Send notification"
    command: "curl -X POST -H 'Content-Type: application/json' -d '{\"message\":\"Incident resolved\"}' {{ webhook_url }}"
    hosts: "localhost"
    delegate_to: "localhost"
```

## Inventory Format

Inventory files define target systems:

```yaml
---
all:
  children:
    webservers:
      hosts:
        web01:
          ansible_host: 192.168.1.10
          ansible_user: admin
        web02:
          ansible_host: 192.168.1.11
          ansible_user: admin
    databases:
      hosts:
        db01:
          ansible_host: 192.168.1.20
          ansible_user: admin

  vars:
    ansible_ssh_private_key_file: ~/.ssh/id_rsa
    ansible_become: true
    ansible_become_method: sudo
```

## Error Handling

The integration includes comprehensive error handling:

- **Binary Not Found**: Clear error messages when Matis binary is missing
- **Execution Failures**: Detailed error reporting with exit codes
- **Unicode Issues**: Proper encoding handling for subprocess output
- **Validation Errors**: Pre-execution checks for required files and permissions

## Integration Points

### AI Agents Framework

Matis integrates with the AI agents framework through:

- **Task Force Execution**: Autonomous execution of IT tasks
- **Event-Driven Triggers**: Respond to incidents and alerts
- **Collaborative Workflows**: Work alongside other AI agents
- **RACI Integration**: Support for role-based task assignment

### ITIL Practices

The integration supports ITIL practices including:

- **Incident Management**: Automated incident response
- **Problem Management**: Root cause analysis automation
- **Change Management**: Controlled automation execution
- **Service Request**: Self-service automation

## Testing

### Unit Tests
```bash
cd python-framework
python -m pytest tests/test_matis_integration.py -v
```

### Integration Tests
```bash
# Test CLI commands
python cli.py matis validate
python cli.py matis simulate --playbook sample_playbook.yaml

# Test orchestrator integration
python -c "from ai_agents.itil_multi_agent_orchestrator import CollaborativeAgentsOrchestrator; o = CollaborativeAgentsOrchestrator(); o.run_demo()"
```

## Troubleshooting

### Common Issues

1. **Matis Binary Not Found**
   - Ensure Matis submodule is properly initialized
   - Verify cargo build completed successfully
   - Check binary path in MatisTaskExecutor

2. **Unicode Decoding Errors**
   - The integration handles most encoding issues automatically
   - If issues persist, check system locale settings

3. **SSH Connection Failures**
   - Verify SSH keys are properly configured
   - Check inventory file format and host accessibility
   - Ensure SSH agent is running

4. **Playbook Execution Errors**
   - Validate YAML syntax
   - Check variable definitions
   - Verify task dependencies

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

- **Cross-Platform Path Detection**: Automatic detection of Matis binary across platforms
- **Advanced Playbook Features**: Support for more complex automation scenarios
- **Real-time Monitoring**: Integration with monitoring systems
- **Audit Logging**: Comprehensive audit trails for all executions
- **Container Support**: Native container execution capabilities

## Contributing

When contributing to the Matis integration:

1. Follow existing code patterns in `matis_task_executor.py`
2. Add comprehensive error handling
3. Include unit tests for new functionality
4. Update this documentation
5. Test across different environments

## References

- [Matis GitHub Repository](https://github.com/yasir2000/Matis)
- [ReasonOps-ITSM Documentation](../README.md)
- [ITIL Framework Documentation](ITIL.md)