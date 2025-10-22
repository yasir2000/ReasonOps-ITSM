"""
ITIL 4 Python Framework
Core Service Value System Implementation

This module provides the foundational classes and structures for implementing
the ITIL 4 Service Value System in Python.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
import uuid
import json


class Priority(Enum):
    """Priority levels for ITIL objects"""
    P1_CRITICAL = "P1 - Critical"
    P2_HIGH = "P2 - High"
    P3_MEDIUM = "P3 - Medium"
    P4_LOW = "P4 - Low"


class Status(Enum):
    """Common status values for ITIL objects"""
    NEW = "New"
    IN_PROGRESS = "In Progress"
    ON_HOLD = "On Hold"
    RESOLVED = "Resolved"
    CLOSED = "Closed"
    CANCELLED = "Cancelled"


class Impact(Enum):
    """Impact levels for ITIL objects"""
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class Urgency(Enum):
    """Urgency levels for ITIL objects"""
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


@dataclass
class Person:
    """Represents a person in the ITIL system"""
    id: str
    name: str
    email: str
    role: str
    department: str
    phone: Optional[str] = None
    manager: Optional[str] = None
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())


@dataclass
class ConfigurationItem:
    """Represents a Configuration Item (CI) in the CMDB"""
    id: str
    name: str
    type: str
    status: str
    environment: str
    owner: Optional[str] = None
    location: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None
    relationships: Optional[List[Dict[str, str]]] = None
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if self.attributes is None:
            self.attributes = {}
        if self.relationships is None:
            self.relationships = []


class ServiceValueSystem:
    """
    Core ITIL 4 Service Value System implementation
    
    Coordinates all components of the Service Value System including:
    - Guiding Principles
    - Governance
    - Service Value Chain
    - Practices
    - Continual Improvement
    """
    
    def __init__(self, organization_name: str):
        self.organization_name = organization_name
        self.guiding_principles = GuidingPrinciples()
        self.governance = GovernanceFramework()
        self.service_value_chain = ServiceValueChain()
        self.practices = PracticeRegistry()
        self.continual_improvement = ContinualImprovement()
        self.created_date = datetime.now()
        
    def __str__(self):
        return f"ITIL 4 Service Value System for {self.organization_name}"
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status and health"""
        return {
            "organization": self.organization_name,
            "created_date": self.created_date.isoformat(),
            "governance_status": self.governance.get_status(),
            "active_practices": self.practices.get_active_practices_count(),
            "improvement_initiatives": self.continual_improvement.get_active_initiatives_count(),
            "system_health": self._calculate_system_health()
        }
    
    def _calculate_system_health(self) -> str:
        """Calculate overall system health score"""
        # Simple health calculation based on component status
        scores = []
        scores.append(self.governance.get_health_score())
        scores.append(self.practices.get_health_score())
        scores.append(self.continual_improvement.get_health_score())
        
        avg_score = sum(scores) / len(scores)
        
        if avg_score >= 80:
            return "Excellent"
        elif avg_score >= 60:
            return "Good"
        elif avg_score >= 40:
            return "Fair"
        else:
            return "Needs Improvement"


class GuidingPrinciples:
    """
    ITIL 4 Seven Guiding Principles implementation
    """
    
    def __init__(self):
        self.principles = {
            "focus_on_value": {
                "name": "Focus on Value",
                "description": "Everything should link back to value for stakeholders",
                "adherence_score": 0,
                "examples": []
            },
            "start_where_you_are": {
                "name": "Start Where You Are",
                "description": "Don't start over without considering what is already available",
                "adherence_score": 0,
                "examples": []
            },
            "progress_iteratively": {
                "name": "Progress Iteratively with Feedback",
                "description": "Resist the temptation to do everything at once",
                "adherence_score": 0,
                "examples": []
            },
            "collaborate_and_promote_visibility": {
                "name": "Collaborate and Promote Visibility",
                "description": "Working together produces better outcomes",
                "adherence_score": 0,
                "examples": []
            },
            "think_work_holistically": {
                "name": "Think and Work Holistically",
                "description": "No service exists in isolation",
                "adherence_score": 0,
                "examples": []
            },
            "keep_it_simple_practical": {
                "name": "Keep It Simple and Practical",
                "description": "If a process doesn't provide value, eliminate it",
                "adherence_score": 0,
                "examples": []
            },
            "optimize_and_automate": {
                "name": "Optimize and Automate",
                "description": "Resources should be used to their best effect",
                "adherence_score": 0,
                "examples": []
            }
        }
    
    def get_principle(self, principle_key: str) -> Dict[str, Any]:
        """Get specific guiding principle information"""
        return self.principles.get(principle_key, {})
    
    def assess_adherence(self, principle_key: str, score: int) -> bool:
        """Assess adherence to a specific principle (0-100 score)"""
        if principle_key in self.principles and 0 <= score <= 100:
            self.principles[principle_key]["adherence_score"] = score
            return True
        return False
    
    def get_overall_adherence(self) -> float:
        """Calculate overall adherence to guiding principles"""
        scores = [p["adherence_score"] for p in self.principles.values()]
        return sum(scores) / len(scores) if scores else 0


