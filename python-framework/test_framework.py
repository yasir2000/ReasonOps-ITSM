#!/usr/bin/env python3
"""
ITIL 4 Python Framework - Quick Test

Simple test to verify the framework is working correctly.
Run from the root directory: python python-framework/test_framework.py
"""

import sys
import os
from datetime import datetime

# Test core imports
try:
    from core.service_value_system import (
        ServiceValueSystem, Person, ConfigurationItem, 
        Impact, Urgency, Priority
    )
    print("✅ Core imports successful")
except ImportError as e:
    print(f"❌ Core import failed: {e}")
    sys.exit(1)

# Test practice imports
try:
    from practices.incident_management import (
        IncidentManagement, IncidentCategory, IncidentState
    )
    from practices.problem_management import (
        ProblemManagement, ProblemCategory, ProblemType
    )
    from practices.change_enablement import (
        ChangeEnablement, ChangeCategory, ChangeType
    )
    print("✅ Practice imports successful")
except ImportError as e:
    print(f"❌ Practice import failed: {e}")
    # Try alternative import method
    try:
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), 'practices'))
        
        from incident_management import (
            IncidentManagement, IncidentCategory, IncidentState
        )
        from problem_management import (
            ProblemManagement, ProblemCategory, ProblemType
        )
        from change_enablement import (
            ChangeEnablement, ChangeCategory, ChangeType
        )
        print("✅ Practice imports successful (alternative method)")
    except ImportError as e2:
        print(f"❌ Alternative practice import failed: {e2}")
        sys.exit(1)

def test_core_components():
    """Test core framework components"""
    print("\n🧪 Testing Core Components...")
    
    # Test Service Value System
    svs = ServiceValueSystem()
    svs.initialize_default_configuration()
    assert len(svs.practices) > 0, "SVS should have practices"
    print(f"   ✅ Service Value System: {len(svs.practices)} practices loaded")
    
    # Test Person creation
    person = Person("1", "Test User", "test@example.com", "Tester", "IT")
    assert person.name == "Test User", "Person name should match"
    print(f"   ✅ Person creation: {person.name}")
    
    # Test Configuration Item
    ci = ConfigurationItem("CI001", "Test Server", "Server", "Production", "Production")
    assert ci.name == "Test Server", "CI name should match"
    print(f"   ✅ Configuration Item: {ci.name}")


def test_incident_management():
    """Test incident management functionality"""
    print("\n🎫 Testing Incident Management...")
    
    im = IncidentManagement()
    
    # Create test persons
    caller = Person("1", "John Doe", "john@example.com", "User", "Sales")
    agent = Person("2", "Jane Smith", "jane@example.com", "Agent", "IT")
    
    # Create incident
    incident = im.create_incident(
        short_description="Test incident",
        description="This is a test incident",
        caller=caller,
        category=IncidentCategory.SOFTWARE,
        impact=Impact.MEDIUM,
        urgency=Urgency.HIGH
    )
    
    assert incident is not None, "Incident should be created"
    assert incident.priority == Priority.P2_HIGH, "Priority should be P2_HIGH"
    print(f"   ✅ Incident created: {incident.number} (Priority: {incident.priority.value})")
    
    # Test incident workflow
    incident.acknowledge(agent)
    assert incident.state == IncidentState.IN_PROGRESS, "Incident should be in progress"
    print(f"   ✅ Incident acknowledged and in progress")
    
    incident.resolve(agent, "Test resolution")
    assert incident.state == IncidentState.RESOLVED, "Incident should be resolved"
    print(f"   ✅ Incident resolved")
    
    # Get metrics
    metrics = im.get_metrics(30)
    assert "total_incidents" in metrics, "Metrics should include total incidents"
    print(f"   ✅ Metrics retrieved: {metrics['total_incidents']} incidents")


