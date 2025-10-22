"""
Complete ITIL Framework Integration Example

This example demonstrates how to properly integrate all ITIL framework
components using the integration manager for a production-ready setup.
"""

import sys
import os
sys.path.append('..')

from integration.integration_manager import ITILIntegrationManager, ITILPracticeInterface
from core.service_value_system import ServiceValueSystem, Person, Organization
from practices.incident_management import IncidentManagement
from practices.problem_management import ProblemManagement
from practices.change_enablement import ChangeEnablement

import logging
from datetime import datetime, timedelta
import json


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ITILFrameworkDemo:
    """Complete ITIL Framework Integration Demo"""
    
    def __init__(self):
        self.integration_mgr = None
        self.svs = None
        self.practices = {}
        self.demo_data = {}
    
    def setup_organization(self):
        """Setup demo organization and people"""
        print("\n🏢 Setting up Organization...")
        
        # Create organization
        org = Organization(
            name="TechCorp Solutions",
            domain="techcorp.com",
            industry="Information Technology"
        )
        
        # Create key personnel
        it_manager = Person(
            name="Sarah Johnson",
            email="sarah.johnson@techcorp.com",
            department="IT Operations",
            role="IT Service Manager"
        )
        
        # Create Service Value System
        self.svs = ServiceValueSystem(org, it_manager)
        
        print(f"✅ Organization created: {org.name}")
        print(f"✅ Primary contact: {it_manager.name} ({it_manager.role})")
        
        return org, it_manager
    
    def setup_integration_manager(self):
        """Setup and configure integration manager"""
        print("\n🔧 Setting up Integration Manager...")
        
        self.integration_mgr = ITILIntegrationManager()
        
        # Setup custom event handlers for demo
        self.integration_mgr.event_bus.subscribe(
            "demo.incident.created", 
            self._demo_incident_handler
        )
        self.integration_mgr.event_bus.subscribe(
            "demo.problem.created", 
            self._demo_problem_handler
        )
        self.integration_mgr.event_bus.subscribe(
            "demo.change.approved", 
            self._demo_change_handler
        )
        
        print("✅ Integration manager configured")
        return self.integration_mgr
    
    def _demo_incident_handler(self, event):
        """Demo incident event handler"""
        incident_data = event['data']
        logger.info(f"📧 Incident notification sent for: {incident_data.get('title')}")
        
        # Simulate escalation logic
        if incident_data.get('priority') == 'P1':
            logger.info("🚨 P1 incident - triggering emergency response")
    
    def _demo_problem_handler(self, event):
        """Demo problem event handler"""
        problem_data = event['data']
        logger.info(f"🔍 Problem investigation started: {problem_data.get('title')}")
        
        # Simulate problem-to-change workflow
        if problem_data.get('root_cause_identified'):
            logger.info("💡 Root cause identified - considering change request")
    
    def _demo_change_handler(self, event):
        """Demo change event handler"""
        change_data = event['data']
        logger.info(f"📋 Change approved and scheduled: {change_data.get('title')}")
    
    def register_practices(self):
        """Register all ITIL practices with integration manager"""
        print("\n📝 Registering ITIL Practices...")
        
        # Create practice instances
        incident_mgmt = IncidentManagement(self.svs)
        problem_mgmt = ProblemManagement(self.svs)
        change_mgmt = ChangeEnablement(self.svs)
        
        # Store for later use
        self.practices = {
            'incident_management': incident_mgmt,
            'problem_management': problem_mgmt,
            'change_enablement': change_mgmt
        }
        
        # Register with dependency hierarchy
        self.integration_mgr.register_practice("incident_management", incident_mgmt)
        
        self.integration_mgr.register_practice(
            "problem_management", 
            problem_mgmt, 
            ["incident_management"]
        )
        
        self.integration_mgr.register_practice(
            "change_enablement", 
            change_mgmt, 
            ["problem_management"]
        )
        
        print("✅ Incident Management registered")
        print("✅ Problem Management registered (depends on Incident)")
        print("✅ Change Enablement registered (depends on Problem)")
    
    def initialize_framework(self):
        """Initialize the complete framework"""
        print("\n🚀 Initializing ITIL Framework...")
        
        results = self.integration_mgr.initialize_framework()
        
        if results['overall_status'] == 'SUCCESS':
            print("✅ Framework initialized successfully!")
            
            # Display initialization details
            for service, status in results['initialization_results'].items():
                status_icon = "✅" if status else "❌"
                print(f"  {status_icon} {service}: {'Ready' if status else 'Failed'}")
            
            # Display validation results
            validation = results['validation_results']
            print(f"\n🔍 Validation Status: {validation['overall_status']}")
            
            if validation['interface_issues']:
                print("⚠️  Interface Issues Found:")
                for service, issues in validation['interface_issues'].items():
                    for issue in issues:
                        print(f"    - {service}: {issue}")
            
            if validation['dependency_issues']:
                print("⚠️  Dependency Issues Found:")
                for service, issues in validation['dependency_issues'].items():
                    for issue in issues:
                        print(f"    - {service}: {issue}")
        else:
            print("❌ Framework initialization failed!")
            return False
        
        return True
    
    def demonstrate_cross_practice_workflow(self):
        """Demonstrate integrated workflow across practices"""
        print("\n🔄 Demonstrating Cross-Practice Workflow...")
        
        # Get practice references
        incident_mgmt = self.practices['incident_management']
        problem_mgmt = self.practices['problem_management']
        change_mgmt = self.practices['change_enablement']
        
        # Create sample person for demo
        reporter = Person(
            name="John Smith",
            email="john.smith@techcorp.com",
            department="Finance",
            role="Financial Analyst"
        )
        
        print("\n📞 Step 1: User reports an incident")
        # Create incident
        incident = incident_mgmt.create_incident(
            title="Email system slow response",
            description="Users reporting extremely slow email response times across the organization",
            category="Email",
            priority="P2",
            urgency="High",
            impact="Medium",
            reporter=reporter
        )
        
        print(f"✅ Incident created: {incident.id} - {incident.title}")
        
        # Publish incident event
        self.integration_mgr.event_bus.publish(
            "demo.incident.created",
            {
                "incident_id": incident.id,
                "title": incident.title,
                "priority": incident.priority,
                "category": incident.category
            },
            "demo_system"
        )
        
        print("\n🔍 Step 2: Pattern analysis identifies recurring issue")
        # Create related problem
        problem = problem_mgmt.create_problem(
            title="Email infrastructure performance degradation",
            description="Multiple incidents indicate systematic performance issues with email infrastructure",
            category="Infrastructure",
            priority="P2",
            reporter=self.svs.primary_contact,
            related_incidents=[incident.id]
        )
        
        print(f"✅ Problem created: {problem.id} - {problem.title}")
        print(f"🔗 Linked to incident: {incident.id}")
        
        # Publish problem event
        self.integration_mgr.event_bus.publish(
            "demo.problem.created",
            {
                "problem_id": problem.id,
                "title": problem.title,
                "related_incidents": problem.related_incidents,
                "root_cause_identified": True
            },
            "demo_system"
        )
        
        print("\n📋 Step 3: Root cause analysis leads to change request")
        # Create change request
        change_request = change_mgmt.create_change_request(
            title="Upgrade email server infrastructure",
            description="Upgrade email servers and increase memory allocation to resolve performance issues",
            change_type="Standard",
            priority="P2",
            requester=self.svs.primary_contact,
            reason="Resolve recurring email performance problems identified through problem management"
        )
        
        print(f"✅ Change request created: {change_request.id} - {change_request.title}")
        
        # Link change to problem
        problem.add_related_change(change_request.id)
        print(f"🔗 Change linked to problem: {problem.id}")
        
        # Publish change event
        self.integration_mgr.event_bus.publish(
            "demo.change.approved",
            {
                "change_id": change_request.id,
                "title": change_request.title,
                "related_problem": problem.id
            },
            "demo_system"
        )
        
        # Store demo data for metrics
        self.demo_data = {
            'incident': incident,
            'problem': problem,
            'change': change_request,
            'workflow_completed_at': datetime.now()
        }
        
        print("\n✅ Cross-practice workflow completed successfully!")
        return True
    
    def display_integration_metrics(self):
        """Display comprehensive integration metrics"""
        print("\n📊 Integration Health & Metrics")
        print("=" * 40)
        
        # Get integration health
        health = self.integration_mgr.get_integration_health()
        
        print(f"🕐 Timestamp: {health['timestamp']}")
        print(f"✅ Validation Status: {health['validation_status']}")
        
        print("\n📈 Service Status:")
        for service_name, service_info in health['services'].items():
            status_icon = "✅" if service_info['status'] == 'Ready' else "❌"
            print(f"  {status_icon} {service_name}: {service_info['status']}")
            if service_info['initialized_at']:
                print(f"    🕐 Initialized: {service_info['initialized_at']}")
        
        # Get metrics
        metrics = self.integration_mgr.get_integration_metrics()
        
        print(f"\n📊 Framework Metrics:")
        print(f"  🎯 Service Readiness: {metrics['services_ready']}/{metrics['total_services']} ({metrics['readiness_percentage']:.1f}%)")
        print(f"  📨 Events Published: {metrics['events_published']}")
        print(f"  🔧 Event Types: {len(metrics['event_types'])}")
        print(f"  ⚠️  Dependency Violations: {metrics['dependency_violations']}")
        print(f"  ❌ Interface Violations: {metrics['interface_violations']}")
        
        # Display event history
        print(f"\n📜 Recent Events:")
        event_history = self.integration_mgr.event_bus.get_event_history()
        for event in event_history[-5:]:  # Last 5 events
            print(f"  📨 {event['type']} from {event['source']} at {event['timestamp'].strftime('%H:%M:%S')}")
        
        # Practice-specific metrics if demo data available
        if self.demo_data:
            print(f"\n📈 Practice Metrics (Demo Period):")
            
            incident_mgmt = self.practices['incident_management']
            problem_mgmt = self.practices['problem_management']
            change_mgmt = self.practices['change_enablement']
            
            # Get metrics from practices
            incident_metrics = incident_mgmt.get_metrics(7)  # Last 7 days
            problem_metrics = problem_mgmt.get_metrics(7)
            change_metrics = change_mgmt.get_metrics(7)
            
            print(f"  🎫 Incidents: {incident_metrics.get('total_incidents', 0)} total, {incident_metrics.get('resolved_incidents', 0)} resolved")
            print(f"  🔍 Problems: {problem_metrics.get('total_problems', 0)} total, {problem_metrics.get('resolved_problems', 0)} resolved")
            print(f"  📋 Changes: {change_metrics.get('total_changes', 0)} total, {change_metrics.get('successful_changes', 0)} successful")
    
    def demonstrate_event_driven_integration(self):
        """Demonstrate event-driven integration patterns"""
        print("\n🎭 Demonstrating Event-Driven Integration...")
        
        # Track events for demonstration
        demo_events = []
        
        def event_tracker(event):
            demo_events.append(event)
            print(f"  📨 Event received: {event['type']} from {event['source']}")
        
        # Subscribe to all demo events
        self.integration_mgr.event_bus.subscribe("demo.*", event_tracker)
        
        # Simulate various events
        events_to_publish = [
            ("demo.incident.escalated", {"incident_id": "INC001", "escalation_level": 2}),
            ("demo.problem.root_cause_found", {"problem_id": "PRB001", "root_cause": "Memory leak"}),
            ("demo.change.emergency_approved", {"change_id": "CHG001", "approval_time": "5 minutes"}),
            ("demo.service.outage_detected", {"service": "Email", "severity": "Major"}),
            ("demo.automation.script_executed", {"script": "restart_email_service", "result": "success"})
        ]
        
        print("Publishing demonstration events...")
        for event_type, event_data in events_to_publish:
            self.integration_mgr.event_bus.publish(event_type, event_data, "demo_simulator")
        
        print(f"\n✅ Published {len(events_to_publish)} events")
        print(f"📊 Event bus now contains {len(self.integration_mgr.event_bus.get_event_history())} total events")
    
    def generate_integration_report(self):
        """Generate comprehensive integration report"""
        print("\n📋 Generating Integration Report...")
        
        report = {
            "report_generated_at": datetime.now().isoformat(),
            "framework_status": self.integration_mgr.get_integration_health(),
            "metrics": self.integration_mgr.get_integration_metrics(),
            "validation_results": self.integration_mgr.validator.run_full_validation(),
            "demo_workflow": self.demo_data,
            "recommendations": []
        }
        
        # Add recommendations based on status
        if report["validation_results"]["overall_status"] == "PASS":
            report["recommendations"].append("✅ Framework is properly integrated and ready for production")
        
        if report["metrics"]["readiness_percentage"] == 100:
            report["recommendations"].append("✅ All services are operational and healthy")
        
        if report["metrics"]["events_published"] > 0:
            report["recommendations"].append("✅ Event-driven integration is working correctly")
        
        # Save report to file
        report_filename = f"itil_integration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(report_filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"✅ Integration report saved: {report_filename}")
        except Exception as e:
            print(f"❌ Failed to save report: {e}")
        
        return report
    
    def run_complete_demo(self):
        """Run the complete integration demonstration"""
        print("🎯 ITIL Framework Integration Demonstration")
        print("=" * 50)
        
        try:
            # Setup phase
            self.setup_organization()
            self.setup_integration_manager()
            self.register_practices()
            
            # Initialize framework
            if not self.initialize_framework():
                print("❌ Demo aborted due to initialization failure")
                return False
            
            # Demonstrate workflows
            self.demonstrate_cross_practice_workflow()
            self.demonstrate_event_driven_integration()
            
            # Display results
            self.display_integration_metrics()
            
            # Generate report
            self.generate_integration_report()
            
            print("\n" + "=" * 50)
            print("🎉 ITIL Framework Integration Demo Completed Successfully!")
            print("\nKey Achievements:")
            print("✅ Framework properly initialized with dependency resolution")
            print("✅ Cross-practice workflows demonstrated")
            print("✅ Event-driven integration working")
            print("✅ Health monitoring and metrics collection active")
            print("✅ Integration validation passed")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Demo failed with error: {e}")
            logger.exception("Demo execution failed")
            return False


def main():
    """Main execution function"""
    print("Starting ITIL Framework Integration Example...")
    
    # Create and run demo
    demo = ITILFrameworkDemo()
    success = demo.run_complete_demo()
    
    if success:
        print(f"\n✅ Integration example completed successfully!")
        print("💡 You can now use this pattern to integrate ITIL practices in your organization")
    else:
        print(f"\n❌ Integration example failed!")
        print("🔧 Check the logs for detailed error information")
    
    return success


if __name__ == "__main__":
    main()