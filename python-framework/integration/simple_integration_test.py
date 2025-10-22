"""
Simplified Integration Test for ITIL Framework

This module contains basic integration tests to validate the framework
components work together properly.
"""

import sys
import os

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from integration_manager import (
    ITILIntegrationManager, 
    ServiceRegistry, 
    EventBus, 
    IntegrationValidator,
    ITILPracticeInterface,
    ServiceStatus
)

import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)


def test_service_registry():
    """Test basic service registry functionality"""
    print("Testing Service Registry...")
    
    registry = ServiceRegistry()
    
    # Test service registration
    test_service = "mock_service"
    registry.register("test", test_service)
    
    assert registry.is_registered("test"), "Service registration failed"
    assert registry.get("test") == test_service, "Service retrieval failed"
    
    print("✅ Service Registry test passed")


def test_event_bus():
    """Test event bus functionality"""
    print("Testing Event Bus...")
    
    event_bus = EventBus()
    received_events = []
    
    def event_handler(event):
        received_events.append(event)
    
    # Test event subscription and publishing
    event_bus.subscribe("test.event", event_handler)
    
    test_data = {"message": "test"}
    event_bus.publish("test.event", test_data, "test_source")
    
    assert len(received_events) == 1, "Event not received"
    assert received_events[0]["type"] == "test.event", "Event type mismatch"
    assert received_events[0]["data"] == test_data, "Event data mismatch"
    
    print("✅ Event Bus test passed")


def test_integration_manager():
    """Test integration manager basic functionality"""
    print("Testing Integration Manager...")
    
    # Create mock ITIL practice
    class MockPractice(ITILPracticeInterface):
        def __init__(self, name):
            self.name = name
        
        def get_metrics(self, period_days: int):
            return {"total_items": 5, "resolved_items": 3}
        
        def get_configuration(self):
            return {"setting1": "value1", "setting2": "value2"}
        
        def validate_configuration(self):
            return True
        
        def get_health_status(self):
            return {"status": "healthy", "uptime": "99.9%"}
    
    # Create integration manager
    integration_mgr = ITILIntegrationManager()
    
    # Register mock practices
    practice1 = MockPractice("Practice 1")
    practice2 = MockPractice("Practice 2")
    
    integration_mgr.register_practice("practice1", practice1)
    integration_mgr.register_practice("practice2", practice2, ["practice1"])
    
    # Initialize framework
    results = integration_mgr.initialize_framework()
    
    assert results["overall_status"] == "SUCCESS", f"Framework initialization failed: {results}"
    assert results["validation_results"]["overall_status"] == "PASS", "Validation failed"
    
    # Test health monitoring
    health = integration_mgr.get_integration_health()
    assert health["validation_status"] == "PASS", "Health check failed"
    
    # Test metrics
    metrics = integration_mgr.get_integration_metrics()
    assert metrics["services_ready"] == 2, "Service readiness check failed"
    assert metrics["total_services"] == 2, "Total services count incorrect"
    
    print("✅ Integration Manager test passed")


def test_event_driven_integration():
    """Test event-driven integration patterns"""
    print("Testing Event-Driven Integration...")
    
    integration_mgr = ITILIntegrationManager()
    received_events = []
    
    def integration_event_handler(event):
        received_events.append(event)
    
    # Subscribe to integration events
    integration_mgr.event_bus.subscribe("integration.test", integration_event_handler)
    
    # Publish test events
    test_events = [
        ("integration.test", {"type": "incident_created", "id": "INC001"}),
        ("integration.test", {"type": "problem_identified", "id": "PRB001"}),
        ("integration.test", {"type": "change_approved", "id": "CHG001"})
    ]
    
    for event_type, event_data in test_events:
        integration_mgr.event_bus.publish(event_type, event_data, "test_system")
    
    assert len(received_events) == 3, "Not all events were received"
    
    # Test event history
    history = integration_mgr.event_bus.get_event_history("integration.test")
    assert len(history) == 3, "Event history not properly maintained"
    
    print("✅ Event-Driven Integration test passed")


def test_dependency_resolution():
    """Test dependency resolution and initialization order"""
    print("Testing Dependency Resolution...")
    
    registry = ServiceRegistry()
    
    # Create services with dependencies
    service_a = {"name": "Service A"}
    service_b = {"name": "Service B"}  
    service_c = {"name": "Service C"}
    
    # Register with dependency chain: C depends on B, B depends on A
    registry.register("service_a", service_a)
    registry.register("service_b", service_b, ["service_a"])
    registry.register("service_c", service_c, ["service_b"])
    
    # Test dependency resolution order
    sorted_services = registry._topological_sort()
    
    # Verify order: A should come before B and C, B should come before C
    assert sorted_services.index("service_a") < sorted_services.index("service_b"), "Dependency order incorrect"
    assert sorted_services.index("service_b") < sorted_services.index("service_c"), "Dependency order incorrect"
    
    print("✅ Dependency Resolution test passed")


def run_all_tests():
    """Run all integration tests"""
    print("ITIL Framework Integration Tests")
    print("=" * 40)
    
    tests = [
        test_service_registry,
        test_event_bus,
        test_integration_manager,
        test_event_driven_integration,
        test_dependency_resolution
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__} failed: {e}")
            failed += 1
    
    print(f"\n" + "=" * 40)
    print(f"Tests completed: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All integration tests passed!")
        return True
    else:
        print(f"⚠️  {failed} test(s) failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)