class ServiceValueChain:
    """
    ITIL 4 Service Value Chain implementation
    
    Represents the six key activities that organizations perform to create value:
    - Plan
    - Improve
    - Engage
    - Design & Transition
    - Obtain/Build
    - Deliver & Support
    """
    
    def __init__(self):
        self.activities = {
            "plan": ServiceValueChainActivity(
                "Plan",
                "Ensure shared understanding of vision, current status, improvement direction"
            ),
            "improve": ServiceValueChainActivity(
                "Improve", 
                "Ensure continual improvement of products, services, and practices"
            ),
            "engage": ServiceValueChainActivity(
                "Engage",
                "Provide good understanding of stakeholder needs and transparency"
            ),
            "design_transition": ServiceValueChainActivity(
                "Design & Transition",
                "Ensure products and services meet stakeholder expectations"
            ),
            "obtain_build": ServiceValueChainActivity(
                "Obtain/Build",
                "Ensure service components are available when needed"
            ),
            "deliver_support": ServiceValueChainActivity(
                "Deliver & Support",
                "Ensure services are delivered and supported according to specifications"
            )
        }
        self.value_streams = []
    
    def create_value_stream(self, name: str, activities: List[str]) -> 'ValueStream':
        """Create a new value stream using specified activities"""
        value_stream = ValueStream(name, activities, self.activities)
        self.value_streams.append(value_stream)
        return value_stream
    
    def get_activity(self, activity_key: str) -> Optional['ServiceValueChainActivity']:
        """Get specific value chain activity"""
        return self.activities.get(activity_key)


class ServiceValueChainActivity:
    """Individual Service Value Chain Activity"""
    
    def __init__(self, name: str, purpose: str):
        self.name = name
        self.purpose = purpose
        self.inputs = []
        self.outputs = []
        self.key_practices = []
        self.performance_metrics = {}
    
    def add_input(self, input_item: str):
        """Add input to the activity"""
        self.inputs.append(input_item)
    
    def add_output(self, output_item: str):
        """Add output from the activity"""
        self.outputs.append(output_item)
    
    def add_practice(self, practice_name: str):
        """Add a practice that supports this activity"""
        self.key_practices.append(practice_name)


class ValueStream:
    """
    Value Stream - specific combination of Service Value Chain activities
    designed to respond to particular scenarios
    """
    
    def __init__(self, name: str, activity_sequence: List[str], activities: Dict[str, ServiceValueChainActivity]):
        self.name = name
        self.activity_sequence = activity_sequence
        self.activities = activities
        self.created_date = datetime.now()
        self.status = Status.NEW
        self.performance_data = {}
    
    def execute(self) -> Dict[str, Any]:
        """Execute the value stream"""
        execution_log = {
            "start_time": datetime.now(),
            "activities": [],
            "status": "success"
        }
        
        for activity_key in self.activity_sequence:
            if activity_key in self.activities:
                activity = self.activities[activity_key]
                execution_log["activities"].append({
                    "activity": activity.name,
                    "timestamp": datetime.now().isoformat(),
                    "status": "completed"
                })
            else:
                execution_log["status"] = "error"
                execution_log["error"] = f"Activity '{activity_key}' not found"
                break
        
        execution_log["end_time"] = datetime.now()
        execution_log["duration"] = (execution_log["end_time"] - execution_log["start_time"]).total_seconds()
        
        return execution_log


