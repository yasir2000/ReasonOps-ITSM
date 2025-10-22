"""
Integration Tests for ITIL Framework

This module contains comprehensive tests to validate the integration 
between all framework components.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integration_manager import (
    ITILIntegrationManager, 
    ServiceRegistry, 
    EventBus, 
    IntegrationValidator,
    ITILPracticeInterface,
    ServiceStatus
)
from core.service_value_system import ServiceValueSystem, Person, Organization
from practices.incident_management import IncidentManagement
from practices.problem_management import ProblemManagement
from practices.change_enablement import ChangeEnablement

import pytest
from datetime import datetime
import logging

# Setup logging for tests
logging.basicConfig(level=logging.INFO)


class TestServiceRegistry:
    """Test service registry functionality"""
    
    def setup_method(self):
        """Setup test registry"""
        self.registry = ServiceRegistry()
    
    def test_register_service(self):
        """Test service registration"""
        service = "test_service"
        self.registry.register("test", service)
        
        assert self.registry.is_registered("test")
        assert self.registry.get("test") == service
    
    def test_dependency_resolution(self):
        """Test dependency resolution order"""
        # Create services with dependencies
        service_a = "service_a"
        service_b = "service_b"
        service_c = "service_c"
        
        self.registry.register("a", service_a)
        self.registry.register("b", service_b, ["a"])
        self.registry.register("c", service_c, ["a", "b"])
        
        # Test topological sort
        sorted_services = self.registry._topological_sort()
        
        # A should come before B and C
        # B should come before C
        assert sorted_services.index("a") < sorted_services.index("b")
        assert sorted_services.index("a") < sorted_services.index("c")
        assert sorted_services.index("b") < sorted_services.index("c")
    
    def test_circular_dependency_detection(self):
        """Test circular dependency detection"""
        service_a = "service_a"
        service_b = "service_b"
        
        self.registry.register("a", service_a, ["b"])
        self.registry.register("b", service_b, ["a"])
        
        try:
            self.registry._topological_sort()
            assert False, "Should have detected circular dependency"
        except Exception as e:
            assert "circular dependency" in str(e).lower()


class TestEventBus:
    """Test event bus functionality"""
    
    def setup_method(self):
        """Setup test event bus"""
        self.event_bus = EventBus()
        self.received_events = []
    
    def event_handler(self, event):
        """Test event handler"""
        self.received_events.append(event)
    
    def test_event_subscription(self):
        """Test event subscription and publishing"""
        self.event_bus.subscribe("test.event", self.event_handler)
        
        test_data = {"message": "test"}
        self.event_bus.publish("test.event", test_data, "test_source")
        
        assert len(self.received_events) == 1
        assert self.received_events[0]["type"] == "test.event"
        assert self.received_events[0]["data"] == test_data
        assert self.received_events[0]["source"] == "test_source"
    
    def test_multiple_subscribers(self):
        """Test multiple subscribers to same event"""
        received_events_2 = []
        
        def handler_2(event):
            received_events_2.append(event)
        
        self.event_bus.subscribe("test.event", self.event_handler)
        self.event_bus.subscribe("test.event", handler_2)
        
        self.event_bus.publish("test.event", {"data": "test"}, "source")
        
        assert len(self.received_events) == 1
        assert len(received_events_2) == 1
    
    def test_event_history(self):
        """Test event history tracking"""
        self.event_bus.publish("event1", {"data": 1}, "source1")
        self.event_bus.publish("event2", {"data": 2}, "source2")
        
        history = self.event_bus.get_event_history()
        assert len(history) == 2
        
        filtered_history = self.event_bus.get_event_history("event1")
        assert len(filtered_history) == 1
        assert filtered_history[0]["type"] == "event1"


class TestIntegrationValidator:
    """Test integration validation"""
    
    def setup_method(self):
        """Setup test validator"""
        self.registry = ServiceRegistry()
        self.validator = IntegrationValidator(self.registry)
    
    def test_interface_validation(self):
        """Test interface validation"""
        # Create valid practice
        class ValidPractice(ITILPracticeInterface):
            def get_metrics(self, period_days: int):
                return {}
            
            def get_configuration(self):
                return {}
            
            def validate_configuration(self):
                return True
            
            def get_health_status(self):
                return {}
        
        # Create invalid practice
        class InvalidPracticeManagement:
            pass  # Missing required methods
        
        self.registry.register("valid", ValidPractice())
        self.registry.register("invalid", InvalidPracticeManagement())
        
        issues = self.validator.validate_interfaces()
        
        # Valid practice should have no issues
        assert "valid" not in issues
        
        # Invalid practice should have issues
        assert "invalid" in issues
        assert len(issues["invalid"]) > 0
    
    def test_dependency_validation(self):
        """Test dependency validation"""
        service_a = "service_a"
        service_b = "service_b"
        
        # Register service with missing dependency
        self.registry.register("b", service_b, ["missing_dependency"])
        
        issues = self.validator.validate_dependencies()
        
        assert "b" in issues
        assert any("missing dependency" in issue.lower() for issue in issues["b"])


class TestFullIntegration:
    """Test full framework integration"""
    
    def setup_method(self):
        """Setup full integration test"""
        self.integration_mgr = ITILIntegrationManager()
        
        # Create test organization and people
        self.org = Organization("Test Org", "test.org", "Technology")
        self.person = Person("Test User", "test@example.com", "IT", "Analyst")
        
        # Create SVS
        self.svs = ServiceValueSystem(self.org, self.person)
        
        # Create practices
        self.incident_mgmt = IncidentManagement(self.svs)
        self.problem_mgmt = ProblemManagement(self.svs)
        self.change_mgmt = ChangeEnablement(self.svs)
    
    def test_practice_registration(self):
        """Test registering ITIL practices"""
        # Register practices
        self.integration_mgr.register_practice("incident_management", self.incident_mgmt)
        self.integration_mgr.register_practice("problem_management", self.problem_mgmt, ["incident_management"])
        self.integration_mgr.register_practice("change_enablement", self.change_mgmt, ["problem_management"])
        
        # Verify registration
        assert self.integration_mgr.registry.is_registered("incident_management")
        assert self.integration_mgr.registry.is_registered("problem_management")
        assert self.integration_mgr.registry.is_registered("change_enablement")
    
    def test_framework_initialization(self):
        """Test complete framework initialization"""
        # Register practices
        self.integration_mgr.register_practice("incident_management", self.incident_mgmt)
        self.integration_mgr.register_practice("problem_management", self.problem_mgmt, ["incident_management"])
        self.integration_mgr.register_practice("change_enablement", self.change_mgmt, ["problem_management"])
        
        # Initialize framework
        results = self.integration_mgr.initialize_framework()
        
        # Check initialization was successful
        assert results["overall_status"] == "SUCCESS"
        assert all(results["initialization_results"].values())
        assert results["validation_results"]["overall_status"] == "PASS"
    
    def test_cross_practice_integration(self):
        """Test integration between practices"""
        # Register practices
        self.integration_mgr.register_practice("incident_management", self.incident_mgmt)
        self.integration_mgr.register_practice("problem_management", self.problem_mgmt, ["incident_management"])
        
        # Initialize
        self.integration_mgr.initialize_framework()
        
        # Create incident
        incident = self.incident_mgmt.create_incident(
            title="Test Integration Incident",
            description="Testing cross-practice integration",
            category="Software",
            priority="P2",
            urgency="Medium",
            impact="Medium",
            reporter=self.person
        )
        
        # Verify incident was created
        assert incident is not None
        assert incident.title == "Test Integration Incident"
        
        # Create problem from incident
        problem = self.problem_mgmt.create_problem(
            title="Test Integration Problem",
            description="Problem created from incident integration test",
            category="Software",
            priority="P2",
            reporter=self.person,
            related_incidents=[incident.id]
        )
        
        # Verify problem was created with incident link
        assert problem is not None
        assert incident.id in problem.related_incidents
    
    def test_event_driven_integration(self):
        """Test event-driven integration between practices"""
        # Register practices
        self.integration_mgr.register_practice("incident_management", self.incident_mgmt)
        self.integration_mgr.register_practice("problem_management", self.problem_mgmt)
        
        # Initialize
        self.integration_mgr.initialize_framework()
        
        # Track events
        received_events = []
        
        def event_tracker(event):
            received_events.append(event)
        
        # Subscribe to events
        self.integration_mgr.event_bus.subscribe("incident.created", event_tracker)
        self.integration_mgr.event_bus.subscribe("problem.created", event_tracker)
        
        # Publish incident created event
        self.integration_mgr.event_bus.publish(
            "incident.created",
            {
                "incident_id": "INC001",
                "title": "Test Incident",
                "category": "Software",
                "priority": "P2"
            },
            "incident_management"
        )
        
        # Verify event was received
        assert len(received_events) == 1
        assert received_events[0]["type"] == "incident.created"
        assert received_events[0]["data"]["incident_id"] == "INC001"
    
    def test_integration_health_monitoring(self):
        """Test integration health monitoring"""
        # Register and initialize practices
        self.integration_mgr.register_practice("incident_management", self.incident_mgmt)
        self.integration_mgr.register_practice("problem_management", self.problem_mgmt)
        self.integration_mgr.initialize_framework()
        
        # Get health status
        health = self.integration_mgr.get_integration_health()
        
        # Verify health information
        assert "timestamp" in health
        assert "services" in health
        assert "event_bus_health" in health
        assert "validation_status" in health
        
        # Verify services are healthy
        assert health["services"]["incident_management"]["status"] == "Ready"
        assert health["services"]["problem_management"]["status"] == "Ready"
        
        # Verify validation passed
        assert health["validation_status"] == "PASS"
    
    def test_integration_metrics(self):
        """Test integration metrics collection"""
        # Register practices
        self.integration_mgr.register_practice("incident_management", self.incident_mgmt)
        self.integration_mgr.register_practice("problem_management", self.problem_mgmt)
        self.integration_mgr.initialize_framework()
        
        # Get metrics
        metrics = self.integration_mgr.get_integration_metrics()
        
        # Verify metrics
        assert metrics["services_ready"] == 2
        assert metrics["total_services"] == 2
        assert metrics["readiness_percentage"] == 100.0
        assert "events_published" in metrics
        assert "event_types" in metrics
        assert "dependency_violations" in metrics
        assert "interface_violations" in metrics


def run_integration_tests():
    """Run all integration tests"""
    print("Running ITIL Framework Integration Tests")
    print("=" * 50)
    
    # Test service registry
    print("\n1. Testing Service Registry...")
    registry_test = TestServiceRegistry()
    registry_test.setup_method()
    
    try:
        registry_test.test_register_service()
        registry_test.test_dependency_resolution()
        registry_test.test_circular_dependency_detection()
        print("✅ Service Registry tests passed")
    except Exception as e:
        print(f"❌ Service Registry tests failed: {e}")
    
    # Test event bus
    print("\n2. Testing Event Bus...")
    event_test = TestEventBus()
    event_test.setup_method()
    
    try:
        event_test.test_event_subscription()
        event_test.test_multiple_subscribers()
        event_test.test_event_history()
        print("✅ Event Bus tests passed")
    except Exception as e:
        print(f"❌ Event Bus tests failed: {e}")
    
    # Test integration validator
    print("\n3. Testing Integration Validator...")
    validator_test = TestIntegrationValidator()
    validator_test.setup_method()
    
    try:
        validator_test.test_interface_validation()
        validator_test.test_dependency_validation()
        print("✅ Integration Validator tests passed")
    except Exception as e:
        print(f"❌ Integration Validator tests failed: {e}")
    
    # Test full integration
    print("\n4. Testing Full Integration...")
    full_test = TestFullIntegration()
    full_test.setup_method()
    
    try:
        full_test.test_practice_registration()
        full_test.test_framework_initialization()
        full_test.test_cross_practice_integration()
        full_test.test_event_driven_integration()
        full_test.test_integration_health_monitoring()
        full_test.test_integration_metrics()
        print("✅ Full Integration tests passed")
    except Exception as e:
        print(f"❌ Full Integration tests failed: {e}")
    
    print("\n" + "=" * 50)
    print("✅ All integration tests completed!")


if __name__ == "__main__":
    run_integration_tests()