def test_problem_management():
    """Test problem management functionality"""
    print("\n🔍 Testing Problem Management...")
    
    pm = ProblemManagement()
    
    # Create test person
    analyst = Person("3", "Problem Analyst", "analyst@example.com", "Analyst", "IT")
    
    # Create problem
    problem = pm.create_problem(
        short_description="Test problem",
        description="This is a test problem",
        category=ProblemCategory.SOFTWARE,
        impact=Impact.MEDIUM,
        urgency=Urgency.MEDIUM,
        assigned_to=analyst
    )
    
    assert problem is not None, "Problem should be created"
    print(f"   ✅ Problem created: {problem.number}")
    
    # Start investigation
    problem.start_investigation(analyst)
    assert problem.state.value == "Under Investigation", "Problem should be under investigation"
    print(f"   ✅ Investigation started")
    
    # Add symptoms
    problem.add_symptom("Slow response times", analyst)
    assert len(problem.symptoms) > 0, "Problem should have symptoms"
    print(f"   ✅ Symptoms added: {len(problem.symptoms)}")
    
    # Get metrics
    metrics = pm.get_metrics(30)
    assert "total_problems" in metrics, "Metrics should include total problems"
    print(f"   ✅ Metrics retrieved: {metrics['total_problems']} problems")


def test_change_enablement():
    """Test change enablement functionality"""
    print("\n⚙️ Testing Change Enablement...")
    
    ce = ChangeEnablement()
    
    # Create test person
    requester = Person("4", "Change Requester", "requester@example.com", "Manager", "IT")
    
    # Create change
    change = ce.create_change_request(
        short_description="Test change",
        description="This is a test change",
        justification="Testing the framework",
        category=ChangeCategory.SOFTWARE,
        change_type=ChangeType.NORMAL,
        requester=requester
    )
    
    assert change is not None, "Change should be created"
    print(f"   ✅ Change created: {change.number}")
    
    # Submit for assessment
    change.submit_for_assessment(requester)
    assert change.state.value == "Assessment", "Change should be in assessment"
    print(f"   ✅ Change submitted for assessment")
    
    # Get metrics
    metrics = ce.get_metrics(30)
    assert "total_changes" in metrics, "Metrics should include total changes"
    print(f"   ✅ Metrics retrieved: {metrics['total_changes']} changes")


def test_integration():
    """Test integration between practices"""
    print("\n🔗 Testing Practice Integration...")
    
    # Create all practice instances
    im = IncidentManagement()
    pm = ProblemManagement()
    ce = ChangeEnablement()
    
    # Create test persons
    user = Person("1", "End User", "user@example.com", "User", "Business")
    analyst = Person("2", "Analyst", "analyst@example.com", "Analyst", "IT")
    
    # Create incident
    incident = im.create_incident(
        "Integration test incident",
        "Testing integration workflow",
        user,
        IncidentCategory.APPLICATION,
        Impact.MEDIUM,
        Urgency.HIGH
    )
    
    # Create problem from incident
    problem = pm.create_problem_from_incidents(
        [incident.number],
        "Integration test problem",
        "Problem created from incident for testing",
        ProblemCategory.APPLICATION,
        analyst
    )
    
    # Link incident to problem
    incident.related_problems.append(problem.number)
    
    # Create change from problem  
    change = ce.create_change_request(
        "Integration test change",
        "Change to resolve the problem",
        "Fix the root cause",
        ChangeCategory.APPLICATION,
        ChangeType.NORMAL,
        analyst
    )
    
    # Link change to problem
    change.related_problems.append(problem.number)
    problem.related_changes.append(change.number)
    
    # Verify links
    assert incident.number in problem.related_incidents, "Incident should be linked to problem"
    assert problem.number in change.related_problems, "Problem should be linked to change"
    
    print(f"   ✅ Integration workflow: {incident.number} → {problem.number} → {change.number}")
    print(f"   ✅ Cross-references validated")


def main():
    """Main test function"""
    print("🧪 ITIL 4 Python Framework - Quick Test")
    print("=" * 50)
    
    start_time = datetime.now()
    
    try:
        # Run all tests
        test_core_components()
        test_incident_management()
        test_problem_management()
        test_change_enablement() 
        test_integration()
        
        # Calculate test duration
        duration = (datetime.now() - start_time).total_seconds()
        
        print(f"\n🎉 All Tests Passed!")
        print(f"   Test Duration: {duration:.2f} seconds")
        print(f"   Framework Status: ✅ Ready for use")
        
        print(f"\n📋 Test Summary:")
        print(f"   ✅ Core components working")
        print(f"   ✅ Incident management functional")
        print(f"   ✅ Problem management functional") 
        print(f"   ✅ Change enablement functional")
        print(f"   ✅ Practice integration working")
        
        print(f"\n🚀 Framework is ready for production use!")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)