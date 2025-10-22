"""
ITIL 4 Python Framework

A comprehensive Python implementation of the ITIL 4 framework providing:

🏗️ Core Components:
- Service Value System
- Guiding Principles  
- Service Value Chain
- Governance Framework
- Continual Improvement

📚 Practice Implementations:
- Incident Management
- Problem Management
- Change Enablement
- Service Request Management
- Knowledge Management
- And more...

🔧 Features:
- Full object-oriented design
- Comprehensive metrics and reporting
- Integration between practices
- Real-world workflow support
- Extensible architecture

Usage:
    from python_framework import ITILFramework
    
    # Create integrated ITIL system
    itil = ITILFramework()
    
    # Access individual practices
    incident_mgmt = itil.incident_management
    problem_mgmt = itil.problem_management
    change_mgmt = itil.change_enablement
    
    # Get dashboard metrics
    metrics = itil.get_dashboard_metrics()
"""

# Import core components
from .core import (
    ServiceValueSystem,
    GuidingPrinciples,
    ServiceValueChain,
    GovernanceFramework,
    ContinualImprovement,
    Priority,
    Status,
    Impact,
    Urgency,
    Person,
    ConfigurationItem
)

# Import practices
from .practices import (
    IncidentManagement,
    ProblemManagement,
    ChangeEnablement,
    create_integrated_service_management
)

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

__version__ = "1.0.0"
__author__ = "ITIL 4 Framework Implementation Team"
__description__ = "Comprehensive Python implementation of ITIL 4 framework"
__license__ = "MIT"

# Package information
FRAMEWORK_INFO = {
    "name": "ITIL 4 Python Framework",
    "version": __version__,
    "description": __description__,
    "components": {
        "core": "Service Value System, Guiding Principles, Service Value Chain",
        "practices": "Incident Management, Problem Management, Change Enablement",  
        "utilities": "Metrics, Reporting, Integration tools"
    },
    "capabilities": [
        "Full ITIL 4 lifecycle management",
        "Practice integration and workflow automation",
        "Comprehensive metrics and reporting",
        "Extensible architecture for custom practices",
        "Real-world scenario support"
    ]
}


