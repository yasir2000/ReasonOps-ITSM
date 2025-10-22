"""
ITIL 4 Incident Management Practice Implementation

This module provides a comprehensive Python implementation of the 
Incident Management practice as defined in ITIL 4.
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import uuid
import json

# Flexible imports to support both package and standalone execution
try:
    from core.service_value_system import Priority, Status, Impact, Urgency, Person, ConfigurationItem
except Exception:
    try:
        from ..core.service_value_system import Priority, Status, Impact, Urgency, Person, ConfigurationItem  # type: ignore
    except Exception:
        # Minimal placeholders to keep module importable without full framework
        from enum import Enum
        class Priority(Enum):
            P1_CRITICAL = "P1 - Critical"; P2_HIGH = "P2 - High"; P3_MEDIUM = "P3 - Medium"; P4_LOW = "P4 - Low"
        class Status(Enum):
            NEW = "New"; IN_PROGRESS = "In Progress"; RESOLVED = "Resolved"; CLOSED = "Closed"
        class Impact(Enum):
            HIGH = "High"; MEDIUM = "Medium"; LOW = "Low"
        class Urgency(Enum):
            HIGH = "High"; MEDIUM = "Medium"; LOW = "Low"
        @dataclass
        class Person:  # type: ignore
            id: str; name: str; email: str; role: str; department: str
        @dataclass
        class ConfigurationItem:  # type: ignore
            id: str; name: str; ci_type: str; environment: str; location: str


class IncidentCategory(Enum):
    """Incident categories for classification"""
    HARDWARE = "Hardware"
    SOFTWARE = "Software"
    NETWORK = "Network"
    SECURITY = "Security"
    SERVICE = "Service"
    INFRASTRUCTURE = "Infrastructure"
    APPLICATION = "Application"
    DATABASE = "Database"


class IncidentState(Enum):
    """Incident lifecycle states"""
    NEW = "New"
    IN_PROGRESS = "In Progress"
    ON_HOLD = "On Hold"
    RESOLVED = "Resolved"
    CLOSED = "Closed"
    CANCELLED = "Cancelled"


class EscalationLevel(Enum):
    """Support escalation levels"""
    L1 = "L1 - Service Desk"
    L2 = "L2 - Technical Support"
    L3 = "L3 - Subject Matter Expert"
    L4 = "L4 - Vendor Support"


@dataclass
class Incident:
    """
    Represents an ITIL Incident
    
    An incident is an unplanned interruption to a service or reduction
    in the quality of a service.
    """
    
    number: str = field(default_factory=lambda: f"INC{str(uuid.uuid4())[:8].upper()}")
    short_description: str = ""
    description: str = ""
    caller: Optional[Person] = None
    category: Optional[IncidentCategory] = None
    subcategory: str = ""
    state: IncidentState = IncidentState.NEW
    priority: Optional[Priority] = None
    impact: Optional[Impact] = None
    urgency: Optional[Urgency] = None
    assignment_group: str = ""
    assigned_to: Optional[Person] = None
    configuration_items: List[ConfigurationItem] = field(default_factory=list)
    
    # Timestamps
    opened_at: datetime = field(default_factory=datetime.now)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    
    # Work tracking
    work_log: List[Dict[str, Any]] = field(default_factory=list)
    resolution_notes: str = ""
    closure_notes: str = ""
    
    # Escalation
    escalation_level: EscalationLevel = EscalationLevel.L1
    escalated_at: Optional[datetime] = None
    escalation_reason: str = ""
    
    # Major incident
    is_major_incident: bool = False
    major_incident_manager: Optional[Person] = None
    
    # Related records
    related_problems: List[str] = field(default_factory=list)
    related_changes: List[str] = field(default_factory=list)
    child_incidents: List[str] = field(default_factory=list)
    parent_incident: Optional[str] = None
    
    # SLA tracking
    response_sla_breach: bool = False
    resolution_sla_breach: bool = False
    sla_due_date: Optional[datetime] = None
    
    # Customer satisfaction
    customer_satisfaction_score: Optional[int] = None
    customer_feedback: str = ""
    
    def __post_init__(self):
        """Post-initialization processing"""
        if self.priority is None and self.impact and self.urgency:
            self.priority = self._calculate_priority(self.impact, self.urgency)
        
        if self.sla_due_date is None:
            self.sla_due_date = self._calculate_sla_due_date()
    
    def _calculate_priority(self, impact: Impact, urgency: Urgency) -> Priority:
        """Calculate priority based on impact and urgency matrix"""
        priority_matrix = {
            (Impact.HIGH, Urgency.HIGH): Priority.P1_CRITICAL,
            (Impact.HIGH, Urgency.MEDIUM): Priority.P2_HIGH,
            (Impact.HIGH, Urgency.LOW): Priority.P3_MEDIUM,
            (Impact.MEDIUM, Urgency.HIGH): Priority.P2_HIGH,
            (Impact.MEDIUM, Urgency.MEDIUM): Priority.P3_MEDIUM,
            (Impact.MEDIUM, Urgency.LOW): Priority.P4_LOW,
            (Impact.LOW, Urgency.HIGH): Priority.P3_MEDIUM,
            (Impact.LOW, Urgency.MEDIUM): Priority.P4_LOW,
            (Impact.LOW, Urgency.LOW): Priority.P4_LOW,
        }
        return priority_matrix.get((impact, urgency), Priority.P4_LOW)
    
    def _calculate_sla_due_date(self) -> datetime:
        """Calculate SLA due date based on priority"""
        sla_hours = {
            Priority.P1_CRITICAL: 1,
            Priority.P2_HIGH: 4,
            Priority.P3_MEDIUM: 8,
            Priority.P4_LOW: 24
        }
        hours = sla_hours.get(self.priority, 24)
        return self.opened_at + timedelta(hours=hours)
    
    def add_work_note(self, note: str, author: Person, is_public: bool = False):
        """Add a work note to the incident"""
        work_note = {
            "timestamp": datetime.now(),
            "author": author.name,
            "note": note,
            "is_public": is_public
        }
        self.work_log.append(work_note)
    
    def acknowledge(self, acknowledger: Person) -> bool:
        """Acknowledge the incident"""
        if self.state == IncidentState.NEW:
            self.acknowledged_at = datetime.now()
            self.state = IncidentState.IN_PROGRESS
            self.add_work_note(f"Incident acknowledged by {acknowledger.name}", acknowledger)
            return True
        return False
    
    def assign(self, assignee: Person, assignment_group: str) -> bool:
        """Assign the incident to a person and group"""
        self.assigned_to = assignee
        self.assignment_group = assignment_group
        self.add_work_note(
            f"Incident assigned to {assignee.name} in group {assignment_group}", 
            assignee
        )
        return True
    
    def escalate(self, level: EscalationLevel, reason: str, escalator: Person) -> bool:
        """Escalate the incident to a higher support level"""
        if level.value > self.escalation_level.value:
            self.escalation_level = level
            self.escalated_at = datetime.now()
            self.escalation_reason = reason
            self.add_work_note(
                f"Incident escalated to {level.value}. Reason: {reason}", 
                escalator
            )
            return True
        return False
    
    def resolve(self, resolver: Person, resolution: str) -> bool:
        """Resolve the incident"""
        if self.state != IncidentState.RESOLVED:
            self.state = IncidentState.RESOLVED
            self.resolved_at = datetime.now()
            self.resolution_notes = resolution
            self.add_work_note(f"Incident resolved: {resolution}", resolver)
            return True
        return False
    
    def close(self, closer: Person, closure_notes: str = "", 
             satisfaction_score: Optional[int] = None) -> bool:
        """Close the incident"""
        if self.state == IncidentState.RESOLVED:
            self.state = IncidentState.CLOSED
            self.closed_at = datetime.now()
            self.closure_notes = closure_notes
            if satisfaction_score is not None:
                self.customer_satisfaction_score = satisfaction_score
            self.add_work_note(f"Incident closed by {closer.name}", closer)
            return True
        return False
    
    def reopen(self, reopener: Person, reason: str) -> bool:
        """Reopen a resolved or closed incident"""
        if self.state in [IncidentState.RESOLVED, IncidentState.CLOSED]:
            self.state = IncidentState.IN_PROGRESS
            self.resolved_at = None
            self.closed_at = None
            self.add_work_note(f"Incident reopened by {reopener.name}. Reason: {reason}", reopener)
            return True
        return False
    
    def promote_to_major(self, manager: Person, reason: str) -> bool:
        """Promote incident to major incident status"""
        if not self.is_major_incident:
            self.is_major_incident = True
            self.major_incident_manager = manager
            self.add_work_note(f"Promoted to Major Incident by {manager.name}. Reason: {reason}", manager)
            return True
        return False
    
    def check_sla_breach(self) -> Dict[str, bool]:
        """Check for SLA breaches"""
        now = datetime.now()
        
        # Check response SLA (acknowledgment within target time)
        if not self.response_sla_breach and not self.acknowledged_at:
            response_target = self.opened_at + timedelta(minutes=15)  # 15 min response target
            if now > response_target:
                self.response_sla_breach = True
        
        # Check resolution SLA
        if not self.resolution_sla_breach and not self.resolved_at:
            if now > self.sla_due_date:
                self.resolution_sla_breach = True
        
        return {
            "response_breach": self.response_sla_breach,
            "resolution_breach": self.resolution_sla_breach
        }
    
    def get_age_in_hours(self) -> float:
        """Get incident age in hours"""
        if self.closed_at:
            return (self.closed_at - self.opened_at).total_seconds() / 3600
        return (datetime.now() - self.opened_at).total_seconds() / 3600
    
    def get_resolution_time_hours(self) -> Optional[float]:
        """Get resolution time in hours"""
        if self.resolved_at:
            return (self.resolved_at - self.opened_at).total_seconds() / 3600
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert incident to dictionary representation"""
        return {
            "number": self.number,
            "short_description": self.short_description,
            "description": self.description,
            "caller": self.caller.name if self.caller else None,
            "category": self.category.value if self.category else None,
            "subcategory": self.subcategory,
            "state": self.state.value,
            "priority": self.priority.value if self.priority else None,
            "impact": self.impact.value if self.impact else None,
            "urgency": self.urgency.value if self.urgency else None,
            "assignment_group": self.assignment_group,
            "assigned_to": self.assigned_to.name if self.assigned_to else None,
            "opened_at": self.opened_at.isoformat(),
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
            "is_major_incident": self.is_major_incident,
            "escalation_level": self.escalation_level.value,
            "sla_breaches": self.check_sla_breach(),
            "age_hours": round(self.get_age_in_hours(), 2),
            "resolution_time_hours": self.get_resolution_time_hours(),
            "customer_satisfaction": self.customer_satisfaction_score
        }


