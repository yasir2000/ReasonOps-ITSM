"""
Enterprise Integration for ITIL Framework

This module implements enterprise integrations with ServiceNow, Jira, Microsoft Teams,
and other enterprise ITSM platforms and collaboration tools.
"""

import sys
import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import json
import logging
import asyncio
from urllib.parse import urljoin
import base64

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# HTTP and API integration imports (with fallbacks)
try:
    import requests
    import aiohttp
    HTTP_AVAILABLE = True
except ImportError:
    print("⚠️  HTTP libraries not installed. Install with: pip install requests aiohttp")
    HTTP_AVAILABLE = False
    
    # Mock classes for demonstration
    class MockResponse:
        def __init__(self, status_code=200, json_data=None):
            self.status_code = status_code
            self._json_data = json_data or {}
        
        def json(self):
            return self._json_data
        
        def raise_for_status(self):
            if self.status_code >= 400:
                raise Exception(f"HTTP Error {self.status_code}")
    
    class requests:
        @staticmethod
        def get(url, **kwargs):
            return MockResponse(200, {"result": "mock_data"})
        
        @staticmethod
        def post(url, **kwargs):
            return MockResponse(201, {"result": {"id": "mock_id"}})
        
        @staticmethod
        def put(url, **kwargs):
            return MockResponse(200, {"result": "updated"})
        
        @staticmethod
        def delete(url, **kwargs):
            return MockResponse(204)

# Microsoft Teams integration (webhook-based)
try:
    import pymsteams
    TEAMS_AVAILABLE = True
except ImportError:
    print("⚠️  Microsoft Teams library not installed. Install with: pip install pymsteams")
    TEAMS_AVAILABLE = False
    
    class pymsteams:
        @staticmethod
        def connectorcard(webhook_url):
            return MockTeamsCard()
    
    class MockTeamsCard:
        def title(self, title): pass
        def text(self, text): pass
        def color(self, color): pass
        def addSection(self, section): pass
        def send(self): return True

from integration.integration_manager import ITILIntegrationManager


class IntegrationType(Enum):
    """Types of enterprise integrations"""
    SERVICENOW = "servicenow"
    JIRA = "jira"
    MICROSOFT_TEAMS = "microsoft_teams"
    SLACK = "slack"
    AZURE_DEVOPS = "azure_devops"
    REMEDY = "remedy"
    CHERWELL = "cherwell"


@dataclass
class IntegrationConfig:
    """Configuration for enterprise integration"""
    integration_type: IntegrationType
    base_url: str
    username: Optional[str] = None
    password: Optional[str] = None
    api_token: Optional[str] = None
    webhook_url: Optional[str] = None
    tenant_id: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    additional_config: Optional[Dict[str, Any]] = None


@dataclass
class SyncResult:
    """Result of synchronization operation"""
    success: bool
    records_processed: int
    records_created: int
    records_updated: int
    records_failed: int
    errors: List[str]
    sync_timestamp: datetime


