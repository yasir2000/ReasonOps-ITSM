# Framework Module Integration Guide

## 🏗️ Ensuring Proper Code Module Integration

This guide demonstrates best practices for integrating code modules in a framework, using our ITIL 4 Python framework as a practical example.

## 🎯 Key Integration Principles

### 1. **Dependency Hierarchy** 
Establish clear dependency layers to avoid circular imports:

```
Application Layer (main framework)
    ↓
Business Logic Layer (practices)
    ↓  
Core Layer (shared components)
    ↓
Foundation Layer (data models, enums)
```

### 2. **Interface Contracts**
Define clear interfaces that modules must implement:

```python
from abc import ABC, abstractmethod

class ITILPractice(ABC):
    @abstractmethod
    def get_metrics(self, period_days: int) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def validate_configuration(self) -> bool:
        pass
```

### 3. **Factory Pattern**
Use factories to create and configure integrated objects:

```python
class ITILFrameworkFactory:
    @staticmethod
    def create_integrated_framework():
        # Creates framework with all practices properly connected
        framework = ITILFramework()
        framework.setup_integrations()
        return framework
```

### 4. **Event-Driven Communication**
Use events for loose coupling between modules:

```python
class EventBus:
    def __init__(self):
        self.subscribers = {}
    
    def publish(self, event_type: str, data: Dict):
        for callback in self.subscribers.get(event_type, []):
            callback(data)
```

## 🔧 Implementation Strategies

### 1. Import Structure Management

**❌ What NOT to do:**
```python
# Circular import - BAD
# practices/incident_management.py
from practices.problem_management import ProblemManagement

# practices/problem_management.py  
from practices.incident_management import IncidentManagement
```

**✅ What TO do:**
```python
# Use dependency injection or registry pattern
# practices/incident_management.py
class IncidentManagement:
    def __init__(self, integration_registry=None):
        self.integration_registry = integration_registry
    
    def create_related_problem(self, incident_data):
        if self.integration_registry:
            problem_mgmt = self.integration_registry.get('problem_management')
            return problem_mgmt.create_from_incident(incident_data)
```

### 2. Configuration-Driven Integration

**Central Configuration:**
```python
# config/integration_config.py
INTEGRATION_CONFIG = {
    'incident_to_problem': {
        'enabled': True,
        'threshold': 3,  # incidents before creating problem
        'auto_link': True
    },
    'problem_to_change': {
        'enabled': True,
        'require_root_cause': True,
        'auto_approve_low_risk': False
    }
}
```

### 3. Registry Pattern

**Service Registry:**
```python
class ServiceRegistry:
    def __init__(self):
        self._services = {}
        self._dependencies = {}
    
    def register(self, name: str, service: Any, dependencies: List[str] = None):
        self._services[name] = service
        self._dependencies[name] = dependencies or []
    
    def get(self, name: str):
        return self._services.get(name)
    
    def initialize_all(self):
        # Initialize services in dependency order
        for service_name in self._topological_sort():
            service = self._services[service_name]
            self._inject_dependencies(service)
```

### 4. Interface Validation

**Runtime Interface Checking:**
```python
def validate_practice_interface(practice):
    """Validate that a practice implements required interface"""
    required_methods = ['get_metrics', 'create_record', 'search_records']
    
    for method in required_methods:
        if not hasattr(practice, method):
            raise IntegrationError(f"Practice missing required method: {method}")
        
        if not callable(getattr(practice, method)):
            raise IntegrationError(f"Practice method not callable: {method}")
```

## 📋 Integration Checklist

### Before Integration:
- [ ] Define clear module boundaries
- [ ] Establish dependency hierarchy  
- [ ] Create interface contracts
- [ ] Plan error handling strategy
- [ ] Design configuration approach

### During Integration:
- [ ] Implement dependency injection
- [ ] Add integration points
- [ ] Create factory methods
- [ ] Set up event communication
- [ ] Add validation checks

### After Integration:
- [ ] Write integration tests
- [ ] Document dependencies
- [ ] Monitor performance impact
- [ ] Test error scenarios
- [ ] Validate configuration

## 🧪 Testing Integration

### Unit Tests with Mocking:
```python
def test_incident_problem_integration():
    # Mock dependencies
    mock_problem_mgmt = Mock()
    mock_registry = Mock()
    mock_registry.get.return_value = mock_problem_mgmt
    
    # Test integration
    incident_mgmt = IncidentManagement(mock_registry)
    incident_mgmt.create_related_problem(incident_data)
    
    # Verify integration call
    mock_problem_mgmt.create_from_incident.assert_called_once()
```

### Integration Tests:
```python
def test_full_workflow_integration():
    """Test complete incident->problem->change workflow"""
    framework = ITILFramework()
    
    # Create incident
    incident = framework.incident_management.create_incident(...)
    
    # Verify problem creation
    problems = framework.problem_management.find_by_incident(incident.number)
    assert len(problems) > 0
    
    # Verify change creation
    changes = framework.change_enablement.find_by_problem(problems[0].number)
    assert len(changes) > 0
```

## 🚨 Common Integration Pitfalls

### 1. Circular Dependencies
**Problem:** Module A imports Module B, Module B imports Module A
**Solution:** Use dependency injection, events, or registry pattern

### 2. Tight Coupling
**Problem:** Modules know too much about each other's internals
**Solution:** Define clear interfaces and use abstraction

### 3. Inconsistent Error Handling
**Problem:** Different modules handle errors differently
**Solution:** Centralized error handling and consistent exceptions

### 4. Configuration Scattered
**Problem:** Configuration spread across multiple files
**Solution:** Centralized configuration with validation

### 5. Testing Difficulties
**Problem:** Can't test modules in isolation
**Solution:** Dependency injection and mocking

## 📊 Integration Health Monitoring

### Metrics to Track:
- Module loading time
- Memory usage per module
- Inter-module call frequency
- Error rates between modules
- Configuration validation failures

### Health Checks:
```python
class IntegrationHealthChecker:
    def check_module_dependencies(self):
        """Verify all dependencies are available"""
        for module_name, deps in self.dependencies.items():
            for dep in deps:
                if not self.is_module_available(dep):
                    return f"Missing dependency: {dep} for {module_name}"
        return "OK"
    
    def check_interface_compliance(self):
        """Verify all modules implement required interfaces"""
        # Implementation here
        pass
```

This comprehensive approach ensures your framework modules integrate properly while remaining maintainable and testable.