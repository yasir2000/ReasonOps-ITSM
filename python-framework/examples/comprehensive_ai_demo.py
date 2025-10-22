"""
Comprehensive AI Agents Demo - Advanced Capabilities

This module demonstrates the complete integration of AI agents with machine learning,
predictive analytics, and enterprise integrations for the ITIL framework.
"""

import sys
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import asyncio

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all AI agent modules
from ai_agents.itil_crewai_integration import ITILAgentCrew
from ai_agents.extended_agents import ExtendedITILAgentCrew
from ai_agents.ml_predictive_analytics import ITILMLModelManager, PredictiveAnalyticsEngine, HistoricalDataGenerator
from ai_agents.enterprise_integration import EnterpriseIntegrationManager, IntegrationConfig, IntegrationType
from integration.integration_manager import ITILIntegrationManager


class ComprehensiveAIDemo:
    """Comprehensive demonstration of all AI agent capabilities"""
    
    def __init__(self):
        # Initialize core ITIL framework
        self.itil_manager = ITILIntegrationManager()
        
        # Setup mock services for demo
        self._setup_mock_services()
        
        # Initialize AI agent crews
        self.core_ai_crew = ITILAgentCrew(self.itil_manager)
        self.extended_ai_crew = ExtendedITILAgentCrew(self.itil_manager)
        
        # Initialize ML and predictive analytics
        self.ml_manager = ITILMLModelManager(self.itil_manager)
        self.predictive_engine = PredictiveAnalyticsEngine(self.ml_manager)
        
        # Initialize enterprise integrations
        self.enterprise_manager = EnterpriseIntegrationManager(self.itil_manager)
        
        # Data generator for realistic scenarios
        self.data_generator = HistoricalDataGenerator()
        
        # Demo metrics
        self.demo_metrics = {
            "incidents_processed": 0,
            "ai_recommendations": 0,
            "ml_predictions": 0,
            "patterns_detected": 0,
            "enterprise_syncs": 0,
            "automation_rate": 0.0
        }
        
        # Incident storage for demo
        self.demo_incidents = {}
    
    def _setup_mock_services(self):
        """Setup mock ITIL services for demonstration"""
        class MockIncidentManagement:
            def __init__(self):
                self.incidents = {}
            
            def create_incident(self, incident_data):
                self.incidents[incident_data['id']] = incident_data
                return incident_data['id']
            
            def get_incident(self, incident_id):
                return self.incidents.get(incident_id)
            
            def update_incident(self, incident_id, updates):
                if incident_id in self.incidents:
                    self.incidents[incident_id].update(updates)
                return self.incidents.get(incident_id)
            
            def get_all_incidents(self):
                return list(self.incidents.values())
            
            def get_metrics(self, period_days):
                return {"total_incidents": len(self.incidents)}
            
            def get_configuration(self):
                return {"sla_targets": {"P1": 4, "P2": 8, "P3": 24, "P4": 72}}
            
            def get_health_status(self):
                return {"status": "healthy", "incidents_open": len(self.incidents)//2}
        
        class MockProblemManagement:
            def __init__(self):
                self.problems = {}
            
            def get_metrics(self, period_days):
                return {"total_problems": len(self.problems)}
            
            def get_configuration(self):
                return {"analysis_threshold": 3}
            
            def get_health_status(self):
                return {"status": "healthy", "problems_open": len(self.problems)//3}
        
        # Register services
        self.itil_manager.register_practice("incident_management", MockIncidentManagement())
        self.itil_manager.register_practice("problem_management", MockProblemManagement(), ["incident_management"])
    
    def create_incident(self, incident_data):
        """Create incident using mock service"""
        incident_service = self.itil_manager.registry.get("incident_management")
        incident_service.create_incident(incident_data)
        self.demo_incidents[incident_data['id']] = incident_data
        
        # Trigger event
        self.itil_manager.event_bus.publish("incident_created", incident_data, "demo")
        
        return incident_data['id']
    
    def get_incident(self, incident_id):
        """Get incident using mock service"""
        return self.demo_incidents.get(incident_id)
    
    def update_incident(self, incident_id, updates):
        """Update incident using mock service"""
        if incident_id in self.demo_incidents:
            self.demo_incidents[incident_id].update(updates)
            
            # Trigger event
            self.itil_manager.event_bus.publish("incident_updated", self.demo_incidents[incident_id], "demo")
        
        return self.demo_incidents.get(incident_id)
    
    def get_all_incidents(self):
        """Get all incidents"""
        return list(self.demo_incidents.values())
    
    def setup_enterprise_integrations(self):
        """Setup enterprise integrations for the demo"""
        print("🏢 Setting up Enterprise Integrations...")
        
        # ServiceNow integration
        servicenow_config = IntegrationConfig(
            integration_type=IntegrationType.SERVICENOW,
            base_url="https://demo.service-now.com",
            username="demo_user",
            password="demo_password"
        )
        self.enterprise_manager.add_integration(IntegrationType.SERVICENOW, servicenow_config)
        
        # Microsoft Teams integration
        teams_config = IntegrationConfig(
            integration_type=IntegrationType.MICROSOFT_TEAMS,
            base_url="",
            webhook_url="https://demo.webhook.url"
        )
        self.enterprise_manager.add_integration(IntegrationType.MICROSOFT_TEAMS, teams_config)
        
        print("✅ Enterprise integrations configured")
    
    def train_ml_models(self):
        """Train all ML models with comprehensive historical data"""
        print("\n🤖 Training Advanced ML Models...")
        
        # Train models with generated historical data
        training_results = self.ml_manager.train_all_models(use_generated_data=True)
        
        print("📊 ML Model Training Results:")
        for model_type, metrics in training_results.items():
            print(f"  🎯 {model_type.value}:")
            print(f"    - Accuracy: {metrics.accuracy:.3f}")
            print(f"    - Precision: {metrics.precision:.3f}")
            print(f"    - F1 Score: {metrics.f1_score:.3f}")
        
        return training_results
    
    def demonstrate_incident_lifecycle(self):
        """Demonstrate complete incident lifecycle with AI automation"""
        print("\n🚨 Demonstrating AI-Powered Incident Lifecycle...")
        
        # Create realistic incident scenarios
        incident_scenarios = [
            {
                "id": "INC-AI-DEMO-001",
                "title": "Critical database performance degradation",
                "description": "Production database showing 300% increase in response times, affecting all customer-facing applications",
                "priority": "P1",
                "category": "Database",
                "impact": "Critical",
                "urgency": "High",
                "affected_users": 5000,
                "reporter": "monitoring.system@company.com",
                "created_date": datetime.now().isoformat()
            },
            {
                "id": "INC-AI-DEMO-002", 
                "title": "Email server intermittent connectivity issues",
                "description": "Users experiencing sporadic email delivery delays and connection timeouts",
                "priority": "P2",
                "category": "Email",
                "impact": "High",
                "urgency": "Medium",
                "affected_users": 800,
                "reporter": "helpdesk@company.com",
                "created_date": datetime.now().isoformat()
            },
            {
                "id": "INC-AI-DEMO-003",
                "title": "Network latency spikes in West Coast region",
                "description": "Multiple reports of network performance issues affecting regional office connectivity",
                "priority": "P3",
                "category": "Network",
                "impact": "Medium",
                "urgency": "Medium",
                "affected_users": 250,
                "reporter": "network.ops@company.com",
                "created_date": datetime.now().isoformat()
            }
        ]
        
        lifecycle_results = []
        
        for incident in incident_scenarios:
            print(f"\n📋 Processing Incident: {incident['id']}")
            
            # Step 1: Create incident in ITIL framework
            self.create_incident(incident)
            self.demo_metrics["incidents_processed"] += 1
            
            # Step 2: AI-powered incident analysis
            print("  🤖 AI Agent Analysis...")
            ai_analysis = self.core_ai_crew.handle_incident(incident)
            self.demo_metrics["ai_recommendations"] += len(ai_analysis.get('recommendations', []))
            
            # Step 3: ML predictions and insights
            print("  🧠 ML Predictions...")
            
            # Category prediction
            category_pred = self.ml_manager.predict_incident_category(incident)
            print(f"    📊 Predicted Category: {category_pred.prediction} ({category_pred.confidence:.2f})")
            
            # Escalation probability
            escalation_pred = self.ml_manager.predict_escalation_probability(incident)
            print(f"    📈 Escalation Risk: {escalation_pred.confidence:.2f}")
            
            # Resolution time prediction
            resolution_pred = self.ml_manager.predict_resolution_time(incident)
            print(f"    ⏱️  Predicted Resolution: {resolution_pred.prediction}")
            
            # Anomaly detection
            anomaly_result = self.ml_manager.detect_anomalies(incident)
            if anomaly_result.prediction:
                print(f"    🚨 Anomaly Detected: {anomaly_result.explanation}")
            
            self.demo_metrics["ml_predictions"] += 4
            
            # Step 4: Enterprise integration notifications
            print("  📢 Enterprise Notifications...")
            self.enterprise_manager.notify_incident_event(incident, "created")
            self.demo_metrics["enterprise_syncs"] += 1
            
            # Step 5: Automated resolution attempt
            print("  🔧 Automated Resolution Attempt...")
            automation_success = self._attempt_automated_resolution(incident, ai_analysis)
            
            if automation_success:
                incident["status"] = "Resolved"
                incident["resolution"] = "Automated resolution successful"
                incident["resolved_date"] = datetime.now().isoformat()
                
                # Update in ITIL framework
                self.update_incident(incident['id'], incident)
                
                # Notify resolution
                self.enterprise_manager.notify_incident_event(incident, "resolved")
                
                print("    ✅ Incident resolved automatically")
                self.demo_metrics["automation_rate"] += 1
            else:
                print("    ⚠️  Automated resolution failed, escalating to human agent")
                incident["status"] = "Escalated"
                self.enterprise_manager.notify_incident_event(incident, "escalated")
            
            lifecycle_results.append({
                "incident_id": incident['id'],
                "ai_analysis": ai_analysis,
                "ml_predictions": {
                    "category": category_pred.prediction,
                    "escalation_risk": escalation_pred.confidence,
                    "resolution_time": resolution_pred.prediction,
                    "anomaly_detected": anomaly_result.prediction
                },
                "automated_resolution": automation_success,
                "final_status": incident["status"]
            })
        
        # Calculate automation rate
        if self.demo_metrics["incidents_processed"] > 0:
            self.demo_metrics["automation_rate"] = (
                self.demo_metrics["automation_rate"] / self.demo_metrics["incidents_processed"]
            )
        
        return lifecycle_results
    
    def _attempt_automated_resolution(self, incident: Dict[str, Any], ai_analysis: Dict[str, Any]) -> bool:
        """Attempt automated resolution based on AI recommendations"""
        
        # Simple rule-based automation logic for demo
        category = incident.get("category", "").lower()
        priority = incident.get("priority", "")
        
        # High success rate for common, lower priority issues
        if category == "email" and priority in ["P3", "P4"]:
            return True  # 100% success for low-priority email issues
        elif category == "network" and priority == "P3":
            return True  # 100% success for medium-priority network issues
        elif category == "database" and priority == "P1":
            return False  # Critical database issues need human intervention
        else:
            # Random success based on AI confidence
            import random
            ai_confidence = ai_analysis.get('confidence', 0.5)
            return random.random() < (ai_confidence * 0.8)  # 80% of AI confidence
    
    def demonstrate_predictive_analytics(self):
        """Demonstrate predictive analytics for proactive incident prevention"""
        print("\n🔮 Demonstrating Predictive Analytics...")
        
        # Generate historical incidents for pattern analysis
        historical_incidents = self.data_generator.generate_incident_data(100)
        
        # Add to ITIL framework for analysis
        for incident in historical_incidents:
            self.create_incident(incident)
        
        # Perform proactive analysis
        prevention_analysis = self.predictive_engine.analyze_proactive_opportunities(historical_incidents)
        
        print("📊 Proactive Prevention Analysis Results:")
        print(f"  🎯 Prevention Opportunities: {len(prevention_analysis['prevention_opportunities'])}")
        print(f"  🚨 Risk Predictions: {len(prevention_analysis['risk_predictions'])}")
        print(f"  💡 Recommended Actions: {len(prevention_analysis['recommended_actions'])}")
        
        # Display top opportunities
        print("\n🔍 Top Prevention Opportunities:")
        for i, opportunity in enumerate(prevention_analysis['prevention_opportunities'][:3], 1):
            print(f"  {i}. {opportunity['description']}")
            print(f"     Action: {opportunity['prevention_action']}")
            print(f"     Impact: {opportunity['potential_impact']}")
            print(f"     Confidence: {opportunity['confidence']:.2f}")
        
        # Display recommendations
        print("\n💡 Recommended Actions:")
        for i, recommendation in enumerate(prevention_analysis['recommended_actions'][:3], 1):
            print(f"  {i}. {recommendation['action']}")
            print(f"     Priority: {recommendation['priority']}")
            print(f"     Timeline: {recommendation['timeline']}")
            print(f"     Expected Impact: {recommendation['expected_impact']}")
        
        self.demo_metrics["patterns_detected"] = len(prevention_analysis['prevention_opportunities'])
        
        # Send AI analysis to enterprise channels
        self.enterprise_manager.notify_ai_analysis({
            "type": "Predictive Analytics",
            "confidence": prevention_analysis['confidence_scores']['overall_analysis'],
            "summary": f"Identified {len(prevention_analysis['prevention_opportunities'])} prevention opportunities",
            "recommendations": prevention_analysis['recommended_actions'][:5],
            "patterns": prevention_analysis['prevention_opportunities']
        })
        
        return prevention_analysis
    
    def demonstrate_extended_agents(self):
        """Demonstrate extended AI agents for Service Request and Release Management"""
        print("\n🚀 Demonstrating Extended AI Agents...")
        
        # Service Request scenario
        service_request = {
            "id": "SR-AI-DEMO-001",
            "title": "New employee laptop setup",
            "description": "Setup laptop and accounts for new marketing team member",
            "category": "Hardware",
            "priority": "P3",
            "requester": "hr@company.com",
            "created_date": datetime.now().isoformat()
        }
        
        print("📋 Processing Service Request...")
        sr_result = self.extended_ai_crew.handle_service_request(service_request)
        
        print(f"  ✅ Service Request Analysis: {sr_result.get('automation_recommendation', 'Manual processing required')}")
        
        # Release Management scenario
        release_request = {
            "id": "REL-AI-DEMO-001",
            "title": "Customer Portal v2.1 Release",
            "description": "Deploy new customer portal with enhanced features",
            "components": ["web-frontend", "api-gateway", "database-updates"],
            "environment": "production",
            "risk_level": "medium",
            "created_date": datetime.now().isoformat()
        }
        
        print("🚀 Processing Release Request...")
        release_result = self.extended_ai_crew.handle_release_planning(release_request)
        
        print(f"  ✅ Release Analysis: {release_result.get('deployment_recommendation', 'Manual deployment required')}")
        
        return {
            "service_request_result": sr_result,
            "release_result": release_result
        }
    
    def demonstrate_cross_platform_sync(self):
        """Demonstrate cross-platform synchronization"""
        print("\n🔄 Demonstrating Cross-Platform Synchronization...")
        
        # Override the enterprise manager to use our demo incidents
        self.enterprise_manager.get_demo_incidents = lambda: self.get_all_incidents()
        
        # Sync to enterprise platforms
        sync_results = self.enterprise_manager.sync_all_incidents(direction="outbound")
        
        print("📊 Synchronization Results:")
        for platform, result in sync_results.items():
            print(f"  🏢 {platform.value}:")
            print(f"    - Records Processed: {result.records_processed}")
            print(f"    - Created: {result.records_created}")
            print(f"    - Updated: {result.records_updated}")
            print(f"    - Failed: {result.records_failed}")
            print(f"    - Success Rate: {((result.records_created + result.records_updated) / result.records_processed * 100):.1f}%")
        
        self.demo_metrics["enterprise_syncs"] += len(sync_results)
        
        return sync_results
    
    def generate_comprehensive_report(self):
        """Generate comprehensive AI demonstration report"""
        print("\n📊 Generating Comprehensive AI Report...")
        
        # Get ML model performance
        ml_performance = self.ml_manager.get_model_performance_summary()
        
        # Get integration status
        integration_status = self.enterprise_manager.get_integration_status()
        
        # Get sync metrics
        sync_metrics = self.enterprise_manager.get_sync_metrics()
        
        # Compile comprehensive report
        report = {
            "demo_summary": {
                "execution_time": datetime.now().isoformat(),
                "incidents_processed": self.demo_metrics["incidents_processed"],
                "ai_recommendations_generated": self.demo_metrics["ai_recommendations"],
                "ml_predictions_made": self.demo_metrics["ml_predictions"],
                "patterns_detected": self.demo_metrics["patterns_detected"],
                "automation_success_rate": f"{self.demo_metrics['automation_rate']:.1%}",
                "enterprise_syncs_performed": self.demo_metrics["enterprise_syncs"]
            },
            "ml_model_performance": ml_performance,
            "integration_status": integration_status,
            "synchronization_metrics": sync_metrics,
            "key_achievements": [
                "✅ 100% incident processing with AI analysis",
                f"✅ {self.demo_metrics['automation_rate']:.1%} automation success rate",
                "✅ Real-time ML predictions and anomaly detection",
                "✅ Proactive incident prevention recommendations",
                "✅ Cross-platform enterprise synchronization",
                "✅ Real-time collaboration notifications",
                "✅ Extended ITIL practice automation"
            ],
            "next_steps": [
                "🔄 Implement continuous ML model retraining",
                "📊 Expand predictive analytics capabilities",
                "🏢 Add more enterprise platform integrations",
                "🤖 Develop custom AI agent specializations",
                "📈 Implement advanced analytics dashboards"
            ]
        }
        
        return report
    
    def run_comprehensive_demo(self):
        """Run the complete AI agents demonstration"""
        print("🤖 COMPREHENSIVE AI AGENTS DEMONSTRATION")
        print("=" * 80)
        print("Showcasing advanced AI capabilities for ITIL framework:")
        print("• Multi-agent incident processing with CrewAI")
        print("• Machine learning predictions and pattern recognition")
        print("• Predictive analytics for proactive prevention")
        print("• Enterprise platform integrations")
        print("• Extended agents for Service Request & Release Management")
        print("• Cross-platform synchronization")
        print("=" * 80)
        
        # Setup phase
        self.setup_enterprise_integrations()
        
        # Training phase
        ml_results = self.train_ml_models()
        
        # Core demonstration phases
        lifecycle_results = self.demonstrate_incident_lifecycle()
        
        predictive_results = self.demonstrate_predictive_analytics()
        
        extended_results = self.demonstrate_extended_agents()
        
        sync_results = self.demonstrate_cross_platform_sync()
        
        # Generate final report
        final_report = self.generate_comprehensive_report()
        
        # Display final summary
        print("\n🎉 DEMONSTRATION COMPLETE!")
        print("=" * 60)
        
        print("\n📊 Final Results Summary:")
        for key, value in final_report["demo_summary"].items():
            print(f"  • {key.replace('_', ' ').title()}: {value}")
        
        print("\n🏆 Key Achievements:")
        for achievement in final_report["key_achievements"]:
            print(f"  {achievement}")
        
        print("\n🚀 Next Steps:")
        for next_step in final_report["next_steps"]:
            print(f"  {next_step}")
        
        print(f"\n✨ AI-Powered ITIL Framework Successfully Demonstrated!")
        print("The framework now includes:")
        print("  🤖 Intelligent multi-agent incident processing")
        print("  🧠 Machine learning-powered predictions")
        print("  🔮 Proactive incident prevention capabilities")
        print("  🏢 Seamless enterprise platform integration")
        print("  📊 Advanced analytics and reporting")
        print("  🚀 Extended ITIL practice automation")
        
        return final_report


def main():
    """Main function to run the comprehensive AI demonstration"""
    demo = ComprehensiveAIDemo()
    final_report = demo.run_comprehensive_demo()
    
    # Save report to file
    report_filename = f"ai_agents_demo_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_filename, 'w') as f:
        json.dump(final_report, f, indent=2, default=str)
    
    print(f"\n📄 Comprehensive report saved to: {report_filename}")


if __name__ == "__main__":
    main()