class ServiceNowIntegration:
    """ServiceNow ITSM platform integration"""
    
    def __init__(self, config: IntegrationConfig):
        self.config = config
        self.base_url = config.base_url.rstrip('/')
        self.session = None
        self._setup_session()
    
    def _setup_session(self):
        """Setup HTTP session with authentication"""
        if HTTP_AVAILABLE:
            self.session = requests.Session()
            if self.config.username and self.config.password:
                self.session.auth = (self.config.username, self.config.password)
            elif self.config.api_token:
                self.session.headers.update({
                    'Authorization': f'Bearer {self.config.api_token}',
                    'Content-Type': 'application/json'
                })
        else:
            self.session = requests()  # Mock session
    
    def sync_incidents_to_servicenow(self, incidents: List[Dict[str, Any]]) -> SyncResult:
        """Synchronize incidents to ServiceNow"""
        print("🔄 Syncing incidents to ServiceNow...")
        
        created = updated = failed = 0
        errors = []
        
        for incident in incidents:
            try:
                # Map ITIL incident to ServiceNow format
                snow_incident = self._map_incident_to_servicenow(incident)
                
                # Check if incident exists
                existing = self._find_servicenow_incident(incident.get('id'))
                
                if existing:
                    # Update existing incident
                    response = self._update_servicenow_incident(existing['sys_id'], snow_incident)
                    if response.status_code == 200:
                        updated += 1
                    else:
                        failed += 1
                        errors.append(f"Failed to update {incident.get('id')}: {response.status_code}")
                else:
                    # Create new incident
                    response = self._create_servicenow_incident(snow_incident)
                    if response.status_code == 201:
                        created += 1
                    else:
                        failed += 1
                        errors.append(f"Failed to create {incident.get('id')}: {response.status_code}")
            
            except Exception as e:
                failed += 1
                errors.append(f"Error processing {incident.get('id')}: {str(e)}")
        
        result = SyncResult(
            success=failed == 0,
            records_processed=len(incidents),
            records_created=created,
            records_updated=updated,
            records_failed=failed,
            errors=errors,
            sync_timestamp=datetime.now()
        )
        
        print(f"✅ ServiceNow sync completed: {created} created, {updated} updated, {failed} failed")
        return result
    
    def _map_incident_to_servicenow(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """Map ITIL incident to ServiceNow incident format"""
        priority_mapping = {
            "P1": "1 - Critical",
            "P2": "2 - High",
            "P3": "3 - Moderate",
            "P4": "4 - Low"
        }
        
        state_mapping = {
            "New": "1",
            "In Progress": "2",
            "Resolved": "6",
            "Closed": "7"
        }
        
        return {
            "short_description": incident.get("title", ""),
            "description": incident.get("description", ""),
            "priority": priority_mapping.get(incident.get("priority"), "3 - Moderate"),
            "state": state_mapping.get(incident.get("status"), "1"),
            "category": incident.get("category", ""),
            "impact": incident.get("impact", "3 - Low"),
            "urgency": incident.get("urgency", "3 - Low"),
            "caller_id": incident.get("reporter", ""),
            "assignment_group": incident.get("assignment_group", ""),
            "assigned_to": incident.get("assigned_to", ""),
            "work_notes": f"Synced from ITIL Framework at {datetime.now().isoformat()}",
            "u_external_id": incident.get("id")  # Custom field to track ITIL ID
        }
    
    def _find_servicenow_incident(self, itil_id: str) -> Optional[Dict[str, Any]]:
        """Find existing ServiceNow incident by ITIL ID"""
        if not HTTP_AVAILABLE:
            return None
        
        url = f"{self.base_url}/api/now/table/incident"
        params = {
            "sysparm_query": f"u_external_id={itil_id}",
            "sysparm_limit": 1
        }
        
        response = self.session.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('result'):
                return data['result'][0]
        
        return None
    
    def _create_servicenow_incident(self, incident_data: Dict[str, Any]) -> Any:
        """Create new incident in ServiceNow"""
        url = f"{self.base_url}/api/now/table/incident"
        
        if HTTP_AVAILABLE:
            return self.session.post(url, json=incident_data)
        else:
            return requests.post(url, json=incident_data)
    
    def _update_servicenow_incident(self, sys_id: str, incident_data: Dict[str, Any]) -> Any:
        """Update existing incident in ServiceNow"""
        url = f"{self.base_url}/api/now/table/incident/{sys_id}"
        
        if HTTP_AVAILABLE:
            return self.session.put(url, json=incident_data)
        else:
            return requests.put(url, json=incident_data)
    
    def fetch_servicenow_incidents(self, since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Fetch incidents from ServiceNow"""
        print("📥 Fetching incidents from ServiceNow...")
        
        url = f"{self.base_url}/api/now/table/incident"
        params = {
            "sysparm_limit": 100,
            "sysparm_fields": "sys_id,number,short_description,description,priority,state,category,caller_id,assignment_group,assigned_to,sys_created_on,sys_updated_on"
        }
        
        if since:
            params["sysparm_query"] = f"sys_updated_on>={since.strftime('%Y-%m-%d %H:%M:%S')}"
        
        if HTTP_AVAILABLE:
            response = self.session.get(url, params=params)
        else:
            response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            incidents = []
            
            for snow_incident in data.get('result', []):
                # Map ServiceNow incident back to ITIL format
                itil_incident = self._map_servicenow_to_incident(snow_incident)
                incidents.append(itil_incident)
            
            print(f"✅ Fetched {len(incidents)} incidents from ServiceNow")
            return incidents
        else:
            print(f"❌ Failed to fetch ServiceNow incidents: {response.status_code}")
            return []
    
    def _map_servicenow_to_incident(self, snow_incident: Dict[str, Any]) -> Dict[str, Any]:
        """Map ServiceNow incident to ITIL incident format"""
        priority_mapping = {
            "1 - Critical": "P1",
            "2 - High": "P2",
            "3 - Moderate": "P3",
            "4 - Low": "P4"
        }
        
        state_mapping = {
            "1": "New",
            "2": "In Progress",
            "6": "Resolved",
            "7": "Closed"
        }
        
        return {
            "id": f"SNOW-{snow_incident.get('number', '')}",
            "title": snow_incident.get("short_description", ""),
            "description": snow_incident.get("description", ""),
            "priority": priority_mapping.get(snow_incident.get("priority"), "P3"),
            "status": state_mapping.get(snow_incident.get("state"), "New"),
            "category": snow_incident.get("category", ""),
            "reporter": snow_incident.get("caller_id", ""),
            "assignment_group": snow_incident.get("assignment_group", ""),
            "assigned_to": snow_incident.get("assigned_to", ""),
            "created_date": snow_incident.get("sys_created_on", ""),
            "updated_date": snow_incident.get("sys_updated_on", ""),
            "external_id": snow_incident.get("sys_id"),
            "source": "ServiceNow"
        }


class JiraIntegration:
    """Jira Service Management integration"""
    
    def __init__(self, config: IntegrationConfig):
        self.config = config
        self.base_url = config.base_url.rstrip('/')
        self.session = None
        self._setup_session()
    
    def _setup_session(self):
        """Setup HTTP session with authentication"""
        if HTTP_AVAILABLE:
            self.session = requests.Session()
            if self.config.username and self.config.api_token:
                # Basic auth with API token
                auth_string = f"{self.config.username}:{self.config.api_token}"
                encoded_auth = base64.b64encode(auth_string.encode()).decode()
                self.session.headers.update({
                    'Authorization': f'Basic {encoded_auth}',
                    'Content-Type': 'application/json'
                })
        else:
            self.session = requests()
    
    def sync_incidents_to_jira(self, incidents: List[Dict[str, Any]]) -> SyncResult:
        """Synchronize incidents to Jira Service Management"""
        print("🔄 Syncing incidents to Jira...")
        
        created = updated = failed = 0
        errors = []
        
        for incident in incidents:
            try:
                # Map ITIL incident to Jira issue format
                jira_issue = self._map_incident_to_jira(incident)
                
                # Check if issue exists
                existing = self._find_jira_issue(incident.get('id'))
                
                if existing:
                    # Update existing issue
                    response = self._update_jira_issue(existing['key'], jira_issue)
                    if response.status_code == 204:
                        updated += 1
                    else:
                        failed += 1
                        errors.append(f"Failed to update {incident.get('id')}: {response.status_code}")
                else:
                    # Create new issue
                    response = self._create_jira_issue(jira_issue)
                    if response.status_code == 201:
                        created += 1
                    else:
                        failed += 1
                        errors.append(f"Failed to create {incident.get('id')}: {response.status_code}")
            
            except Exception as e:
                failed += 1
                errors.append(f"Error processing {incident.get('id')}: {str(e)}")
        
        result = SyncResult(
            success=failed == 0,
            records_processed=len(incidents),
            records_created=created,
            records_updated=updated,
            records_failed=failed,
            errors=errors,
            sync_timestamp=datetime.now()
        )
        
        print(f"✅ Jira sync completed: {created} created, {updated} updated, {failed} failed")
        return result
    
    def _map_incident_to_jira(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """Map ITIL incident to Jira issue format"""
        priority_mapping = {
            "P1": "Highest",
            "P2": "High",
            "P3": "Medium",
            "P4": "Low"
        }
        
        return {
            "fields": {
                "project": {"key": self.config.additional_config.get("project_key", "ITSM")},
                "summary": incident.get("title", ""),
                "description": incident.get("description", ""),
                "issuetype": {"name": "Incident"},
                "priority": {"name": priority_mapping.get(incident.get("priority"), "Medium")},
                "labels": ["itil-integration", incident.get("category", "").lower()],
                "customfield_10000": incident.get("id")  # Custom field for ITIL ID
            }
        }
    
    def _find_jira_issue(self, itil_id: str) -> Optional[Dict[str, Any]]:
        """Find existing Jira issue by ITIL ID"""
        if not HTTP_AVAILABLE:
            return None
        
        url = f"{self.base_url}/rest/api/3/search"
        params = {
            "jql": f"cf[10000] ~ '{itil_id}'",  # Custom field search
            "maxResults": 1
        }
        
        response = self.session.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('issues'):
                return data['issues'][0]
        
        return None
    
    def _create_jira_issue(self, issue_data: Dict[str, Any]) -> Any:
        """Create new issue in Jira"""
        url = f"{self.base_url}/rest/api/3/issue"
        
        if HTTP_AVAILABLE:
            return self.session.post(url, json=issue_data)
        else:
            return requests.post(url, json=issue_data)
    
    def _update_jira_issue(self, issue_key: str, issue_data: Dict[str, Any]) -> Any:
        """Update existing issue in Jira"""
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}"
        
        if HTTP_AVAILABLE:
            return self.session.put(url, json=issue_data)
        else:
            return requests.put(url, json=issue_data)


class MicrosoftTeamsIntegration:
    """Microsoft Teams collaboration integration"""
    
    def __init__(self, config: IntegrationConfig):
        self.config = config
        self.webhook_url = config.webhook_url
    
    def send_incident_notification(self, incident: Dict[str, Any], notification_type: str = "created") -> bool:
        """Send incident notification to Microsoft Teams"""
        print(f"📢 Sending {notification_type} notification to Teams...")
        
        try:
            if TEAMS_AVAILABLE:
                # Create Teams card
                teams_card = pymsteams.connectorcard(self.webhook_url)
            else:
                teams_card = pymsteams.connectorcard(self.webhook_url)
            
            # Set card properties based on notification type
            if notification_type == "created":
                teams_card.title(f"🚨 New Incident: {incident.get('title', 'Unknown')}")
                teams_card.color("FF6B35")  # Orange
            elif notification_type == "resolved":
                teams_card.title(f"✅ Incident Resolved: {incident.get('title', 'Unknown')}")
                teams_card.color("28A745")  # Green
            elif notification_type == "escalated":
                teams_card.title(f"⚠️ Incident Escalated: {incident.get('title', 'Unknown')}")
                teams_card.color("DC3545")  # Red
            
            # Add incident details
            incident_details = self._format_incident_for_teams(incident)
            teams_card.text(incident_details)
            
            # Add action section
            action_section = pymsteams.cardsection()
            action_section.activityTitle("Incident Details")
            action_section.activitySubtitle(f"Priority: {incident.get('priority', 'Unknown')}")
            action_section.activityText(f"Status: {incident.get('status', 'Unknown')}")
            teams_card.addSection(action_section)
            
            # Send the card
            result = teams_card.send()
            
            if result:
                print("✅ Teams notification sent successfully")
            else:
                print("❌ Failed to send Teams notification")
            
            return result
            
        except Exception as e:
            print(f"❌ Error sending Teams notification: {str(e)}")
            return False
    
    def _format_incident_for_teams(self, incident: Dict[str, Any]) -> str:
        """Format incident information for Teams message"""
        return f"""
**Incident ID:** {incident.get('id', 'Unknown')}
**Category:** {incident.get('category', 'Unknown')}
**Priority:** {incident.get('priority', 'Unknown')}
**Affected Users:** {incident.get('affected_users', 'Unknown')}
**Assigned To:** {incident.get('assigned_to', 'Unassigned')}

**Description:** {incident.get('description', 'No description available')}
"""
    
    def send_ai_analysis_update(self, analysis_result: Dict[str, Any]) -> bool:
        """Send AI analysis results to Teams"""
        print("🤖 Sending AI analysis update to Teams...")
        
        try:
            if TEAMS_AVAILABLE:
                teams_card = pymsteams.connectorcard(self.webhook_url)
            else:
                teams_card = pymsteams.connectorcard(self.webhook_url)
            
            teams_card.title("🤖 AI Analysis Complete")
            teams_card.color("007ACC")  # Blue
            
            # Format analysis results
            analysis_text = f"""
**Analysis Type:** {analysis_result.get('type', 'Unknown')}
**Confidence:** {analysis_result.get('confidence', 0):.2f}
**Recommendations:** {len(analysis_result.get('recommendations', []))}
**Patterns Detected:** {len(analysis_result.get('patterns', []))}

**Key Insights:**
{analysis_result.get('summary', 'No summary available')}
"""
            
            teams_card.text(analysis_text)
            
            # Add recommendations section
            if analysis_result.get('recommendations'):
                rec_section = pymsteams.cardsection()
                rec_section.activityTitle("Top Recommendations")
                recommendations_text = "\n".join([
                    f"• {rec.get('action', 'Unknown action')}"
                    for rec in analysis_result.get('recommendations', [])[:3]
                ])
                rec_section.activityText(recommendations_text)
                teams_card.addSection(rec_section)
            
            result = teams_card.send()
            
            if result:
                print("✅ AI analysis update sent to Teams")
            else:
                print("❌ Failed to send AI analysis update")
            
            return result
            
        except Exception as e:
            print(f"❌ Error sending AI analysis update: {str(e)}")
            return False


class EnterpriseIntegrationManager:
    """Manages all enterprise integrations for ITIL framework"""
    
    def __init__(self, itil_manager: ITILIntegrationManager):
        self.itil_manager = itil_manager
        self.integrations: Dict[IntegrationType, Any] = {}
        self.sync_history: List[SyncResult] = []
        self.notification_channels: List[Any] = []
    
    def add_integration(self, integration_type: IntegrationType, config: IntegrationConfig):
        """Add an enterprise integration"""
        print(f"🔧 Adding {integration_type.value} integration...")
        
        if integration_type == IntegrationType.SERVICENOW:
            self.integrations[integration_type] = ServiceNowIntegration(config)
        elif integration_type == IntegrationType.JIRA:
            self.integrations[integration_type] = JiraIntegration(config)
        elif integration_type == IntegrationType.MICROSOFT_TEAMS:
            self.integrations[integration_type] = MicrosoftTeamsIntegration(config)
            self.notification_channels.append(self.integrations[integration_type])
        
        print(f"✅ {integration_type.value} integration added successfully")
    
    def sync_all_incidents(self, direction: str = "bidirectional") -> Dict[IntegrationType, SyncResult]:
        """Synchronize incidents across all integrated platforms"""
        print("🔄 Starting enterprise-wide incident synchronization...")
        
        sync_results = {}
        
        # Get incidents from ITIL framework - use demo override if available
        if hasattr(self, 'get_demo_incidents'):
            itil_incidents = self.get_demo_incidents()
        else:
            try:
                incident_service = self.itil_manager.registry.get("incident_management")
                itil_incidents = incident_service.get_all_incidents()
            except Exception as e:
                print(f"⚠️  Could not retrieve incidents from ITIL framework: {e}")
                itil_incidents = []
        
        # Sync to external platforms
        if direction in ["outbound", "bidirectional"]:
            for int_type, integration in self.integrations.items():
                if int_type == IntegrationType.SERVICENOW:
                    result = integration.sync_incidents_to_servicenow(itil_incidents)
                    sync_results[int_type] = result
                    self.sync_history.append(result)
                
                elif int_type == IntegrationType.JIRA:
                    result = integration.sync_incidents_to_jira(itil_incidents)
                    sync_results[int_type] = result
                    self.sync_history.append(result)
        
        # Sync from external platforms
        if direction in ["inbound", "bidirectional"]:
            for int_type, integration in self.integrations.items():
                if int_type == IntegrationType.SERVICENOW:
                    external_incidents = integration.fetch_servicenow_incidents()
                    self._merge_external_incidents(external_incidents)
                
                # Jira fetch would be implemented similarly
        
        print(f"✅ Enterprise synchronization completed for {len(sync_results)} platforms")
        return sync_results
    
    def _merge_external_incidents(self, external_incidents: List[Dict[str, Any]]):
        """Merge incidents from external platforms into ITIL framework"""
        print(f"🔄 Merging {len(external_incidents)} external incidents...")
        
        for ext_incident in external_incidents:
            # Check if incident already exists in ITIL framework
            existing = self.itil_manager.get_incident(ext_incident.get('id'))
            
            if not existing:
                # Create new incident in ITIL framework
                self.itil_manager.create_incident(ext_incident)
                print(f"  ➕ Created incident {ext_incident.get('id')}")
            else:
                # Update existing incident if external version is newer
                ext_updated = datetime.fromisoformat(ext_incident.get('updated_date', ''))
                itil_updated = datetime.fromisoformat(existing.get('updated_date', ''))
                
                if ext_updated > itil_updated:
                    self.itil_manager.update_incident(ext_incident.get('id'), ext_incident)
                    print(f"  🔄 Updated incident {ext_incident.get('id')}")
    
    def notify_incident_event(self, incident: Dict[str, Any], event_type: str):
        """Send notifications about incident events to all channels"""
        print(f"📢 Broadcasting {event_type} notification for incident {incident.get('id')}")
        
        for channel in self.notification_channels:
            if isinstance(channel, MicrosoftTeamsIntegration):
                channel.send_incident_notification(incident, event_type)
        
        print(f"✅ Notifications sent to {len(self.notification_channels)} channels")
    
    def notify_ai_analysis(self, analysis_result: Dict[str, Any]):
        """Send AI analysis results to notification channels"""
        print("🤖 Broadcasting AI analysis results...")
        
        for channel in self.notification_channels:
            if isinstance(channel, MicrosoftTeamsIntegration):
                channel.send_ai_analysis_update(analysis_result)
        
        print(f"✅ AI analysis notifications sent to {len(self.notification_channels)} channels")
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get status of all integrations"""
        status = {
            "total_integrations": len(self.integrations),
            "active_integrations": [],
            "sync_history_count": len(self.sync_history),
            "last_sync": None,
            "notification_channels": len(self.notification_channels)
        }
        
        for int_type in self.integrations.keys():
            status["active_integrations"].append(int_type.value)
        
        if self.sync_history:
            status["last_sync"] = max(self.sync_history, key=lambda x: x.sync_timestamp).sync_timestamp.isoformat()
        
        return status
    
    def get_sync_metrics(self) -> Dict[str, Any]:
        """Get synchronization metrics"""
        if not self.sync_history:
            return {"message": "No sync history available"}
        
        total_syncs = len(self.sync_history)
        successful_syncs = len([s for s in self.sync_history if s.success])
        total_processed = sum(s.records_processed for s in self.sync_history)
        total_created = sum(s.records_created for s in self.sync_history)
        total_updated = sum(s.records_updated for s in self.sync_history)
        total_failed = sum(s.records_failed for s in self.sync_history)
        
        return {
            "total_synchronizations": total_syncs,
            "success_rate": successful_syncs / total_syncs if total_syncs > 0 else 0,
            "records_processed": total_processed,
            "records_created": total_created,
            "records_updated": total_updated,
            "records_failed": total_failed,
            "error_rate": total_failed / total_processed if total_processed > 0 else 0
        }


def main():
    """Main function to demonstrate enterprise integrations"""
    print("🏢 Enterprise Integration for ITIL Framework")
    print("=" * 60)
    
    # Initialize ITIL integration manager
    print("\n🔧 Initializing ITIL Framework...")
    itil_manager = ITILIntegrationManager()
    
    # Initialize enterprise integration manager
    enterprise_manager = EnterpriseIntegrationManager(itil_manager)
    
    # Configure ServiceNow integration
    print("\n🔧 Configuring ServiceNow Integration...")
    servicenow_config = IntegrationConfig(
        integration_type=IntegrationType.SERVICENOW,
        base_url="https://dev12345.service-now.com",
        username="itil_integration_user",
        password="secure_password",
        additional_config={"instance": "dev12345"}
    )
    enterprise_manager.add_integration(IntegrationType.SERVICENOW, servicenow_config)
    
    # Configure Jira integration
    print("\n🔧 Configuring Jira Integration...")
    jira_config = IntegrationConfig(
        integration_type=IntegrationType.JIRA,
        base_url="https://company.atlassian.net",
        username="itil.integration@company.com",
        api_token="ATATT3xFfGF0...secure_token",
        additional_config={"project_key": "ITSM"}
    )
    enterprise_manager.add_integration(IntegrationType.JIRA, jira_config)
    
    # Configure Microsoft Teams integration
    print("\n🔧 Configuring Microsoft Teams Integration...")
    teams_config = IntegrationConfig(
        integration_type=IntegrationType.MICROSOFT_TEAMS,
        base_url="",  # Not needed for webhook
        webhook_url="https://outlook.office.com/webhook/...secure_webhook_url"
    )
    enterprise_manager.add_integration(IntegrationType.MICROSOFT_TEAMS, teams_config)
    
    # Create sample incidents for testing
    print("\n📝 Creating sample incidents for integration testing...")
    sample_incidents = [
        {
            "id": "INC-ENT-001",
            "title": "Email server performance degradation",
            "description": "Users reporting slow email response times across multiple departments",
            "priority": "P2",
            "status": "In Progress",
            "category": "Email",
            "impact": "High",
            "urgency": "Medium",
            "affected_users": 150,
            "reporter": "john.doe@company.com",
            "assignment_group": "Email Support Team",
            "assigned_to": "jane.smith@company.com",
            "created_date": datetime.now().isoformat(),
            "updated_date": datetime.now().isoformat()
        },
        {
            "id": "INC-ENT-002",
            "title": "Network connectivity issues in Building A",
            "description": "Complete network outage affecting all users in Building A",
            "priority": "P1",
            "status": "New",
            "category": "Network",
            "impact": "Critical",
            "urgency": "High",
            "affected_users": 300,
            "reporter": "network.ops@company.com",
            "assignment_group": "Network Operations",
            "assigned_to": "",
            "created_date": datetime.now().isoformat(),
            "updated_date": datetime.now().isoformat()
        }
    ]
    
    # Add incidents to ITIL framework
    for incident in sample_incidents:
        itil_manager.create_incident(incident)
    
    print(f"✅ Created {len(sample_incidents)} sample incidents")
    
    # Test enterprise synchronization
    print("\n🔄 Testing Enterprise-wide Synchronization...")
    sync_results = enterprise_manager.sync_all_incidents(direction="outbound")
    
    # Display sync results
    for integration_type, result in sync_results.items():
        print(f"\n📊 {integration_type.value} Sync Results:")
        print(f"  ✅ Success: {result.success}")
        print(f"  📝 Processed: {result.records_processed}")
        print(f"  ➕ Created: {result.records_created}")
        print(f"  🔄 Updated: {result.records_updated}")
        print(f"  ❌ Failed: {result.records_failed}")
        
        if result.errors:
            print(f"  🚨 Errors: {len(result.errors)}")
            for error in result.errors[:3]:  # Show first 3 errors
                print(f"    - {error}")
    
    # Test notification system
    print("\n📢 Testing Notification System...")
    
    # Test incident notifications
    test_incident = sample_incidents[0]
    enterprise_manager.notify_incident_event(test_incident, "created")
    
    # Simulate incident resolution
    test_incident["status"] = "Resolved"
    enterprise_manager.notify_incident_event(test_incident, "resolved")
    
    # Test AI analysis notification
    mock_analysis = {
        "type": "Incident Pattern Analysis",
        "confidence": 0.87,
        "summary": "Detected recurring email performance issues during peak hours. Recommend proactive monitoring.",
        "recommendations": [
            {"action": "Implement email server monitoring alerts"},
            {"action": "Schedule performance optimization during off-peak hours"},
            {"action": "Consider email server capacity upgrade"}
        ],
        "patterns": [
            {"pattern": "Peak hour performance degradation", "confidence": 0.9}
        ]
    }
    
    enterprise_manager.notify_ai_analysis(mock_analysis)
    
    # Get integration status
    print("\n📊 Integration Status Summary:")
    status = enterprise_manager.get_integration_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    # Get sync metrics
    print("\n📈 Synchronization Metrics:")
    metrics = enterprise_manager.get_sync_metrics()
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2%}")
        else:
            print(f"  {key}: {value}")
    
    print(f"\n🎉 Enterprise Integration Setup Complete!")
    
    print(f"\nEnterprise Capabilities Added:")
    print(f"✅ ServiceNow ITSM integration with bidirectional sync")
    print(f"✅ Jira Service Management integration")
    print(f"✅ Microsoft Teams real-time notifications")
    print(f"✅ Cross-platform incident synchronization")
    print(f"✅ AI analysis result broadcasting")
    print(f"✅ Enterprise-wide status monitoring")
    print(f"✅ Comprehensive sync metrics and reporting")


if __name__ == "__main__":
    main()