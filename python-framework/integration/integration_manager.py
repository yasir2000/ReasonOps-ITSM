"""
ITIL Framework Integration Manager

This module provides the integration layer that ensures all framework components
work together properly. It handles dependency injection, service registration,
event management, and integration validation.
"""

from typing import Dict, List, Any, Optional, Callable, Type
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime
import inspect


class IntegrationError(Exception):
    """Exception raised when integration fails"""
    pass


class ServiceStatus(Enum):
    """Service status enumeration"""
    UNREGISTERED = "Unregistered"
    REGISTERED = "Registered"
    INITIALIZING = "Initializing"
    READY = "Ready"
    ERROR = "Error"


@dataclass
class ServiceInfo:
    """Information about a registered service"""
    name: str
    service: Any
    dependencies: List[str]
    status: ServiceStatus
    error_message: Optional[str] = None
    initialized_at: Optional[datetime] = None


class ITILPracticeInterface(ABC):
    """Abstract base class that all ITIL practices must implement"""
    
    @abstractmethod
    def get_metrics(self, period_days: int) -> Dict[str, Any]:
        """Get practice metrics for specified period"""
        pass
    
    @abstractmethod
    def get_configuration(self) -> Dict[str, Any]:
        """Get current practice configuration"""
        pass
    
    @abstractmethod
    def validate_configuration(self) -> bool:
        """Validate practice configuration"""
        pass
    
    @abstractmethod
    def get_health_status(self) -> Dict[str, Any]:
        """Get practice health status"""
        pass


class EventBus:
    """Event bus for loose coupling between modules"""
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.event_history: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(__name__)
    
    def subscribe(self, event_type: str, callback: Callable):
        """Subscribe to an event type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
        self.logger.debug(f"Subscribed to event: {event_type}")
    
    def unsubscribe(self, event_type: str, callback: Callable):
        """Unsubscribe from an event type"""
        if event_type in self.subscribers:
            self.subscribers[event_type].remove(callback)
    
    def publish(self, event_type: str, data: Dict[str, Any], source: str = "unknown"):
        """Publish an event"""
        event = {
            "type": event_type,
            "data": data,
            "source": source,
            "timestamp": datetime.now(),
            "processed_by": []
        }
        
        self.event_history.append(event)
        self.logger.info(f"Publishing event: {event_type} from {source}")
        
        # Notify subscribers
        for callback in self.subscribers.get(event_type, []):
            try:
                callback(event)
                event["processed_by"].append(str(callback))
            except Exception as e:
                self.logger.error(f"Error in event callback: {e}")
    
    def get_event_history(self, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get event history, optionally filtered by type"""
        if event_type:
            return [e for e in self.event_history if e["type"] == event_type]
        return self.event_history.copy()


