"""
Real-World AI Agents Example for ITIL Framework

This example demonstrates how AI agents can be used in a production
environment to handle real ITIL scenarios with multiple incidents,
problem identification, and autonomous resolution planning.
"""

import sys
import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_agents.itil_crewai_integration import ITILAgentCrew, AgentRole, create_sample_incident
from integration.integration_manager import ITILIntegrationManager
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ITILAIOpsDemo:
    """Demonstrates AI-powered ITIL operations"""
    
    def __init__(self):
        self.itil_manager = None
        self.agent_crew = None
        self.incident_history = []
        self.problem_records = []
        self.change_requests = []
        self.knowledge_base = []
    
    def setup_environment(self):
        """Setup the ITIL and AI environment"""
        print("🔧 Setting up ITIL AIOps Environment...")
        
        # Initialize ITIL framework
        self.itil_manager = ITILIntegrationManager()
        
        # Create mock ITIL services
        self._setup_mock_services()
        
        # Initialize framework
        results = self.itil_manager.initialize_framework()
        if results["overall_status"] != "SUCCESS":
            raise Exception("Failed to initialize ITIL framework")
        
        # Create AI agent crew
        self.agent_crew = ITILAgentCrew(self.itil_manager)
        
        print("✅ Environment setup completed")
    
    def _setup_mock_services(self):
        """Setup mock ITIL services for demonstration"""
        
        class MockIncidentManagement:
            def __init__(self):
                self.incidents = []
            
            def create_incident(self, **kwargs):
                incident = {"id": f"INC-{len(self.incidents)+1:03d}", **kwargs}
                self.incidents.append(incident)
                return incident
            
            def get_metrics(self, period_days: int):
                return {"total_incidents": len(self.incidents), "resolved_incidents": len(self.incidents)//2}
            
            def get_configuration(self):
                return {"sla_targets": {"P1": "1h", "P2": "4h", "P3": "24h", "P4": "5d"}}
            
            def validate_configuration(self):
                return True
            
            def get_health_status(self):
                return {"status": "healthy", "incidents_open": len(self.incidents)//2}
        
        class MockProblemManagement:
            def __init__(self):
                self.problems = []
            
            def create_problem(self, **kwargs):
                problem = {"id": f"PRB-{len(self.problems)+1:03d}", **kwargs}
                self.problems.append(problem)
                return problem
            
            def get_metrics(self, period_days: int):
                return {"total_problems": len(self.problems), "resolved_problems": len(self.problems)//3}
            
            def get_configuration(self):
                return {"rca_methods": ["5 Whys", "Fishbone", "Fault Tree"]}
            
            def validate_configuration(self):
                return True
            
            def get_health_status(self):
                return {"status": "healthy", "problems_open": len(self.problems)//3}
        
        # Register services
        self.itil_manager.register_practice("incident_management", MockIncidentManagement())
        self.itil_manager.register_practice("problem_management", MockProblemManagement(), ["incident_management"])
    
    def create_realistic_incidents(self) -> List[Dict[str, Any]]:
        """Create a set of realistic incidents for demonstration"""
        
        base_time = datetime.now() - timedelta(hours=8)
        
        incidents = [
            {
                "id": "INC-2025-001",
                "title": "Email server not responding",
                "description": "Users unable to access email. Server appears to be down. Critical business impact.",
                "category": "Email",
                "priority": "P1",
                "urgency": "High",
                "impact": "Critical",
                "affected_users": 500,
                "reported_time": (base_time + timedelta(hours=0)).isoformat(),
                "reporter": {"name": "IT Operations", "dept": "IT"},
                "business_impact": "Critical - All email communication stopped"
            },
            {
                "id": "INC-2025-002", 
                "title": "VPN connection slow",
                "description": "Remote workers reporting very slow VPN connections. Takes 5+ minutes to connect.",
                "category": "Network",
                "priority": "P2",
                "urgency": "Medium",
                "impact": "High",
                "affected_users": 150,
                "reported_time": (base_time + timedelta(hours=1)).isoformat(),
                "reporter": {"name": "Sarah Johnson", "dept": "HR"},
                "business_impact": "High - Remote workers cannot access systems efficiently"
            },
            {
                "id": "INC-2025-003",
                "title": "Email attachments not downloading",
                "description": "Users can receive emails but attachments fail to download. Error message appears.",
                "category": "Email", 
                "priority": "P2",
                "urgency": "Medium",
                "impact": "Medium",
                "affected_users": 200,
                "reported_time": (base_time + timedelta(hours=2)).isoformat(),
                "reporter": {"name": "Mike Chen", "dept": "Finance"},
                "business_impact": "Medium - Important documents cannot be accessed"
            },
            {
                "id": "INC-2025-004",
                "title": "Slow email response times",
                "description": "Email system responding slowly. Takes 30+ seconds to open emails.",
                "category": "Email",
                "priority": "P3", 
                "urgency": "Low",
                "impact": "Medium",
                "affected_users": 300,
                "reported_time": (base_time + timedelta(hours=3)).isoformat(),
                "reporter": {"name": "Lisa Brown", "dept": "Marketing"},
                "business_impact": "Medium - Productivity impact due to slow response"
            },
            {
                "id": "INC-2025-005",
                "title": "Cannot send emails with large attachments",
                "description": "Users cannot send emails with attachments larger than 5MB. System times out.",
                "category": "Email",
                "priority": "P3",
                "urgency": "Low", 
                "impact": "Low",
                "affected_users": 50,
                "reported_time": (base_time + timedelta(hours=4)).isoformat(),
                "reporter": {"name": "David Wilson", "dept": "Sales"},
                "business_impact": "Low - Workaround available using file sharing"
            },
            {
                "id": "INC-2025-006",
                "title": "Database connection timeouts",
                "description": "CRM application showing database connection timeout errors. Intermittent issue.",
                "category": "Database",
                "priority": "P2",
                "urgency": "Medium",
                "impact": "High", 
                "affected_users": 80,
                "reported_time": (base_time + timedelta(hours=5)).isoformat(),
                "reporter": {"name": "Jennifer Davis", "dept": "Sales"},
                "business_impact": "High - CRM system unreliable, affecting customer service"
            }
        ]
        
        return incidents
    
    def process_incidents_with_ai(self, incidents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process multiple incidents using AI agents"""
        
        print(f"\n🤖 AI Agents Processing {len(incidents)} Incidents...")
        print("=" * 60)
        
        results = {
            "incidents_processed": [],
            "patterns_identified": [],
            "problems_recommended": [],
            "escalations_needed": [],
            "knowledge_gaps": [],
            "processing_summary": {}
        }
        
        for i, incident in enumerate(incidents, 1):
            print(f"\n📋 Processing Incident {i}/{len(incidents)}: {incident['id']}")
            print(f"   Title: {incident['title']}")
            print(f"   Priority: {incident['priority']} | Impact: {incident['impact']} | Users: {incident['affected_users']}")
            
            # Process with AI agents
            try:
                agent_result = self.agent_crew.handle_incident(incident)
                
                # Store results
                incident_result = {
                    "incident_id": incident['id'],
                    "status": agent_result['status'],
                    "confidence": agent_result.get('confidence_score', 0),
                    "recommendations": agent_result.get('recommendations', {}),
                    "next_steps": agent_result.get('next_steps', [])
                }
                
                results["incidents_processed"].append(incident_result)
                
                # Check for escalations
                if agent_result.get('recommendations', {}).get('escalation_needed'):
                    results["escalations_needed"].append(incident['id'])
                    print(f"   🚨 Escalation needed for {incident['id']}")
                
                # Check for problem creation
                if agent_result.get('recommendations', {}).get('problem_creation'):
                    results["problems_recommended"].append(incident['id'])
                    print(f"   🔍 Problem record recommended for {incident['id']}")
                
                # Check for knowledge updates
                if agent_result.get('recommendations', {}).get('knowledge_update'):
                    results["knowledge_gaps"].append(incident['id'])
                    print(f"   📚 Knowledge base update needed for {incident['id']}")
                
                print(f"   ✅ Processed with {agent_result.get('confidence_score', 0):.2f} confidence")
                
            except Exception as e:
                print(f"   ❌ Error processing {incident['id']}: {e}")
                results["incidents_processed"].append({
                    "incident_id": incident['id'],
                    "status": "error",
                    "error": str(e)
                })
        
        # Analyze patterns across all incidents
        print(f"\n🔍 Analyzing Patterns Across All Incidents...")
        patterns = self._analyze_incident_patterns(incidents)
        results["patterns_identified"] = patterns
        
        # Generate processing summary
        results["processing_summary"] = self._generate_processing_summary(results)
        
        return results
    
    def _analyze_incident_patterns(self, incidents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze patterns across multiple incidents"""
        
        # Group by category
        category_groups = {}
        for incident in incidents:
            category = incident.get('category', 'Unknown')
            if category not in category_groups:
                category_groups[category] = []
            category_groups[category].append(incident)
        
        patterns = []
        
        # Check for patterns in each category
        for category, cat_incidents in category_groups.items():
            if len(cat_incidents) >= 3:  # Pattern threshold
                pattern = {
                    "type": "recurring_category",
                    "category": category,
                    "incident_count": len(cat_incidents),
                    "affected_users_total": sum(inc.get('affected_users', 0) for inc in cat_incidents),
                    "priority_distribution": self._get_priority_distribution(cat_incidents),
                    "recommendation": f"Create problem record for recurring {category} issues",
                    "incidents": [inc['id'] for inc in cat_incidents]
                }
                patterns.append(pattern)
                print(f"   📊 Pattern detected: {len(cat_incidents)} {category} incidents")
        
        # Check for time-based patterns
        time_pattern = self._analyze_time_patterns(incidents)
        if time_pattern:
            patterns.append(time_pattern)
        
        return patterns
    
    def _get_priority_distribution(self, incidents: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get priority distribution for incidents"""
        distribution = {}
        for incident in incidents:
            priority = incident.get('priority', 'Unknown')
            distribution[priority] = distribution.get(priority, 0) + 1
        return distribution
    
    def _analyze_time_patterns(self, incidents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze time-based patterns in incidents"""
        # Mock implementation - in real system would analyze actual timestamps
        return {
            "type": "time_based",
            "pattern": "morning_peak", 
            "description": "Higher incident volume during morning hours (9-11 AM)",
            "recommendation": "Increase monitoring during peak hours",
            "confidence": 0.75
        }
    
    def _generate_processing_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of processing results"""
        
        total_incidents = len(results["incidents_processed"])
        successful_processing = len([r for r in results["incidents_processed"] if r["status"] != "error"])
        
        return {
            "total_incidents": total_incidents,
            "successfully_processed": successful_processing,
            "processing_success_rate": (successful_processing / total_incidents * 100) if total_incidents > 0 else 0,
            "escalations_needed": len(results["escalations_needed"]),
            "problems_recommended": len(results["problems_recommended"]),
            "knowledge_gaps_identified": len(results["knowledge_gaps"]),
            "patterns_found": len(results["patterns_identified"]),
            "average_confidence": self._calculate_average_confidence(results["incidents_processed"])
        }
    
    def _calculate_average_confidence(self, incident_results: List[Dict[str, Any]]) -> float:
        """Calculate average confidence score"""
        confidences = [r.get("confidence", 0) for r in incident_results if "confidence" in r]
        return sum(confidences) / len(confidences) if confidences else 0
    
    def demonstrate_problem_management(self, patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Demonstrate AI-driven problem management"""
        
        print(f"\n🔍 AI-Driven Problem Management")
        print("=" * 40)
        
        problems_created = []
        
        for pattern in patterns:
            if pattern["type"] == "recurring_category" and pattern["incident_count"] >= 3:
                print(f"\n📋 Creating Problem Record for {pattern['category']} Issues...")
                
                # Use AI to analyze the pattern and create problem record
                problem_data = {
                    "title": f"Recurring {pattern['category']} Performance Issues",
                    "description": f"Pattern identified: {pattern['incident_count']} related incidents affecting {pattern['affected_users_total']} users",
                    "category": pattern['category'],
                    "priority": self._determine_problem_priority(pattern),
                    "related_incidents": pattern['incidents'],
                    "root_cause_hypothesis": self._generate_root_cause_hypothesis(pattern),
                    "investigation_plan": self._create_investigation_plan(pattern)
                }
                
                problems_created.append(problem_data)
                
                print(f"   ✅ Problem PRB-{len(problems_created):03d} created")
                print(f"   🎯 Priority: {problem_data['priority']}")
                print(f"   🔗 Linked incidents: {len(problem_data['related_incidents'])}")
                print(f"   💡 Hypothesis: {problem_data['root_cause_hypothesis']}")
        
        return problems_created
    
    def _determine_problem_priority(self, pattern: Dict[str, Any]) -> str:
        """Determine problem priority based on pattern analysis"""
        affected_users = pattern.get('affected_users_total', 0)
        incident_count = pattern.get('incident_count', 0)
        
        if affected_users > 300 or incident_count >= 5:
            return "P1"
        elif affected_users > 100 or incident_count >= 4:
            return "P2"
        else:
            return "P3"
    
    def _generate_root_cause_hypothesis(self, pattern: Dict[str, Any]) -> str:
        """Generate root cause hypothesis using AI analysis"""
        category = pattern.get('category', 'Unknown')
        
        hypotheses = {
            "Email": "Email server resource exhaustion due to increased load and insufficient capacity planning",
            "Network": "Network infrastructure bandwidth limitations during peak usage periods",
            "Database": "Database performance degradation due to query optimization issues or hardware constraints",
            "Server": "Server hardware aging and inadequate resource allocation for current workload"
        }
        
        return hypotheses.get(category, "Unknown underlying system issue requiring investigation")
    
    def _create_investigation_plan(self, pattern: Dict[str, Any]) -> List[str]:
        """Create investigation plan for the problem"""
        category = pattern.get('category', 'Unknown')
        
        plans = {
            "Email": [
                "Review email server performance metrics and resource utilization",
                "Analyze email server logs for error patterns and bottlenecks",
                "Check email server configuration and capacity limits",
                "Review recent changes to email infrastructure",
                "Perform load testing on email server during off-peak hours"
            ],
            "Network": [
                "Analyze network traffic patterns and bandwidth utilization",
                "Review network device performance and error logs",
                "Check for network configuration changes or updates",
                "Perform network latency and throughput testing",
                "Review network capacity planning and growth projections"
            ],
            "Database": [
                "Analyze database performance metrics and query execution times",
                "Review database server resource utilization (CPU, memory, I/O)",
                "Check for database configuration changes or schema modifications",
                "Analyze slow query logs and execution plans",
                "Review database maintenance schedules and optimization history"
            ]
        }
        
        return plans.get(category, [
            "Gather detailed information about affected systems",
            "Perform root cause analysis using systematic approach",
            "Review recent changes and their potential impact",
            "Analyze system performance and resource utilization",
            "Develop and test potential solutions"
        ])
    
    def generate_comprehensive_report(self, processing_results: Dict[str, Any], problems_created: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive AIOps report"""
        
        print(f"\n📊 Generating Comprehensive AIOps Report...")
        
        report = {
            "report_timestamp": datetime.now().isoformat(),
            "executive_summary": self._create_executive_summary(processing_results, problems_created),
            "incident_analysis": processing_results,
            "problem_management": {
                "problems_created": problems_created,
                "total_problems": len(problems_created),
                "root_causes_identified": len([p for p in problems_created if p.get('root_cause_hypothesis')])
            },
            "ai_performance": {
                "agent_effectiveness": self._assess_agent_effectiveness(processing_results),
                "automation_rate": self._calculate_automation_rate(processing_results),
                "confidence_metrics": self._analyze_confidence_metrics(processing_results)
            },
            "recommendations": self._generate_strategic_recommendations(processing_results, problems_created),
            "next_actions": self._determine_next_actions(processing_results, problems_created)
        }
        
        return report
    
    def _create_executive_summary(self, processing_results: Dict[str, Any], problems_created: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create executive summary of AIOps session"""
        summary = processing_results["processing_summary"]
        
        return {
            "incidents_handled": summary["total_incidents"],
            "automation_success_rate": f"{summary['processing_success_rate']:.1f}%",
            "critical_escalations": summary["escalations_needed"],
            "problems_identified": len(problems_created),
            "key_finding": f"AI agents identified {summary['patterns_found']} significant patterns requiring attention",
            "business_impact": "Proactive problem identification and automated triage improved incident response efficiency"
        }
    
    def _assess_agent_effectiveness(self, processing_results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the effectiveness of AI agents"""
        summary = processing_results["processing_summary"]
        
        return {
            "processing_accuracy": f"{summary['processing_success_rate']:.1f}%",
            "average_confidence": f"{summary['average_confidence']:.2f}",
            "pattern_detection": "Excellent" if summary["patterns_found"] > 0 else "Good",
            "escalation_precision": "High" if summary["escalations_needed"] <= summary["total_incidents"] * 0.3 else "Medium"
        }
    
    def _calculate_automation_rate(self, processing_results: Dict[str, Any]) -> float:
        """Calculate the automation rate achieved"""
        total = processing_results["processing_summary"]["total_incidents"]
        escalations = processing_results["processing_summary"]["escalations_needed"]
        
        # Automation rate = incidents handled without human escalation
        automation_rate = ((total - escalations) / total * 100) if total > 0 else 0
        return round(automation_rate, 1)
    
    def _analyze_confidence_metrics(self, processing_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze confidence metrics from AI processing"""
        incidents = processing_results["incidents_processed"]
        confidences = [r.get("confidence", 0) for r in incidents if "confidence" in r]
        
        if not confidences:
            return {"status": "No confidence data available"}
        
        return {
            "average_confidence": round(sum(confidences) / len(confidences), 2),
            "high_confidence_rate": f"{len([c for c in confidences if c >= 0.8]) / len(confidences) * 100:.1f}%",
            "low_confidence_incidents": len([c for c in confidences if c < 0.6]),
            "confidence_trend": "Stable" if max(confidences) - min(confidences) < 0.3 else "Variable"
        }
    
    def _generate_strategic_recommendations(self, processing_results: Dict[str, Any], problems_created: List[Dict[str, Any]]) -> List[str]:
        """Generate strategic recommendations based on analysis"""
        recommendations = []
        
        # Based on processing results
        summary = processing_results["processing_summary"]
        
        if summary["patterns_found"] > 1:
            recommendations.append("Implement proactive monitoring for identified service patterns to prevent future incidents")
        
        if summary["escalations_needed"] > summary["total_incidents"] * 0.4:
            recommendations.append("Review escalation criteria and agent training to reduce unnecessary escalations")
        
        if summary["knowledge_gaps_identified"] > 0:
            recommendations.append("Update knowledge base with new solutions identified during incident resolution")
        
        # Based on problems created
        if len(problems_created) > 0:
            recommendations.append("Prioritize root cause analysis for identified recurring issues to prevent future incidents")
        
        # AI-specific recommendations
        if summary["average_confidence"] < 0.7:
            recommendations.append("Enhance AI agent training with additional incident data to improve confidence scores")
        
        return recommendations
    
    def _determine_next_actions(self, processing_results: Dict[str, Any], problems_created: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Determine next actions based on analysis"""
        actions = []
        
        # Immediate actions for escalations
        if processing_results["escalations_needed"]:
            actions.append({
                "priority": "High",
                "action": "Review and address escalated incidents",
                "owner": "Senior Technical Team",
                "timeline": "Immediate",
                "description": f"Address {len(processing_results['escalations_needed'])} incidents requiring escalation"
            })
        
        # Problem management actions
        for problem in problems_created:
            actions.append({
                "priority": problem["priority"],
                "action": f"Execute investigation plan for {problem['title']}",
                "owner": "Problem Management Team",
                "timeline": "1-3 days",
                "description": f"Investigate root cause of recurring {problem['category']} issues"
            })
        
        # Knowledge management actions
        if processing_results["processing_summary"]["knowledge_gaps_identified"] > 0:
            actions.append({
                "priority": "Medium",
                "action": "Update knowledge base with new solutions",
                "owner": "Knowledge Management Team", 
                "timeline": "1 week",
                "description": "Capture and document solutions from recent incident resolutions"
            })
        
        return actions
    
    def run_comprehensive_demo(self):
        """Run the complete AIOps demonstration"""
        
        print("🚀 ITIL AIOps Comprehensive Demonstration")
        print("=" * 60)
        
        try:
            # Setup environment
            self.setup_environment()
            
            # Create realistic incident scenarios
            incidents = self.create_realistic_incidents()
            print(f"📋 Created {len(incidents)} realistic incident scenarios")
            
            # Process incidents with AI agents
            processing_results = self.process_incidents_with_ai(incidents)
            
            # Demonstrate problem management
            problems_created = self.demonstrate_problem_management(processing_results["patterns_identified"])
            
            # Generate comprehensive report
            final_report = self.generate_comprehensive_report(processing_results, problems_created)
            
            # Display results
            self.display_final_results(final_report)
            
            # Save report
            self.save_report(final_report)
            
            return True
            
        except Exception as e:
            print(f"❌ Demo failed: {e}")
            logger.exception("Demo execution failed")
            return False
    
    def display_final_results(self, report: Dict[str, Any]):
        """Display final results of the AIOps demonstration"""
        
        print(f"\n🎯 ITIL AIOps Demonstration Results")
        print("=" * 50)
        
        # Executive Summary
        exec_summary = report["executive_summary"]
        print(f"\n📈 Executive Summary:")
        print(f"  📊 Incidents Processed: {exec_summary['incidents_handled']}")
        print(f"  🤖 Automation Success: {exec_summary['automation_success_rate']}")
        print(f"  🚨 Critical Escalations: {exec_summary['critical_escalations']}")
        print(f"  🔍 Problems Identified: {exec_summary['problems_identified']}")
        print(f"  💡 Key Finding: {exec_summary['key_finding']}")
        
        # AI Performance
        ai_perf = report["ai_performance"]
        print(f"\n🤖 AI Agent Performance:")
        print(f"  🎯 Processing Accuracy: {ai_perf['agent_effectiveness']['processing_accuracy']}")
        print(f"  📈 Average Confidence: {ai_perf['agent_effectiveness']['average_confidence']}")
        print(f"  🔄 Automation Rate: {ai_perf['automation_rate']}%")
        print(f"  🔍 Pattern Detection: {ai_perf['agent_effectiveness']['pattern_detection']}")
        
        # Strategic Recommendations
        print(f"\n💡 Strategic Recommendations:")
        for i, rec in enumerate(report["recommendations"], 1):
            print(f"  {i}. {rec}")
        
        # Next Actions
        print(f"\n📋 Next Actions:")
        for action in report["next_actions"]:
            print(f"  🎯 {action['priority']}: {action['action']}")
            print(f"     Owner: {action['owner']} | Timeline: {action['timeline']}")
        
        print(f"\n🎉 Demonstration Completed Successfully!")
    
    def save_report(self, report: Dict[str, Any]):
        """Save the comprehensive report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"itil_aiops_report_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"💾 Report saved: {filename}")
        except Exception as e:
            print(f"❌ Failed to save report: {e}")


def main():
    """Main execution function"""
    print("Starting ITIL AIOps Comprehensive Demo...")
    
    demo = ITILAIOpsDemo()
    success = demo.run_comprehensive_demo()
    
    if success:
        print(f"\n✅ ITIL AIOps demonstration completed successfully!")
        print(f"🎯 Key achievements:")
        print(f"   • Autonomous incident analysis and classification")
        print(f"   • Intelligent pattern recognition across multiple incidents")
        print(f"   • Automated problem identification and investigation planning")
        print(f"   • Multi-agent collaboration for complex ITIL processes")
        print(f"   • Comprehensive reporting and strategic recommendations")
    else:
        print(f"❌ Demonstration failed - check logs for details")
    
    return success


if __name__ == "__main__":
    main()