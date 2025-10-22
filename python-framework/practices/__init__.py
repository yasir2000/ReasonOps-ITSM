"""
ITIL 4 Practices Module

This module provides Python implementations of key ITIL 4 practices:
- Incident Management
- Problem Management 
- Change Enablement
- Service Request Management
- Knowledge Management
- And more...

Each practice is implemented as a comprehensive class with full lifecycle
management, metrics, reporting, and integration capabilities.
"""

# Guarded imports to avoid package init failures in different execution contexts
try:
    from .incident_management import (
        IncidentManagement,
        Incident,
        IncidentCategory,
        IncidentState,
        EscalationLevel
    )
except Exception:
    IncidentManagement = None  # type: ignore
    Incident = None  # type: ignore
    IncidentCategory = None  # type: ignore
    IncidentState = None  # type: ignore
    EscalationLevel = None  # type: ignore

try:
    from .problem_management import (
        ProblemManagement,
        Problem,
        ProblemCategory,
        ProblemState,
        ProblemType,
        RootCauseAnalysisMethod,
        KnownError,
        RootCause
    )
except Exception:
    ProblemManagement = None  # type: ignore
    Problem = None  # type: ignore
    ProblemCategory = None  # type: ignore
    ProblemState = None  # type: ignore
    ProblemType = None  # type: ignore
    RootCauseAnalysisMethod = None  # type: ignore
    KnownError = None  # type: ignore
    RootCause = None  # type: ignore

try:
    from .change_enablement import (
        ChangeEnablement,
        Change,
        ChangeType,
        ChangeCategory,
        ChangeState,
        ChangeRisk,
        ChangeAdvisoryBoard,
        ImplementationPlan,
        BackoutPlan,
        TestPlan
    )
except Exception:
    ChangeEnablement = None  # type: ignore
    Change = None  # type: ignore
    ChangeType = None  # type: ignore
    ChangeCategory = None  # type: ignore
    ChangeState = None  # type: ignore
    ChangeRisk = None  # type: ignore
    ChangeAdvisoryBoard = None  # type: ignore
    ImplementationPlan = None  # type: ignore
    BackoutPlan = None  # type: ignore
    TestPlan = None  # type: ignore

__all__ = [
    # Incident Management
    'IncidentManagement',
    'Incident',
    'IncidentCategory',
    'IncidentState',
    'EscalationLevel',
    
    # Problem Management
    'ProblemManagement',
    'Problem',
    'ProblemCategory',
    'ProblemState',
    'ProblemType',
    'RootCauseAnalysisMethod',
    'KnownError',
    'RootCause',
    
    # Change Enablement
    'ChangeEnablement',
    'Change',
    'ChangeType',
    'ChangeCategory',
    'ChangeState',
    'ChangeRisk',
    'ChangeAdvisoryBoard',
    'ImplementationPlan',
    'BackoutPlan',
    'TestPlan'
]

# Version information
__version__ = "1.0.0"
__author__ = "ITIL 4 Framework Implementation"
__description__ = "Comprehensive Python implementation of ITIL 4 practices"

def get_available_practices():
    """Get list of available ITIL 4 practices in this module"""
    return [
        {
            "name": "Incident Management",
            "description": "Minimize negative impact of incidents by restoring service operation as quickly as possible",
            "class": "IncidentManagement",
            "module": "incident_management"
        },
        {
            "name": "Problem Management", 
            "description": "Reduce likelihood and impact of incidents by identifying actual and potential causes",
            "class": "ProblemManagement",
            "module": "problem_management"
        },
        {
            "name": "Change Enablement",
            "description": "Maximize successful service changes by ensuring risks are assessed and changes authorized",
            "class": "ChangeEnablement", 
            "module": "change_enablement"
        }
    ]

