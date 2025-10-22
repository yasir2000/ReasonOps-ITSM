"""
ITIL 4 Change Enablement Practice Implementation

This module provides a comprehensive Python implementation of the 
Change Enablement practice as defined in ITIL 4.
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
import uuid
import json

from ..core.service_value_system import Priority, Status, Impact, Urgency, Person, ConfigurationItem


class ChangeType(Enum):
    """Types of changes"""
    STANDARD = "Standard"
    NORMAL = "Normal"
    EMERGENCY = "Emergency"


class ChangeCategory(Enum):
    """Change categories"""
    HARDWARE = "Hardware"
    SOFTWARE = "Software"
    NETWORK = "Network"
    SECURITY = "Security"
    PROCESS = "Process"
    DOCUMENTATION = "Documentation"
    INFRASTRUCTURE = "Infrastructure"
    APPLICATION = "Application"
    DATABASE = "Database"


class ChangeState(Enum):
    """Change lifecycle states"""
    NEW = "New"
    ASSESSMENT = "Assessment"
    AUTHORIZATION = "Authorization"
    SCHEDULED = "Scheduled"
    IMPLEMENTATION = "Implementation"
    REVIEW = "Review"
    CLOSED = "Closed"
    CANCELLED = "Cancelled"


class ChangeRisk(Enum):
    """Change risk levels"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    VERY_HIGH = "Very High"


class ApprovalStatus(Enum):
    """Approval statuses"""
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    WITHDRAWN = "Withdrawn"


@dataclass
class ChangeApproval:
    """Change approval information"""
    approver: Person
    status: ApprovalStatus = ApprovalStatus.PENDING
    comments: str = ""
    approved_at: Optional[datetime] = None
    
    def approve(self, comments: str = ""):
        """Approve the change"""
        self.status = ApprovalStatus.APPROVED
        self.comments = comments
        self.approved_at = datetime.now()
    
    def reject(self, comments: str):
        """Reject the change"""
        self.status = ApprovalStatus.REJECTED
        self.comments = comments
        self.approved_at = datetime.now()


@dataclass
class ImplementationPlan:
    """Change implementation plan"""
    description: str = ""
    steps: List[str] = field(default_factory=list)
    estimated_duration: Optional[timedelta] = None
    resources_required: List[str] = field(default_factory=list)
    technical_requirements: List[str] = field(default_factory=list)
    
    def add_step(self, step: str, position: Optional[int] = None):
        """Add an implementation step"""
        if position is not None:
            self.steps.insert(position, step)
        else:
            self.steps.append(step)
    
    def remove_step(self, step_index: int) -> bool:
        """Remove an implementation step"""
        if 0 <= step_index < len(self.steps):
            self.steps.pop(step_index)
            return True
        return False


@dataclass
class BackoutPlan:
    """Change backout/rollback plan"""
    description: str = ""
    steps: List[str] = field(default_factory=list)
    estimated_duration: Optional[timedelta] = None
    trigger_conditions: List[str] = field(default_factory=list)
    
    def add_step(self, step: str, position: Optional[int] = None):
        """Add a backout step"""
        if position is not None:
            self.steps.insert(position, step)
        else:
            self.steps.append(step)
    
    def add_trigger_condition(self, condition: str):
        """Add a backout trigger condition"""
        self.trigger_conditions.append(condition)


@dataclass
class TestPlan:
    """Change testing plan"""
    description: str = ""
    test_cases: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)
    test_environment: str = ""
    estimated_duration: Optional[timedelta] = None
    
    def add_test_case(self, test_case: str):
        """Add a test case"""
        self.test_cases.append(test_case)
    
    def add_success_criteria(self, criteria: str):
        """Add success criteria"""
        self.success_criteria.append(criteria)


