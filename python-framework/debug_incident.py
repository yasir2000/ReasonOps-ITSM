#!/usr/bin/env python3

"""Debug incident creation"""

import sys
import traceback

def test_incident_creation():
    """Test creating an incident"""
    try:
        print("1. Testing imports...")
        from practices.incident_management import IncidentManagement, IncidentCategory
        from core.service_value_system import Person, Impact, Urgency
        print("✓ Imports successful")
        
        print("2. Creating IncidentManagement instance...")
        incident_mgmt = IncidentManagement()
        print("✓ IncidentManagement instance created")
        
        print("3. Setting up parameters...")
        impact = Impact.HIGH
        urgency = Urgency.HIGH
        print(f"✓ Impact: {impact}, Urgency: {urgency}")
        
        print("4. Creating caller...")
        caller = Person("system", "System", "system@company.com", "System", "IT")
        print(f"✓ Caller created: {caller.name}")
        
        print("5. Creating incident...")
        incident = incident_mgmt.create_incident(
            short_description="Test Website Performance Issues", 
            description="Users reporting slow page load times",
            caller=caller,
            category=IncidentCategory.APPLICATION,
            impact=impact,
            urgency=urgency
        )
        print(f"✓ Incident created: {incident.number}")
        print(f"  Title: {incident.short_description}")
        print(f"  Priority: {incident.priority.value}")
        print(f"  Status: {incident.state.value}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        print("\nFull traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_incident_creation()
    sys.exit(0 if success else 1)