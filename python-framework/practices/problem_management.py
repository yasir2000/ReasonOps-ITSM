"""
ITIL 4 Problem Management Practice Implementation

This module provides a comprehensive Python implementation of the 
Problem Management practice as defined in ITIL 4.
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
import uuid
import json

from ..core.service_value_system import Priority, Status, Impact, Urgency, Person, ConfigurationItem


class ProblemCategory(Enum):
    """Problem categories for classification"""
    HARDWARE = "Hardware"
    SOFTWARE = "Software"
    NETWORK = "Network"
    SECURITY = "Security"
    PROCESS = "Process"
    INFRASTRUCTURE = "Infrastructure"
    APPLICATION = "Application"
    DATABASE = "Database"
    CAPACITY = "Capacity"
    AVAILABILITY = "Availability"


class ProblemState(Enum):
    """Problem lifecycle states"""
    NEW = "New"
    UNDER_INVESTIGATION = "Under Investigation"
    ROOT_CAUSE_ANALYSIS = "Root Cause Analysis"
    KNOWN_ERROR = "Known Error"
    RESOLVED = "Resolved"
    CLOSED = "Closed"
    CANCELLED = "Cancelled"


class RootCauseAnalysisMethod(Enum):
    """Root cause analysis methodologies"""
    FIVE_WHYS = "5 Whys"
    FISHBONE = "Fishbone Diagram"
    FAULT_TREE = "Fault Tree Analysis"
    TIMELINE = "Timeline Analysis"
    ISHIKAWA = "Ishikawa Diagram"
    PARETO = "Pareto Analysis"
    BRAINSTORMING = "Brainstorming"


class ProblemType(Enum):
    """Types of problems"""
    REACTIVE = "Reactive"  # Identified from incidents
    PROACTIVE = "Proactive"  # Identified through analysis
    MAJOR_PROBLEM = "Major Problem"  # Business critical


@dataclass
class RootCause:
    """Root cause information"""
    description: str
    analysis_method: RootCauseAnalysisMethod
    contributing_factors: List[str] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)
    confidence_level: int = 0  # 0-100%
    identified_by: Optional[Person] = None
    identified_at: datetime = field(default_factory=datetime.now)


@dataclass
class KnownError:
    """Known Error information"""
    id: str = field(default_factory=lambda: f"KE{str(uuid.uuid4())[:8].upper()}")
    description: str = ""
    workaround: str = ""
    root_cause: Optional[RootCause] = None
    created_by: Optional[Person] = None
    created_at: datetime = field(default_factory=datetime.now)
    status: Status = Status.ACTIVE
    
    # Related records
    related_problems: List[str] = field(default_factory=list)
    related_incidents: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "description": self.description,
            "workaround": self.workaround,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by.name if self.created_by else None,
            "related_problems": self.related_problems,
            "related_incidents": self.related_incidents
        }


@dataclass
class Problem:
    """
    Represents an ITIL Problem
    
    A problem is the cause of one or more incidents that have occurred 
    or may occur in the future.
    """
    
    number: str = field(default_factory=lambda: f"PRB{str(uuid.uuid4())[:8].upper()}")
    short_description: str = ""
    description: str = ""
    category: Optional[ProblemCategory] = None
    subcategory: str = ""
    state: ProblemState = ProblemState.NEW
    priority: Optional[Priority] = None
    impact: Optional[Impact] = None
    urgency: Optional[Urgency] = None
    problem_type: ProblemType = ProblemType.REACTIVE
    
    # Assignment
    assignment_group: str = ""
    assigned_to: Optional[Person] = None
    problem_manager: Optional[Person] = None
    
    # Configuration items
    configuration_items: List[ConfigurationItem] = field(default_factory=list)
    
    # Timestamps
    opened_at: datetime = field(default_factory=datetime.now)
    investigation_started_at: Optional[datetime] = None
    root_cause_identified_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    
    # Problem investigation
    symptoms: List[str] = field(default_factory=list)
    investigation_notes: str = ""
    root_cause: Optional[RootCause] = None
    workaround: str = ""
    
    # Known Error
    known_error: Optional[KnownError] = None
    
    # Related records
    related_incidents: Set[str] = field(default_factory=set)
    related_changes: List[str] = field(default_factory=list)
    related_problems: List[str] = field(default_factory=list)
    
    # Work tracking
    work_log: List[Dict[str, Any]] = field(default_factory=list)
    resolution_notes: str = ""
    closure_notes: str = ""
    
    # Major problem
    is_major_problem: bool = False
    major_problem_review_board: List[Person] = field(default_factory=list)
    
    # Prevention measures
    prevention_measures: List[str] = field(default_factory=list)
    lessons_learned: str = ""
    
    def __post_init__(self):
        """Post-initialization processing"""
        if self.priority is None and self.impact and self.urgency:
            self.priority = self._calculate_priority(self.impact, self.urgency)
        
        # Convert related_incidents to set if it's a list
        if isinstance(self.related_incidents, list):
            self.related_incidents = set(self.related_incidents)
    
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
        """Add a work note to the problem"""
        work_note = {
            "timestamp": datetime.now(),
            "author": author.name,
            "note": note,
            "is_public": is_public
        }
        self.work_log.append(work_note)
    
    def add_related_incident(self, incident_number: str, investigator: Person):
        """Add a related incident to the problem"""
        self.related_incidents.add(incident_number)
        self.add_work_note(f"Related incident {incident_number} added", investigator)
    
    def remove_related_incident(self, incident_number: str, investigator: Person):
        """Remove a related incident from the problem"""
        self.related_incidents.discard(incident_number)
        self.add_work_note(f"Related incident {incident_number} removed", investigator)
    
    def start_investigation(self, investigator: Person) -> bool:
        """Start problem investigation"""
        if self.state == ProblemState.NEW:
            self.state = ProblemState.UNDER_INVESTIGATION
            self.investigation_started_at = datetime.now()
            self.assigned_to = investigator
            self.add_work_note(f"Investigation started by {investigator.name}", investigator)
            return True
        return False
    
    def add_symptom(self, symptom: str, investigator: Person):
        """Add a symptom to the problem"""
        self.symptoms.append(symptom)
        self.add_work_note(f"Symptom added: {symptom}", investigator)
    
    def start_root_cause_analysis(self, analyst: Person, method: RootCauseAnalysisMethod):
        """Start root cause analysis"""
        if self.state == ProblemState.UNDER_INVESTIGATION:
            self.state = ProblemState.ROOT_CAUSE_ANALYSIS
            self.add_work_note(
                f"Root cause analysis started using {method.value} by {analyst.name}", 
                analyst
            )
    
    def identify_root_cause(self, root_cause: RootCause, analyst: Person) -> bool:
        """Identify the root cause of the problem"""
        if self.state == ProblemState.ROOT_CAUSE_ANALYSIS:
            self.root_cause = root_cause
            self.root_cause_identified_at = datetime.now()
            self.add_work_note(
                f"Root cause identified: {root_cause.description}", 
                analyst
            )
            return True
        return False
    
    def create_known_error(self, creator: Person, workaround: str = "") -> KnownError:
        """Create a known error record"""
        if not self.known_error:
            self.known_error = KnownError(
                description=self.short_description,
                workaround=workaround or self.workaround,
                root_cause=self.root_cause,
                created_by=creator
            )
            self.known_error.related_problems.append(self.number)
            self.known_error.related_incidents.extend(list(self.related_incidents))
            
            self.state = ProblemState.KNOWN_ERROR
            self.add_work_note(
                f"Known Error {self.known_error.id} created by {creator.name}", 
                creator
            )
        
        return self.known_error
    
    def add_workaround(self, workaround: str, creator: Person):
        """Add a workaround for the problem"""
        self.workaround = workaround
        self.add_work_note(f"Workaround added: {workaround}", creator)
        
        # Update known error if exists
        if self.known_error:
            self.known_error.workaround = workaround
    
    def resolve(self, resolver: Person, resolution: str, 
               prevention_measures: List[str] = None) -> bool:
        """Resolve the problem"""
        if self.state in [ProblemState.UNDER_INVESTIGATION, 
                         ProblemState.ROOT_CAUSE_ANALYSIS, 
                         ProblemState.KNOWN_ERROR]:
            self.state = ProblemState.RESOLVED
            self.resolved_at = datetime.now()
            self.resolution_notes = resolution
            
            if prevention_measures:
                self.prevention_measures.extend(prevention_measures)
            
            self.add_work_note(f"Problem resolved: {resolution}", resolver)
            return True
        return False
    
    def close(self, closer: Person, closure_notes: str = "", 
             lessons_learned: str = "") -> bool:
        """Close the problem"""
        if self.state == ProblemState.RESOLVED:
            self.state = ProblemState.CLOSED
            self.closed_at = datetime.now()
            self.closure_notes = closure_notes
            self.lessons_learned = lessons_learned
            self.add_work_note(f"Problem closed by {closer.name}", closer)
            return True
        return False
    
    def promote_to_major(self, manager: Person, reason: str) -> bool:
        """Promote problem to major problem status"""
        if not self.is_major_problem:
            self.is_major_problem = True
            self.problem_manager = manager
            self.add_work_note(f"Promoted to Major Problem by {manager.name}. Reason: {reason}", manager)
            return True
        return False
    
    def get_age_in_days(self) -> float:
        """Get problem age in days"""
        if self.closed_at:
            return (self.closed_at - self.opened_at).days
        return (datetime.now() - self.opened_at).days
    
    def get_resolution_time_days(self) -> Optional[float]:
        """Get resolution time in days"""
        if self.resolved_at:
            return (self.resolved_at - self.opened_at).days
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert problem to dictionary representation"""
        return {
            "number": self.number,
            "short_description": self.short_description,
            "description": self.description,
            "category": self.category.value if self.category else None,
            "subcategory": self.subcategory,
            "state": self.state.value,
            "priority": self.priority.value if self.priority else None,
            "impact": self.impact.value if self.impact else None,
            "urgency": self.urgency.value if self.urgency else None,
            "problem_type": self.problem_type.value,
            "assignment_group": self.assignment_group,
            "assigned_to": self.assigned_to.name if self.assigned_to else None,
            "problem_manager": self.problem_manager.name if self.problem_manager else None,
            "opened_at": self.opened_at.isoformat(),
            "investigation_started_at": self.investigation_started_at.isoformat() if self.investigation_started_at else None,
            "root_cause_identified_at": self.root_cause_identified_at.isoformat() if self.root_cause_identified_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
            "is_major_problem": self.is_major_problem,
            "related_incidents_count": len(self.related_incidents),
            "has_known_error": self.known_error is not None,
            "has_workaround": bool(self.workaround),
            "age_days": self.get_age_in_days(),
            "resolution_time_days": self.get_resolution_time_days(),
            "symptoms_count": len(self.symptoms),
            "prevention_measures_count": len(self.prevention_measures)
        }