@dataclass
class Change:
    """
    Represents an ITIL Change
    
    A change is the addition, modification, or removal of anything that 
    could have a direct or indirect effect on services.
    """
    
    number: str = field(default_factory=lambda: f"CHG{str(uuid.uuid4())[:8].upper()}")
    short_description: str = ""
    description: str = ""
    justification: str = ""
    category: Optional[ChangeCategory] = None
    change_type: ChangeType = ChangeType.NORMAL
    state: ChangeState = ChangeState.NEW
    
    # Risk and Impact
    risk: ChangeRisk = ChangeRisk.MEDIUM
    impact: Optional[Impact] = None
    urgency: Optional[Urgency] = None
    priority: Optional[Priority] = None
    
    # People
    requester: Optional[Person] = None
    assigned_to: Optional[Person] = None
    change_manager: Optional[Person] = None
    implementation_team: List[Person] = field(default_factory=list)
    
    # Configuration Items
    configuration_items: List[ConfigurationItem] = field(default_factory=list)
    
    # Timestamps
    requested_at: datetime = field(default_factory=datetime.now)
    planned_start: Optional[datetime] = None
    planned_end: Optional[datetime] = None
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    
    # Approval
    approvals: List[ChangeApproval] = field(default_factory=list)
    change_advisory_board_review: bool = False
    emergency_change_board_review: bool = False
    
    # Plans
    implementation_plan: Optional[ImplementationPlan] = None
    backout_plan: Optional[BackoutPlan] = None
    test_plan: Optional[TestPlan] = None
    
    # Related records
    related_incidents: List[str] = field(default_factory=list)
    related_problems: List[str] = field(default_factory=list)
    related_changes: List[str] = field(default_factory=list)
    
    # Work tracking
    work_log: List[Dict[str, Any]] = field(default_factory=list)
    
    # Implementation results
    implementation_successful: Optional[bool] = None
    implementation_notes: str = ""
    post_implementation_review_notes: str = ""
    lessons_learned: str = ""
    
    def __post_init__(self):
        """Post-initialization processing"""
        if self.priority is None and self.impact and self.urgency:
            self.priority = self._calculate_priority(self.impact, self.urgency)
    
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
    
    def add_work_note(self, note: str, author: Person, is_public: bool = False):
        """Add a work note to the change"""
        work_note = {
            "timestamp": datetime.now(),
            "author": author.name,
            "note": note,
            "is_public": is_public
        }
        self.work_log.append(work_note)
    
    def add_approver(self, approver: Person) -> ChangeApproval:
        """Add an approver to the change"""
        approval = ChangeApproval(approver=approver)
        self.approvals.append(approval)
        self.add_work_note(f"Approver {approver.name} added", approver)
        return approval
    
    def submit_for_assessment(self, submitter: Person) -> bool:
        """Submit change for assessment"""
        if self.state == ChangeState.NEW:
            self.state = ChangeState.ASSESSMENT
            self.add_work_note(f"Change submitted for assessment by {submitter.name}", submitter)
            return True
        return False
    
    def assess_change(self, assessor: Person, risk: ChangeRisk, 
                     impact: Impact, urgency: Urgency,
                     assessment_notes: str = "") -> bool:
        """Assess the change risk and impact"""
        if self.state == ChangeState.ASSESSMENT:
            self.risk = risk
            self.impact = impact
            self.urgency = urgency
            self.priority = self._calculate_priority(impact, urgency)
            
            self.add_work_note(
                f"Change assessed by {assessor.name}. Risk: {risk.value}, Impact: {impact.value}, Urgency: {urgency.value}. {assessment_notes}",
                assessor
            )
            
            # Determine approval requirements based on risk and impact
            self._determine_approval_requirements()
            
            self.state = ChangeState.AUTHORIZATION
            return True
        return False
    
    def _determine_approval_requirements(self):
        """Determine what approvals are needed based on risk and impact"""
        # High risk or high impact changes need CAB review
        if self.risk in [ChangeRisk.HIGH, ChangeRisk.VERY_HIGH] or self.impact == Impact.HIGH:
            self.change_advisory_board_review = True
        
        # Emergency changes need ECB review
        if self.change_type == ChangeType.EMERGENCY:
            self.emergency_change_board_review = True
    
    def approve_change(self, approver: Person, comments: str = "") -> bool:
        """Approve the change"""
        # Find the approver in the approvals list
        for approval in self.approvals:
            if approval.approver.id == approver.id:
                approval.approve(comments)
                self.add_work_note(f"Change approved by {approver.name}. {comments}", approver)
                
                # Check if all approvals are complete
                if self.are_all_approvals_complete():
                    self.state = ChangeState.SCHEDULED
                    self.add_work_note("All approvals complete. Change scheduled for implementation.", approver)
                
                return True
        return False
    
    def reject_change(self, approver: Person, comments: str) -> bool:
        """Reject the change"""
        for approval in self.approvals:
            if approval.approver.id == approver.id:
                approval.reject(comments)
                self.state = ChangeState.CANCELLED
                self.add_work_note(f"Change rejected by {approver.name}. {comments}", approver)
                return True
        return False
    
    def are_all_approvals_complete(self) -> bool:
        """Check if all required approvals are complete"""
        if not self.approvals:
            return True
        
        for approval in self.approvals:
            if approval.status == ApprovalStatus.PENDING:
                return False
            if approval.status == ApprovalStatus.REJECTED:
                return False
        
        return True
    
    def schedule_change(self, scheduler: Person, start_time: datetime, 
                       end_time: datetime) -> bool:
        """Schedule the change implementation"""
        if self.state == ChangeState.SCHEDULED:
            self.planned_start = start_time
            self.planned_end = end_time
            self.add_work_note(
                f"Change scheduled by {scheduler.name} from {start_time} to {end_time}",
                scheduler
            )
            return True
        return False
    
    def start_implementation(self, implementer: Person) -> bool:
        """Start change implementation"""
        if self.state == ChangeState.SCHEDULED:
            self.state = ChangeState.IMPLEMENTATION
            self.actual_start = datetime.now()
            self.add_work_note(f"Implementation started by {implementer.name}", implementer)
            return True
        return False
    
    def complete_implementation(self, implementer: Person, successful: bool, 
                              notes: str = "") -> bool:
        """Complete change implementation"""
        if self.state == ChangeState.IMPLEMENTATION:
            self.state = ChangeState.REVIEW
            self.actual_end = datetime.now()
            self.implementation_successful = successful
            self.implementation_notes = notes
            
            status = "successfully" if successful else "unsuccessfully"
            self.add_work_note(
                f"Implementation completed {status} by {implementer.name}. {notes}",
                implementer
            )
            return True
        return False
    
    def execute_backout(self, implementer: Person, reason: str) -> bool:
        """Execute backout plan"""
        if self.state == ChangeState.IMPLEMENTATION and self.backout_plan:
            self.implementation_successful = False
            self.implementation_notes = f"Backout executed: {reason}"
            self.add_work_note(f"Backout plan executed by {implementer.name}. Reason: {reason}", implementer)
            return True
        return False
    
    def conduct_post_implementation_review(self, reviewer: Person, 
                                         review_notes: str,
                                         lessons_learned: str = "") -> bool:
        """Conduct post-implementation review"""
        if self.state == ChangeState.REVIEW:
            self.post_implementation_review_notes = review_notes
            self.lessons_learned = lessons_learned
            self.state = ChangeState.CLOSED
            self.add_work_note(
                f"Post-implementation review completed by {reviewer.name}. {review_notes}",
                reviewer
            )
            return True
        return False
    
    def get_duration_hours(self) -> Optional[float]:
        """Get actual implementation duration in hours"""
        if self.actual_start and self.actual_end:
            return (self.actual_end - self.actual_start).total_seconds() / 3600
        return None
    
    def is_overdue(self) -> bool:
        """Check if change implementation is overdue"""
        if self.planned_end and not self.actual_end:
            return datetime.now() > self.planned_end
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert change to dictionary representation"""
        return {
            "number": self.number,
            "short_description": self.short_description,
            "description": self.description,
            "category": self.category.value if self.category else None,
            "change_type": self.change_type.value,
            "state": self.state.value,
            "risk": self.risk.value,
            "impact": self.impact.value if self.impact else None,
            "urgency": self.urgency.value if self.urgency else None,
            "priority": self.priority.value if self.priority else None,
            "requester": self.requester.name if self.requester else None,
            "assigned_to": self.assigned_to.name if self.assigned_to else None,
            "change_manager": self.change_manager.name if self.change_manager else None,
            "requested_at": self.requested_at.isoformat(),
            "planned_start": self.planned_start.isoformat() if self.planned_start else None,
            "planned_end": self.planned_end.isoformat() if self.planned_end else None,
            "actual_start": self.actual_start.isoformat() if self.actual_start else None,
            "actual_end": self.actual_end.isoformat() if self.actual_end else None,
            "implementation_successful": self.implementation_successful,
            "duration_hours": self.get_duration_hours(),
            "is_overdue": self.is_overdue(),
            "approval_status": "Complete" if self.are_all_approvals_complete() else "Pending",
            "cab_review_required": self.change_advisory_board_review,
            "has_implementation_plan": self.implementation_plan is not None,
            "has_backout_plan": self.backout_plan is not None,
            "has_test_plan": self.test_plan is not None
        }


class ChangeAdvisoryBoard:
    """Change Advisory Board for reviewing and approving changes"""
    
    def __init__(self, name: str = "Change Advisory Board"):
        self.name = name
        self.members: List[Person] = []
        self.chair: Optional[Person] = None
        self.meeting_schedule: List[datetime] = []
        self.meeting_minutes: List[Dict[str, Any]] = []
    
    def add_member(self, member: Person, is_chair: bool = False):
        """Add a member to the CAB"""
        if member not in self.members:
            self.members.append(member)
        
        if is_chair:
            self.chair = member
    
    def schedule_meeting(self, meeting_time: datetime, agenda: List[str] = None):
        """Schedule a CAB meeting"""
        self.meeting_schedule.append(meeting_time)
        
        meeting = {
            "scheduled_time": meeting_time,
            "agenda": agenda or [],
            "attendees": [],
            "decisions": [],
            "action_items": []
        }
        self.meeting_minutes.append(meeting)
    
    def review_change(self, change: Change, decision: str, 
                     reasoning: str, reviewer: Person) -> Dict[str, Any]:
        """Review a change request"""
        review = {
            "change_number": change.number,
            "decision": decision,  # "Approved", "Rejected", "Deferred"
            "reasoning": reasoning,
            "reviewer": reviewer.name,
            "review_date": datetime.now(),
            "risk_assessment": change.risk.value,
            "impact_assessment": change.impact.value if change.impact else None
        }
        
        change.add_work_note(f"CAB Review: {decision}. {reasoning}", reviewer)
        
        return review


class ChangeEnablement:
    """
    ITIL 4 Change Enablement Practice Implementation
    
    Maximizes the number of successful service and product changes by ensuring 
    that risks have been properly assessed, authorizing changes to proceed, 
    and managing a change schedule.
    """
    
    def __init__(self):
        self.changes: Dict[str, Change] = {}
        self.standard_changes: Dict[str, Dict[str, Any]] = {}
        self.change_advisory_board = ChangeAdvisoryBoard()
        self.emergency_change_board = ChangeAdvisoryBoard("Emergency Change Board")
        self.change_schedule: List[Dict[str, Any]] = []
        self.change_windows = {}
        self.frozen_periods: List[Dict[str, Any]] = []
    
    def create_change_request(self, short_description: str, description: str,
                            justification: str, category: ChangeCategory,
                            change_type: ChangeType, requester: Person,
                            impact: Impact = Impact.MEDIUM,
                            urgency: Urgency = Urgency.MEDIUM) -> Change:
        """Create a new change request"""
        
        change = Change(
            short_description=short_description,
            description=description,
            justification=justification,
            category=category,
            change_type=change_type,
            requester=requester,
            impact=impact,
            urgency=urgency
        )
        
        # Store change
        self.changes[change.number] = change
        
        # Log creation
        change.add_work_note(
            f"Change request created by {requester.name}. Type: {change_type.value}, Category: {category.value}",
            requester
        )
        
        # Auto-assign based on category and type
        self._auto_assign_change(change)
        
        return change
    
    def create_standard_change(self, template_name: str, requester: Person,
                             parameters: Dict[str, Any] = None) -> Optional[Change]:
        """Create a change from a standard change template"""
        
        if template_name not in self.standard_changes:
            return None
        
        template = self.standard_changes[template_name]
        
        change = Change(
            short_description=template["short_description"],
            description=template["description"],
            category=ChangeCategory(template["category"]),
            change_type=ChangeType.STANDARD,
            requester=requester,
            impact=Impact(template["impact"]),
            urgency=Urgency(template["urgency"]),
            risk=ChangeRisk(template["risk"])
        )
        
        # Apply template parameters
        if parameters:
            for key, value in parameters.items():
                if hasattr(change, key):
                    setattr(change, key, value)
        
        # Standard changes are pre-approved
        change.state = ChangeState.SCHEDULED
        
        self.changes[change.number] = change
        
        change.add_work_note(
            f"Standard change created from template '{template_name}' by {requester.name}",
            requester
        )
        
        return change
    
    def create_emergency_change(self, short_description: str, description: str,
                              justification: str, category: ChangeCategory,
                              requester: Person, emergency_reason: str) -> Change:
        """Create an emergency change request"""
        
        change = self.create_change_request(
            short_description=short_description,
            description=description,
            justification=f"{justification} | EMERGENCY: {emergency_reason}",
            category=category,
            change_type=ChangeType.EMERGENCY,
            requester=requester,
            impact=Impact.HIGH,
            urgency=Urgency.HIGH
        )
        
        # Emergency changes require ECB review
        change.emergency_change_board_review = True
        
        # Add emergency change board members as approvers
        for member in self.emergency_change_board.members:
            change.add_approver(member)
        
        change.add_work_note(f"Emergency change created. Reason: {emergency_reason}", requester)
        
        return change
    
    def define_standard_change(self, name: str, description: str, 
                             category: ChangeCategory, risk: ChangeRisk,
                             impact: Impact, urgency: Urgency,
                             implementation_template: ImplementationPlan,
                             authorized_by: Person) -> bool:
        """Define a new standard change template"""
        
        template = {
            "name": name,
            "short_description": f"Standard Change: {name}",
            "description": description,
            "category": category.value,
            "risk": risk.value,
            "impact": impact.value,
            "urgency": urgency.value,
            "implementation_template": implementation_template,
            "authorized_by": authorized_by.name,
            "authorized_at": datetime.now(),
            "usage_count": 0
        }
        
        self.standard_changes[name] = template
        return True
    
    def get_change(self, change_number: str) -> Optional[Change]:
        """Retrieve change by number"""
        return self.changes.get(change_number)
    
    def search_changes(self, criteria: Dict[str, Any]) -> List[Change]:
        """Search changes based on criteria"""
        results = []
        
        for change in self.changes.values():
            match = True
            
            for field, value in criteria.items():
                if hasattr(change, field):
                    change_value = getattr(change, field)
                    if isinstance(change_value, Enum):
                        change_value = change_value.value
                    
                    if change_value != value:
                        match = False
                        break
            
            if match:
                results.append(change)
        
        return results
    
    def get_changes_by_state(self, state: ChangeState) -> List[Change]:
        """Get all changes in a specific state"""
        return [chg for chg in self.changes.values() if chg.state == state]
    
    def get_emergency_changes(self) -> List[Change]:
        """Get all emergency changes"""
        return [chg for chg in self.changes.values() if chg.change_type == ChangeType.EMERGENCY]
    
    def get_pending_approvals(self, approver: Person) -> List[Change]:
        """Get changes pending approval from specific person"""
        pending = []
        
        for change in self.changes.values():
            for approval in change.approvals:
                if (approval.approver.id == approver.id and 
                    approval.status == ApprovalStatus.PENDING):
                    pending.append(change)
                    break
        
        return pending
    
    def get_change_schedule(self, start_date: datetime, 
                          end_date: datetime) -> List[Dict[str, Any]]:
        """Get change schedule for a date range"""
        schedule = []
        
        for change in self.changes.values():
            if (change.planned_start and change.planned_end and
                change.planned_start >= start_date and 
                change.planned_end <= end_date):
                
                schedule.append({
                    "change_number": change.number,
                    "description": change.short_description,
                    "planned_start": change.planned_start,
                    "planned_end": change.planned_end,
                    "risk": change.risk.value,
                    "impact": change.impact.value if change.impact else None,
                    "assigned_to": change.assigned_to.name if change.assigned_to else None,
                    "state": change.state.value
                })
        
        # Sort by planned start time
        schedule.sort(key=lambda x: x["planned_start"])
        
        return schedule
    
    def check_change_conflicts(self, change: Change) -> List[Dict[str, Any]]:
        """Check for potential conflicts with other changes"""
        conflicts = []
        
        if not change.planned_start or not change.planned_end:
            return conflicts
        
        for other_change in self.changes.values():
            if (other_change.number != change.number and
                other_change.planned_start and other_change.planned_end):
                
                # Check time overlap
                if (change.planned_start < other_change.planned_end and
                    change.planned_end > other_change.planned_start):
                    
                    # Check CI overlap
                    change_cis = set(ci.id for ci in change.configuration_items)
                    other_cis = set(ci.id for ci in other_change.configuration_items)
                    
                    if change_cis.intersection(other_cis):
                        conflicts.append({
                            "change_number": other_change.number,
                            "description": other_change.short_description,
                            "conflict_type": "CI Overlap",
                            "overlapping_time": {
                                "start": max(change.planned_start, other_change.planned_start),
                                "end": min(change.planned_end, other_change.planned_end)
                            },
                            "overlapping_cis": list(change_cis.intersection(other_cis))
                        })
        
        return conflicts
    
    def define_change_window(self, name: str, description: str,
                           start_time: datetime, end_time: datetime,
                           recurrence: str = "one-time",
                           allowed_risk_levels: List[ChangeRisk] = None):
        """Define a change window"""
        
        change_window = {
            "name": name,
            "description": description,
            "start_time": start_time,
            "end_time": end_time,
            "recurrence": recurrence,
            "allowed_risk_levels": allowed_risk_levels or [ChangeRisk.LOW, ChangeRisk.MEDIUM],
            "blackout_periods": []
        }
        
        self.change_windows[name] = change_window
    
    def add_frozen_period(self, name: str, description: str,
                         start_date: datetime, end_date: datetime,
                         reason: str):
        """Add a change freeze period"""
        
        frozen_period = {
            "name": name,
            "description": description,
            "start_date": start_date,
            "end_date": end_date,
            "reason": reason,
            "exceptions": []
        }
        
        self.frozen_periods.append(frozen_period)
    
    def is_change_allowed_in_period(self, change: Change, 
                                   planned_start: datetime) -> Dict[str, Any]:
        """Check if change is allowed in the planned time period"""
        
        # Check frozen periods
        for frozen in self.frozen_periods:
            if (planned_start >= frozen["start_date"] and 
                planned_start <= frozen["end_date"]):
                
                # Check if this change has an exception
                if change.number not in frozen.get("exceptions", []):
                    return {
                        "allowed": False,
                        "reason": f"Change freeze period: {frozen['name']}",
                        "details": frozen["description"]
                    }
        
        # Check change windows
        for window_name, window in self.change_windows.items():
            if (planned_start >= window["start_time"] and 
                planned_start <= window["end_time"]):
                
                if change.risk not in window["allowed_risk_levels"]:
                    return {
                        "allowed": False,
                        "reason": f"Change risk {change.risk.value} not allowed in window {window_name}",
                        "details": f"Allowed risk levels: {[r.value for r in window['allowed_risk_levels']]}"
                    }
        
        return {"allowed": True}
    
    def get_metrics(self, period_days: int = 30) -> Dict[str, Any]:
        """Get change enablement metrics for specified period"""
        cutoff_date = datetime.now() - timedelta(days=period_days)
        period_changes = [
            chg for chg in self.changes.values() 
            if chg.requested_at >= cutoff_date
        ]
        
        if not period_changes:
            return {"error": "No changes in specified period"}
        
        # Volume metrics
        total_changes = len(period_changes)
        successful_changes = len([chg for chg in period_changes if chg.implementation_successful == True])
        failed_changes = len([chg for chg in period_changes if chg.implementation_successful == False])
        
        # Type distribution
        type_dist = {}
        for change_type in ChangeType:
            count = len([chg for chg in period_changes if chg.change_type == change_type])
            type_dist[change_type.value] = count
        
        # Risk distribution
        risk_dist = {}
        for risk in ChangeRisk:
            count = len([chg for chg in period_changes if chg.risk == risk])
            risk_dist[risk.value] = count
        
        # State distribution
        state_dist = {}
        for state in ChangeState:
            count = len([chg for chg in period_changes if chg.state == state])
            state_dist[state.value] = count
        
        # Category distribution
        category_dist = {}
        for category in ChangeCategory:
            count = len([chg for chg in period_changes if chg.category == category])
            category_dist[category.value] = count
        
        # Timeline metrics
        completed_changes = [chg for chg in period_changes if chg.actual_end]
        durations = [chg.get_duration_hours() for chg in completed_changes if chg.get_duration_hours()]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        # Approval metrics
        changes_with_approvals = [chg for chg in period_changes if chg.approvals]
        avg_approvals_per_change = sum(len(chg.approvals) for chg in changes_with_approvals) / len(changes_with_approvals) if changes_with_approvals else 0
        
        return {
            "period_days": period_days,
            "total_changes": total_changes,
            "successful_changes": successful_changes,
            "failed_changes": failed_changes,
            "success_rate": (successful_changes / (successful_changes + failed_changes) * 100) if (successful_changes + failed_changes) > 0 else 0,
            "type_distribution": type_dist,
            "risk_distribution": risk_dist,
            "state_distribution": state_dist,
            "category_distribution": category_dist,
            "avg_implementation_duration_hours": round(avg_duration, 2),
            "avg_approvals_per_change": round(avg_approvals_per_change, 2),
            "standard_change_templates": len(self.standard_changes),
            "change_windows_defined": len(self.change_windows),
            "frozen_periods_active": len([fp for fp in self.frozen_periods if fp["end_date"] > datetime.now()])
        }
    
    def _auto_assign_change(self, change: Change):
        """Auto-assign change based on category and type"""
        assignment_map = {
            ChangeCategory.HARDWARE: "Hardware Team",
            ChangeCategory.SOFTWARE: "Software Team",
            ChangeCategory.NETWORK: "Network Team",
            ChangeCategory.SECURITY: "Security Team",
            ChangeCategory.PROCESS: "Process Team",
            ChangeCategory.DOCUMENTATION: "Documentation Team",
            ChangeCategory.INFRASTRUCTURE: "Infrastructure Team",
            ChangeCategory.APPLICATION: "Application Team",
            ChangeCategory.DATABASE: "Database Team"
        }
        
        # Emergency changes go to specialized team
        if change.change_type == ChangeType.EMERGENCY:
            change.assigned_to = self.emergency_change_board.chair
        elif change.category in assignment_map:
            # Would typically look up actual person from assignment group
            pass
    
    def generate_change_report(self, change_number: str) -> Dict[str, Any]:
        """Generate comprehensive change report"""
        change = self.get_change(change_number)
        if not change:
            return {"error": "Change not found"}
        
        report = {
            "change_details": change.to_dict(),
            "timeline": [
                {
                    "event": "Change Requested",
                    "timestamp": change.requested_at.isoformat(),
                    "details": f"Requested by {change.requester.name if change.requester else 'Unknown'}"
                }
            ],
            "approvals": [
                {
                    "approver": approval.approver.name,
                    "status": approval.status.value,
                    "comments": approval.comments,
                    "approved_at": approval.approved_at.isoformat() if approval.approved_at else None
                }
                for approval in change.approvals
            ],
            "plans": {
                "implementation": {
                    "has_plan": change.implementation_plan is not None,
                    "steps_count": len(change.implementation_plan.steps) if change.implementation_plan else 0
                },
                "backout": {
                    "has_plan": change.backout_plan is not None,
                    "steps_count": len(change.backout_plan.steps) if change.backout_plan else 0
                },
                "test": {
                    "has_plan": change.test_plan is not None,
                    "test_cases_count": len(change.test_plan.test_cases) if change.test_plan else 0
                }
            },
            "conflicts": self.check_change_conflicts(change),
            "work_log": change.work_log,
            "related_records": {
                "incidents": change.related_incidents,
                "problems": change.related_problems,
                "changes": change.related_changes
            }
        }
        
        # Add timeline events based on state transitions
        if change.planned_start:
            report["timeline"].append({
                "event": "Change Scheduled",
                "timestamp": change.planned_start.isoformat(),
                "details": f"Planned implementation: {change.planned_start} to {change.planned_end}"
            })
        
        if change.actual_start:
            report["timeline"].append({
                "event": "Implementation Started",
                "timestamp": change.actual_start.isoformat(),
                "details": "Change implementation began"
            })
        
        if change.actual_end:
            status = "successfully" if change.implementation_successful else "with issues"
            report["timeline"].append({
                "event": "Implementation Completed",
                "timestamp": change.actual_end.isoformat(),
                "details": f"Implementation completed {status}"
            })
        
        return report


# Example usage and testing
if __name__ == "__main__":
    print("ITIL 4 Change Enablement Practice")
    print("=" * 40)
    
    # Create change enablement system
    ce = ChangeEnablement()
    
    # Create sample persons
    requester = Person("1", "Alice Johnson", "alice.johnson@company.com", "Business Analyst", "Business")
    change_manager = Person("2", "Bob Wilson", "bob.wilson@company.com", "Change Manager", "IT")
    approver = Person("3", "Carol Davis", "carol.davis@company.com", "IT Manager", "IT")
    implementer = Person("4", "Dave Smith", "dave.smith@company.com", "System Administrator", "IT")
    
    # Set up CAB
    ce.change_advisory_board.add_member(approver, is_chair=True)
    ce.change_advisory_board.add_member(change_manager)
    
    # Create a normal change
    change = ce.create_change_request(
        short_description="Upgrade web server software",
        description="Upgrade Apache web server from version 2.4.41 to 2.4.54 for security patches",
        justification="Security vulnerabilities in current version need to be addressed",
        category=ChangeCategory.SOFTWARE,
        change_type=ChangeType.NORMAL,
        requester=requester,
        impact=Impact.MEDIUM,
        urgency=Urgency.MEDIUM
    )
    
    print(f"Created change: {change.number}")
    print(f"Priority: {change.priority.value}")
    
    # Submit for assessment
    change.submit_for_assessment(requester)
    
    # Assess change
    change.assess_change(
        change_manager, 
        ChangeRisk.MEDIUM, 
        Impact.MEDIUM, 
        Urgency.MEDIUM,
        "Standard software upgrade with tested procedures"
    )
    
    # Add approver and approve
    change.add_approver(approver)
    change.approve_change(approver, "Approved for implementation during maintenance window")
    
    # Create implementation plan
    impl_plan = ImplementationPlan(
        description="Upgrade Apache web server",
        steps=[
            "1. Backup current configuration",
            "2. Stop Apache service",
            "3. Install new version",
            "4. Restore configuration",
            "5. Start Apache service",
            "6. Verify functionality"
        ],
        estimated_duration=timedelta(hours=2),
        resources_required=["System Administrator", "Maintenance Window"]
    )
    change.implementation_plan = impl_plan
    
    # Create backout plan
    backout_plan = BackoutPlan(
        description="Rollback to previous Apache version",
        steps=[
            "1. Stop Apache service",
            "2. Restore previous version",
            "3. Restore previous configuration",
            "4. Start Apache service",
            "5. Verify functionality"
        ],
        trigger_conditions=["Service unavailable", "Configuration issues", "Performance degradation"]
    )
    change.backout_plan = backout_plan
    
    # Schedule change
    start_time = datetime.now() + timedelta(days=1)
    end_time = start_time + timedelta(hours=2)
    change.schedule_change(change_manager, start_time, end_time)
    
    print(f"Change scheduled from {start_time} to {end_time}")
    
    # Generate report
    report = ce.generate_change_report(change.number)
    print(f"\nChange Report:")
    print(json.dumps(report, indent=2, default=str))
    
    # Create a standard change template
    standard_impl_plan = ImplementationPlan(
        description="Password reset for user account",
        steps=[
            "1. Verify user identity",
            "2. Generate temporary password",
            "3. Update user account",
            "4. Notify user of new password",
            "5. Require password change on next login"
        ]
    )
    
    ce.define_standard_change(
        name="User Password Reset",
        description="Standard procedure for resetting user passwords",
        category=ChangeCategory.SECURITY,
        risk=ChangeRisk.LOW,
        impact=Impact.LOW,
        urgency=Urgency.MEDIUM,
        implementation_template=standard_impl_plan,
        authorized_by=change_manager
    )
    
    # Create standard change from template
    standard_change = ce.create_standard_change(
        "User Password Reset",
        requester,
        {"short_description": "Password reset for user john.doe"}
    )
    
    if standard_change:
        print(f"\nCreated standard change: {standard_change.number}")
    
    # Get metrics
    metrics = ce.get_metrics(30)
    print(f"\nChange Enablement Metrics (30 days):")
    print(json.dumps(metrics, indent=2))