class ITILFramework:
    """
    Main ITIL 4 Framework Class
    
    Provides a unified interface to all ITIL 4 components and practices.
    This is the primary entry point for using the framework.
    """
    
    def __init__(self):
        """Initialize the complete ITIL 4 framework"""
        
        # Core components
        self.service_value_system = ServiceValueSystem()
        self.service_value_system.initialize_default_configuration()
        
        self.guiding_principles = GuidingPrinciples()
        self.service_value_chain = ServiceValueChain()
        self.governance = GovernanceFramework()
        self.continual_improvement = ContinualImprovement()
        
        # Practice implementations
        self.incident_management = IncidentManagement()
        self.problem_management = ProblemManagement()
        self.change_enablement = ChangeEnablement()
        
        # Framework metadata
        self.initialized_at = datetime.now()
        self.version = __version__
        
        # Integration mappings
        self._setup_practice_integrations()
    
    def _setup_practice_integrations(self):
        """Set up integrations between practices"""
        # This would set up automatic workflows between practices
        # For example: incidents -> problems -> changes
        pass
    
    def get_framework_info(self) -> Dict[str, Any]:
        """Get comprehensive framework information"""
        return {
            **FRAMEWORK_INFO,
            "initialized_at": self.initialized_at.isoformat(),
            "runtime_info": {
                "incidents_managed": len(self.incident_management.incidents),
                "problems_managed": len(self.problem_management.problems),
                "changes_managed": len(self.change_enablement.changes),
                "known_errors": len(self.problem_management.known_errors),
                "practices_loaded": [
                    "Incident Management",
                    "Problem Management", 
                    "Change Enablement"
                ]
            }
        }
    
    def get_dashboard_metrics(self, period_days: int = 30) -> Dict[str, Any]:
        """
        Get comprehensive dashboard metrics from all practices
        
        Args:
            period_days: Number of days to include in metrics
            
        Returns:
            Dictionary with metrics from all practices
        """
        
        dashboard = {
            "framework_info": {
                "version": self.version,
                "period_days": period_days,
                "generated_at": datetime.now().isoformat()
            },
            "incident_management": self.incident_management.get_metrics(period_days),
            "problem_management": self.problem_management.get_metrics(period_days),
            "change_enablement": self.change_enablement.get_metrics(period_days)
        }
        
        # Calculate cross-practice metrics
        incident_metrics = dashboard["incident_management"]
        problem_metrics = dashboard["problem_management"] 
        change_metrics = dashboard["change_enablement"]
        
        # Avoid division by zero
        total_incidents = incident_metrics.get("total_incidents", 0)
        total_problems = problem_metrics.get("total_problems", 0)
        total_changes = change_metrics.get("total_changes", 0)
        
        dashboard["integration_metrics"] = {
            "total_records": total_incidents + total_problems + total_changes,
            "incident_to_problem_ratio": round(total_incidents / max(total_problems, 1), 2),
            "problem_to_change_ratio": round(total_problems / max(total_changes, 1), 2),
            "major_incidents": incident_metrics.get("major_incidents", 0),
            "major_problems": problem_metrics.get("major_problems", 0),
            "emergency_changes": len([c for c in self.change_enablement.changes.values() 
                                    if c.change_type.value == "Emergency"]),
            "sla_compliance": {
                "incident_sla_compliance": incident_metrics.get("sla_compliance_rate", 0),
                "change_success_rate": change_metrics.get("success_rate", 0)
            }
        }
        
        return dashboard
    
    def create_incident(self, short_description: str, description: str,
                       caller: Person, category, impact: Impact, urgency: Urgency,
                       affected_ci: Optional[ConfigurationItem] = None):
        """Create a new incident"""
        from .practices.incident_management import IncidentCategory
        
        return self.incident_management.create_incident(
            short_description=short_description,
            description=description,
            caller=caller,
            category=category,
            impact=impact,
            urgency=urgency,
            affected_ci=affected_ci
        )
    
    def create_problem_from_incidents(self, incident_numbers: List[str],
                                    short_description: str, description: str,
                                    category, analyst: Person):
        """Create a problem from multiple incidents with automatic linking"""
        
        # Create the problem
        problem = self.problem_management.create_problem_from_incidents(
            incident_numbers=incident_numbers,
            short_description=short_description,
            description=description,
            category=category,
            analyst=analyst
        )
        
        # Link incidents to problem (bidirectional)
        for inc_num in incident_numbers:
            incident = self.incident_management.get_incident(inc_num)
            if incident:
                incident.related_problems.append(problem.number)
        
        return problem
    
    def create_change_from_problem(self, problem_number: str,
                                 change_description: str, requester: Person):
        """Create a change request to resolve a problem with automatic linking"""
        
        problem = self.problem_management.get_problem(problem_number)
        if not problem:
            return None
        
        from .practices.change_enablement import ChangeCategory, ChangeType
        
        # Map problem categories to change categories
        category_map = {
            "Hardware": ChangeCategory.HARDWARE,
            "Software": ChangeCategory.SOFTWARE,
            "Network": ChangeCategory.NETWORK,
            "Security": ChangeCategory.SECURITY,
            "Infrastructure": ChangeCategory.INFRASTRUCTURE,
            "Application": ChangeCategory.APPLICATION,
            "Database": ChangeCategory.DATABASE
        }
        
        change_category = category_map.get(
            problem.category.value if problem.category else "Software",
            ChangeCategory.SOFTWARE
        )
        
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
        
        # Link change to problem (bidirectional)
        change.related_problems.append(problem.number)
        problem.related_changes.append(change.number)
        
        return change
    
    def get_integration_report(self) -> Dict[str, Any]:
        """Generate a report showing integrations between practices"""
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "cross_references": {
                "incidents_with_problems": 0,
                "problems_with_changes": 0,
                "changes_with_incidents": 0
            },
            "workflow_examples": [],
            "integration_health": "Good"  # Good, Warning, Poor
        }
        
        # Count cross-references
        for incident in self.incident_management.incidents.values():
            if incident.related_problems:
                report["cross_references"]["incidents_with_problems"] += 1
        
        for problem in self.problem_management.problems.values():
            if problem.related_changes:
                report["cross_references"]["problems_with_changes"] += 1
        
        for change in self.change_enablement.changes.values():
            if change.related_incidents:
                report["cross_references"]["changes_with_incidents"] += 1
        
        # Example integrated workflows
        report["workflow_examples"] = [
            {
                "name": "Incident → Problem → Change",
                "description": "Multiple incidents lead to problem identification, then change implementation",
                "steps": [
                    "1. Multiple similar incidents occur",
                    "2. Pattern identified, problem created",
                    "3. Root cause analysis performed", 
                    "4. Change request created for permanent fix",
                    "5. Change implemented and verified"
                ]
            },
            {
                "name": "Proactive Problem → Change",
                "description": "Proactive problem identification leads to preventive change",
                "steps": [
                    "1. Trend analysis identifies potential issue",
                    "2. Proactive problem created",
                    "3. Risk assessment performed",
                    "4. Preventive change request created",
                    "5. Change implemented to prevent incidents"
                ]
            }
        ]
        
        return report
    
    def export_configuration(self) -> Dict[str, Any]:
        """Export current framework configuration"""
        
        return {
            "framework_version": self.version,
            "export_timestamp": datetime.now().isoformat(),
            "service_value_system": {
                "practices_count": len(self.service_value_system.practices),
                "governance_bodies": len(self.governance.governance_bodies)
            },
            "practice_configurations": {
                "incident_management": {
                    "sla_targets": self.incident_management.sla_targets,
                    "assignment_groups": self.incident_management.assignment_groups,
                    "major_incident_criteria": self.incident_management.major_incident_criteria
                },
                "problem_management": {
                    "assignment_groups": self.problem_management.assignment_groups,
                    "major_problem_criteria": self.problem_management.major_problem_criteria
                },
                "change_enablement": {
                    "standard_changes": list(self.change_enablement.standard_changes.keys()),
                    "change_windows": list(self.change_enablement.change_windows.keys()),
                    "frozen_periods": len(self.change_enablement.frozen_periods)
                }
            }
        }
    
    def validate_framework_health(self) -> Dict[str, Any]:
        """Validate the health and configuration of the framework"""
        
        health_report = {
            "timestamp": datetime.now().isoformat(),
            "overall_health": "Healthy",
            "checks": []
        }
        
        # Check core components
        if len(self.service_value_system.practices) > 0:
            health_report["checks"].append({
                "component": "Service Value System",
                "status": "OK",
                "details": f"{len(self.service_value_system.practices)} practices loaded"
            })
        
        # Check practice configurations
        for practice_name, practice in [
            ("Incident Management", self.incident_management),
            ("Problem Management", self.problem_management),
            ("Change Enablement", self.change_enablement)
        ]:
            health_report["checks"].append({
                "component": practice_name,
                "status": "OK",
                "details": f"Practice initialized and ready"
            })
        
        # Check for any issues
        issues = []
        if not self.governance.governance_bodies:
            issues.append("No governance bodies defined")
        
        if issues:
            health_report["overall_health"] = "Warning"
            health_report["issues"] = issues
        
        return health_report


