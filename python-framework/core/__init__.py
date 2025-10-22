"""
ITIL 4 Core Module

This module provides the foundational components of the ITIL 4 framework:
- Service Value System
- Guiding Principles
- Service Value Chain
- Governance Framework
- Four Dimensions of Service Management
- Continual Improvement

These core components form the foundation for all ITIL practices.
"""

from .service_value_system import (
    # Enums
    Priority,
    Status,
    Impact,
    Urgency,
    
    # Data Classes
    Person,
    ConfigurationItem,
    
    # Main Classes
    ServiceValueSystem,
    GuidingPrinciples,
    ServiceValueChain,
    GovernanceFramework,
    PracticeRegistry,
    ContinualImprovement,
    ValueStream,
    GovernanceBody,
    ImprovementInitiative,
    ImprovementModel
)

__all__ = [
    # Enums
    'Priority',
    'Status', 
    'Impact',
    'Urgency',
    
    # Data Classes
    'Person',
    'ConfigurationItem',
    
    # Main Classes
    'ServiceValueSystem',
    'GuidingPrinciples',
    'ServiceValueChain',
    'GovernanceFramework',
    'PracticeRegistry',
    'ContinualImprovement',
    'ValueStream',
    'GovernanceBody',
    'ImprovementInitiative',
    'ImprovementModel'
]

# Version information
__version__ = "1.0.0"
__author__ = "ITIL 4 Framework Implementation"
__description__ = "Core components of the ITIL 4 Service Value System"

def create_service_value_system():
    """Factory function to create a fully configured Service Value System"""
    
    # Create and configure the SVS
    svs = ServiceValueSystem()
    
    # Initialize with default configuration
    svs.initialize_default_configuration()
    
    return svs

def get_guiding_principles():
    """Get the ITIL 4 Guiding Principles"""
    principles = GuidingPrinciples()
    return principles.get_all_principles()

def get_service_value_chain_activities():
    """Get all Service Value Chain activities"""
    svc = ServiceValueChain()
    return svc.get_all_activities()

def create_governance_framework():
    """Create a basic governance framework"""
    return GovernanceFramework()

def create_continual_improvement_model():
    """Create the continual improvement model"""
    return ContinualImprovement()

# Framework utilities
class ITILFrameworkUtils:
    """Utility class for ITIL 4 framework operations"""
    
    @staticmethod
    def validate_person(person: Person) -> bool:
        """Validate a Person object"""
        return (person.id and person.name and person.email and 
                person.role and person.department)
    
    @staticmethod
    def validate_configuration_item(ci: ConfigurationItem) -> bool:
        """Validate a Configuration Item object"""
        return (ci.id and ci.name and ci.type and 
                ci.status and ci.environment)
    
    @staticmethod
    def calculate_priority_matrix() -> dict:
        """Get the standard ITIL priority matrix"""
        return {
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
    
    @staticmethod
    def get_framework_overview() -> dict:
        """Get an overview of the ITIL 4 framework components"""
        return {
            "service_value_system": {
                "description": "The ITIL service value system (SVS) describes how all the components and activities of the organization work together as a system to enable value creation",
                "components": [
                    "Guiding Principles",
                    "Governance", 
                    "Service Value Chain",
                    "Practices",
                    "Continual Improvement"
                ]
            },
            "guiding_principles": {
                "description": "Seven high-level guidance principles that guide an organization in all circumstances",
                "count": 7,
                "principles": [
                    "Focus on value",
                    "Start where you are", 
                    "Progress iteratively with feedback",
                    "Collaborate and promote visibility",
                    "Think and work holistically",
                    "Keep it simple and practical",
                    "Optimize and automate"
                ]
            },
            "service_value_chain": {
                "description": "Operating model that outlines key activities required to respond to demand and facilitate value realization",
                "activities": [
                    "Plan",
                    "Improve", 
                    "Engage",
                    "Design & Transition",
                    "Obtain/Build",
                    "Deliver & Support"
                ]
            },
            "practices": {
                "description": "Sets of organizational resources designed for performing work or accomplishing an objective",
                "total_count": 34,
                "categories": {
                    "General Management": 14,
                    "Service Management": 17,
                    "Technical Management": 3
                }
            },
            "four_dimensions": {
                "description": "Four dimensions that organizations should consider for holistic approach to service management",
                "dimensions": [
                    "Organizations and people",
                    "Information and technology",
                    "Partners and suppliers", 
                    "Value streams and processes"
                ]
            }
        }

# Example usage
if __name__ == "__main__":
    print("ITIL 4 Core Module")
    print("=" * 25)
    
    # Create Service Value System
    print("Creating Service Value System...")
    svs = create_service_value_system()
    print(f"✅ Service Value System created with {len(svs.practices)} practices")
    
    # Show Guiding Principles
    print("\nGetting Guiding Principles...")
    principles = get_guiding_principles()
    print(f"✅ {len(principles)} Guiding Principles loaded:")
    for principle in principles:
        print(f"  - {principle['name']}")
    
    # Show Service Value Chain
    print("\nGetting Service Value Chain Activities...")
    activities = get_service_value_chain_activities()
    print(f"✅ {len(activities)} Service Value Chain activities:")
    for activity in activities:
        print(f"  - {activity['name']}")
    
    # Create Governance Framework
    print("\nCreating Governance Framework...")
    governance = create_governance_framework()
    print(f"✅ Governance Framework created")
    
    # Create Continual Improvement
    print("\nCreating Continual Improvement Model...")
    ci = create_continual_improvement_model()
    print(f"✅ Continual Improvement Model created")
    
    # Show framework overview
    print("\nFramework Overview:")
    utils = ITILFrameworkUtils()
    overview = utils.get_framework_overview()
    
    print(f"📋 ITIL 4 Service Value System Components:")
    for component, details in overview.items():
        print(f"  - {component.replace('_', ' ').title()}: {details['description']}")
    
    # Show priority matrix
    print(f"\n🔢 Priority Calculation Matrix:")
    matrix = utils.calculate_priority_matrix()
    print("   Impact →    HIGH      MEDIUM     LOW")
    print("Urgency ↓")
    for urgency in [Urgency.HIGH, Urgency.MEDIUM, Urgency.LOW]:
        row = f"{urgency.value:>8}   "
        for impact in [Impact.HIGH, Impact.MEDIUM, Impact.LOW]:
            priority = matrix.get((impact, urgency), Priority.P4_LOW)
            row += f"{priority.value:>8}  "
        print(row)
    
    print(f"\n✅ ITIL 4 Core Module ready for use!")
    print(f"   Import with: from python_framework.core import *")