class ProblemManagement:
    """
    ITIL 4 Problem Management Practice Implementation
    
    Manages the complete problem lifecycle including reactive and proactive
    problem identification, root cause analysis, and known error management.
    """
    
    def __init__(self):
        self.problems: Dict[str, Problem] = {}
        self.known_errors: Dict[str, KnownError] = {}
        self.assignment_groups = {}
        self.rca_templates = {}
        self.major_problem_criteria = {
            "incident_count_threshold": 5,
            "business_impact_threshold": Impact.HIGH,
            "customer_count_threshold": 100
        }
        self.proactive_monitoring_rules = {}
    
    def create_problem(self, short_description: str, description: str, 
                      category: ProblemCategory, impact: Impact, urgency: Urgency,
                      problem_type: ProblemType = ProblemType.REACTIVE,
                      related_incidents: List[str] = None,
                      assigned_to: Optional[Person] = None) -> Problem:
        """Create a new problem"""
        
        problem = Problem(
            short_description=short_description,
            description=description,
            category=category,
            impact=impact,
            urgency=urgency,
            problem_type=problem_type,
            assigned_to=assigned_to
        )
        
        if related_incidents:
            problem.related_incidents.update(related_incidents)
        
        # Auto-assign based on category
        self._auto_assign_problem(problem)
        
        # Check for major problem criteria
        if self._meets_major_problem_criteria(problem):
            problem.is_major_problem = True
        
        # Store problem
        self.problems[problem.number] = problem
        
        # Log creation
        problem.add_work_note(
            f"Problem created. Category: {category.value}, Priority: {problem.priority.value}, Type: {problem_type.value}",
            assigned_to or Person("system", "System", "system@company.com", "System", "System")
        )
        
        return problem
    
    def create_problem_from_incidents(self, incident_numbers: List[str], 
                                    short_description: str, description: str,
                                    category: ProblemCategory, analyst: Person) -> Problem:
        """Create a problem from multiple related incidents"""
        
        # Determine impact and urgency based on incidents
        impact = Impact.MEDIUM  # Would analyze incidents to determine
        urgency = Urgency.MEDIUM
        
        problem = self.create_problem(
            short_description=short_description,
            description=description,
            category=category,
            impact=impact,
            urgency=urgency,
            problem_type=ProblemType.REACTIVE,
            related_incidents=incident_numbers,
            assigned_to=analyst
        )
        
        problem.add_work_note(
            f"Problem created from {len(incident_numbers)} related incidents: {', '.join(incident_numbers)}",
            analyst
        )
        
        return problem
    
    def create_proactive_problem(self, short_description: str, description: str,
                               category: ProblemCategory, identified_by: Person,
                               risk_level: Impact = Impact.MEDIUM) -> Problem:
        """Create a proactive problem from trend analysis or monitoring"""
        
        problem = self.create_problem(
            short_description=short_description,
            description=description,
            category=category,
            impact=risk_level,
            urgency=Urgency.LOW,
            problem_type=ProblemType.PROACTIVE,
            assigned_to=identified_by
        )
        
        problem.add_work_note(
            f"Proactive problem identified by {identified_by.name} through trend analysis",
            identified_by
        )
        
        return problem
    
    def get_problem(self, problem_number: str) -> Optional[Problem]:
        """Retrieve problem by number"""
        return self.problems.get(problem_number)
    
    def search_problems(self, criteria: Dict[str, Any]) -> List[Problem]:
        """Search problems based on criteria"""
        results = []
        
        for problem in self.problems.values():
            match = True
            
            for field, value in criteria.items():
                if hasattr(problem, field):
                    problem_value = getattr(problem, field)
                    if isinstance(problem_value, Enum):
                        problem_value = problem_value.value
                    
                    if problem_value != value:
                        match = False
                        break
            
            if match:
                results.append(problem)
        
        return results
    
    def get_problems_by_state(self, state: ProblemState) -> List[Problem]:
        """Get all problems in a specific state"""
        return [prob for prob in self.problems.values() if prob.state == state]
    
    def get_major_problems(self) -> List[Problem]:
        """Get all major problems"""
        return [prob for prob in self.problems.values() if prob.is_major_problem]
    
    def get_problems_with_known_errors(self) -> List[Problem]:
        """Get problems that have known errors"""
        return [prob for prob in self.problems.values() if prob.known_error is not None]
    
    def get_known_errors(self) -> List[KnownError]:
        """Get all known errors"""
        return list(self.known_errors.values())
    
    def search_known_errors(self, search_term: str) -> List[KnownError]:
        """Search known errors by description or workaround"""
        results = []
        search_term = search_term.lower()
        
        for ke in self.known_errors.values():
            if (search_term in ke.description.lower() or 
                search_term in ke.workaround.lower()):
                results.append(ke)
        
        return results
    
    def conduct_root_cause_analysis(self, problem_number: str, 
                                  method: RootCauseAnalysisMethod,
                                  analyst: Person) -> Dict[str, Any]:
        """Conduct root cause analysis for a problem"""
        problem = self.get_problem(problem_number)
        if not problem:
            return {"error": "Problem not found"}
        
        problem.start_root_cause_analysis(analyst, method)
        
        # Provide RCA template/guidance based on method
        rca_guidance = {
            RootCauseAnalysisMethod.FIVE_WHYS: {
                "description": "Ask 'Why?' five times to drill down to root cause",
                "steps": [
                    "1. State the problem clearly",
                    "2. Ask why the problem occurred",
                    "3. For each answer, ask why again",
                    "4. Continue until you reach the root cause",
                    "5. Verify the root cause addresses all symptoms"
                ]
            },
            RootCauseAnalysisMethod.FISHBONE: {
                "description": "Analyze potential causes in categories",
                "categories": ["People", "Process", "Technology", "Environment", "Materials", "Methods"]
            },
            RootCauseAnalysisMethod.TIMELINE: {
                "description": "Create chronological timeline of events",
                "steps": [
                    "1. List all events chronologically",
                    "2. Identify what changed before the problem",
                    "3. Correlate changes with problem occurrence",
                    "4. Identify causal relationships"
                ]
            }
        }
        
        return {
            "problem_number": problem_number,
            "method": method.value,
            "guidance": rca_guidance.get(method, {}),
            "symptoms": problem.symptoms,
            "related_incidents": list(problem.related_incidents),
            "configuration_items": [ci.name for ci in problem.configuration_items]
        }
    
    def identify_trends_for_proactive_problems(self, period_days: int = 30) -> List[Dict[str, Any]]:
        """Identify trends that might indicate proactive problems"""
        cutoff_date = datetime.now() - timedelta(days=period_days)
        
        # Analyze incident patterns (would integrate with incident management)
        trends = []
        
        # Example trend analysis
        category_counts = {}
        for problem in self.problems.values():
            if problem.opened_at >= cutoff_date and problem.category:
                category_counts[problem.category.value] = category_counts.get(problem.category.value, 0) + 1
        
        # Identify categories with increasing problems
        for category, count in category_counts.items():
            if count >= 3:  # Threshold for concern
                trends.append({
                    "type": "Recurring Problems",
                    "category": category,
                    "count": count,
                    "recommendation": f"Consider proactive problem investigation for {category} issues",
                    "risk_level": "Medium" if count < 5 else "High"
                })
        
        return trends
    
    def get_metrics(self, period_days: int = 30) -> Dict[str, Any]:
        """Get problem management metrics for specified period"""
        cutoff_date = datetime.now() - timedelta(days=period_days)
        period_problems = [
            prob for prob in self.problems.values() 
            if prob.opened_at >= cutoff_date
        ]
        
        if not period_problems:
            return {"error": "No problems in specified period"}
        
        # Volume metrics
        total_problems = len(period_problems)
        closed_problems = len([prob for prob in period_problems if prob.state == ProblemState.CLOSED])
        major_problems = len([prob for prob in period_problems if prob.is_major_problem])
        
        # Type distribution
        reactive_problems = len([prob for prob in period_problems if prob.problem_type == ProblemType.REACTIVE])
        proactive_problems = len([prob for prob in period_problems if prob.problem_type == ProblemType.PROACTIVE])
        
        # Resolution metrics
        resolved_problems = [prob for prob in period_problems if prob.resolved_at]
        resolution_times = [prob.get_resolution_time_days() for prob in resolved_problems if prob.get_resolution_time_days()]
        
        # Root cause analysis metrics
        problems_with_rca = len([prob for prob in period_problems if prob.root_cause])
        problems_with_known_errors = len([prob for prob in period_problems if prob.known_error])
        
        # Category distribution
        category_dist = {}
        for category in ProblemCategory:
            count = len([prob for prob in period_problems if prob.category == category])
            category_dist[category.value] = count
        
        # State distribution
        state_dist = {}
        for state in ProblemState:
            count = len([prob for prob in period_problems if prob.state == state])
            state_dist[state.value] = count
        
        # Calculate averages
        avg_resolution_time = sum(resolution_times) / len(resolution_times) if resolution_times else 0
        
        return {
            "period_days": period_days,
            "total_problems": total_problems,
            "closed_problems": closed_problems,
            "resolution_rate": (closed_problems / total_problems * 100) if total_problems > 0 else 0,
            "avg_resolution_time_days": round(avg_resolution_time, 2),
            "major_problems": major_problems,
            "reactive_problems": reactive_problems,
            "proactive_problems": proactive_problems,
            "proactive_ratio": (proactive_problems / total_problems * 100) if total_problems > 0 else 0,
            "problems_with_rca": problems_with_rca,
            "rca_completion_rate": (problems_with_rca / total_problems * 100) if total_problems > 0 else 0,
            "problems_with_known_errors": problems_with_known_errors,
            "known_error_creation_rate": (problems_with_known_errors / total_problems * 100) if total_problems > 0 else 0,
            "category_distribution": category_dist,
            "state_distribution": state_dist,
            "total_known_errors": len(self.known_errors)
        }
    
    def _auto_assign_problem(self, problem: Problem):
        """Auto-assign problem based on category"""
        assignment_map = {
            ProblemCategory.HARDWARE: "Hardware Engineering",
            ProblemCategory.SOFTWARE: "Software Engineering",
            ProblemCategory.NETWORK: "Network Engineering",
            ProblemCategory.SECURITY: "Security Team",
            ProblemCategory.PROCESS: "Process Improvement",
            ProblemCategory.INFRASTRUCTURE: "Infrastructure Team",
            ProblemCategory.APPLICATION: "Application Engineering",
            ProblemCategory.DATABASE: "Database Administration",
            ProblemCategory.CAPACITY: "Capacity Management",
            ProblemCategory.AVAILABILITY: "Availability Management"
        }
        
        if problem.category in assignment_map:
            problem.assignment_group = assignment_map[problem.category]
    
    def _meets_major_problem_criteria(self, problem: Problem) -> bool:
        """Check if problem meets major problem criteria"""
        # Check incident count
        if len(problem.related_incidents) >= self.major_problem_criteria["incident_count_threshold"]:
            return True
        
        # Check business impact
        if problem.impact == self.major_problem_criteria["business_impact_threshold"]:
            return True
        
        return False
    
    def generate_problem_report(self, problem_number: str) -> Dict[str, Any]:
        """Generate comprehensive problem report"""
        problem = self.get_problem(problem_number)
        if not problem:
            return {"error": "Problem not found"}
        
        report = {
            "problem_details": problem.to_dict(),
            "timeline": [
                {
                    "event": "Problem Created",
                    "timestamp": problem.opened_at.isoformat(),
                    "details": f"Problem type: {problem.problem_type.value}"
                }
            ],
            "investigation": {
                "symptoms": problem.symptoms,
                "investigation_notes": problem.investigation_notes,
                "root_cause": {
                    "description": problem.root_cause.description if problem.root_cause else None,
                    "method": problem.root_cause.analysis_method.value if problem.root_cause else None,
                    "confidence": problem.root_cause.confidence_level if problem.root_cause else None
                } if problem.root_cause else None
            },
            "known_error": problem.known_error.to_dict() if problem.known_error else None,
            "related_records": {
                "incidents": list(problem.related_incidents),
                "changes": problem.related_changes,
                "problems": problem.related_problems
            },
            "work_log": problem.work_log,
            "prevention": {
                "measures": problem.prevention_measures,
                "lessons_learned": problem.lessons_learned
            }
        }
        
        # Add timeline events
        if problem.investigation_started_at:
            report["timeline"].append({
                "event": "Investigation Started",
                "timestamp": problem.investigation_started_at.isoformat(),
                "details": f"Assigned to {problem.assigned_to.name if problem.assigned_to else 'Unknown'}"
            })
        
        if problem.root_cause_identified_at:
            report["timeline"].append({
                "event": "Root Cause Identified",
                "timestamp": problem.root_cause_identified_at.isoformat(),
                "details": problem.root_cause.description if problem.root_cause else ""
            })
        
        if problem.known_error:
            report["timeline"].append({
                "event": "Known Error Created",
                "timestamp": problem.known_error.created_at.isoformat(),
                "details": f"Known Error ID: {problem.known_error.id}"
            })
        
        if problem.resolved_at:
            report["timeline"].append({
                "event": "Problem Resolved",
                "timestamp": problem.resolved_at.isoformat(),
                "details": problem.resolution_notes
            })
        
        if problem.closed_at:
            report["timeline"].append({
                "event": "Problem Closed",
                "timestamp": problem.closed_at.isoformat(),
                "details": problem.closure_notes
            })
        
        return report


