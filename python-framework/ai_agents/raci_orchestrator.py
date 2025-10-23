"""
RACI-Enabled AI Agent Orchestrator for ReasonOps ITIL Framework

This orchestrator uses the RACI model to intelligently assign ITIL activities
to AI agents based on their defined responsibilities, accountability, consultation,
and information requirements.

Features:
- Automatic agent assignment based on RACI definitions
- Dynamic workload distribution 
- Intelligent escalation patterns
- Audit trail for accountability
- Multi-agent collaboration for complex activities
"""

from __future__ import annotations
import os
import sys
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime
from dataclasses import dataclass, field
import json
import logging

# Ensure package imports resolve
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_agents.raci_model import (
    RACIMatrix, RACIRole, ITILProcess, AgentRole, ProcessActivity,
    RACIAssignment, create_default_raci_matrix
)
from ai_agents.itil_crewai_integration import ITILAgentCrew
from integration.integration_manager import ITILIntegrationManager
from integration.event_bus import EventBus
from storage import json_store

logger = logging.getLogger(__name__)


@dataclass
class ActivityExecution:
    """Tracks execution of an ITIL activity"""
    activity_id: str
    execution_id: str
    timestamp: datetime
    status: str  # planned, in_progress, completed, failed
    assigned_agents: Dict[AgentRole, RACIRole] = field(default_factory=dict)
    results: Dict[str, Any] = field(default_factory=dict)
    escalations: List[Dict[str, Any]] = field(default_factory=list)
    consultation_log: List[Dict[str, Any]] = field(default_factory=list)
    notifications_sent: List[AgentRole] = field(default_factory=list)


@dataclass 
class AgentWorkload:
    """Tracks agent workload for load balancing"""
    agent_role: AgentRole
    active_activities: List[str] = field(default_factory=list)
    pending_consultations: List[str] = field(default_factory=list)
    capacity_utilization: float = 0.0  # 0.0 to 1.0
    last_activity_timestamp: Optional[datetime] = None


