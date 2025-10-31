"""
Matis Task Automation Executor

Integrates Matis (Modern IT Automation Platform) as the core task force automation executor
for IT tasks and other tasks within the ReasonOps ITSM framework.

Matis provides:
- Agentless Architecture using SSH/WinRM
- Zero-dependency execution (no Python runtime required on target systems)
- Type-safe configuration with YAML schema validation
- Memory-safe operations with Rust's guarantees
- Concurrent execution with configurable thread pools
- Extensible plugin system

This module enables intelligent and autonomous execution of IT automation tasks
through the ReasonOps AI agents framework.
"""

import os
import sys
import subprocess
import tempfile
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TaskExecutionResult:
    """Result of a Matis task execution"""
    success: bool
    output: str
    error: str
    execution_time: float
    task_id: str
    timestamp: datetime


class MatisTaskExecutor:
    """
    Core Task Force Automation Executor using Matis

    Provides intelligent and autonomous execution of IT tasks through
    the Matis automation platform integrated with ReasonOps ITSM.
    """

    def __init__(self, matis_binary_path: Optional[str] = None):
        """
        Initialize the Matis Task Executor

        Args:
            matis_binary_path: Path to the Matis binary. If None, assumes it's in PATH
                               or looks in the matis submodule.
        """
        if matis_binary_path:
            self.matis_binary = matis_binary_path
        else:
            # Use the Windows path for this environment
            self.matis_binary = "e:\\Code\\ReasonOps-ITSM\\matis\\target\\release\\matis"

        self.execution_history: List[TaskExecutionResult] = []

    def _run_matis_command(self, args: List[str], cwd: Optional[str] = None) -> subprocess.CompletedProcess:
        """
        Run a Matis command

        Args:
            args: Command line arguments for Matis
            cwd: Working directory

        Returns:
            CompletedProcess with stdout, stderr, returncode
        """
        cmd = [self.matis_binary] + args
        try:
            # First try with text=True
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=cwd,
                timeout=300  # 5 minute timeout
            )
            return result
        except UnicodeDecodeError:
            # If Unicode decoding fails, try with bytes
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=False,
                cwd=cwd,
                timeout=300
            )
            # Convert bytes to string with error handling
            try:
                result.stdout = result.stdout.decode('utf-8', errors='replace')
                result.stderr = result.stderr.decode('utf-8', errors='replace')
            except:
                result.stdout = str(result.stdout)
                result.stderr = str(result.stderr)
            return result
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Matis command timed out: {' '.join(cmd)}")
        except FileNotFoundError:
            raise RuntimeError(f"Matis binary not found: {self.matis_binary}")

    def validate_matis_installation(self) -> bool:
        """
        Validate that Matis is properly installed and accessible

        Returns:
            True if Matis is available, False otherwise
        """
        try:
            result = self._run_matis_command(["--version"])
            return result.returncode == 0
        except RuntimeError:
            return False

    def execute_playbook(self,
                        playbook_content: Union[str, Dict],
                        inventory_content: Optional[Union[str, Dict]] = None,
                        extra_vars: Optional[Dict[str, Any]] = None,
                        task_id: Optional[str] = None) -> TaskExecutionResult:
        """
        Execute a Matis playbook

        Args:
            playbook_content: Playbook as YAML string or dict
            inventory_content: Inventory as YAML string or dict
            extra_vars: Extra variables to pass
            task_id: Unique identifier for the task

        Returns:
            TaskExecutionResult with execution details
        """
        import time
        start_time = time.time()

        if not task_id:
            task_id = f"task_{int(start_time)}"

        try:
            # Create temporary files for playbook and inventory
            with tempfile.TemporaryDirectory() as temp_dir:
                playbook_file = Path(temp_dir) / "playbook.yml"

                # Convert playbook to YAML if it's a dict
                if isinstance(playbook_content, dict):
                    playbook_yaml = yaml.dump(playbook_content, default_flow_style=False)
                else:
                    playbook_yaml = playbook_content

                playbook_file.write_text(playbook_yaml)

                # Prepare command arguments
                args = ["local", "--playbook", str(playbook_file)]

                # Add inventory if provided
                if inventory_content:
                    inventory_file = Path(temp_dir) / "inventory.yml"
                    if isinstance(inventory_content, dict):
                        inventory_yaml = yaml.dump(inventory_content, default_flow_style=False)
                    else:
                        inventory_yaml = inventory_content
                    inventory_file.write_text(inventory_yaml)
                    args.extend(["--inventory", str(inventory_file)])

                # Add extra vars if provided
                if extra_vars:
                    for key, value in extra_vars.items():
                        args.extend(["--extra-vars", f"{key}={value}"])

                # Execute the playbook
                result = self._run_matis_command(args, cwd=temp_dir)

                execution_time = time.time() - start_time

                task_result = TaskExecutionResult(
                    success=result.returncode == 0,
                    output=result.stdout,
                    error=result.stderr,
                    execution_time=execution_time,
                    task_id=task_id,
                    timestamp=datetime.now()
                )

                self.execution_history.append(task_result)
                return task_result

        except Exception as e:
            execution_time = time.time() - start_time
            task_result = TaskExecutionResult(
                success=False,
                output="",
                error=str(e),
                execution_time=execution_time,
                task_id=task_id,
                timestamp=datetime.now()
            )
            self.execution_history.append(task_result)
            return task_result

    def execute_ssh_playbook(self,
                           playbook_content: Union[str, Dict],
                           inventory_content: Union[str, Dict],
                           ssh_user: Optional[str] = None,
                           ssh_key: Optional[str] = None,
                           threads: int = 4,
                           task_id: Optional[str] = None) -> TaskExecutionResult:
        """
        Execute a Matis playbook over SSH on remote hosts

        Args:
            playbook_content: Playbook as YAML string or dict
            inventory_content: Inventory as YAML string or dict
            ssh_user: SSH username
            ssh_key: Path to SSH private key
            threads: Number of parallel threads
            task_id: Unique identifier for the task

        Returns:
            TaskExecutionResult with execution details
        """
        import time
        start_time = time.time()

        if not task_id:
            task_id = f"ssh_task_{int(start_time)}"

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                playbook_file = Path(temp_dir) / "playbook.yml"
                inventory_file = Path(temp_dir) / "inventory.yml"

                # Convert to YAML
                if isinstance(playbook_content, dict):
                    playbook_yaml = yaml.dump(playbook_content, default_flow_style=False)
                else:
                    playbook_yaml = playbook_content
                playbook_file.write_text(playbook_yaml)

                if isinstance(inventory_content, dict):
                    inventory_yaml = yaml.dump(inventory_content, default_flow_style=False)
                else:
                    inventory_yaml = inventory_content
                inventory_file.write_text(inventory_yaml)

                # Prepare SSH command
                args = ["ssh", "--inventory", str(inventory_file), "--playbook", str(playbook_file)]

                if ssh_user:
                    args.extend(["--user", ssh_user])
                if ssh_key:
                    args.extend(["--key", ssh_key])
                if threads > 1:
                    args.extend(["--threads", str(threads)])

                result = self._run_matis_command(args, cwd=temp_dir)

                execution_time = time.time() - start_time

                task_result = TaskExecutionResult(
                    success=result.returncode == 0,
                    output=result.stdout,
                    error=result.stderr,
                    execution_time=execution_time,
                    task_id=task_id,
                    timestamp=datetime.now()
                )

                self.execution_history.append(task_result)
                return task_result

        except Exception as e:
            execution_time = time.time() - start_time
            task_result = TaskExecutionResult(
                success=False,
                output="",
                error=str(e),
                execution_time=execution_time,
                task_id=task_id,
                timestamp=datetime.now()
            )
            self.execution_history.append(task_result)
            return task_result

    def simulate_execution(self,
                          playbook_content: Union[str, Dict],
                          inventory_content: Optional[Union[str, Dict]] = None,
                          task_id: Optional[str] = None) -> TaskExecutionResult:
        """
        Simulate playbook execution without making changes

        Args:
            playbook_content: Playbook to simulate
            inventory_content: Inventory for simulation
            task_id: Unique identifier for the task

        Returns:
            TaskExecutionResult with simulation details
        """
        import time
        start_time = time.time()

        if not task_id:
            task_id = f"sim_task_{int(start_time)}"

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                playbook_file = Path(temp_dir) / "playbook.yml"

                if isinstance(playbook_content, dict):
                    playbook_yaml = yaml.dump(playbook_content, default_flow_style=False)
                else:
                    playbook_yaml = playbook_content
                playbook_file.write_text(playbook_yaml)

                args = ["simulate", "--playbook", str(playbook_file)]

                if inventory_content:
                    inventory_file = Path(temp_dir) / "inventory.yml"
                    if isinstance(inventory_content, dict):
                        inventory_yaml = yaml.dump(inventory_content, default_flow_style=False)
                    else:
                        inventory_yaml = inventory_content
                    inventory_file.write_text(inventory_yaml)
                    args.extend(["--inventory", str(inventory_file)])

                result = self._run_matis_command(args, cwd=temp_dir)

                execution_time = time.time() - start_time

                task_result = TaskExecutionResult(
                    success=result.returncode == 0,
                    output=result.stdout,
                    error=result.stderr,
                    execution_time=execution_time,
                    task_id=task_id,
                    timestamp=datetime.now()
                )

                self.execution_history.append(task_result)
                return task_result

        except Exception as e:
            execution_time = time.time() - start_time
            task_result = TaskExecutionResult(
                success=False,
                output="",
                error=str(e),
                execution_time=execution_time,
                task_id=task_id,
                timestamp=datetime.now()
            )
            self.execution_history.append(task_result)
            return task_result

    def get_execution_history(self, limit: Optional[int] = None) -> List[TaskExecutionResult]:
        """
        Get execution history

        Args:
            limit: Maximum number of recent results to return

        Returns:
            List of TaskExecutionResult objects
        """
        if limit:
            return self.execution_history[-limit:]
        return self.execution_history

    def create_sample_incident_response_playbook(self) -> Dict:
        """
        Create a sample incident response playbook for demonstration

        Returns:
            Playbook dictionary
        """
        return {
            "name": "Incident Response Automation",
            "hosts": "webservers",
            "become": True,
            "vars": {
                "incident_id": "INC-{{ ansible_date_time.iso8601 }}",
                "severity": "high"
            },
            "tasks": [
                {
                    "name": "Log incident start",
                    "command": "echo 'Starting incident response for {{ incident_id }}'"
                },
                {
                    "name": "Check system status",
                    "command": "systemctl status nginx",
                    "register": "nginx_status"
                },
                {
                    "name": "Restart nginx if down",
                    "service": {
                        "name": "nginx",
                        "state": "restarted"
                    },
                    "when": "nginx_status.rc != 0"
                },
                {
                    "name": "Collect system logs",
                    "command": "journalctl -u nginx --since '1 hour ago' > /tmp/incident_logs.txt"
                },
                {
                    "name": "Send notification",
                    "command": "echo 'Incident {{ incident_id }} response completed' | mail -s 'Incident Response' admin@example.com"
                }
            ]
        }

    def generate_automation_playbook(self, incident_description: str, target_hosts: str = "all",
                                   automation_type: str = "incident_response") -> Dict:
        """
        Generate a custom automation playbook using AI based on incident description

        Args:
            incident_description: Description of the incident or automation requirement
            target_hosts: Target hosts for the automation (default: "all")
            automation_type: Type of automation (incident_response, maintenance, deployment, etc.)

        Returns:
            Generated playbook dictionary
        """
        try:
            import asyncio
            from .multi_llm_provider import MultiLLMManager

            # Initialize LLM manager
            llm_manager = MultiLLMManager()

            # Create prompt for AI-driven playbook generation
            prompt = f"""
            Generate a Matis/Ansible YAML automation playbook for the following scenario:

            SCENARIO: {incident_description}
            AUTOMATION TYPE: {automation_type}
            TARGET HOSTS: {target_hosts}

            Requirements:
            1. Use proper YAML syntax compatible with Matis automation
            2. Include appropriate tasks for the scenario
            3. Add error handling and conditional logic where appropriate
            4. Use variables for dynamic content
            5. Include logging and notification steps
            6. Ensure tasks are idempotent where possible

            Generate only the playbook content as a valid YAML dictionary, no explanations.

            Example structure:
            name: "Generated Automation"
            hosts: "{target_hosts}"
            become: true
            vars:
              timestamp: "{{{{ ansible_date_time.iso8601 }}}}"
            tasks:
            - name: "Task description"
              command: "command here"
            """

            # Get AI-generated playbook (run async in sync context)
            async def get_response():
                response = await llm_manager.generate_response(prompt)
                return response.content if response else ""

            response = asyncio.run(get_response())

            # Parse the YAML response
            import yaml
            try:
                playbook = yaml.safe_load(response)
                # Validate basic structure
                if not isinstance(playbook, dict) or 'tasks' not in playbook:
                    raise ValueError("Invalid playbook structure generated")

                # Ensure required fields
                playbook.setdefault('name', f'AI Generated {automation_type.title()} Automation')
                playbook.setdefault('hosts', target_hosts)
                playbook.setdefault('become', True)

                return playbook

            except yaml.YAMLError as e:
                print(f"❌ Failed to parse AI-generated YAML: {e}")
                # Fallback to sample playbook
                return self.create_sample_incident_response_playbook()

        except Exception as e:
            print(f"❌ AI playbook generation failed: {e}")
            # Fallback to sample playbook
            return self.create_sample_incident_response_playbook()

    def generate_incident_response_playbook(self, incident_title: str, incident_description: str,
                                          affected_services: List[str] = None) -> Dict:
        """
        Generate an incident-specific response playbook using AI

        Args:
            incident_title: Title of the incident
            incident_description: Detailed description of the incident
            affected_services: List of affected services/systems

        Returns:
            AI-generated incident response playbook
        """
        if affected_services is None:
            affected_services = ["webservers"]

        # Create comprehensive incident context
        full_description = f"""
        INCIDENT TITLE: {incident_title}

        INCIDENT DESCRIPTION: {incident_description}

        AFFECTED SERVICES: {', '.join(affected_services)}

        Generate an automated response playbook that:
        1. Checks the status of affected services
        2. Attempts automated remediation
        3. Collects diagnostic information
        4. Notifies stakeholders
        5. Logs all actions taken
        """

        return self.generate_automation_playbook(
            incident_description=full_description,
            target_hosts=affected_services[0] if len(affected_services) == 1 else "all",
            automation_type="incident_response"
        )
        

# Global instance for use across the framework
matis_executor = MatisTaskExecutor()


def get_matis_executor() -> MatisTaskExecutor:
    """Get the global Matis executor instance"""
    return matis_executor


if __name__ == "__main__":
    # Demo usage
    executor = MatisTaskExecutor()

    if not executor.validate_matis_installation():
        print("❌ Matis is not properly installed")
        sys.exit(1)

    print("✅ Matis Task Executor initialized successfully")

    # Create sample playbook and inventory
    playbook = executor.create_sample_incident_response_playbook()
    inventory = executor.create_sample_inventory()

    print("📋 Sample Incident Response Playbook:")
    print(yaml.dump(playbook, default_flow_style=False))

    print("🏗️ Sample Inventory:")
    print(yaml.dump(inventory, default_flow_style=False))

    # Simulate execution
    print("🔍 Simulating playbook execution...")
    result = executor.simulate_execution(playbook, inventory, "demo_simulation")

    print(f"Simulation Result: {'✅ Success' if result.success else '❌ Failed'}")
    print(f"Execution Time: {result.execution_time:.2f}s")
    if result.output:
        print("Output:")
        print(result.output)
    if result.error:
        print("Error:")
        print(result.error)