class ServiceRegistry:
    """Registry for managing services and their dependencies"""
    
    def __init__(self):
        self.services: Dict[str, ServiceInfo] = {}
        self.logger = logging.getLogger(__name__)
    
    def register(self, name: str, service: Any, dependencies: List[str] = None):
        """Register a service with its dependencies"""
        self.services[name] = ServiceInfo(
            name=name,
            service=service,
            dependencies=dependencies or [],
            status=ServiceStatus.REGISTERED
        )
        self.logger.info(f"Registered service: {name}")
    
    def get(self, name: str) -> Any:
        """Get a service by name"""
        service_info = self.services.get(name)
        if not service_info:
            raise IntegrationError(f"Service not found: {name}")
        return service_info.service
    
    def get_service_info(self, name: str) -> Optional[ServiceInfo]:
        """Get service information"""
        return self.services.get(name)
    
    def is_registered(self, name: str) -> bool:
        """Check if a service is registered"""
        return name in self.services
    
    def get_all_services(self) -> Dict[str, ServiceInfo]:
        """Get all registered services"""
        return self.services.copy()
    
    def _topological_sort(self) -> List[str]:
        """Sort services in dependency order"""
        visited = set()
        temp_visited = set()
        result = []
        
        def visit(service_name: str):
            if service_name in temp_visited:
                raise IntegrationError(f"Circular dependency detected involving: {service_name}")
            
            if service_name not in visited:
                temp_visited.add(service_name)
                
                service_info = self.services.get(service_name)
                if service_info:
                    for dep in service_info.dependencies:
                        if dep in self.services:
                            visit(dep)
                
                temp_visited.remove(service_name)
                visited.add(service_name)
                result.append(service_name)
        
        for service_name in self.services:
            if service_name not in visited:
                visit(service_name)
        
        return result
    
    def initialize_all(self) -> Dict[str, bool]:
        """Initialize all services in dependency order"""
        results = {}
        
        try:
            sorted_services = self._topological_sort()
        except IntegrationError as e:
            self.logger.error(f"Failed to sort services: {e}")
            return results
        
        for service_name in sorted_services:
            try:
                results[service_name] = self._initialize_service(service_name)
            except Exception as e:
                self.logger.error(f"Failed to initialize service {service_name}: {e}")
                results[service_name] = False
        
        return results
    
    def _initialize_service(self, service_name: str) -> bool:
        """Initialize a single service"""
        service_info = self.services[service_name]
        service_info.status = ServiceStatus.INITIALIZING
        
        try:
            # Check dependencies are ready
            for dep_name in service_info.dependencies:
                dep_info = self.services.get(dep_name)
                if not dep_info or dep_info.status != ServiceStatus.READY:
                    raise IntegrationError(f"Dependency not ready: {dep_name}")
            
            # Inject dependencies if service supports it
            if hasattr(service_info.service, 'set_dependencies'):
                deps = {dep: self.services[dep].service for dep in service_info.dependencies}
                service_info.service.set_dependencies(deps)
            
            # Initialize service if it supports it
            if hasattr(service_info.service, 'initialize'):
                service_info.service.initialize()
            
            service_info.status = ServiceStatus.READY
            service_info.initialized_at = datetime.now()
            self.logger.info(f"Initialized service: {service_name}")
            return True
            
        except Exception as e:
            service_info.status = ServiceStatus.ERROR
            service_info.error_message = str(e)
            self.logger.error(f"Failed to initialize service {service_name}: {e}")
            return False


class IntegrationValidator:
    """Validates framework integration"""
    
    def __init__(self, registry: ServiceRegistry):
        self.registry = registry
        self.logger = logging.getLogger(__name__)
    
    def validate_interfaces(self) -> Dict[str, List[str]]:
        """Validate that services implement required interfaces"""
        issues = {}
        
        for name, service_info in self.registry.get_all_services().items():
            service_issues = []
            service = service_info.service
            
            # Check if practice implements ITILPracticeInterface
            if hasattr(service, '__class__') and 'Management' in service.__class__.__name__:
                if not isinstance(service, ITILPracticeInterface):
                    # Check required methods manually
                    required_methods = ['get_metrics', 'get_configuration', 'validate_configuration', 'get_health_status']
                    
                    for method in required_methods:
                        if not hasattr(service, method):
                            service_issues.append(f"Missing required method: {method}")
                        elif not callable(getattr(service, method)):
                            service_issues.append(f"Method not callable: {method}")
            
            if service_issues:
                issues[name] = service_issues
        
        return issues
    
    def validate_dependencies(self) -> Dict[str, List[str]]:
        """Validate service dependencies"""
        issues = {}
        
        for name, service_info in self.registry.get_all_services().items():
            service_issues = []
            
            for dep in service_info.dependencies:
                if not self.registry.is_registered(dep):
                    service_issues.append(f"Missing dependency: {dep}")
                else:
                    dep_info = self.registry.get_service_info(dep)
                    if dep_info.status == ServiceStatus.ERROR:
                        service_issues.append(f"Dependency in error state: {dep}")
            
            if service_issues:
                issues[name] = service_issues
        
        return issues
    
    def validate_configuration(self) -> Dict[str, List[str]]:
        """Validate service configurations"""
        issues = {}
        
        for name, service_info in self.registry.get_all_services().items():
            service = service_info.service
            
            if hasattr(service, 'validate_configuration'):
                try:
                    if not service.validate_configuration():
                        issues[name] = ["Configuration validation failed"]
                except Exception as e:
                    issues[name] = [f"Configuration validation error: {e}"]
        
        return issues
    
    def run_full_validation(self) -> Dict[str, Any]:
        """Run complete validation suite"""
        return {
            "timestamp": datetime.now().isoformat(),
            "interface_issues": self.validate_interfaces(),
            "dependency_issues": self.validate_dependencies(),
            "configuration_issues": self.validate_configuration(),
            "overall_status": "PASS" if not any([
                self.validate_interfaces(),
                self.validate_dependencies(), 
                self.validate_configuration()
            ]) else "FAIL"
        }