class RACIAgentOrchestrator:
    """RACI-enabled orchestrator for intelligent ITIL agent assignment"""
    
    def __init__(self, raci_matrix: Optional[RACIMatrix] = None):
        self.raci_matrix = raci_matrix or create_default_raci_matrix()
        self.integration = ITILIntegrationManager()
        self.event_bus = EventBus()
        self.agent_crews: Dict[AgentRole, ITILAgentCrew] = {}
        self.active_executions: Dict[str, ActivityExecution] = {}
        self.agent_workloads: Dict[AgentRole, AgentWorkload] = {}
        
        self._initialize_agents()
        self._setup_event_handlers()
    
    def _initialize_agents(self):
        """Initialize AI agent crews for each role in RACI matrix"""
        unique_roles = set()
        for activity in self.raci_matrix.activities.values():
            for assignment in activity.raci_assignments:
                unique_roles.add(assignment.agent_role)
        
        for role in unique_roles:
            self.agent_crews[role] = ITILAgentCrew(
                self.integration,
                primary_role=role.value
            )
            self.agent_workloads[role] = AgentWorkload(agent_role=role)
        
        logger.info(f"Initialized {len(self.agent_crews)} agent crews for RACI roles")
    
    def _setup_event_handlers(self):
        """Setup event handlers for automatic activity triggering"""
        self.event_bus.subscribe("incident.created", self._handle_incident_created)
        self.event_bus.subscribe("problem.identified", self._handle_problem_identified)
        self.event_bus.subscribe("change.requested", self._handle_change_requested)
        self.event_bus.subscribe("service_request.submitted", self._handle_service_request)
    
    def _handle_incident_created(self, payload: Dict[str, Any]):
        """Handle incident creation event"""
        incident_id = payload.get("incident_id")
        severity = payload.get("severity", "medium")
        
        # Start incident management workflow
        self.execute_activity("inc_001", {
            "incident_id": incident_id,
            "severity": severity,
            "description": payload.get("description", ""),
            "affected_service": payload.get("service_name", "")
        })
    
    def _handle_problem_identified(self, payload: Dict[str, Any]):
        """Handle problem identification event"""
        problem_id = payload.get("problem_id")
        
        self.execute_activity("prb_001", {
            "problem_id": problem_id,
            "related_incidents": payload.get("related_incidents", []),
            "description": payload.get("description", "")
        })
    
    def _handle_change_requested(self, payload: Dict[str, Any]):
        """Handle change request event"""
        change_id = payload.get("change_id")
        
        self.execute_activity("chg_001", {
            "change_id": change_id,
            "change_type": payload.get("change_type", "standard"),
            "description": payload.get("description", ""),
            "requestor": payload.get("requestor", "")
        })
    
    def _handle_service_request(self, payload: Dict[str, Any]):
        """Handle service request event"""
        request_id = payload.get("request_id")
        
        self.execute_activity("sd_001", {
            "request_id": request_id,
            "request_type": payload.get("request_type", ""),
            "requestor": payload.get("requestor", ""),
            "description": payload.get("description", "")
        })
    
    def execute_activity(self, activity_id: str, context: Dict[str, Any]) -> str:
        """Execute an ITIL activity using RACI assignments"""
        activity = self.raci_matrix.get_activity(activity_id)
        if not activity:
            raise ValueError(f"Activity {activity_id} not found in RACI matrix")
        
        execution_id = f"{activity_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        execution = ActivityExecution(
            activity_id=activity_id,
            execution_id=execution_id,
            timestamp=datetime.now(),
            status="planned"
        )
        
        self.active_executions[execution_id] = execution
        
        logger.info(f"🎯 Executing activity: {activity.activity_name} ({execution_id})")
        
        try:
            # Phase 1: Assign agents based on RACI
            self._assign_agents_to_activity(execution, activity, context)
            
            # Phase 2: Execute with responsible agents
            self._execute_with_responsible_agents(execution, activity, context)
            
            # Phase 3: Consult with designated agents
            self._consult_with_agents(execution, activity, context)
            
            # Phase 4: Inform designated agents
            self._inform_agents(execution, activity, context)
            
            # Phase 5: Get accountability sign-off
            self._get_accountability_signoff(execution, activity, context)
            
            execution.status = "completed"
            logger.info(f"✅ Activity {activity.activity_name} completed successfully")
            
        except Exception as e:
            execution.status = "failed"
            logger.error(f"❌ Activity {activity.activity_name} failed: {str(e)}")
            self._handle_activity_failure(execution, activity, str(e))
        
        # Store execution record
        self._store_execution_record(execution)
        
        return execution_id
    
    def _assign_agents_to_activity(self, execution: ActivityExecution, 
                                  activity: ProcessActivity, context: Dict[str, Any]):
        """Assign agents to activity based on RACI matrix"""
        for assignment in activity.raci_assignments:
            # Check conditions if any
            if self._evaluate_assignment_conditions(assignment, context):
                execution.assigned_agents[assignment.agent_role] = assignment.raci_role
                
                # Update agent workload
                if assignment.raci_role == RACIRole.RESPONSIBLE:
                    self.agent_workloads[assignment.agent_role].active_activities.append(
                        execution.execution_id
                    )
                elif assignment.raci_role == RACIRole.CONSULTED:
                    self.agent_workloads[assignment.agent_role].pending_consultations.append(
                        execution.execution_id
                    )
        
        logger.info(f"Assigned {len(execution.assigned_agents)} agents to activity {activity.activity_id}")
    
    def _evaluate_assignment_conditions(self, assignment: RACIAssignment, 
                                      context: Dict[str, Any]) -> bool:
        """Evaluate if assignment conditions are met"""
        if not assignment.conditions:
            return True
        
        for condition_key, condition_value in assignment.conditions.items():
            context_value = context.get(condition_key)
            if context_value != condition_value:
                return False
        
        return True
    
    def _execute_with_responsible_agents(self, execution: ActivityExecution,
                                       activity: ProcessActivity, context: Dict[str, Any]):
        """Execute activity with responsible agents"""
        execution.status = "in_progress"
        
        responsible_agents = [role for role, raci_role in execution.assigned_agents.items()
                            if raci_role == RACIRole.RESPONSIBLE]
        
        if not responsible_agents:
            raise ValueError(f"No responsible agents assigned to activity {activity.activity_id}")
        
        # Execute with primary responsible agent (highest priority)
        primary_agent = self._select_primary_responsible_agent(responsible_agents, activity)
        
        logger.info(f"🔧 Executing with primary responsible agent: {primary_agent.value}")
        
        # Get agent crew and execute
        agent_crew = self.agent_crews[primary_agent]
        results = agent_crew.execute_itil_activity(
            activity_type=activity.process.value,
            activity_name=activity.activity_name,
            context=context
        )
        
        execution.results["primary_execution"] = {
            "agent_role": primary_agent.value,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
        # Update agent workload
        self.agent_workloads[primary_agent].last_activity_timestamp = datetime.now()
    
    def _select_primary_responsible_agent(self, responsible_agents: List[AgentRole],
                                        activity: ProcessActivity) -> AgentRole:
        """Select primary responsible agent based on priority and workload"""
        # Get assignment priorities
        agent_priorities = {}
        for assignment in activity.raci_assignments:
            if (assignment.agent_role in responsible_agents and 
                assignment.raci_role == RACIRole.RESPONSIBLE):
                agent_priorities[assignment.agent_role] = assignment.priority
        
        # Sort by priority (lower number = higher priority) and workload
        sorted_agents = sorted(responsible_agents, key=lambda agent: (
            agent_priorities.get(agent, 999),
            self.agent_workloads[agent].capacity_utilization
        ))
        
        return sorted_agents[0]
    
    def _consult_with_agents(self, execution: ActivityExecution,
                           activity: ProcessActivity, context: Dict[str, Any]):
        """Consult with designated agents"""
        consulted_agents = [role for role, raci_role in execution.assigned_agents.items()
                          if raci_role == RACIRole.CONSULTED]
        
        for agent_role in consulted_agents:
            logger.info(f"💬 Consulting with {agent_role.value}")
            
            agent_crew = self.agent_crews[agent_role]
            consultation_results = agent_crew.provide_consultation(
                activity_type=activity.process.value,
                activity_context=context,
                current_results=execution.results.get("primary_execution", {})
            )
            
            execution.consultation_log.append({
                "agent_role": agent_role.value,
                "consultation": consultation_results,
                "timestamp": datetime.now().isoformat()
            })
            
            # Remove from pending consultations
            if execution.execution_id in self.agent_workloads[agent_role].pending_consultations:
                self.agent_workloads[agent_role].pending_consultations.remove(execution.execution_id)
    
    def _inform_agents(self, execution: ActivityExecution,
                      activity: ProcessActivity, context: Dict[str, Any]):
        """Inform designated agents of activity results"""
        informed_agents = [role for role, raci_role in execution.assigned_agents.items()
                         if raci_role == RACIRole.INFORMED]
        
        for agent_role in informed_agents:
            logger.info(f"📢 Informing {agent_role.value}")
            
            # Create notification
            notification = {
                "activity_id": activity.activity_id,
                "activity_name": activity.activity_name,
                "execution_id": execution.execution_id,
                "status": execution.status,
                "results_summary": self._create_results_summary(execution),
                "timestamp": datetime.now().isoformat()
            }
            
            # Send notification (in real implementation, this could be email, chat, etc.)
            self._send_notification(agent_role, notification)
            execution.notifications_sent.append(agent_role)
    
    def _get_accountability_signoff(self, execution: ActivityExecution,
                                  activity: ProcessActivity, context: Dict[str, Any]):
        """Get sign-off from accountable agent"""
        accountable_agents = [role for role, raci_role in execution.assigned_agents.items()
                            if raci_role == RACIRole.ACCOUNTABLE]
        
        if not accountable_agents:
            logger.warning(f"No accountable agent for activity {activity.activity_id}")
            return
        
        accountable_agent = accountable_agents[0]  # Should be only one
        logger.info(f"✅ Getting accountability sign-off from {accountable_agent.value}")
        
        agent_crew = self.agent_crews[accountable_agent]
        signoff_result = agent_crew.provide_accountability_signoff(
            activity_type=activity.process.value,
            execution_summary=execution.results,
            consultation_log=execution.consultation_log
        )
        
        execution.results["accountability_signoff"] = {
            "agent_role": accountable_agent.value,
            "signoff": signoff_result,
            "timestamp": datetime.now().isoformat()
        }
    
    def _handle_activity_failure(self, execution: ActivityExecution,
                               activity: ProcessActivity, error_message: str):
        """Handle activity execution failure"""
        logger.error(f"Activity {activity.activity_name} failed: {error_message}")
        
        # Determine escalation based on RACI
        accountable_agent = next(
            (role for role, raci_role in execution.assigned_agents.items()
             if raci_role == RACIRole.ACCOUNTABLE), None
        )
        
        if accountable_agent:
            escalation = {
                "timestamp": datetime.now().isoformat(),
                "escalated_to": accountable_agent.value,
                "reason": "activity_failure",
                "error_message": error_message
            }
            execution.escalations.append(escalation)
            
            # Notify accountable agent
            self._send_escalation_notification(accountable_agent, execution, error_message)
    
    def _create_results_summary(self, execution: ActivityExecution) -> Dict[str, Any]:
        """Create summary of execution results"""
        return {
            "execution_id": execution.execution_id,
            "status": execution.status,
            "agents_involved": len(execution.assigned_agents),
            "consultations_completed": len(execution.consultation_log),
            "has_accountability_signoff": "accountability_signoff" in execution.results
        }
    
    def _send_notification(self, agent_role: AgentRole, notification: Dict[str, Any]):
        """Send notification to agent (placeholder for actual implementation)"""
        # In real implementation, this would send actual notifications
        json_store.append_record("agent_notifications", {
            "agent_role": agent_role.value,
            "notification": notification
        })
    
    def _send_escalation_notification(self, agent_role: AgentRole, 
                                    execution: ActivityExecution, error_message: str):
        """Send escalation notification"""
        json_store.append_record("agent_escalations", {
            "agent_role": agent_role.value,
            "execution_id": execution.execution_id,
            "error_message": error_message,
            "timestamp": datetime.now().isoformat()
        })
    
    def _store_execution_record(self, execution: ActivityExecution):
        """Store execution record for audit trail"""
        json_store.append_record("activity_executions", {
            "execution_id": execution.execution_id,
            "activity_id": execution.activity_id,
            "timestamp": execution.timestamp.isoformat(),
            "status": execution.status,
            "assigned_agents": {
                role.value: raci_role.value 
                for role, raci_role in execution.assigned_agents.items()
            },
            "results": execution.results,
            "escalations": execution.escalations,
            "consultation_log": execution.consultation_log,
            "notifications_sent": [role.value for role in execution.notifications_sent]
        })
    
    def get_agent_workload_report(self) -> Dict[str, Any]:
        """Generate agent workload report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "agents": {}
        }
        
        for role, workload in self.agent_workloads.items():
            report["agents"][role.value] = {
                "active_activities": len(workload.active_activities),
                "pending_consultations": len(workload.pending_consultations),
                "capacity_utilization": workload.capacity_utilization,
                "last_activity": workload.last_activity_timestamp.isoformat() 
                              if workload.last_activity_timestamp else None
            }
        
        return report
    
    def get_raci_compliance_report(self) -> Dict[str, Any]:
        """Generate RACI compliance report"""
        validation_issues = self.raci_matrix.validate_matrix()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_activities": len(self.raci_matrix.activities),
            "validation_issues": validation_issues,
            "compliance_status": "compliant" if not validation_issues else "non_compliant"
        }


def create_raci_orchestrator(custom_raci_matrix: Optional[RACIMatrix] = None) -> RACIAgentOrchestrator:
    """Create a RACI-enabled agent orchestrator"""
    return RACIAgentOrchestrator(custom_raci_matrix)


if __name__ == "__main__":
    # Demo: RACI-enabled agent orchestration
    print("🎯 ReasonOps RACI-Enabled Agent Orchestrator")
    print("=" * 50)
    
    # Create orchestrator
    orchestrator = create_raci_orchestrator()
    
    # Show agent initialization
    print(f"✅ Initialized {len(orchestrator.agent_crews)} AI agent crews")
    
    # Demo incident handling
    print("\n🚨 Demo: Incident Management with RACI")
    incident_context = {
        "incident_id": "INC-2024-001",
        "severity": "high", 
        "description": "Database connection timeout",
        "service_name": "Customer Portal",
        "affected_users": 1500
    }
    
    execution_id = orchestrator.execute_activity("inc_002", incident_context)
    print(f"📋 Incident classification executed: {execution_id}")
    
    # Show workload report
    print("\n📊 Agent Workload Report:")
    workload_report = orchestrator.get_agent_workload_report()
    for agent, workload in workload_report["agents"].items():
        if workload["active_activities"] > 0 or workload["pending_consultations"] > 0:
            print(f"   {agent}: {workload['active_activities']} active, {workload['pending_consultations']} pending")
    
    # Show compliance report
    print("\n🔍 RACI Compliance Report:")
    compliance = orchestrator.get_raci_compliance_report()
    print(f"   Status: {compliance['compliance_status']}")
    print(f"   Total Activities: {compliance['total_activities']}")
    if compliance['validation_issues']:
        print(f"   Issues: {len(compliance['validation_issues'])}")