def create_integrated_service_management():
    """Create an integrated service management system with all practices"""
    
    class IntegratedServiceManagement:
        """Integrated ITSM system combining multiple ITIL practices"""
        
        def __init__(self):
            self.incident_management = IncidentManagement()
            self.problem_management = ProblemManagement()
            self.change_enablement = ChangeEnablement()
            
        def get_dashboard_metrics(self, period_days: int = 30):
            """Get combined dashboard metrics from all practices"""
            return {
                "incident_metrics": self.incident_management.get_metrics(period_days),
                "problem_metrics": self.problem_management.get_metrics(period_days),
                "change_metrics": self.change_enablement.get_metrics(period_days),
                "period_days": period_days
            }
        
        def create_problem_from_incidents(self, incident_numbers: list, 
                                        description: str, analyst):
            """Create a problem from multiple related incidents"""
            # Get incidents from incident management
            incidents = []
            for inc_num in incident_numbers:
                incident = self.incident_management.get_incident(inc_num)
                if incident:
                    incidents.append(incident)
            
            if not incidents:
                return None
                
            # Determine category from incidents
            categories = [inc.category for inc in incidents if inc.category]
            most_common_category = max(set(categories), key=categories.count) if categories else None
            
            # Create problem
            problem = self.problem_management.create_problem_from_incidents(
                incident_numbers=incident_numbers,
                short_description=description,
                description=f"Problem created from {len(incidents)} related incidents",
                category=most_common_category or ProblemCategory.APPLICATION,
                analyst=analyst
            )
            
            # Link incidents to problem
            for incident in incidents:
                incident.related_problems.append(problem.number)
            
            return problem
        
        def create_change_from_problem(self, problem_number: str, 
                                     change_description: str, requester):
            """Create a change request to resolve a problem"""
            problem = self.problem_management.get_problem(problem_number)
            if not problem:
                return None
            
            # Determine change category based on problem
            change_category_map = {
                ProblemCategory.HARDWARE: ChangeCategory.HARDWARE,
                ProblemCategory.SOFTWARE: ChangeCategory.SOFTWARE,
                ProblemCategory.NETWORK: ChangeCategory.NETWORK,
                ProblemCategory.SECURITY: ChangeCategory.SECURITY,
                ProblemCategory.INFRASTRUCTURE: ChangeCategory.INFRASTRUCTURE,
                ProblemCategory.APPLICATION: ChangeCategory.APPLICATION,
                ProblemCategory.DATABASE: ChangeCategory.DATABASE
            }
            
            change_category = change_category_map.get(problem.category, ChangeCategory.SOFTWARE)
            
            # Create change
            change = self.change_enablement.create_change_request(
                short_description=change_description,
                description=f"Change to resolve problem {problem.number}: {problem.short_description}",
                justification=f"Permanent fix for problem: {problem.description}",
                category=change_category,
                change_type=ChangeType.NORMAL,
                requester=requester,
                impact=problem.impact or Impact.MEDIUM,
                urgency=problem.urgency or Urgency.MEDIUM
            )
            
            # Link change to problem
            change.related_problems.append(problem.number)
            problem.related_changes.append(change.number)
            
            return change
    
    return IntegratedServiceManagement()


# Example of how to use the integrated system
if __name__ == "__main__":
    print("ITIL 4 Practices Module")
    print("=" * 30)
    
    # Show available practices
    practices = get_available_practices()
    print("Available Practices:")
    for practice in practices:
        print(f"- {practice['name']}: {practice['description']}")
    
    # Create integrated system
    print(f"\nCreating integrated service management system...")
    itsm = create_integrated_service_management()
    
    print("✅ Integrated ITSM system created with:")
    print("  - Incident Management")
    print("  - Problem Management") 
    print("  - Change Enablement")
    
    # Example integration workflow
    from ..core.service_value_system import Person, Impact, Urgency
    
    # Sample persons
    user = Person("1", "John User", "john.user@company.com", "End User", "Sales")
    agent = Person("2", "Jane Agent", "jane.agent@company.com", "Service Desk Agent", "IT")
    analyst = Person("3", "Bob Analyst", "bob.analyst@company.com", "Problem Analyst", "IT")
    
    print(f"\n📋 Example Integration Workflow:")
    
    # 1. Create some incidents
    incident1 = itsm.incident_management.create_incident(
        "Email server slow response",
        "Users reporting slow email response times",
        user,
        IncidentCategory.APPLICATION,
        Impact.MEDIUM,
        Urgency.HIGH
    )
    
    incident2 = itsm.incident_management.create_incident(
        "Email timeouts",
        "Email client timeouts when sending messages",
        user,
        IncidentCategory.APPLICATION,
        Impact.MEDIUM,
        Urgency.HIGH
    )
    
    print(f"1. Created incidents: {incident1.number}, {incident2.number}")
    
    # 2. Create problem from incidents
    problem = itsm.create_problem_from_incidents(
        [incident1.number, incident2.number],
        "Email server performance issues",
        analyst
    )
    
    print(f"2. Created problem: {problem.number}")
    
    # 3. Create change to fix problem
    change = itsm.create_change_from_problem(
        problem.number,
        "Upgrade email server memory and optimize configuration",
        analyst
    )
    
    print(f"3. Created change: {change.number}")
    
    # 4. Get integrated metrics
    metrics = itsm.get_dashboard_metrics(30)
    print(f"4. Retrieved integrated metrics for last 30 days")
    
    print(f"\n✅ Integration workflow completed successfully!")
    print(f"   - Incidents linked to problem")
    print(f"   - Change created to resolve problem") 
    print(f"   - All records cross-referenced")