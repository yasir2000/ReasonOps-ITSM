"""
RACI Model Framework for ReasonOps ITIL/ITSM AI Agents

This module implements the RACI (Responsible, Accountable, Consulted, Informed) model
for intelligent assignment of ITIL/ITSM activities to AI agents.

Based on YaSM RACI Matrix for ITIL processes, this framework enables:
- Automatic role assignment for AI agents based on RACI definitions
- Dynamic responsibility distribution for ITIL activities
- Intelligent escalation and consultation patterns
- Audit trail for accountability tracking

Reference: YaSM-RACI-Matrix.pdf in docs/
"""

from __future__ import annotations
import json
from typing import Dict, List, Set, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class RACIRole(Enum):
    """RACI responsibility types"""
    RESPONSIBLE = "R"  # Does the work to complete the task
    ACCOUNTABLE = "A"  # Ultimately answerable for completion and sign-off
    CONSULTED = "C"    # Provides input and advice
    INFORMED = "I"     # Needs to be informed of results/decisions


class ITILProcess(Enum):
    """ITIL 4 Processes/Practices for RACI assignment"""
    # Service Management Practices
    INCIDENT_MANAGEMENT = "incident_management"
    PROBLEM_MANAGEMENT = "problem_management"
    CHANGE_ENABLEMENT = "change_enablement"
    RELEASE_MANAGEMENT = "release_management"
    SERVICE_REQUEST_MANAGEMENT = "service_request_management"
    SERVICE_DESK = "service_desk"
    SERVICE_LEVEL_MANAGEMENT = "service_level_management"
    SERVICE_CATALOGUE_MANAGEMENT = "service_catalogue_management"
    SERVICE_CONFIGURATION_MANAGEMENT = "service_configuration_management"
    AVAILABILITY_MANAGEMENT = "availability_management"
    CAPACITY_MANAGEMENT = "capacity_management"
    IT_ASSET_MANAGEMENT = "it_asset_management"
    MONITORING_EVENT_MANAGEMENT = "monitoring_event_management"
    SERVICE_CONTINUITY_MANAGEMENT = "service_continuity_management"
    SERVICE_VALIDATION_TESTING = "service_validation_testing"
    
    # General Management Practices
    CONTINUAL_IMPROVEMENT = "continual_improvement"
    INFORMATION_SECURITY_MANAGEMENT = "information_security_management"
    KNOWLEDGE_MANAGEMENT = "knowledge_management"
    MEASUREMENT_REPORTING = "measurement_reporting"
    ORGANIZATIONAL_CHANGE_MANAGEMENT = "organizational_change_management"
    PORTFOLIO_MANAGEMENT = "portfolio_management"
    PROJECT_MANAGEMENT = "project_management"
    RELATIONSHIP_MANAGEMENT = "relationship_management"
    RISK_MANAGEMENT = "risk_management"
    SERVICE_FINANCIAL_MANAGEMENT = "service_financial_management"
    STRATEGY_MANAGEMENT = "strategy_management"
    SUPPLIER_MANAGEMENT = "supplier_management"
    WORKFORCE_TALENT_MANAGEMENT = "workforce_talent_management"


