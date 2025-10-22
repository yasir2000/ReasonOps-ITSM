"""
ITIL 4 Event Management Practice Implementation

This module provides comprehensive event management capabilities including:
- Real-time event processing and correlation
- Event-to-incident automation
- Proactive monitoring and alerting
- Event lifecycle management
- Integration with monitoring tools
"""

import sys
import os
from typing import Dict, List, Any, Optional, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import logging
import asyncio
import threading
import queue
import time
import uuid
from collections import defaultdict, deque

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.service_value_system import Priority, Status, Impact, Urgency, ConfigurationItem
from practices.incident_management import IncidentManager, Incident


class EventType(Enum):
    """Types of events that can occur"""
    INFORMATIONAL = "Informational"
    WARNING = "Warning"
    EXCEPTION = "Exception"
    ALERT = "Alert"
    CRITICAL = "Critical"


class EventStatus(Enum):
    """Event processing status"""
    NEW = "New"
    ACKNOWLEDGED = "Acknowledged"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"
    CLOSED = "Closed"
    CORRELATED = "Correlated"
    SUPPRESSED = "Suppressed"


class EventSource(Enum):
    """Sources of events"""
    MONITORING_TOOL = "Monitoring Tool"
    APPLICATION = "Application"
    INFRASTRUCTURE = "Infrastructure"
    NETWORK = "Network"
    SECURITY = "Security"
    USER_REPORT = "User Report"
    AUTOMATED_SCAN = "Automated Scan"
    SYNTHETIC_MONITORING = "Synthetic Monitoring"