# Example usage and testing
if __name__ == "__main__":
    print("ITIL 4 Problem Management Practice")
    print("=" * 40)
    
    # Create problem management system
    pm = ProblemManagement()
    
    # Create sample persons
    analyst = Person("1", "Alice Johnson", "alice.johnson@company.com", "Problem Analyst", "IT Support")
    engineer = Person("2", "Bob Wilson", "bob.wilson@company.com", "Senior Engineer", "Infrastructure")
    
    # Create sample CI
    ci = ConfigurationItem("1", "Database Server", "Server", "Production", "Production")
    
    # Create problem from incidents
    problem = pm.create_problem_from_incidents(
        incident_numbers=["INC001", "INC002", "INC003"],
        short_description="Database performance degradation",
        description="Multiple incidents reported slow database queries and timeouts",
        category=ProblemCategory.DATABASE,
        analyst=analyst
    )
    
    print(f"Created problem: {problem.number}")
    print(f"Priority: {problem.priority.value}")
    print(f"Related incidents: {len(problem.related_incidents)}")
    
    # Start investigation
    problem.start_investigation(engineer)
    problem.add_symptom("Query response time > 10 seconds", engineer)
    problem.add_symptom("Connection pool exhaustion", engineer)
    
    # Conduct RCA
    rca_guidance = pm.conduct_root_cause_analysis(
        problem.number, 
        RootCauseAnalysisMethod.FIVE_WHYS, 
        engineer
    )
    print(f"\nRCA Method: {rca_guidance['method']}")
    
    # Identify root cause
    root_cause = RootCause(
        description="Inefficient database indexing causing table scans",
        analysis_method=RootCauseAnalysisMethod.FIVE_WHYS,
        contributing_factors=["Missing indexes", "Query optimization not performed"],
        confidence_level=90,
        identified_by=engineer
    )
    problem.identify_root_cause(root_cause, engineer)
    
    # Create known error with workaround
    known_error = problem.create_known_error(
        engineer, 
        "Use query hints to force index usage until proper indexes are created"
    )
    print(f"\nCreated Known Error: {known_error.id}")
    
    # Resolve problem
    problem.resolve(
        engineer, 
        "Created proper database indexes and optimized queries",
        prevention_measures=["Implement query performance monitoring", "Regular index maintenance"]
    )
    
    # Generate report
    report = pm.generate_problem_report(problem.number)
    print(f"\nProblem Report:")
    print(json.dumps(report, indent=2, default=str))
    
    # Get metrics
    metrics = pm.get_metrics(30)
    print(f"\nProblem Management Metrics (30 days):")
    print(json.dumps(metrics, indent=2))