class AgentRole(Enum):
    """Enhanced AI Agent roles based on ITIL organizational roles"""
    # Service Management Roles
    INCIDENT_ANALYST = "incident_analyst"
    INCIDENT_MANAGER = "incident_manager"
    PROBLEM_ANALYST = "problem_analyst"
    PROBLEM_MANAGER = "problem_manager"
    CHANGE_COORDINATOR = "change_coordinator"
    CHANGE_MANAGER = "change_manager"
    CHANGE_ADVISORY_BOARD = "change_advisory_board"
    RELEASE_MANAGER = "release_manager"
    SERVICE_DESK_AGENT = "service_desk_agent"
    SERVICE_DESK_SUPERVISOR = "service_desk_supervisor"
    SERVICE_LEVEL_MANAGER = "service_level_manager"
    SERVICE_OWNER = "service_owner"
    PROCESS_OWNER = "process_owner"
    
    # Technical Roles
    TECHNICAL_SPECIALIST = "technical_specialist"
    TECHNICAL_ANALYST = "technical_analyst"
    SYSTEM_ADMINISTRATOR = "system_administrator"
    NETWORK_ADMINISTRATOR = "network_administrator"
    DATABASE_ADMINISTRATOR = "database_administrator"
    SECURITY_ANALYST = "security_analyst"
    SECURITY_MANAGER = "security_manager"
    
    # Management Roles
    IT_MANAGER = "it_manager"
    SERVICE_MANAGER = "service_manager"
    OPERATIONS_MANAGER = "operations_manager"
    ESCALATION_MANAGER = "escalation_manager"
    KNOWLEDGE_MANAGER = "knowledge_manager"
    CAPACITY_MANAGER = "capacity_manager"
    AVAILABILITY_MANAGER = "availability_manager"
    CONTINUITY_MANAGER = "continuity_manager"
    
    # Business Roles
    BUSINESS_RELATIONSHIP_MANAGER = "business_relationship_manager"
    BUSINESS_ANALYST = "business_analyst"
    CUSTOMER_REPRESENTATIVE = "customer_representative"
    USER_REPRESENTATIVE = "user_representative"
    
    # Specialized Roles
    COMPLIANCE_OFFICER = "compliance_officer"
    AUDIT_MANAGER = "audit_manager"
    VENDOR_MANAGER = "vendor_manager"
    FINANCIAL_MANAGER = "financial_manager"


@dataclass
class RACIAssignment:
    """Individual RACI assignment for a role in an activity"""
    agent_role: AgentRole
    raci_role: RACIRole
    priority: int = 1  # 1=highest, used for conflict resolution
    conditions: Dict[str, Any] = field(default_factory=dict)  # Conditional assignments
    
    def __str__(self) -> str:
        return f"{self.agent_role.value}({self.raci_role.value})"


@dataclass
class ProcessActivity:
    """Represents an ITIL process activity with RACI assignments"""
    activity_id: str
    activity_name: str
    process: ITILProcess
    description: str
    raci_assignments: List[RACIAssignment] = field(default_factory=list)
    sub_activities: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    artifacts: List[str] = field(default_factory=list)
    
    def get_responsible_agents(self) -> List[AgentRole]:
        """Get all agents with Responsible (R) role"""
        return [assignment.agent_role for assignment in self.raci_assignments 
                if assignment.raci_role == RACIRole.RESPONSIBLE]
    
    def get_accountable_agent(self) -> Optional[AgentRole]:
        """Get the accountable agent (should be only one)"""
        accountable = [assignment.agent_role for assignment in self.raci_assignments 
                      if assignment.raci_role == RACIRole.ACCOUNTABLE]
        return accountable[0] if accountable else None
    
    def get_consulted_agents(self) -> List[AgentRole]:
        """Get all agents to be consulted"""
        return [assignment.agent_role for assignment in self.raci_assignments 
                if assignment.raci_role == RACIRole.CONSULTED]
    
    def get_informed_agents(self) -> List[AgentRole]:
        """Get all agents to be informed"""
        return [assignment.agent_role for assignment in self.raci_assignments 
                if assignment.raci_role == RACIRole.INFORMED]