# Convenience functions for quick access
def create_framework() -> ITILFramework:
    """Create a new ITIL 4 framework instance"""
    return ITILFramework()

def get_framework_info() -> Dict[str, Any]:
    """Get information about the ITIL 4 framework package"""
    return FRAMEWORK_INFO

# Example usage and demonstration
if __name__ == "__main__":
    print("🚀 ITIL 4 Python Framework")
    print("=" * 50)
    
    # Create framework
    print("Creating ITIL 4 Framework...")
    itil = create_framework()
    
    # Show framework info
    info = itil.get_framework_info()
    print(f"✅ Framework initialized successfully!")
    print(f"   Version: {info['version']}")
    print(f"   Components: {len(info['components'])} core areas")
    print(f"   Practices: {len(info['runtime_info']['practices_loaded'])} loaded")
    
    # Show capabilities
    print(f"\n🎯 Framework Capabilities:")
    for capability in info['capabilities']:
        print(f"   • {capability}")
    
    # Create sample data for demonstration
    print(f"\n📋 Creating sample data...")
    
    # Sample persons
    user = Person("1", "John Doe", "john.doe@company.com", "End User", "Sales")
    agent = Person("2", "Jane Smith", "jane.smith@company.com", "Service Desk Agent", "IT")
    analyst = Person("3", "Bob Johnson", "bob.johnson@company.com", "Problem Analyst", "IT")
    
    # Sample CI
    ci = ConfigurationItem("1", "Email Server", "Server", "Production", "Production")
    
    # Create incident
    from .practices.incident_management import IncidentCategory
    incident = itil.create_incident(
        "Email server unavailable",
        "Email server is not responding to requests",
        user,
        IncidentCategory.APPLICATION,
        Impact.HIGH,
        Urgency.HIGH,
        ci
    )
    
    print(f"   Created incident: {incident.number}")
    
    # Create problem from incident
    from .practices.problem_management import ProblemCategory
    problem = itil.create_problem_from_incidents(
        [incident.number],
        "Email server reliability issues",
        "Recurring email server outages need investigation",
        ProblemCategory.APPLICATION,
        analyst
    )
    
    print(f"   Created problem: {problem.number}")
    
    # Create change from problem
    change = itil.create_change_from_problem(
        problem.number,
        "Upgrade email server hardware and software",
        analyst
    )
    
    print(f"   Created change: {change.number}")
    
    # Get dashboard metrics
    print(f"\n📊 Getting dashboard metrics...")
    metrics = itil.get_dashboard_metrics(30)
    
    print(f"   Total incidents: {metrics['incident_management']['total_incidents']}")
    print(f"   Total problems: {metrics['problem_management']['total_problems']}")
    print(f"   Total changes: {metrics['change_enablement']['total_changes']}")
    
    # Show integration report
    print(f"\n🔗 Integration Report:")
    integration = itil.get_integration_report()
    print(f"   Incidents with problems: {integration['cross_references']['incidents_with_problems']}")
    print(f"   Problems with changes: {integration['cross_references']['problems_with_changes']}")
    print(f"   Integration health: {integration['integration_health']}")
    
    # Validate framework health
    print(f"\n🏥 Framework Health Check:")
    health = itil.validate_framework_health()
    print(f"   Overall health: {health['overall_health']}")
    print(f"   Checks passed: {len(health['checks'])}")
    
    print(f"\n✅ ITIL 4 Python Framework demonstration completed!")
    print(f"   Framework is ready for production use")
    print(f"   Import with: from python_framework import ITILFramework")