@dataclass
class Event:
    """Represents an ITIL event"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    event_type: EventType = EventType.INFORMATIONAL
    status: EventStatus = EventStatus.NEW
    source: EventSource = EventSource.MONITORING_TOOL
    source_system: str = ""
    configuration_item: Optional[str] = None
    service_affected: Optional[str] = None
    priority: Priority = Priority.P4_LOW
    impact: Impact = Impact.LOW
    urgency: Urgency = Urgency.LOW
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    assigned_to: Optional[str] = None
    correlation_id: Optional[str] = None
    parent_event_id: Optional[str] = None
    related_events: List[str] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)
    escalation_level: int = 0
    auto_close_timer: Optional[datetime] = None
    notification_sent: bool = False
    incident_created: Optional[str] = None  # Incident ID if one was created
    
    def __post_init__(self):
        """Post-initialization processing"""
        if not self.title and self.description:
            self.title = self.description[:100] + "..." if len(self.description) > 100 else self.description


@dataclass
class EventRule:
    """Rules for event processing and correlation"""
    id: str
    name: str
    description: str
    conditions: Dict[str, Any]
    actions: List[Dict[str, Any]]
    priority: int = 100
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0


@dataclass
class EventCorrelation:
    """Event correlation definition"""
    id: str
    name: str
    correlation_rules: List[Dict[str, Any]]
    time_window: timedelta
    max_events: int
    suppress_duplicates: bool = True
    create_incident: bool = False
    escalate_after: Optional[timedelta] = None


class EventProcessor:
    """Processes events according to defined rules"""
    
    def __init__(self):
        self.rules: List[EventRule] = []
        self.correlations: List[EventCorrelation] = []
        self.logger = logging.getLogger(__name__)
    
    def add_rule(self, rule: EventRule):
        """Add a processing rule"""
        self.rules.append(rule)
        self.rules.sort(key=lambda r: r.priority)
    
    def add_correlation(self, correlation: EventCorrelation):
        """Add a correlation rule"""
        self.correlations.append(correlation)
    
    async def process_event(self, event: Event) -> List[Dict[str, Any]]:
        """Process an event through all applicable rules"""
        actions_taken = []
        
        # Process through rules
        for rule in self.rules:
            if not rule.enabled:
                continue
                
            if self._rule_matches(event, rule):
                rule_actions = await self._execute_rule_actions(event, rule)
                actions_taken.extend(rule_actions)
                
                # Update rule statistics
                rule.last_triggered = datetime.now()
                rule.trigger_count += 1
        
        return actions_taken
    
    def _rule_matches(self, event: Event, rule: EventRule) -> bool:
        """Check if an event matches rule conditions"""
        conditions = rule.conditions
        
        # Check event type
        if "event_type" in conditions:
            if event.event_type.value not in conditions["event_type"]:
                return False
        
        # Check source
        if "source" in conditions:
            if event.source.value not in conditions["source"]:
                return False
        
        # Check configuration item
        if "configuration_item" in conditions:
            if event.configuration_item not in conditions["configuration_item"]:
                return False
        
        # Check attributes
        if "attributes" in conditions:
            for key, expected_value in conditions["attributes"].items():
                if key not in event.attributes or event.attributes[key] != expected_value:
                    return False
        
        # Check tags
        if "tags" in conditions:
            required_tags = set(conditions["tags"])
            if not required_tags.issubset(event.tags):
                return False
        
        return True
    
    async def _execute_rule_actions(self, event: Event, rule: EventRule) -> List[Dict[str, Any]]:
        """Execute actions defined in a rule"""
        actions_taken = []
        
        for action in rule.actions:
            action_type = action.get("type")
            
            try:
                if action_type == "set_priority":
                    old_priority = event.priority
                    event.priority = Priority(action["value"])
                    actions_taken.append({
                        "action": "priority_changed",
                        "from": old_priority.value,
                        "to": event.priority.value,
                        "rule": rule.name
                    })
                
                elif action_type == "assign":
                    event.assigned_to = action["assignee"]
                    actions_taken.append({
                        "action": "assigned",
                        "assignee": action["assignee"],
                        "rule": rule.name
                    })
                
                elif action_type == "add_tag":
                    event.tags.add(action["tag"])
                    actions_taken.append({
                        "action": "tag_added",
                        "tag": action["tag"],
                        "rule": rule.name
                    })
                
                elif action_type == "correlate":
                    correlation_id = action.get("correlation_id", str(uuid.uuid4()))
                    event.correlation_id = correlation_id
                    actions_taken.append({
                        "action": "correlated",
                        "correlation_id": correlation_id,
                        "rule": rule.name
                    })
                
                elif action_type == "create_incident":
                    # This would integrate with incident management
                    actions_taken.append({
                        "action": "incident_creation_requested",
                        "rule": rule.name
                    })
                
                elif action_type == "suppress":
                    event.status = EventStatus.SUPPRESSED
                    actions_taken.append({
                        "action": "suppressed",
                        "rule": rule.name
                    })
                
                elif action_type == "escalate":
                    event.escalation_level += 1
                    actions_taken.append({
                        "action": "escalated",
                        "level": event.escalation_level,
                        "rule": rule.name
                    })
                
            except Exception as e:
                self.logger.error(f"Error executing action {action_type}: {e}")
                actions_taken.append({
                    "action": "error",
                    "error": str(e),
                    "rule": rule.name
                })
        
        return actions_taken


class EventCorrelationEngine:
    """Correlates related events and manages event relationships"""
    
    def __init__(self):
        self.correlation_windows: Dict[str, deque] = defaultdict(deque)
        self.logger = logging.getLogger(__name__)
    
    async def correlate_event(self, event: Event, correlations: List[EventCorrelation]) -> Optional[Dict[str, Any]]:
        """Correlate an event with existing events"""
        
        for correlation in correlations:
            correlation_result = await self._check_correlation(event, correlation)
            if correlation_result:
                return correlation_result
        
        return None
    
    async def _check_correlation(self, event: Event, correlation: EventCorrelation) -> Optional[Dict[str, Any]]:
        """Check if event matches correlation rules"""
        
        # Get events in time window
        cutoff_time = datetime.now() - correlation.time_window
        window_key = f"{correlation.id}_{event.configuration_item or 'global'}"
        
        # Clean old events from window
        while (self.correlation_windows[window_key] and 
               self.correlation_windows[window_key][0]['timestamp'] < cutoff_time):
            self.correlation_windows[window_key].popleft()
        
        # Add current event to window
        self.correlation_windows[window_key].append({
            'event': event,
            'timestamp': event.created_at
        })
        
        # Check if correlation threshold is met
        if len(self.correlation_windows[window_key]) >= correlation.max_events:
            # Create correlation
            correlation_id = str(uuid.uuid4())
            
            # Mark all events in window as correlated
            correlated_events = []
            for item in self.correlation_windows[window_key]:
                item['event'].correlation_id = correlation_id
                item['event'].status = EventStatus.CORRELATED
                correlated_events.append(item['event'].id)
            
            return {
                "correlation_id": correlation_id,
                "correlation_name": correlation.name,
                "event_count": len(correlated_events),
                "events": correlated_events,
                "time_window": correlation.time_window.total_seconds(),
                "create_incident": correlation.create_incident
            }
        
        return None


class EventManager:
    """Main event management system implementing ITIL Event Management practice"""
    
    def __init__(self, incident_manager: Optional[IncidentManager] = None):
        self.events: Dict[str, Event] = {}
        self.event_queue = queue.Queue()
        self.processor = EventProcessor()
        self.correlation_engine = EventCorrelationEngine()
        self.incident_manager = incident_manager
        self.running = False
        self.worker_thread = None
        self.logger = logging.getLogger(__name__)
        
        # Event statistics
        self.stats = {
            "total_events": 0,
            "events_by_type": defaultdict(int),
            "events_by_source": defaultdict(int),
            "incidents_created": 0,
            "events_correlated": 0,
            "events_suppressed": 0
        }
        
        # Load default rules and correlations
        self._load_default_configuration()
    
    def _load_default_configuration(self):
        """Load default event processing rules and correlations"""
        
        # Default rules
        critical_event_rule = EventRule(
            id="critical_event_escalation",
            name="Critical Event Escalation",
            description="Automatically escalate critical events",
            conditions={"event_type": ["Critical"]},
            actions=[
                {"type": "set_priority", "value": "P1 - Critical"},
                {"type": "assign", "assignee": "critical_team"},
                {"type": "add_tag", "tag": "auto_escalated"}
            ],
            priority=10
        )
        
        duplicate_suppression_rule = EventRule(
            id="duplicate_suppression",
            name="Duplicate Event Suppression",
            description="Suppress duplicate events within 5 minutes",
            conditions={"tags": ["duplicate"]},
            actions=[{"type": "suppress"}],
            priority=5
        )
        
        self.processor.add_rule(critical_event_rule)
        self.processor.add_rule(duplicate_suppression_rule)
        
        # Default correlations
        server_down_correlation = EventCorrelation(
            id="server_down_correlation",
            name="Server Down Correlation",
            correlation_rules=[
                {"attribute": "event_type", "value": "Critical"},
                {"attribute": "source", "value": "Infrastructure"}
            ],
            time_window=timedelta(minutes=5),
            max_events=3,
            create_incident=True,
            escalate_after=timedelta(minutes=15)
        )
        
        self.correlation_engine.correlation_windows[server_down_correlation.id] = deque()
        self.processor.add_correlation(server_down_correlation)
    
    def start_processing(self):
        """Start the event processing worker thread"""
        if not self.running:
            self.running = True
            self.worker_thread = threading.Thread(target=self._process_events_worker)
            self.worker_thread.daemon = True
            self.worker_thread.start()
            self.logger.info("Event processing started")
    
    def stop_processing(self):
        """Stop the event processing worker thread"""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        self.logger.info("Event processing stopped")
    
    def _process_events_worker(self):
        """Worker thread for processing events"""
        while self.running:
            try:
                # Get event from queue with timeout
                event = self.event_queue.get(timeout=1)
                
                # Process the event
                asyncio.run(self._process_single_event(event))
                
                # Mark task as done
                self.event_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error processing event: {e}")
    
    async def _process_single_event(self, event: Event):
        """Process a single event through the complete pipeline"""
        try:
            # Update statistics
            self.stats["total_events"] += 1
            self.stats["events_by_type"][event.event_type.value] += 1
            self.stats["events_by_source"][event.source.value] += 1
            
            # Check for duplicates
            await self._check_for_duplicates(event)
            
            # Process through rules
            actions = await self.processor.process_event(event)
            
            # Check for correlations
            correlation_result = await self.correlation_engine.correlate_event(
                event, self.processor.correlations
            )
            
            if correlation_result:
                self.stats["events_correlated"] += 1
                self.logger.info(f"Event {event.id} correlated: {correlation_result}")
                
                # Create incident if correlation requires it
                if correlation_result.get("create_incident") and self.incident_manager:
                    await self._create_incident_from_correlation(correlation_result)
            
            # Check if individual event should create incident
            elif (event.event_type in [EventType.CRITICAL, EventType.EXCEPTION] and 
                  event.status != EventStatus.SUPPRESSED):
                if self.incident_manager:
                    await self._create_incident_from_event(event)
            
            # Update event timestamp
            event.updated_at = datetime.now()
            
            # Store processed event
            self.events[event.id] = event
            
            self.logger.info(f"Processed event {event.id}: {len(actions)} actions taken")
            
        except Exception as e:
            self.logger.error(f"Error processing event {event.id}: {e}")
            event.status = EventStatus.NEW  # Reset for retry
    
    async def _check_for_duplicates(self, event: Event):
        """Check for duplicate events and mark accordingly"""
        
        # Simple duplicate detection based on title and CI within last 5 minutes
        cutoff_time = datetime.now() - timedelta(minutes=5)
        
        for existing_event in self.events.values():
            if (existing_event.created_at > cutoff_time and
                existing_event.title == event.title and
                existing_event.configuration_item == event.configuration_item and
                existing_event.status not in [EventStatus.CLOSED, EventStatus.RESOLVED]):
                
                event.tags.add("duplicate")
                event.parent_event_id = existing_event.id
                existing_event.related_events.append(event.id)
                break
    
    async def _create_incident_from_event(self, event: Event):
        """Create an incident from a single critical event"""
        try:
            incident_data = {
                "title": f"Incident from Event: {event.title}",
                "description": f"Automatically created from event {event.id}\n\n{event.description}",
                "priority": event.priority.value,
                "impact": event.impact.value,
                "urgency": event.urgency.value,
                "category": "Technical",
                "subcategory": event.source.value,
                "configuration_item": event.configuration_item,
                "reporter": "Event Management System",
                "source_event_id": event.id
            }
            
            incident = await self.incident_manager.create_incident(incident_data)
            event.incident_created = incident.id
            self.stats["incidents_created"] += 1
            
            self.logger.info(f"Created incident {incident.id} from event {event.id}")
            
        except Exception as e:
            self.logger.error(f"Failed to create incident from event {event.id}: {e}")
    
    async def _create_incident_from_correlation(self, correlation_result: Dict[str, Any]):
        """Create an incident from correlated events"""
        try:
            if not self.incident_manager:
                return
            
            correlated_events = [self.events[event_id] for event_id in correlation_result["events"]]
            primary_event = correlated_events[0]  # Use first event as primary
            
            incident_data = {
                "title": f"Incident from Correlation: {correlation_result['correlation_name']}",
                "description": f"Automatically created from {correlation_result['event_count']} correlated events\n\n" +
                              f"Correlation ID: {correlation_result['correlation_id']}\n" +
                              f"Events: {', '.join(correlation_result['events'])}",
                "priority": primary_event.priority.value,
                "impact": Impact.HIGH.value,  # Correlated events typically indicate higher impact
                "urgency": primary_event.urgency.value,
                "category": "Technical",
                "subcategory": "Correlated Events",
                "configuration_item": primary_event.configuration_item,
                "reporter": "Event Management System"
            }
            
            incident = await self.incident_manager.create_incident(incident_data)
            
            # Link all correlated events to the incident
            for event in correlated_events:
                event.incident_created = incident.id
            
            self.stats["incidents_created"] += 1
            
            self.logger.info(f"Created incident {incident.id} from correlation {correlation_result['correlation_id']}")
            
        except Exception as e:
            self.logger.error(f"Failed to create incident from correlation: {e}")
    
    async def create_event(self, event_data: Dict[str, Any]) -> Event:
        """Create a new event and queue it for processing"""
        
        # Create event object
        event = Event(
            title=event_data.get("title", ""),
            description=event_data.get("description", ""),
            event_type=EventType(event_data.get("event_type", "Informational")),
            source=EventSource(event_data.get("source", "Monitoring Tool")),
            source_system=event_data.get("source_system", ""),
            configuration_item=event_data.get("configuration_item"),
            service_affected=event_data.get("service_affected"),
            priority=Priority(event_data.get("priority", "P4 - Low")),
            impact=Impact(event_data.get("impact", "Low")),
            urgency=Urgency(event_data.get("urgency", "Low")),
            attributes=event_data.get("attributes", {}),
            tags=set(event_data.get("tags", []))
        )
        
        # Queue for processing
        self.event_queue.put(event)
        
        self.logger.info(f"Created event {event.id}: {event.title}")
        return event
    
    def get_event(self, event_id: str) -> Optional[Event]:
        """Get an event by ID"""
        return self.events.get(event_id)
    
    def get_events_by_status(self, status: EventStatus) -> List[Event]:
        """Get all events with specified status"""
        return [event for event in self.events.values() if event.status == status]
    
    def get_events_by_correlation(self, correlation_id: str) -> List[Event]:
        """Get all events with specified correlation ID"""
        return [event for event in self.events.values() if event.correlation_id == correlation_id]
    
    def get_event_statistics(self) -> Dict[str, Any]:
        """Get event processing statistics"""
        return {
            **self.stats,
            "queue_size": self.event_queue.qsize(),
            "total_stored_events": len(self.events),
            "processing_status": "running" if self.running else "stopped"
        }
    
    async def acknowledge_event(self, event_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an event"""
        event = self.events.get(event_id)
        if event and event.status == EventStatus.NEW:
            event.status = EventStatus.ACKNOWLEDGED
            event.acknowledged_at = datetime.now()
            event.acknowledged_by = acknowledged_by
            event.updated_at = datetime.now()
            
            self.logger.info(f"Event {event_id} acknowledged by {acknowledged_by}")
            return True
        return False
    
    async def resolve_event(self, event_id: str, resolved_by: str, resolution_notes: str = "") -> bool:
        """Resolve an event"""
        event = self.events.get(event_id)
        if event and event.status in [EventStatus.NEW, EventStatus.ACKNOWLEDGED, EventStatus.IN_PROGRESS]:
            event.status = EventStatus.RESOLVED
            event.resolved_at = datetime.now()
            event.attributes["resolved_by"] = resolved_by
            event.attributes["resolution_notes"] = resolution_notes
            event.updated_at = datetime.now()
            
            self.logger.info(f"Event {event_id} resolved by {resolved_by}")
            return True
        return False
    
    async def close_event(self, event_id: str, closed_by: str, closure_notes: str = "") -> bool:
        """Close an event"""
        event = self.events.get(event_id)
        if event and event.status == EventStatus.RESOLVED:
            event.status = EventStatus.CLOSED
            event.attributes["closed_by"] = closed_by
            event.attributes["closure_notes"] = closure_notes
            event.updated_at = datetime.now()
            
            self.logger.info(f"Event {event_id} closed by {closed_by}")
            return True
        return False