class GovernanceFramework:
    """
    ITIL 4 Governance Framework implementation
    """
    
    def __init__(self):
        self.governance_bodies = {}
        self.policies = {}
        self.decisions = []
        self.compliance_status = {}
        
    def create_governance_body(self, name: str, purpose: str, members: List[str]) -> 'GovernanceBody':
        """Create a new governance body"""
        body = GovernanceBody(name, purpose, members)
        self.governance_bodies[name] = body
        return body
    
    def add_policy(self, name: str, description: str, compliance_level: str) -> bool:
        """Add a governance policy"""
        self.policies[name] = {
            "description": description,
            "compliance_level": compliance_level,
            "created_date": datetime.now(),
            "status": "active"
        }
        return True
    
    def record_decision(self, decision: Dict[str, Any]) -> str:
        """Record a governance decision"""
        decision_id = str(uuid.uuid4())
        decision["id"] = decision_id
        decision["timestamp"] = datetime.now()
        self.decisions.append(decision)
        return decision_id
    
    def get_status(self) -> Dict[str, Any]:
        """Get governance framework status"""
        return {
            "governance_bodies": len(self.governance_bodies),
            "active_policies": len([p for p in self.policies.values() if p["status"] == "active"]),
            "decisions_this_month": len([d for d in self.decisions 
                                       if d["timestamp"].month == datetime.now().month]),
            "compliance_score": self._calculate_compliance_score()
        }
    
    def get_health_score(self) -> float:
        """Calculate governance health score"""
        # Simple calculation based on number of governance elements
        score = 0
        if len(self.governance_bodies) > 0:
            score += 30
        if len(self.policies) > 0:
            score += 30
        if len(self.decisions) > 0:
            score += 20
        if self._calculate_compliance_score() > 70:
            score += 20
        return min(score, 100)
    
    def _calculate_compliance_score(self) -> float:
        """Calculate overall compliance score"""
        if not self.compliance_status:
            return 0
        scores = list(self.compliance_status.values())
        return sum(scores) / len(scores) if scores else 0


class GovernanceBody:
    """Individual Governance Body (e.g., CAB, Investment Board)"""
    
    def __init__(self, name: str, purpose: str, members: List[str]):
        self.name = name
        self.purpose = purpose
        self.members = members
        self.meetings = []
        self.decisions = []
        self.created_date = datetime.now()
    
    def schedule_meeting(self, date: datetime, agenda: List[str]) -> str:
        """Schedule a governance meeting"""
        meeting_id = str(uuid.uuid4())
        meeting = {
            "id": meeting_id,
            "date": date,
            "agenda": agenda,
            "attendees": [],
            "decisions": [],
            "status": "scheduled"
        }
        self.meetings.append(meeting)
        return meeting_id
    
    def make_decision(self, decision_text: str, decision_type: str, impact: str) -> str:
        """Record a decision made by this governance body"""
        decision_id = str(uuid.uuid4())
        decision = {
            "id": decision_id,
            "text": decision_text,
            "type": decision_type,
            "impact": impact,
            "date": datetime.now(),
            "status": "approved"
        }
        self.decisions.append(decision)
        return decision_id


class PracticeRegistry:
    """
    Registry for all ITIL 4 Practices
    """
    
    def __init__(self):
        self.practices = {}
        self.practice_categories = {
            "general_management": [],
            "service_management": [],
            "technical_management": []
        }
        self._initialize_practices()
    
    def _initialize_practices(self):
        """Initialize the practice registry with all 34 ITIL practices"""
        # General Management Practices (14)
        general_practices = [
            "Architecture Management", "Continual Improvement", "Information Security Management",
            "Knowledge Management", "Measurement and Reporting", "Organizational Change Management",
            "Portfolio Management", "Project Management", "Relationship Management", "Risk Management",
            "Service Financial Management", "Strategy Management", "Supplier Management",
            "Workforce and Talent Management"
        ]
        
        # Service Management Practices (17)
        service_practices = [
            "Availability Management", "Business Analysis", "Capacity and Performance Management",
            "Change Enablement", "Incident Management", "IT Asset Management",
            "Monitoring and Event Management", "Problem Management", "Release Management",
            "Service Catalogue Management", "Service Configuration Management",
            "Service Continuity Management", "Service Design", "Service Desk",
            "Service Level Management", "Service Request Management", "Service Validation and Testing"
        ]
        
        # Technical Management Practices (3)
        technical_practices = [
            "Deployment Management", "Infrastructure and Platform Management",
            "Software Development and Management"
        ]
        
        # Register all practices
        for practice in general_practices:
            self.register_practice(practice, "general_management")
        
        for practice in service_practices:
            self.register_practice(practice, "service_management")
        
        for practice in technical_practices:
            self.register_practice(practice, "technical_management")
    
    def register_practice(self, name: str, category: str) -> bool:
        """Register a practice in the system"""
        if category in self.practice_categories:
            practice_id = name.lower().replace(" ", "_")
            self.practices[practice_id] = {
                "name": name,
                "category": category,
                "status": "not_implemented",
                "maturity_level": 0,
                "owner": None,
                "implementation_date": None
            }
            self.practice_categories[category].append(practice_id)
            return True
        return False
    
    def get_practice(self, practice_id: str) -> Optional[Dict[str, Any]]:
        """Get practice information"""
        return self.practices.get(practice_id)
    
    def get_practices_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all practices in a specific category"""
        if category in self.practice_categories:
            return [self.practices[pid] for pid in self.practice_categories[category]]
        return []
    
    def get_active_practices_count(self) -> int:
        """Get count of active/implemented practices"""
        return len([p for p in self.practices.values() if p["status"] in ["implemented", "optimized"]])
    
    def get_health_score(self) -> float:
        """Calculate practices health score"""
        if not self.practices:
            return 0
        
        implemented = self.get_active_practices_count()
        total = len(self.practices)
        return (implemented / total) * 100


class ContinualImprovement:
    """
    ITIL 4 Continual Improvement implementation
    """
    
    def __init__(self):
        self.improvement_initiatives = {}
        self.improvement_model = ImprovementModel()
        self.metrics = {}
        self.improvement_register = []
    
    def create_improvement_initiative(self, name: str, description: str, 
                                   priority: Priority, scope: str) -> 'ImprovementInitiative':
        """Create a new improvement initiative"""
        initiative = ImprovementInitiative(name, description, priority, scope)
        self.improvement_initiatives[initiative.id] = initiative
        return initiative
    
    def get_active_initiatives_count(self) -> int:
        """Get count of active improvement initiatives"""
        return len([i for i in self.improvement_initiatives.values() 
                   if i.status not in [Status.CLOSED, Status.CANCELLED]])
    
    def get_health_score(self) -> float:
        """Calculate continual improvement health score"""
        if not self.improvement_initiatives:
            return 50  # Base score if no initiatives
        
        completed = len([i for i in self.improvement_initiatives.values() 
                        if i.status == Status.CLOSED])
        total = len(self.improvement_initiatives)
        completion_rate = (completed / total) * 100 if total > 0 else 0
        
        # Factor in active initiatives
        active = self.get_active_initiatives_count()
        activity_score = min(active * 10, 50)  # Cap at 50 points
        
        return min(completion_rate * 0.5 + activity_score, 100)


class ImprovementModel:
    """
    ITIL 4 Continual Improvement Model
    
    Structured approach to improvement using the seven-step model:
    1. What is the vision?
    2. Where are we now?
    3. Where do we want to be?
    4. How do we get there?
    5. Take action
    6. Did we get there?
    7. How do we keep momentum going?
    """
    
    def __init__(self):
        self.steps = [
            "What is the vision?",
            "Where are we now?",
            "Where do we want to be?",
            "How do we get there?",
            "Take action",
            "Did we get there?",
            "How do we keep momentum going?"
        ]
    
    def apply_model(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply the improvement model to a specific context"""
        improvement_plan = {
            "context": context,
            "steps": {},
            "created_date": datetime.now(),
            "status": "in_planning"
        }
        
        for i, step in enumerate(self.steps, 1):
            improvement_plan["steps"][f"step_{i}"] = {
                "name": step,
                "status": "pending",
                "output": None,
                "notes": []
            }
        
        return improvement_plan