class IncidentManagement:
    """
    ITIL 4 Incident Management Practice Implementation
    
    Manages the complete incident lifecycle from detection through closure,
    including SLA management, escalation, and major incident coordination.
    """
    
    def __init__(self):
        self.incidents: Dict[str, Incident] = {}
        self.assignment_groups = {}
        self.sla_targets = {
            Priority.P1_CRITICAL: {"response_minutes": 15, "resolution_hours": 1},
            Priority.P2_HIGH: {"response_minutes": 30, "resolution_hours": 4},
            Priority.P3_MEDIUM: {"response_minutes": 60, "resolution_hours": 8},
            Priority.P4_LOW: {"response_minutes": 240, "resolution_hours": 24}
        }
        self.auto_assignment_rules = {}
        self.escalation_rules = {}
        self.major_incident_criteria = {
            "priority_threshold": Priority.P1_CRITICAL,
            "user_impact_threshold": 100,
            "business_critical_services": []
        }
    
    def create_incident(self, short_description: str, description: str, 
                       caller: Person, category: IncidentCategory,
                       impact: Impact, urgency: Urgency,
                       affected_ci: Optional[ConfigurationItem] = None) -> Incident:
        """Create a new incident"""
        
        incident = Incident(
            short_description=short_description,
            description=description,
            caller=caller,
            category=category,
            impact=impact,
            urgency=urgency
        )
        
        if affected_ci:
            incident.configuration_items.append(affected_ci)
        
        # Auto-assign based on rules
        self._auto_assign_incident(incident)
        
        # Check for major incident criteria
        if self._meets_major_incident_criteria(incident):
            incident.is_major_incident = True
        
        # Store incident
        self.incidents[incident.number] = incident
        
        # Log creation
        incident.add_work_note(
            f"Incident created by {caller.name}. Category: {category.value}, Priority: {incident.priority.value}",
            caller
        )
        
        return incident
    
    def get_incident(self, incident_number: str) -> Optional[Incident]:
        """Retrieve incident by number"""
        return self.incidents.get(incident_number)
    
    def update_incident(self, incident_number: str, updates: Dict[str, Any], 
                       updater: Person) -> bool:
        """Update incident with new information"""
        incident = self.get_incident(incident_number)
        if not incident:
            return False
        
        update_notes = []
        
        for field, value in updates.items():
            if hasattr(incident, field):
                old_value = getattr(incident, field)
                setattr(incident, field, value)
                update_notes.append(f"{field}: {old_value} -> {value}")
        
        if update_notes:
            incident.add_work_note(f"Incident updated: {', '.join(update_notes)}", updater)
        
        return True
    
    def search_incidents(self, criteria: Dict[str, Any]) -> List[Incident]:
        """Search incidents based on criteria"""
        results = []
        
        for incident in self.incidents.values():
            match = True
            
            for field, value in criteria.items():
                if hasattr(incident, field):
                    incident_value = getattr(incident, field)
                    if isinstance(incident_value, Enum):
                        incident_value = incident_value.value
                    
                    if incident_value != value:
                        match = False
                        break
            
            if match:
                results.append(incident)
        
        return results
    
    def get_incidents_by_state(self, state: IncidentState) -> List[Incident]:
        """Get all incidents in a specific state"""
        return [inc for inc in self.incidents.values() if inc.state == state]
    
    def get_incidents_by_priority(self, priority: Priority) -> List[Incident]:
        """Get all incidents with specific priority"""
        return [inc for inc in self.incidents.values() if inc.priority == priority]
    
    def get_major_incidents(self) -> List[Incident]:
        """Get all major incidents"""
        return [inc for inc in self.incidents.values() if inc.is_major_incident]
    
    def get_sla_breached_incidents(self) -> List[Incident]:
        """Get incidents with SLA breaches"""
        breached = []
        for incident in self.incidents.values():
            sla_status = incident.check_sla_breach()
            if sla_status["response_breach"] or sla_status["resolution_breach"]:
                breached.append(incident)
        return breached
    
    def get_metrics(self, period_days: int = 30) -> Dict[str, Any]:
        """Get incident management metrics for specified period"""
        cutoff_date = datetime.now() - timedelta(days=period_days)
        period_incidents = [
            inc for inc in self.incidents.values() 
            if inc.opened_at >= cutoff_date
        ]
        
        if not period_incidents:
            return {"error": "No incidents in specified period"}
        
        # Volume metrics
        total_incidents = len(period_incidents)
        closed_incidents = len([inc for inc in period_incidents if inc.state == IncidentState.CLOSED])
        
        # Resolution metrics
        resolved_incidents = [inc for inc in period_incidents if inc.resolved_at]
        resolution_times = [inc.get_resolution_time_hours() for inc in resolved_incidents if inc.get_resolution_time_hours()]
        
        # SLA metrics
        sla_breaches = len(self.get_sla_breached_incidents())
        
        # Priority distribution
        priority_dist = {}
        for priority in Priority:
            count = len([inc for inc in period_incidents if inc.priority == priority])
            priority_dist[priority.value] = count
        
        # Category distribution
        category_dist = {}
        for category in IncidentCategory:
            count = len([inc for inc in period_incidents if inc.category == category])
            category_dist[category.value] = count
        
        # Calculate averages
        avg_resolution_time = sum(resolution_times) / len(resolution_times) if resolution_times else 0
        
        # Customer satisfaction
        satisfaction_scores = [inc.customer_satisfaction_score for inc in period_incidents 
                             if inc.customer_satisfaction_score is not None]
        avg_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores) if satisfaction_scores else 0
        
        return {
            "period_days": period_days,
            "total_incidents": total_incidents,
            "closed_incidents": closed_incidents,
            "resolution_rate": (closed_incidents / total_incidents * 100) if total_incidents > 0 else 0,
            "avg_resolution_time_hours": round(avg_resolution_time, 2),
            "sla_breach_count": sla_breaches,
            "sla_compliance_rate": ((total_incidents - sla_breaches) / total_incidents * 100) if total_incidents > 0 else 100,
            "priority_distribution": priority_dist,
            "category_distribution": category_dist,
            "avg_customer_satisfaction": round(avg_satisfaction, 2),
            "major_incidents": len([inc for inc in period_incidents if inc.is_major_incident])
        }
    
    def _auto_assign_incident(self, incident: Incident):
        """Auto-assign incident based on category and priority"""
        # Simple auto-assignment logic
        assignment_map = {
            IncidentCategory.HARDWARE: "Hardware Support",
            IncidentCategory.SOFTWARE: "Application Support",
            IncidentCategory.NETWORK: "Network Operations",
            IncidentCategory.SECURITY: "Security Operations",
            IncidentCategory.SERVICE: "Service Desk",
            IncidentCategory.INFRASTRUCTURE: "Infrastructure Team",
            IncidentCategory.APPLICATION: "Application Support",
            IncidentCategory.DATABASE: "Database Administration"
        }
        
        if incident.category in assignment_map:
            incident.assignment_group = assignment_map[incident.category]
    
    def _meets_major_incident_criteria(self, incident: Incident) -> bool:
        """Check if incident meets major incident criteria"""
        # Check priority threshold
        if incident.priority == Priority.P1_CRITICAL:
            return True
        
        # Check if affects business critical service
        for ci in incident.configuration_items:
            if ci.name in self.major_incident_criteria["business_critical_services"]:
                return True
        
        return False
    
    def generate_incident_report(self, incident_number: str) -> Dict[str, Any]:
        """Generate comprehensive incident report"""
        incident = self.get_incident(incident_number)
        if not incident:
            return {"error": "Incident not found"}
        
        report = {
            "incident_details": incident.to_dict(),
            "timeline": [
                {
                    "event": "Incident Created",
                    "timestamp": incident.opened_at.isoformat(),
                    "details": f"Reported by {incident.caller.name if incident.caller else 'Unknown'}"
                }
            ],
            "work_log": incident.work_log,
            "sla_performance": {
                "target_resolution": incident.sla_due_date.isoformat() if incident.sla_due_date else None,
                "actual_resolution": incident.resolved_at.isoformat() if incident.resolved_at else None,
                "sla_met": not incident.resolution_sla_breach if incident.resolved_at else None
            },
            "related_records": {
                "problems": incident.related_problems,
                "changes": incident.related_changes,
                "child_incidents": incident.child_incidents
            }
        }
        
        # Add timeline events
        if incident.acknowledged_at:
            report["timeline"].append({
                "event": "Incident Acknowledged",
                "timestamp": incident.acknowledged_at.isoformat(),
                "details": f"Acknowledged by {incident.assigned_to.name if incident.assigned_to else 'Unknown'}"
            })
        
        if incident.escalated_at:
            report["timeline"].append({
                "event": "Incident Escalated",
                "timestamp": incident.escalated_at.isoformat(),
                "details": f"Escalated to {incident.escalation_level.value}"
            })
        
        if incident.resolved_at:
            report["timeline"].append({
                "event": "Incident Resolved",
                "timestamp": incident.resolved_at.isoformat(),
                "details": incident.resolution_notes
            })
        
        if incident.closed_at:
            report["timeline"].append({
                "event": "Incident Closed",
                "timestamp": incident.closed_at.isoformat(),
                "details": incident.closure_notes
            })
        
        return report