# Example monitoring integrations
class MonitoringIntegration:
    """Base class for monitoring tool integrations"""
    
    def __init__(self, event_manager: EventManager):
        self.event_manager = event_manager
        self.logger = logging.getLogger(__name__)
    
    async def process_monitoring_alert(self, alert_data: Dict[str, Any]) -> Event:
        """Process an alert from a monitoring tool"""
        
        # Transform monitoring alert to ITIL event
        event_data = self._transform_alert_to_event(alert_data)
        
        # Create event
        return await self.event_manager.create_event(event_data)
    
    def _transform_alert_to_event(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform monitoring alert format to ITIL event format"""
        # This would be customized for each monitoring tool
        return {
            "title": alert_data.get("summary", "Monitoring Alert"),
            "description": alert_data.get("description", ""),
            "event_type": self._map_severity_to_event_type(alert_data.get("severity", "low")),
            "source": "Monitoring Tool",
            "source_system": alert_data.get("source", "Unknown"),
            "configuration_item": alert_data.get("host") or alert_data.get("service"),
            "attributes": alert_data
        }
    
    def _map_severity_to_event_type(self, severity: str) -> str:
        """Map monitoring tool severity to ITIL event type"""
        mapping = {
            "critical": "Critical",
            "high": "Exception", 
            "medium": "Warning",
            "low": "Informational"
        }
        return mapping.get(severity.lower(), "Informational")


async def main():
    """Main function to demonstrate event management"""
    print("🚨 ITIL 4 Event Management System")
    print("=" * 50)
    
    # Initialize managers
    from practices.incident_management import IncidentManager
    incident_manager = IncidentManager()
    event_manager = EventManager(incident_manager)
    
    # Start processing
    event_manager.start_processing()
    
    print("✅ Event processing started")
    
    # Create some test events
    test_events = [
        {
            "title": "Database Connection Timeout",
            "description": "Database server not responding to connection requests",
            "event_type": "Critical",
            "source": "Infrastructure",
            "source_system": "Database Monitor",
            "configuration_item": "PROD-DB-01",
            "service_affected": "Customer Portal",
            "priority": "P1 - Critical",
            "impact": "High",
            "urgency": "High",
            "tags": ["database", "timeout", "production"]
        },
        {
            "title": "High CPU Usage",
            "description": "CPU usage above 90% for 5 minutes",
            "event_type": "Warning",
            "source": "Infrastructure", 
            "source_system": "System Monitor",
            "configuration_item": "PROD-WEB-01",
            "priority": "P3 - Medium",
            "impact": "Medium",
            "urgency": "Medium",
            "tags": ["cpu", "performance", "threshold"]
        },
        {
            "title": "Application Error",
            "description": "Multiple 500 errors in application logs",
            "event_type": "Exception",
            "source": "Application",
            "source_system": "Log Monitor",
            "configuration_item": "CustomerPortal-App",
            "service_affected": "Customer Portal",
            "priority": "P2 - High",
            "impact": "High", 
            "urgency": "Medium",
            "tags": ["application", "error", "logs"]
        },
        {
            "title": "Backup Completed Successfully",
            "description": "Daily backup completed without errors",
            "event_type": "Informational",
            "source": "Automated Scan",
            "source_system": "Backup System",
            "configuration_item": "BACKUP-SYS-01",
            "priority": "P4 - Low",
            "impact": "Low",
            "urgency": "Low",
            "tags": ["backup", "success", "routine"]
        }
    ]
    
    print(f"\n🔄 Creating {len(test_events)} test events...")
    created_events = []
    
    for event_data in test_events:
        event = await event_manager.create_event(event_data)
        created_events.append(event)
        print(f"Created event: {event.id} - {event.title}")
    
    # Wait for processing
    print(f"\n⏳ Waiting for event processing...")
    await asyncio.sleep(3)
    
    # Display statistics
    stats = event_manager.get_event_statistics()
    print(f"\n📊 Event Processing Statistics:")
    print(f"Total Events: {stats['total_events']}")
    print(f"Incidents Created: {stats['incidents_created']}")
    print(f"Events Correlated: {stats['events_correlated']}")
    print(f"Queue Size: {stats['queue_size']}")
    
    print(f"\nEvents by Type:")
    for event_type, count in stats['events_by_type'].items():
        print(f"  {event_type}: {count}")
    
    print(f"\nEvents by Source:")
    for source, count in stats['events_by_source'].items():
        print(f"  {source}: {count}")
    
    # Display processed events
    print(f"\n📋 Processed Events:")
    for event in created_events:
        if event.id in event_manager.events:
            processed_event = event_manager.events[event.id]
            print(f"  {processed_event.id}:")
            print(f"    Status: {processed_event.status.value}")
            print(f"    Priority: {processed_event.priority.value}")
            print(f"    Tags: {', '.join(processed_event.tags)}")
            if processed_event.incident_created:
                print(f"    Incident Created: {processed_event.incident_created}")
            if processed_event.correlation_id:
                print(f"    Correlation ID: {processed_event.correlation_id}")
    
    # Test event lifecycle operations
    print(f"\n🔄 Testing Event Lifecycle Operations...")
    
    if created_events:
        test_event = created_events[0]
        
        # Acknowledge event
        await event_manager.acknowledge_event(test_event.id, "test_user")
        print(f"✅ Acknowledged event {test_event.id}")
        
        # Resolve event
        await event_manager.resolve_event(test_event.id, "test_user", "Issue resolved")
        print(f"✅ Resolved event {test_event.id}")
        
        # Close event
        await event_manager.close_event(test_event.id, "test_user", "Closure confirmed")
        print(f"✅ Closed event {test_event.id}")
    
    # Stop processing
    event_manager.stop_processing()
    print(f"\n🛑 Event processing stopped")
    
    print(f"\n🎉 Event Management Demo Complete!")
    print("Key Features Demonstrated:")
    print("✅ Real-time event processing")
    print("✅ Rule-based event handling")
    print("✅ Event correlation")
    print("✅ Automatic incident creation")
    print("✅ Event lifecycle management")
    print("✅ Statistics and monitoring")


if __name__ == "__main__":
    asyncio.run(main())