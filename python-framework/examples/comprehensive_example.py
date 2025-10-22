#!/usr/bin/env python3
"""
ITIL 4 Python Framework - Comprehensive Example

This example demonstrates the full capabilities of the ITIL 4 Python Framework
including integrated workflows, metrics, and real-world scenarios.

Run this script to see the framework in action:
    python examples/comprehensive_example.py
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import the framework
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from python_framework import ITILFramework
from python_framework.core import Person, ConfigurationItem, Impact, Urgency, Priority
from python_framework.practices import (
    IncidentCategory, IncidentState, EscalationLevel,
    ProblemCategory, ProblemType, RootCauseAnalysisMethod,
    ChangeCategory, ChangeType, ChangeRisk, ImplementationPlan, BackoutPlan
)


def print_banner(title: str, char: str = "="):
    """Print a formatted banner"""
    print(f"\n{char * 60}")
    print(f"{title:^60}")
    print(f"{char * 60}")


def print_section(title: str):
    """Print a section header"""
    print(f"\n{'─' * 40}")
    print(f"📋 {title}")
    print(f"{'─' * 40}")


def create_sample_people():
    """Create sample people for the demonstration"""
    return {
        'end_user': Person("1", "Alice Johnson", "alice.johnson@company.com", "Business Analyst", "Finance"),
        'service_desk_agent': Person("2", "Bob Smith", "bob.smith@company.com", "Service Desk Agent", "IT Support"),
        'network_engineer': Person("3", "Carol Davis", "carol.davis@company.com", "Network Engineer", "IT Infrastructure"),
        'problem_analyst': Person("4", "David Wilson", "david.wilson@company.com", "Problem Manager", "IT Support"),
        'change_manager': Person("5", "Eva Brown", "eva.brown@company.com", "Change Manager", "IT Governance"),
        'it_manager': Person("6", "Frank Miller", "frank.miller@company.com", "IT Manager", "IT Management"),
        'system_admin': Person("7", "Grace Lee", "grace.lee@company.com", "System Administrator", "IT Infrastructure")
    }


def create_sample_cis():
    """Create sample Configuration Items"""
    return {
        'email_server': ConfigurationItem("CI001", "Email Server", "Server", "Production", "Production"),
        'web_server': ConfigurationItem("CI002", "Web Application Server", "Server", "Production", "Production"),
        'database_server': ConfigurationItem("CI003", "Primary Database Server", "Database", "Production", "Production"),
        'network_switch': ConfigurationItem("CI004", "Core Network Switch", "Network Device", "Production", "Production"),
        'firewall': ConfigurationItem("CI005", "Perimeter Firewall", "Security Device", "Production", "Production")
    }


def demonstrate_incident_management(itil: ITILFramework, people: dict, cis: dict):
    """Demonstrate incident management capabilities"""
    print_section("Incident Management Demonstration")
    
    incidents = []
    
    # Create various types of incidents
    print("Creating different types of incidents...")
    
    # P1 Critical Incident
    critical_incident = itil.create_incident(
        short_description="Email server completely down",
        description="Email server is not responding. All users unable to send/receive email.",
        caller=people['end_user'],
        category=IncidentCategory.APPLICATION,
        impact=Impact.HIGH,
        urgency=Urgency.HIGH,
        affected_ci=cis['email_server']
    )
    incidents.append(critical_incident)
    print(f"✅ Created P1 Critical incident: {critical_incident.number}")
    
    # P2 High Priority Incident
    high_incident = itil.create_incident(
        short_description="Slow web application response",
        description="Web application loading slowly, affecting productivity for 50+ users.",
        caller=people['end_user'],
        category=IncidentCategory.APPLICATION,
        impact=Impact.MEDIUM,
        urgency=Urgency.HIGH,
        affected_ci=cis['web_server']
    )
    incidents.append(high_incident)
    print(f"✅ Created P2 High incident: {high_incident.number}")
    
    # P3 Medium Priority Incident
    medium_incident = itil.create_incident(
        short_description="Printer offline in Building A",
        description="Network printer in Building A Conference Room is offline.",
        caller=people['end_user'],
        category=IncidentCategory.HARDWARE,
        impact=Impact.LOW,
        urgency=Urgency.MEDIUM
    )
    incidents.append(medium_incident)
    print(f"✅ Created P3 Medium incident: {medium_incident.number}")
    
    # Demonstrate incident workflow
    print(f"\n📝 Processing critical incident {critical_incident.number}:")
    
    # Acknowledge incident
    critical_incident.acknowledge(people['service_desk_agent'])
    print(f"   • Acknowledged by {people['service_desk_agent'].name}")
    
    # Assign to technical team
    critical_incident.assign(people['system_admin'], "Infrastructure Team")
    print(f"   • Assigned to {people['system_admin'].name}")
    
    # Add work notes
    critical_incident.add_work_note(
        "Investigating email server connectivity", 
        people['system_admin']
    )
    print(f"   • Work note added: Investigating connectivity")
    
    # Escalate if needed
    critical_incident.escalate(
        EscalationLevel.L2, 
        "Requires senior engineering expertise", 
        people['system_admin']
    )
    print(f"   • Escalated to L2 support")
    
    # Resolve incident
    critical_incident.resolve(
        people['system_admin'], 
        "Email server restarted. Root cause was memory leak in mail processing service."
    )
    print(f"   • Resolved by {people['system_admin'].name}")
    
    # Check SLA status
    sla_status = critical_incident.check_sla_breach()
    print(f"   • SLA Status: Response breach: {sla_status['response_breach']}, Resolution breach: {sla_status['resolution_breach']}")
    
    return incidents


def demonstrate_problem_management(itil: ITILFramework, people: dict, incidents: list):
    """Demonstrate problem management capabilities"""
    print_section("Problem Management Demonstration")
    
    # Create related incidents for pattern analysis
    print("Creating additional related incidents...")
    
    related_incidents = []
    for i in range(3):
        incident = itil.create_incident(
            short_description=f"Email performance issue #{i+1}",
            description=f"Users reporting intermittent email delays - occurrence #{i+1}",
            caller=people['end_user'],
            category=IncidentCategory.APPLICATION,
            impact=Impact.MEDIUM,
            urgency=Urgency.MEDIUM
        )
        related_incidents.append(incident)
        print(f"✅ Created related incident: {incident.number}")
    
    # Create problem from incident pattern
    print(f"\n🔍 Creating problem from incident pattern...")
    
    incident_numbers = [inc.number for inc in related_incidents]
    problem = itil.create_problem_from_incidents(
        incident_numbers=incident_numbers,
        short_description="Recurring email performance degradation",
        description="Multiple incidents indicate systemic email server performance issues",
        category=ProblemCategory.APPLICATION,
        analyst=people['problem_analyst']
    )
    
    print(f"✅ Created problem: {problem.number}")
    print(f"   • Linked to {len(incident_numbers)} incidents")
    
    # Demonstrate problem investigation workflow
    print(f"\n🔬 Problem investigation workflow:")
    
    # Start investigation
    problem.start_investigation(people['problem_analyst'])
    print(f"   • Investigation started by {people['problem_analyst'].name}")
    
    # Add symptoms
    symptoms = [
        "Email response times > 30 seconds during peak hours",
        "Intermittent connection timeouts",
        "Memory usage spikes on email server",
        "Database query performance degradation"
    ]
    
    for symptom in symptoms:
        problem.add_symptom(symptom, people['problem_analyst'])
    print(f"   • Added {len(symptoms)} symptoms")
    
    # Conduct root cause analysis
    print(f"   • Conducting root cause analysis using 5 Whys method...")
    
    rca_guidance = itil.problem_management.conduct_root_cause_analysis(
        problem.number,
        RootCauseAnalysisMethod.FIVE_WHYS,
        people['problem_analyst']
    )
    
    # Identify root cause
    from python_framework.practices.problem_management import RootCause
    
    root_cause = RootCause(
        description="Email server database indexes are fragmented and not optimized",
        analysis_method=RootCauseAnalysisMethod.FIVE_WHYS,
        contributing_factors=[
            "Database maintenance not performed regularly",
            "Query optimization not implemented", 
            "Index fragmentation > 80%",
            "Statistics not updated"
        ],
        evidence=[
            "Database performance counters show slow query execution",
            "Index fragmentation analysis results",
            "Email server logs show database timeout errors"
        ],
        confidence_level=95,
        identified_by=people['problem_analyst']
    )
    
    problem.identify_root_cause(root_cause, people['problem_analyst'])
    print(f"   • Root cause identified with {root_cause.confidence_level}% confidence")
    
    # Create known error with workaround
    known_error = problem.create_known_error(
        people['problem_analyst'],
        "Temporary workaround: Restart email service every 4 hours during business hours until permanent fix is implemented"
    )
    print(f"   • Known Error created: {known_error.id}")
    
    return problem


def demonstrate_change_enablement(itil: ITILFramework, people: dict, problem):
    """Demonstrate change enablement capabilities"""
    print_section("Change Enablement Demonstration")
    
    # Create change to resolve the problem
    print(f"Creating change to resolve problem {problem.number}...")
    
    change = itil.create_change_from_problem(
        problem_number=problem.number,
        change_description="Optimize email server database performance",
        requester=people['problem_analyst']
    )
    
    print(f"✅ Created change: {change.number}")
    print(f"   • Category: {change.category.value}")
    print(f"   • Priority: {change.priority.value}")
    
    # Demonstrate change workflow
    print(f"\n⚙️ Change enablement workflow:")
    
    # Submit for assessment
    change.submit_for_assessment(people['problem_analyst'])
    print(f"   • Submitted for assessment")
    
    # Assess the change
    change.assess_change(
        people['change_manager'],
        ChangeRisk.MEDIUM,
        Impact.MEDIUM,
        Urgency.MEDIUM,
        "Standard database optimization with tested procedures"
    )
    print(f"   • Assessed by {people['change_manager'].name}")
    print(f"   • Risk: {change.risk.value}, Impact: {change.impact.value}")
    
    # Add approvers
    approval = change.add_approver(people['it_manager'])
    print(f"   • Approver added: {people['it_manager'].name}")
    
    # Create implementation plan
    impl_plan = ImplementationPlan(
        description="Database optimization and email server tuning",
        steps=[
            "1. Backup email database",
            "2. Analyze current index usage and fragmentation",
            "3. Rebuild fragmented indexes",
            "4. Update database statistics",
            "5. Optimize email server configuration",
            "6. Test email functionality",
            "7. Monitor performance for 2 hours",
            "8. Document changes made"
        ],
        estimated_duration=timedelta(hours=6),
        resources_required=["Database Administrator", "Email Administrator", "Maintenance Window"],
        technical_requirements=["Database backup space", "Performance monitoring tools"]
    )
    change.implementation_plan = impl_plan
    print(f"   • Implementation plan created with {len(impl_plan.steps)} steps")
    
    # Create backout plan
    backout_plan = BackoutPlan(
        description="Restore email server to previous state",
        steps=[
            "1. Stop email services",
            "2. Restore database from backup",
            "3. Restore previous email server configuration",
            "4. Start email services",
            "5. Verify email functionality",
            "6. Notify users of restoration"
        ],
        estimated_duration=timedelta(hours=2),
        trigger_conditions=[
            "Email service unavailable for > 15 minutes",
            "Database performance worse than baseline",
            "User complaints > 10 within 1 hour"
        ]
    )
    change.backout_plan = backout_plan
    print(f"   • Backout plan created with {len(backout_plan.steps)} steps")
    
    # Approve the change
    change.approve_change(
        people['it_manager'], 
        "Approved for implementation during next maintenance window. Risk is acceptable."
    )
    print(f"   • Change approved by {people['it_manager'].name}")
    
    # Schedule the change
    start_time = datetime.now() + timedelta(days=2, hours=20)  # Saturday 8 PM
    end_time = start_time + timedelta(hours=6)
    
    change.schedule_change(people['change_manager'], start_time, end_time)
    print(f"   • Change scheduled: {start_time.strftime('%Y-%m-%d %H:%M')} - {end_time.strftime('%Y-%m-%d %H:%M')}")
    
    # Check for conflicts
    conflicts = itil.change_enablement.check_change_conflicts(change)
    print(f"   • Conflict check: {len(conflicts)} conflicts found")
    
    return change


def demonstrate_integration_workflows(itil: ITILFramework, people: dict):
    """Demonstrate integration between practices"""
    print_section("Integration Workflows Demonstration")
    
    print("🔗 Demonstrating cross-practice integration...")
    
    # Get integration report
    integration_report = itil.get_integration_report()
    
    print(f"Cross-reference Statistics:")
    print(f"   • Incidents with Problems: {integration_report['cross_references']['incidents_with_problems']}")
    print(f"   • Problems with Changes: {integration_report['cross_references']['problems_with_changes']}")
    print(f"   • Changes with Incidents: {integration_report['cross_references']['changes_with_incidents']}")
    print(f"   • Integration Health: {integration_report['integration_health']}")
    
    # Show workflow examples
    print(f"\n📋 Available Integration Workflows:")
    for workflow in integration_report['workflow_examples']:
        print(f"\n   {workflow['name']}:")
        print(f"   {workflow['description']}")
        for step in workflow['steps']:
            print(f"      {step}")


def demonstrate_metrics_and_reporting(itil: ITILFramework):
    """Demonstrate metrics and reporting capabilities"""
    print_section("Metrics and Reporting Demonstration")
    
    print("📊 Generating comprehensive metrics...")
    
    # Get dashboard metrics
    dashboard = itil.get_dashboard_metrics(period_days=30)
    
    print(f"\n📈 Dashboard Summary (Last 30 days):")
    print(f"   Framework Version: {dashboard['framework_info']['version']}")
    print(f"   Generated At: {dashboard['framework_info']['generated_at'][:19]}")
    
    # Incident Management Metrics
    inc_metrics = dashboard['incident_management']
    if 'error' not in inc_metrics:
        print(f"\n🎫 Incident Management:")
        print(f"   • Total Incidents: {inc_metrics['total_incidents']}")
        print(f"   • Closed Incidents: {inc_metrics['closed_incidents']}")
        print(f"   • Resolution Rate: {inc_metrics['resolution_rate']:.1f}%")
        print(f"   • Avg Resolution Time: {inc_metrics['avg_resolution_time_hours']:.1f} hours")
        print(f"   • SLA Compliance: {inc_metrics['sla_compliance_rate']:.1f}%")
        print(f"   • Major Incidents: {inc_metrics['major_incidents']}")
    
    # Problem Management Metrics
    prob_metrics = dashboard['problem_management']
    if 'error' not in prob_metrics:
        print(f"\n🔍 Problem Management:")
        print(f"   • Total Problems: {prob_metrics['total_problems']}")
        print(f"   • Closed Problems: {prob_metrics['closed_problems']}")
        print(f"   • Resolution Rate: {prob_metrics['resolution_rate']:.1f}%")
        print(f"   • Avg Resolution Time: {prob_metrics['avg_resolution_time_days']:.1f} days")
        print(f"   • RCA Completion Rate: {prob_metrics['rca_completion_rate']:.1f}%")
        print(f"   • Proactive Ratio: {prob_metrics['proactive_ratio']:.1f}%")
        print(f"   • Known Errors Created: {prob_metrics['problems_with_known_errors']}")
    
    # Change Enablement Metrics
    chg_metrics = dashboard['change_enablement']
    if 'error' not in chg_metrics:
        print(f"\n⚙️ Change Enablement:")
        print(f"   • Total Changes: {chg_metrics['total_changes']}")
        print(f"   • Successful Changes: {chg_metrics['successful_changes']}")
        print(f"   • Success Rate: {chg_metrics['success_rate']:.1f}%")
        print(f"   • Avg Duration: {chg_metrics['avg_implementation_duration_hours']:.1f} hours")
        print(f"   • Standard Templates: {chg_metrics['standard_change_templates']}")
    
    # Integration Metrics
    int_metrics = dashboard['integration_metrics']
    print(f"\n🔗 Integration Metrics:")
    print(f"   • Total Records: {int_metrics['total_records']}")
    print(f"   • Incident/Problem Ratio: {int_metrics['incident_to_problem_ratio']}")
    print(f"   • Problem/Change Ratio: {int_metrics['problem_to_change_ratio']}")
    print(f"   • Emergency Changes: {int_metrics['emergency_changes']}")


def demonstrate_framework_health(itil: ITILFramework):
    """Demonstrate framework health monitoring"""
    print_section("Framework Health Monitoring")
    
    print("🏥 Checking framework health...")
    
    # Validate framework health
    health = itil.validate_framework_health()
    
    print(f"Overall Health: {health['overall_health']}")
    print(f"Health Checks Performed: {len(health['checks'])}")
    
    print(f"\n✅ Component Status:")
    for check in health['checks']:
        print(f"   • {check['component']}: {check['status']} - {check['details']}")
    
    if 'issues' in health:
        print(f"\n⚠️ Issues Found:")
        for issue in health['issues']:
            print(f"   • {issue}")
    else:
        print(f"\n✅ No issues found - Framework is healthy!")
    
    # Export configuration
    print(f"\n💾 Exporting configuration...")
    config = itil.export_configuration()
    
    print(f"Configuration exported:")
    print(f"   • Framework Version: {config['framework_version']}")
    print(f"   • Export Timestamp: {config['export_timestamp'][:19]}")
    print(f"   • Practices Configured: {len(config['practice_configurations'])}")


def main():
    """Main demonstration function"""
    print_banner("ITIL 4 Python Framework - Comprehensive Example")
    
    print("🚀 Initializing ITIL 4 Framework...")
    
    # Create the framework
    itil = ITILFramework()
    
    # Show framework information
    info = itil.get_framework_info()
    print(f"✅ Framework initialized successfully!")
    print(f"   Version: {info['version']}")
    print(f"   Components: {', '.join(info['components'].keys())}")
    print(f"   Practices Loaded: {len(info['runtime_info']['practices_loaded'])}")
    
    # Create sample data
    print(f"\n👥 Creating sample people and configuration items...")
    people = create_sample_people()
    cis = create_sample_cis()
    
    print(f"   • Created {len(people)} sample people")
    print(f"   • Created {len(cis)} sample configuration items")
    
    # Demonstrate each practice
    try:
        # Incident Management
        incidents = demonstrate_incident_management(itil, people, cis)
        
        # Problem Management  
        problem = demonstrate_problem_management(itil, people, incidents)
        
        # Change Enablement
        change = demonstrate_change_enablement(itil, people, problem)
        
        # Integration Workflows
        demonstrate_integration_workflows(itil, people)
        
        # Metrics and Reporting
        demonstrate_metrics_and_reporting(itil)
        
        # Framework Health
        demonstrate_framework_health(itil)
        
        # Final summary
        print_banner("Demonstration Complete", "🎉")
        
        print("✅ Successfully demonstrated:")
        print("   • Complete incident lifecycle management")
        print("   • Problem investigation and root cause analysis")
        print("   • Change planning and approval workflows")
        print("   • Cross-practice integration and workflows")
        print("   • Comprehensive metrics and reporting")
        print("   • Framework health monitoring")
        
        print(f"\n📊 Final Statistics:")
        final_metrics = itil.get_dashboard_metrics(30)
        int_metrics = final_metrics['integration_metrics']
        print(f"   • Total Records Created: {int_metrics['total_records']}")
        print(f"   • Framework Health: {itil.validate_framework_health()['overall_health']}")
        
        print(f"\n🎯 Key Achievements:")
        print(f"   • Demonstrated real-world ITSM workflows")
        print(f"   • Showed integration between ITIL practices")
        print(f"   • Provided comprehensive metrics and monitoring")
        print(f"   • Validated framework health and performance")
        
        print(f"\n🔗 Next Steps:")
        print(f"   • Explore individual practice capabilities")
        print(f"   • Implement custom workflows for your organization")
        print(f"   • Integrate with external systems and databases")
        print(f"   • Extend framework with additional practices")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print_banner("Thank you for exploring the ITIL 4 Python Framework!", "🙏")
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)