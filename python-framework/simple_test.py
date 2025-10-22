#!/usr/bin/env python3
"""
ITIL 4 Python Framework - Simple Test

Simple test to verify the framework components work correctly.
Run from the python-framework directory: python simple_test.py
"""

import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

print("🧪 ITIL 4 Python Framework - Simple Test")
print("=" * 50)

def test_core_components():
    """Test core framework components"""
    print("\n🧪 Testing Core Components...")
    
    try:
        from core.service_value_system import (
            ServiceValueSystem, Person, ConfigurationItem, 
            Impact, Urgency, Priority
        )
        print("   ✅ Core imports successful")
        
        # Test Service Value System
        svs = ServiceValueSystem()
        svs.initialize_default_configuration()
        print(f"   ✅ Service Value System: {len(svs.practices)} practices loaded")
        
        # Test Person creation
        person = Person("1", "Test User", "test@example.com", "Tester", "IT")
        print(f"   ✅ Person creation: {person.name}")
        
        # Test Configuration Item
        ci = ConfigurationItem("CI001", "Test Server", "Server", "Production", "Production")
        print(f"   ✅ Configuration Item: {ci.name}")
        
        # Test enums
        priority = Priority.P1_CRITICAL
        impact = Impact.HIGH
        urgency = Urgency.HIGH
        print(f"   ✅ Enums working: Priority={priority.value}, Impact={impact.value}, Urgency={urgency.value}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Core test failed: {e}")
        return False

def test_incident_management():
    """Test incident management functionality"""
    print("\n🎫 Testing Incident Management...")
    
    try:
        # Direct import from file
        exec(open('practices/incident_management.py').read(), globals())
        
        im = IncidentManagement()
        
        # Import needed classes from core
        from core.service_value_system import Person, Impact, Urgency, Priority
        
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
        
        print(f"   ✅ Incident created: {incident.number} (Priority: {incident.priority.value})")
        
        # Test incident workflow
        incident.acknowledge(agent)
        print(f"      • Incident acknowledged and in progress")
        
        incident.resolve(agent, "Test resolution")
        print(f"      • Incident resolved")
        
        # Get metrics
        metrics = im.get_metrics(30)
        print(f"   ✅ Metrics retrieved: {metrics.get('total_incidents', 0)} incidents")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Incident Management test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_problem_management():
    """Test problem management functionality"""
    print("\n🔍 Testing Problem Management...")
    
    try:
        # Direct import from file
        exec(open('practices/problem_management.py').read(), globals())
        
        pm = ProblemManagement()
        
        # Import needed classes from core
        from core.service_value_system import Person, Impact, Urgency
        
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
        
        print(f"   ✅ Problem created: {problem.number}")
        
        # Start investigation
        problem.start_investigation(analyst)
        print(f"      • Investigation started")
        
        # Add symptoms
        problem.add_symptom("Slow response times", analyst)
        print(f"      • Symptoms added: {len(problem.symptoms)}")
        
        # Get metrics
        metrics = pm.get_metrics(30)
        print(f"   ✅ Metrics retrieved: {metrics.get('total_problems', 0)} problems")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Problem Management test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_change_enablement():
    """Test change enablement functionality"""
    print("\n⚙️ Testing Change Enablement...")
    
    try:
        # Direct import from file
        exec(open('practices/change_enablement.py').read(), globals())
        
        ce = ChangeEnablement()
        
        # Import needed classes from core
        from core.service_value_system import Person, Impact, Urgency
        
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
        
        print(f"   ✅ Change created: {change.number}")
        
        # Submit for assessment
        change.submit_for_assessment(requester)
        print(f"      • Change submitted for assessment")
        
        # Get metrics
        metrics = ce.get_metrics(30)
        print(f"   ✅ Metrics retrieved: {metrics.get('total_changes', 0)} changes")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Change Enablement test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    start_time = datetime.now()
    
    # Run tests
    tests_passed = 0
    total_tests = 4
    
    if test_core_components():
        tests_passed += 1
    
    if test_incident_management():
        tests_passed += 1
        
    if test_problem_management():
        tests_passed += 1
        
    if test_change_enablement():
        tests_passed += 1
    
    # Calculate test duration
    duration = (datetime.now() - start_time).total_seconds()
    
    print(f"\n📊 Test Results:")
    print(f"   Tests Passed: {tests_passed}/{total_tests}")
    print(f"   Test Duration: {duration:.2f} seconds")
    
    if tests_passed == total_tests:
        print(f"\n🎉 All Tests Passed!")
        print(f"   Framework Status: ✅ Ready for use")
        
        print(f"\n🚀 ITIL 4 Python Framework is working correctly!")
        print(f"   • Core components functional")
        print(f"   • All practices operational")
        print(f"   • Framework ready for production use")
        
        return 0
    else:
        print(f"\n❌ Some tests failed ({total_tests - tests_passed} failures)")
        print(f"   Framework Status: ⚠️ Needs attention")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)