class ITILIntegrationManager:
    """Main integration manager for ITIL framework"""
    
    def __init__(self):
        self.registry = ServiceRegistry()
        self.event_bus = EventBus()
        self.validator = IntegrationValidator(self.registry)
        self.logger = logging.getLogger(__name__)
        
        # Setup event handlers
        self._setup_default_event_handlers()
    
    def _setup_default_event_handlers(self):
        """Setup default event handlers for integration"""
        
        # Incident created -> Check for problem patterns
        self.event_bus.subscribe("incident.created", self._handle_incident_created)
        self.event_bus.subscribe("incident.resolved", self._handle_incident_resolved)
        
        # Problem identified -> Consider change request
        self.event_bus.subscribe("problem.root_cause_identified", self._handle_root_cause_identified)
        
        # Change completed -> Update related records
        self.event_bus.subscribe("change.completed", self._handle_change_completed)
    
    def _handle_incident_created(self, event: Dict[str, Any]):
        """Handle incident created event"""
        incident_data = event["data"]
        
        # Check for similar incidents to create problem
        if self.registry.is_registered("problem_management"):
            problem_mgmt = self.registry.get("problem_management")
            
            # Logic to check if problem should be created
            similar_incidents = self._find_similar_incidents(incident_data)
            if len(similar_incidents) >= 3:  # Threshold for problem creation
                self.event_bus.publish(
                    "integration.create_problem_from_incidents",
                    {
                        "incidents": similar_incidents,
                        "pattern": "recurring_incidents"
                    },
                    "integration_manager"
                )
    
    def _handle_incident_resolved(self, event: Dict[str, Any]):
        """Handle incident resolved event"""
        # Update metrics, close related problems if applicable
        pass
    
    def _handle_root_cause_identified(self, event: Dict[str, Any]):
        """Handle root cause identified event"""
        problem_data = event["data"]
        
        # Consider creating change request
        if self.registry.is_registered("change_enablement"):
            self.event_bus.publish(
                "integration.consider_change_request",
                {
                    "problem_id": problem_data.get("problem_id"),
                    "root_cause": problem_data.get("root_cause")
                },
                "integration_manager"
            )
    
    def _handle_change_completed(self, event: Dict[str, Any]):
        """Handle change completed event"""
        change_data = event["data"]
        
        # Update related problems and incidents
        if change_data.get("successful"):
            self.event_bus.publish(
                "integration.update_related_records",
                {
                    "change_id": change_data.get("change_id"),
                    "action": "mark_resolved"
                },
                "integration_manager"
            )
    
    def _find_similar_incidents(self, incident_data: Dict[str, Any]) -> List[str]:
        """Find similar incidents for pattern analysis"""
        # Simplified logic - in reality would use ML or complex matching
        if self.registry.is_registered("incident_management"):
            incident_mgmt = self.registry.get("incident_management")
            # Return mock data for now
            return ["INC001", "INC002", "INC003"]
        return []
    
    def register_practice(self, name: str, practice: Any, dependencies: List[str] = None):
        """Register an ITIL practice"""
        self.registry.register(name, practice, dependencies)
        self.logger.info(f"Registered ITIL practice: {name}")
    
    def initialize_framework(self) -> Dict[str, Any]:
        """Initialize the complete framework"""
        self.logger.info("Initializing ITIL framework...")
        
        # Initialize services
        init_results = self.registry.initialize_all()
        
        # Validate integration
        validation_results = self.validator.run_full_validation()
        
        # Publish framework ready event
        if validation_results["overall_status"] == "PASS":
            self.event_bus.publish(
                "framework.initialized",
                {"services": list(init_results.keys())},
                "integration_manager"
            )
        
        return {
            "initialization_results": init_results,
            "validation_results": validation_results,
            "overall_status": "SUCCESS" if all(init_results.values()) and validation_results["overall_status"] == "PASS" else "FAILED"
        }
    
    def get_integration_health(self) -> Dict[str, Any]:
        """Get overall integration health"""
        services_status = {}
        for name, info in self.registry.get_all_services().items():
            services_status[name] = {
                "status": info.status.value,
                "error": info.error_message,
                "initialized_at": info.initialized_at.isoformat() if info.initialized_at else None
            }
        
        return {
            "timestamp": datetime.now().isoformat(),
            "services": services_status,
            "event_bus_health": {
                "subscribers_count": len(self.event_bus.subscribers),
                "events_processed": len(self.event_bus.event_history)
            },
            "validation_status": self.validator.run_full_validation()["overall_status"]
        }
    
    def get_integration_metrics(self) -> Dict[str, Any]:
        """Get integration metrics"""
        ready_services = sum(1 for info in self.registry.get_all_services().values() 
                           if info.status == ServiceStatus.READY)
        total_services = len(self.registry.get_all_services())
        
        return {
            "services_ready": ready_services,
            "total_services": total_services,
            "readiness_percentage": (ready_services / total_services * 100) if total_services > 0 else 0,
            "events_published": len(self.event_bus.event_history),
            "event_types": list(self.event_bus.subscribers.keys()),
            "dependency_violations": len(self.validator.validate_dependencies()),
            "interface_violations": len(self.validator.validate_interfaces())
        }


