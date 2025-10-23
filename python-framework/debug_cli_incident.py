#!/usr/bin/env python3

"""Debug CLI incident creation exactly as it does"""

import sys
import traceback
import argparse

# Set up mock args like CLI would
class MockArgs:
    def __init__(self):
        self.title = "Website Performance Issues"
        self.description = "Users reporting slow page load times"
        self.caller = None
        self.category = "performance"
        self.impact = "high"
        self.urgency = "high"
        self.json = False

def test_cli_incident_creation():
    """Test creating an incident exactly like CLI does"""
    try:
        args = MockArgs()
        
        print("1. Testing imports...")
        from practices.incident_management import IncidentManagement, IncidentCategory
        from core.service_value_system import Person, Impact, Urgency
        print("✓ Imports successful")
        
        print("2. Creating IncidentManagement instance...")
        incident_mgmt = IncidentManagement()
        print("✓ IncidentManagement instance created")
        
        print("3. Setting up enum mappings...")
        # Map string values to enums
        impact_map = {"low": Impact.LOW, "medium": Impact.MEDIUM, "high": Impact.HIGH, "critical": Impact.CRITICAL}
        urgency_map = {"low": Urgency.LOW, "medium": Urgency.MEDIUM, "high": Urgency.HIGH, "critical": Urgency.CRITICAL}
        
        impact = impact_map.get(args.impact, Impact.MEDIUM) if args.impact else Impact.MEDIUM
        urgency = urgency_map.get(args.urgency, Urgency.MEDIUM) if args.urgency else Urgency.MEDIUM
        print(f"✓ Impact: {impact}, Urgency: {urgency}")
        
        print("4. Creating caller...")
        # Create caller - use provided or default
        if args.caller:
            caller = Person("user1", args.caller, args.caller, "End User", "IT")
        else:
            caller = Person("system", "System", "system@company.com", "System", "IT")
        print(f"✓ Caller: {caller.name}")
        
        print("5. Setting up category mapping...")
        # Map category string to enum
        category_map = {
            "hardware": IncidentCategory.HARDWARE,
            "software": IncidentCategory.SOFTWARE,
            "network": IncidentCategory.NETWORK,
            "security": IncidentCategory.SECURITY,
            "service": IncidentCategory.SERVICE,
            "infrastructure": IncidentCategory.INFRASTRUCTURE,
            "application": IncidentCategory.APPLICATION,
            "database": IncidentCategory.DATABASE,
            "performance": IncidentCategory.APPLICATION  # Map performance to application
        }
        
        category = category_map.get(args.category.lower() if args.category else "service", IncidentCategory.SERVICE)
        print(f"✓ Category: {category}")
        
        print("6. Creating incident...")
        incident = incident_mgmt.create_incident(
            short_description=args.title,
            description=args.description or args.title,
            caller=caller,
            category=category,
            impact=impact,
            urgency=urgency
        )
        print(f"✓ Incident created: {incident.number}")
        
        print("7. Building result...")
        result = {
            "incident_id": incident.number,
            "title": incident.short_description,
            "status": incident.state.value,
            "priority": incident.priority.value,
            "created": incident.opened_at.isoformat()
        }
        
        if args.json:
            import json
            print(json.dumps(result, indent=2))
        else:
            print(f"✓ Created incident: {incident.number}")
            print(f"  Title: {incident.short_description}")
            print(f"  Priority: {incident.priority.value}")
            print(f"  Status: {incident.state.value}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        print(f"✗ Error type: {type(e)}")
        print("\nFull traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_cli_incident_creation()
    sys.exit(0 if success else 1)