class RACIMatrix:
    """RACI Matrix implementation for ITIL processes"""
    
    def __init__(self):
        self.activities: Dict[str, ProcessActivity] = {}
        self.role_mappings: Dict[AgentRole, List[str]] = {}
        self._load_default_raci_definitions()
    
    def _load_default_raci_definitions(self):
        """Load default RACI definitions based on YaSM RACI Matrix"""
        # Incident Management RACI definitions
        self._define_incident_management_raci()
        self._define_problem_management_raci()
        self._define_change_enablement_raci()
        self._define_service_desk_raci()
        self._define_service_level_management_raci()
        # Add more processes as needed
    
    def _define_incident_management_raci(self):
        """Define RACI for Incident Management activities"""
        
        # Incident Detection and Recording
        self.add_activity(ProcessActivity(
            activity_id="inc_001",
            activity_name="Incident Detection and Recording",
            process=ITILProcess.INCIDENT_MANAGEMENT,
            description="Detect, receive, and record incidents",
            raci_assignments=[
                RACIAssignment(AgentRole.SERVICE_DESK_AGENT, RACIRole.RESPONSIBLE),
                RACIAssignment(AgentRole.INCIDENT_MANAGER, RACIRole.ACCOUNTABLE),
                RACIAssignment(AgentRole.MONITORING_AGENT, RACIRole.RESPONSIBLE, conditions={"trigger": "automated"}),
                RACIAssignment(AgentRole.USER_REPRESENTATIVE, RACIRole.INFORMED),
            ]
        ))
        
        # Incident Classification and Prioritization
        self.add_activity(ProcessActivity(
            activity_id="inc_002", 
            activity_name="Incident Classification and Prioritization",
            process=ITILProcess.INCIDENT_MANAGEMENT,
            description="Classify and prioritize incidents based on impact and urgency",
            raci_assignments=[
                RACIAssignment(AgentRole.INCIDENT_ANALYST, RACIRole.RESPONSIBLE),
                RACIAssignment(AgentRole.INCIDENT_MANAGER, RACIRole.ACCOUNTABLE),
                RACIAssignment(AgentRole.SERVICE_OWNER, RACIRole.CONSULTED),
                RACIAssignment(AgentRole.BUSINESS_RELATIONSHIP_MANAGER, RACIRole.CONSULTED),
                RACIAssignment(AgentRole.SERVICE_DESK_SUPERVISOR, RACIRole.INFORMED),
            ]
        ))
        
        # Initial Diagnosis and Investigation
        self.add_activity(ProcessActivity(
            activity_id="inc_003",
            activity_name="Initial Diagnosis and Investigation", 
            process=ITILProcess.INCIDENT_MANAGEMENT,
            description="Perform initial diagnosis and investigation",
            raci_assignments=[
                RACIAssignment(AgentRole.SERVICE_DESK_AGENT, RACIRole.RESPONSIBLE, priority=1),
                RACIAssignment(AgentRole.TECHNICAL_SPECIALIST, RACIRole.RESPONSIBLE, priority=2),
                RACIAssignment(AgentRole.INCIDENT_ANALYST, RACIRole.ACCOUNTABLE),
                RACIAssignment(AgentRole.KNOWLEDGE_MANAGER, RACIRole.CONSULTED),
                RACIAssignment(AgentRole.PROBLEM_ANALYST, RACIRole.CONSULTED),
            ]
        ))
        
        # Escalation (Functional and Hierarchical)
        self.add_activity(ProcessActivity(
            activity_id="inc_004",
            activity_name="Incident Escalation",
            process=ITILProcess.INCIDENT_MANAGEMENT, 
            description="Escalate incidents functionally or hierarchically",
            raci_assignments=[
                RACIAssignment(AgentRole.ESCALATION_MANAGER, RACIRole.RESPONSIBLE),
                RACIAssignment(AgentRole.INCIDENT_MANAGER, RACIRole.ACCOUNTABLE),
                RACIAssignment(AgentRole.TECHNICAL_SPECIALIST, RACIRole.RESPONSIBLE, conditions={"escalation_type": "functional"}),
                RACIAssignment(AgentRole.IT_MANAGER, RACIRole.RESPONSIBLE, conditions={"escalation_type": "hierarchical"}),
                RACIAssignment(AgentRole.SERVICE_OWNER, RACIRole.INFORMED),
                RACIAssignment(AgentRole.CUSTOMER_REPRESENTATIVE, RACIRole.INFORMED),
            ]
        ))
        
        # Resolution and Recovery
        self.add_activity(ProcessActivity(
            activity_id="inc_005",
            activity_name="Resolution and Recovery",
            process=ITILProcess.INCIDENT_MANAGEMENT,
            description="Resolve incident and recover normal service",
            raci_assignments=[
                RACIAssignment(AgentRole.TECHNICAL_SPECIALIST, RACIRole.RESPONSIBLE),
                RACIAssignment(AgentRole.INCIDENT_ANALYST, RACIRole.ACCOUNTABLE),
                RACIAssignment(AgentRole.CHANGE_COORDINATOR, RACIRole.CONSULTED, conditions={"requires_change": True}),
                RACIAssignment(AgentRole.SERVICE_OWNER, RACIRole.INFORMED),
                RACIAssignment(AgentRole.USER_REPRESENTATIVE, RACIRole.INFORMED),
            ]
        ))
        
        # Incident Closure
        self.add_activity(ProcessActivity(
            activity_id="inc_006",
            activity_name="Incident Closure",
            process=ITILProcess.INCIDENT_MANAGEMENT,
            description="Close incident and update records",
            raci_assignments=[
                RACIAssignment(AgentRole.SERVICE_DESK_AGENT, RACIRole.RESPONSIBLE),
                RACIAssignment(AgentRole.INCIDENT_MANAGER, RACIRole.ACCOUNTABLE),
                RACIAssignment(AgentRole.USER_REPRESENTATIVE, RACIRole.CONSULTED),
                RACIAssignment(AgentRole.KNOWLEDGE_MANAGER, RACIRole.INFORMED),
                RACIAssignment(AgentRole.PROBLEM_ANALYST, RACIRole.INFORMED),
            ]
        ))
    
    def _define_problem_management_raci(self):
        """Define RACI for Problem Management activities"""
        
        # Problem Identification
        self.add_activity(ProcessActivity(
            activity_id="prb_001",
            activity_name="Problem Identification",
            process=ITILProcess.PROBLEM_MANAGEMENT,
            description="Identify problems from incident patterns or proactively",
            raci_assignments=[
                RACIAssignment(AgentRole.PROBLEM_ANALYST, RACIRole.RESPONSIBLE),
                RACIAssignment(AgentRole.PROBLEM_MANAGER, RACIRole.ACCOUNTABLE),
                RACIAssignment(AgentRole.INCIDENT_ANALYST, RACIRole.CONSULTED),
                RACIAssignment(AgentRole.MONITORING_AGENT, RACIRole.CONSULTED),
                RACIAssignment(AgentRole.SERVICE_OWNER, RACIRole.INFORMED),
            ]
        ))
        
        # Problem Investigation and Diagnosis
        self.add_activity(ProcessActivity(
            activity_id="prb_002",
            activity_name="Problem Investigation and Diagnosis",
            process=ITILProcess.PROBLEM_MANAGEMENT,
            description="Investigate and diagnose root cause of problems",
            raci_assignments=[
                RACIAssignment(AgentRole.PROBLEM_ANALYST, RACIRole.RESPONSIBLE),
                RACIAssignment(AgentRole.TECHNICAL_SPECIALIST, RACIRole.RESPONSIBLE),
                RACIAssignment(AgentRole.PROBLEM_MANAGER, RACIRole.ACCOUNTABLE),
                RACIAssignment(AgentRole.INCIDENT_ANALYST, RACIRole.CONSULTED),
                RACIAssignment(AgentRole.CHANGE_COORDINATOR, RACIRole.CONSULTED),
                RACIAssignment(AgentRole.KNOWLEDGE_MANAGER, RACIRole.CONSULTED),
            ]
        ))
        
        # Workaround Development
        self.add_activity(ProcessActivity(
            activity_id="prb_003",
            activity_name="Workaround Development",
            process=ITILProcess.PROBLEM_MANAGEMENT,
            description="Develop workarounds for known errors",
            raci_assignments=[
                RACIAssignment(AgentRole.TECHNICAL_SPECIALIST, RACIRole.RESPONSIBLE),
                RACIAssignment(AgentRole.PROBLEM_ANALYST, RACIRole.ACCOUNTABLE),
                RACIAssignment(AgentRole.SERVICE_DESK_AGENT, RACIRole.CONSULTED),
                RACIAssignment(AgentRole.KNOWLEDGE_MANAGER, RACIRole.INFORMED),
                RACIAssignment(AgentRole.INCIDENT_ANALYST, RACIRole.INFORMED),
            ]
        ))
    
    def _define_change_enablement_raci(self):
        """Define RACI for Change Enablement activities"""
        
        # Change Request Creation
        self.add_activity(ProcessActivity(
            activity_id="chg_001",
            activity_name="Change Request Creation",
            process=ITILProcess.CHANGE_ENABLEMENT,
            description="Create and submit change requests",
            raci_assignments=[
                RACIAssignment(AgentRole.CHANGE_COORDINATOR, RACIRole.RESPONSIBLE),
                RACIAssignment(AgentRole.CHANGE_MANAGER, RACIRole.ACCOUNTABLE),
                RACIAssignment(AgentRole.SERVICE_OWNER, RACIRole.CONSULTED),
                RACIAssignment(AgentRole.TECHNICAL_SPECIALIST, RACIRole.CONSULTED),
                RACIAssignment(AgentRole.BUSINESS_ANALYST, RACIRole.CONSULTED),
            ]
        ))
        
        # Change Assessment and Authorization
        self.add_activity(ProcessActivity(
            activity_id="chg_002",
            activity_name="Change Assessment and Authorization",
            process=ITILProcess.CHANGE_ENABLEMENT,
            description="Assess change impact, risk, and authorize implementation",
            raci_assignments=[
                RACIAssignment(AgentRole.CHANGE_ADVISORY_BOARD, RACIRole.RESPONSIBLE),
                RACIAssignment(AgentRole.CHANGE_MANAGER, RACIRole.ACCOUNTABLE),
                RACIAssignment(AgentRole.RISK_ANALYST, RACIRole.CONSULTED),
                RACIAssignment(AgentRole.SECURITY_ANALYST, RACIRole.CONSULTED),
                RACIAssignment(AgentRole.SERVICE_OWNER, RACIRole.CONSULTED),
                RACIAssignment(AgentRole.BUSINESS_RELATIONSHIP_MANAGER, RACIRole.INFORMED),
            ]
        ))
    
    def _define_service_desk_raci(self):
        """Define RACI for Service Desk activities"""
        
        # User Contact and Request Logging
        self.add_activity(ProcessActivity(
            activity_id="sd_001",
            activity_name="User Contact and Request Logging",
            process=ITILProcess.SERVICE_DESK,
            description="Receive user contacts and log service requests",
            raci_assignments=[
                RACIAssignment(AgentRole.SERVICE_DESK_AGENT, RACIRole.RESPONSIBLE),
                RACIAssignment(AgentRole.SERVICE_DESK_SUPERVISOR, RACIRole.ACCOUNTABLE),
                RACIAssignment(AgentRole.KNOWLEDGE_MANAGER, RACIRole.CONSULTED),
                RACIAssignment(AgentRole.USER_REPRESENTATIVE, RACIRole.INFORMED),
            ]
        ))
    
    def _define_service_level_management_raci(self):
        """Define RACI for Service Level Management activities"""
        
        # SLA Development and Negotiation
        self.add_activity(ProcessActivity(
            activity_id="slm_001",
            activity_name="SLA Development and Negotiation", 
            process=ITILProcess.SERVICE_LEVEL_MANAGEMENT,
            description="Develop and negotiate service level agreements",
            raci_assignments=[
                RACIAssignment(AgentRole.SERVICE_LEVEL_MANAGER, RACIRole.RESPONSIBLE),
                RACIAssignment(AgentRole.SERVICE_MANAGER, RACIRole.ACCOUNTABLE),
                RACIAssignment(AgentRole.BUSINESS_RELATIONSHIP_MANAGER, RACIRole.CONSULTED),
                RACIAssignment(AgentRole.SERVICE_OWNER, RACIRole.CONSULTED),
                RACIAssignment(AgentRole.CUSTOMER_REPRESENTATIVE, RACIRole.CONSULTED),
                RACIAssignment(AgentRole.OPERATIONS_MANAGER, RACIRole.INFORMED),
            ]
        ))
    
    def add_activity(self, activity: ProcessActivity):
        """Add an activity to the RACI matrix"""
        self.activities[activity.activity_id] = activity
        
        # Update role mappings
        for assignment in activity.raci_assignments:
            if assignment.agent_role not in self.role_mappings:
                self.role_mappings[assignment.agent_role] = []
            self.role_mappings[assignment.agent_role].append(activity.activity_id)
    
    def get_activity(self, activity_id: str) -> Optional[ProcessActivity]:
        """Get activity by ID"""
        return self.activities.get(activity_id)
    
    def get_activities_for_role(self, role: AgentRole) -> List[ProcessActivity]:
        """Get all activities where a role has any RACI assignment"""
        activity_ids = self.role_mappings.get(role, [])
        return [self.activities[aid] for aid in activity_ids if aid in self.activities]
    
    def get_activities_for_process(self, process: ITILProcess) -> List[ProcessActivity]:
        """Get all activities for a specific ITIL process"""
        return [activity for activity in self.activities.values() 
                if activity.process == process]
    
    def get_responsible_agents_for_activity(self, activity_id: str) -> List[AgentRole]:
        """Get all responsible agents for an activity"""
        activity = self.get_activity(activity_id)
        return activity.get_responsible_agents() if activity else []
    
    def get_accountable_agent_for_activity(self, activity_id: str) -> Optional[AgentRole]:
        """Get the accountable agent for an activity"""
        activity = self.get_activity(activity_id)
        return activity.get_accountable_agent() if activity else None
    
    def validate_matrix(self) -> List[str]:
        """Validate RACI matrix for common issues"""
        issues = []
        
        for activity in self.activities.values():
            # Check for accountable agent (should have exactly one)
            accountable_agents = [a for a in activity.raci_assignments 
                                if a.raci_role == RACIRole.ACCOUNTABLE]
            if len(accountable_agents) == 0:
                issues.append(f"Activity {activity.activity_id} has no accountable agent")
            elif len(accountable_agents) > 1:
                issues.append(f"Activity {activity.activity_id} has multiple accountable agents")
            
            # Check for responsible agents (should have at least one)
            responsible_agents = [a for a in activity.raci_assignments 
                                if a.raci_role == RACIRole.RESPONSIBLE]
            if len(responsible_agents) == 0:
                issues.append(f"Activity {activity.activity_id} has no responsible agents")
        
        return issues
    
    def export_to_dict(self) -> Dict[str, Any]:
        """Export RACI matrix to dictionary format"""
        return {
            "activities": {
                aid: {
                    "activity_name": activity.activity_name,
                    "process": activity.process.value,
                    "description": activity.description,
                    "raci_assignments": [
                        {
                            "agent_role": assignment.agent_role.value,
                            "raci_role": assignment.raci_role.value,
                            "priority": assignment.priority,
                            "conditions": assignment.conditions
                        }
                        for assignment in activity.raci_assignments
                    ],
                    "sub_activities": activity.sub_activities,
                    "prerequisites": activity.prerequisites,
                    "artifacts": activity.artifacts
                }
                for aid, activity in self.activities.items()
            },
            "validation_issues": self.validate_matrix()
        }
    
    def save_to_file(self, filepath: str):
        """Save RACI matrix to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.export_to_dict(), f, indent=2)


# Add missing agent roles for monitoring
class MonitoringAgent:
    pass

AgentRole.MONITORING_AGENT = "monitoring_agent"
AgentRole.RISK_ANALYST = "risk_analyst"


def create_default_raci_matrix() -> RACIMatrix:
    """Create and return a default RACI matrix for ITIL processes"""
    return RACIMatrix()


if __name__ == "__main__":
    # Demo: Create and validate RACI matrix
    matrix = create_default_raci_matrix()
    
    print("🎯 ReasonOps RACI Matrix for ITIL AI Agents")
    print("=" * 50)
    
    # Show validation results
    issues = matrix.validate_matrix()
    if issues:
        print(f"⚠️  Found {len(issues)} validation issues:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("✅ RACI Matrix validation passed")
    
    # Show some statistics
    print(f"\n📊 Matrix Statistics:")
    print(f"   - Total Activities: {len(matrix.activities)}")
    print(f"   - Total Agent Roles: {len(matrix.role_mappings)}")
    
    # Show example assignments
    print(f"\n🔍 Example: Incident Classification (inc_002)")
    activity = matrix.get_activity("inc_002")
    if activity:
        print(f"   Responsible: {[r.value for r in activity.get_responsible_agents()]}")
        print(f"   Accountable: {activity.get_accountable_agent().value if activity.get_accountable_agent() else 'None'}")
        print(f"   Consulted: {[r.value for r in activity.get_consulted_agents()]}")
        print(f"   Informed: {[r.value for r in activity.get_informed_agents()]}")