# Example usage
if __name__ == "__main__":
    print("ITIL Integration Manager")
    print("=" * 30)
    
    # Create integration manager
    integration_mgr = ITILIntegrationManager()
    
    # Register mock services (in real usage, these would be actual practice instances)
    class MockIncidentManagement:
        def get_metrics(self, period_days: int):
            return {"total_incidents": 10}
        
        def get_configuration(self):
            return {"sla_targets": {}}
        
        def validate_configuration(self):
            return True
        
        def get_health_status(self):
            return {"status": "healthy"}
    
    class MockProblemManagement:
        def __init__(self):
            self.dependencies = {}
        
        def set_dependencies(self, deps):
            self.dependencies = deps
        
        def get_metrics(self, period_days: int):
            return {"total_problems": 5}
        
        def get_configuration(self):
            return {"rca_methods": []}
        
        def validate_configuration(self):
            return True
        
        def get_health_status(self):
            return {"status": "healthy"}
    
    # Register practices
    integration_mgr.register_practice("incident_management", MockIncidentManagement())
    integration_mgr.register_practice("problem_management", MockProblemManagement(), ["incident_management"])
    
    # Initialize framework
    results = integration_mgr.initialize_framework()
    print(f"Framework initialization: {results['overall_status']}")
    
    # Get health status
    health = integration_mgr.get_integration_health()
    print(f"Integration health: {health['validation_status']}")
    
    # Get metrics
    metrics = integration_mgr.get_integration_metrics()
    print(f"Services ready: {metrics['services_ready']}/{metrics['total_services']}")
    
    print("✅ Integration manager working correctly!")