class ImprovementInitiative:
    """Individual Improvement Initiative"""
    
    def __init__(self, name: str, description: str, priority: Priority, scope: str):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.priority = priority
        self.scope = scope
        self.status = Status.NEW
        self.created_date = datetime.now()
        self.owner = None
        self.target_completion_date = None
        self.actual_completion_date = None
        self.benefits_realized = {}
        self.lessons_learned = []
    
    def start_initiative(self, owner: str, target_date: datetime) -> bool:
        """Start the improvement initiative"""
        self.owner = owner
        self.target_completion_date = target_date
        self.status = Status.IN_PROGRESS
        return True
    
    def complete_initiative(self, benefits: Dict[str, Any], lessons: List[str]) -> bool:
        """Complete the improvement initiative"""
        self.status = Status.CLOSED
        self.actual_completion_date = datetime.now()
        self.benefits_realized = benefits
        self.lessons_learned = lessons
        return True
    
    def get_summary(self) -> Dict[str, Any]:
        """Get initiative summary"""
        return {
            "id": self.id,
            "name": self.name,
            "priority": self.priority.value,
            "status": self.status.value,
            "owner": self.owner,
            "created_date": self.created_date.isoformat(),
            "target_completion": self.target_completion_date.isoformat() if self.target_completion_date else None,
            "actual_completion": self.actual_completion_date.isoformat() if self.actual_completion_date else None
        }


if __name__ == "__main__":
    # Example usage
    print("ITIL 4 Python Framework - Service Value System")
    print("=" * 50)
    
    # Create a Service Value System
    svs = ServiceValueSystem("Acme Corporation")
    print(f"Created: {svs}")
    
    # Check system status
    status = svs.get_system_status()
    print(f"\nSystem Status: {json.dumps(status, indent=2)}")
    
    # Create a value stream
    incident_response_stream = svs.service_value_chain.create_value_stream(
        "Incident Response",
        ["engage", "deliver_support", "improve"]
    )
    
    print(f"\nCreated Value Stream: {incident_response_stream.name}")
    
    # Execute the value stream
    execution_result = incident_response_stream.execute()
    print(f"Execution Result: {json.dumps(execution_result, default=str, indent=2)}")