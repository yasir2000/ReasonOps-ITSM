"""
ITIL Framework Integration Module

This module provides the integration layer for the ITIL framework,
ensuring proper dependency management, event handling, and validation
across all framework components.
"""

from .integration_manager import (
    ITILIntegrationManager,
    ServiceRegistry,
    EventBus,
    IntegrationValidator,
    ITILPracticeInterface,
    ServiceStatus,
    ServiceInfo,
    IntegrationError
)

__all__ = [
    'ITILIntegrationManager',
    'ServiceRegistry', 
    'EventBus',
    'IntegrationValidator',
    'ITILPracticeInterface',
    'ServiceStatus',
    'ServiceInfo',
    'IntegrationError'
]

__version__ = '1.0.0'
__author__ = 'ITIL Framework Team'