# Example usage and testing
if __name__ == "__main__":
    print("ITIL 4 Incident Management Practice")
    print("=" * 40)
    
    # Create incident management system
    im = IncidentManagement()
    
    # Create sample persons
    caller = Person("1", "John Doe", "john.doe@company.com", "Business User", "Sales")
    agent = Person("2", "Jane Smith", "jane.smith@company.com", "Service Desk Agent", "IT Support")
    
    # Create sample CI
    ci = ConfigurationItem("1", "Email Server", "Application", "Production", "Production")
    
    # Create incident
    incident = im.create_incident(
        short_description="Email server not responding",
        description="Users unable to access email. Email server appears to be down.",
        caller=caller,
        category=IncidentCategory.APPLICATION,
        impact=Impact.HIGH,
        urgency=Urgency.HIGH,
        affected_ci=ci
    )
    
    print(f"Created incident: {incident.number}")
    print(f"Priority: {incident.priority.value}")
    print(f"SLA Due: {incident.sla_due_date}")
    
    # Acknowledge and work on incident
    incident.acknowledge(agent)
    incident.add_work_note("Investigating email server connectivity", agent)
    incident.add_work_note("Found network connectivity issue", agent)
    incident.resolve(agent, "Resolved network connectivity issue. Email server now responding normally.")
    
    # Generate report
    report = im.generate_incident_report(incident.number)
    print(f"\nIncident Report:")
    print(json.dumps(report, indent=2, default=str))
    
    # Get metrics
    metrics = im.get_metrics(30)
    print(f"\nIncident Metrics (30 days):")
    print(json.dumps(metrics, indent=2))