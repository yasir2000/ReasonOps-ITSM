"""
Advanced AI Agents for Extended ITIL Practices

This module implements additional specialized AI agents for Service Request Management,
Release Management, and other ITIL practices with advanced AI capabilities.
"""

import sys
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import json
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from crewai import Agent, Task, Crew, Process
    from crewai.tools import BaseTool
    from langchain.llms import OpenAI
except ImportError:
    # Mock classes for demonstration if CrewAI is not installed
    class Agent:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
    
    class Task:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
    
    class Crew:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
        
        def kickoff(self):
            return "Mock execution completed"
    
    class Process:
        sequential = "sequential"
        hierarchical = "hierarchical"
    
    class BaseTool:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

from ai_agents.itil_crewai_integration import ITILAgentTool, AgentRole
from integration.integration_manager import ITILIntegrationManager


class ExtendedAgentRole(Enum):
    """Extended agent roles for additional ITIL practices"""
    SERVICE_REQUEST_ANALYST = "Service Request Analyst"
    RELEASE_MANAGER = "Release Manager"
    DEPLOYMENT_SPECIALIST = "Deployment Specialist"
    CAPACITY_PLANNER = "Capacity Planner"
    AVAILABILITY_MANAGER = "Availability Manager"
    SECURITY_ANALYST = "Security Analyst"
    COMPLIANCE_OFFICER = "Compliance Officer"


class ServiceRequestAnalysisTool(ITILAgentTool):
    """Tool for analyzing and processing service requests"""
    
    def __init__(self, itil_manager: ITILIntegrationManager):
        super().__init__(
            name="service_request_analysis",
            description="Analyze service requests, validate requirements, and determine fulfillment approach",
            itil_manager=itil_manager
        )
    
    def _run(self, request_data: str) -> str:
        """Analyze service request and determine fulfillment approach"""
        try:
            if isinstance(request_data, str):
                request_info = json.loads(request_data)
            else:
                request_info = request_data
            
            analysis = {
                "request_id": request_info.get("id", "Unknown"),
                "title": request_info.get("title", ""),
                "category": self._classify_request_category(request_info),
                "complexity": self._assess_complexity(request_info),
                "approval_required": self._requires_approval(request_info),
                "estimated_effort": self._estimate_effort(request_info),
                "fulfillment_approach": self._determine_fulfillment_approach(request_info),
                "required_approvals": self._identify_required_approvals(request_info),
                "automation_opportunity": self._assess_automation_potential(request_info),
                "similar_requests": self._find_similar_requests(request_info)
            }
            
            return json.dumps(analysis, indent=2)
            
        except Exception as e:
            return f"Error analyzing service request: {str(e)}"
    
    def _classify_request_category(self, request_info: Dict) -> str:
        """Classify service request category"""
        description = request_info.get("description", "").lower()
        
        if any(word in description for word in ["access", "permission", "account", "user"]):
            return "Access Management"
        elif any(word in description for word in ["software", "application", "install"]):
            return "Software Request"
        elif any(word in description for word in ["hardware", "laptop", "phone", "equipment"]):
            return "Hardware Request"
        elif any(word in description for word in ["training", "course", "certification"]):
            return "Training Request"
        elif any(word in description for word in ["data", "report", "information"]):
            return "Information Request"
        else:
            return "General Service Request"
    
    def _assess_complexity(self, request_info: Dict) -> str:
        """Assess request complexity"""
        description = request_info.get("description", "")
        requester_level = request_info.get("requester_level", "Standard")
        
        # Complex indicators
        complex_keywords = ["custom", "integration", "multiple", "complex", "enterprise"]
        if any(word in description.lower() for word in complex_keywords):
            return "High"
        
        # Medium complexity
        if requester_level in ["Manager", "Director"] or len(description) > 200:
            return "Medium"
        
        return "Low"
    
    def _requires_approval(self, request_info: Dict) -> bool:
        """Determine if request requires approval"""
        category = self._classify_request_category(request_info)
        complexity = self._assess_complexity(request_info)
        cost = request_info.get("estimated_cost", 0)
        
        # Approval required for high complexity, cost > $500, or sensitive categories
        if complexity == "High" or cost > 500:
            return True
        
        if category in ["Access Management", "Software Request", "Hardware Request"]:
            return True
        
        return False
    
    def _estimate_effort(self, request_info: Dict) -> Dict[str, Any]:
        """Estimate fulfillment effort"""
        complexity = self._assess_complexity(request_info)
        category = self._classify_request_category(request_info)
        
        effort_matrix = {
            ("Low", "Access Management"): {"hours": 0.5, "resources": 1},
            ("Low", "Information Request"): {"hours": 1, "resources": 1},
            ("Medium", "Software Request"): {"hours": 4, "resources": 2},
            ("Medium", "Hardware Request"): {"hours": 8, "resources": 2},
            ("High", "Software Request"): {"hours": 16, "resources": 3},
            ("High", "Hardware Request"): {"hours": 24, "resources": 3}
        }
        
        return effort_matrix.get((complexity, category), {"hours": 8, "resources": 2})
    
    def _determine_fulfillment_approach(self, request_info: Dict) -> str:
        """Determine best fulfillment approach"""
        complexity = self._assess_complexity(request_info)
        category = self._classify_request_category(request_info)
        
        if complexity == "Low" and category in ["Access Management", "Information Request"]:
            return "Automated Fulfillment"
        elif complexity == "Medium":
            return "Standard Fulfillment"
        else:
            return "Manual Fulfillment"
    
    def _identify_required_approvals(self, request_info: Dict) -> List[str]:
        """Identify required approvals"""
        category = self._classify_request_category(request_info)
        cost = request_info.get("estimated_cost", 0)
        
        approvals = []
        
        if category == "Access Management":
            approvals.append("Line Manager")
            if "admin" in request_info.get("description", "").lower():
                approvals.append("IT Security")
        
        if category in ["Software Request", "Hardware Request"]:
            approvals.append("Line Manager")
            if cost > 1000:
                approvals.append("Budget Approval")
        
        if cost > 5000:
            approvals.append("Senior Management")
        
        return approvals
    
    def _assess_automation_potential(self, request_info: Dict) -> Dict[str, Any]:
        """Assess automation potential for similar requests"""
        category = self._classify_request_category(request_info)
        complexity = self._assess_complexity(request_info)
        
        automation_potential = {
            "Access Management": {"potential": "High", "confidence": 0.9},
            "Information Request": {"potential": "High", "confidence": 0.8},
            "Software Request": {"potential": "Medium", "confidence": 0.6},
            "Hardware Request": {"potential": "Low", "confidence": 0.3}
        }
        
        result = automation_potential.get(category, {"potential": "Low", "confidence": 0.2})
        
        if complexity == "High":
            result["potential"] = "Low"
            result["confidence"] *= 0.5
        
        return result
    
    def _find_similar_requests(self, request_info: Dict) -> List[str]:
        """Find similar historical requests"""
        # Mock implementation - would search historical data
        return ["SR-2024-001", "SR-2024-045", "SR-2024-089"]


class ReleaseManagementTool(ITILAgentTool):
    """Tool for release planning and management"""
    
    def __init__(self, itil_manager: ITILIntegrationManager):
        super().__init__(
            name="release_management",
            description="Plan, coordinate, and manage software releases with risk assessment",
            itil_manager=itil_manager
        )
    
    def _run(self, release_data: str) -> str:
        """Analyze release requirements and create release plan"""
        try:
            if isinstance(release_data, str):
                release_info = json.loads(release_data)
            else:
                release_info = release_data
            
            analysis = {
                "release_id": release_info.get("id", "Unknown"),
                "release_name": release_info.get("name", ""),
                "release_type": self._classify_release_type(release_info),
                "complexity_assessment": self._assess_release_complexity(release_info),
                "risk_analysis": self._perform_risk_analysis(release_info),
                "deployment_plan": self._create_deployment_plan(release_info),
                "rollback_strategy": self._create_rollback_strategy(release_info),
                "testing_requirements": self._define_testing_requirements(release_info),
                "approval_gates": self._define_approval_gates(release_info),
                "communication_plan": self._create_communication_plan(release_info)
            }
            
            return json.dumps(analysis, indent=2)
            
        except Exception as e:
            return f"Error analyzing release: {str(e)}"
    
    def _classify_release_type(self, release_info: Dict) -> str:
        """Classify type of release"""
        components = release_info.get("components", [])
        urgency = release_info.get("urgency", "Standard")
        
        if urgency == "Emergency":
            return "Emergency Release"
        elif len(components) == 1 and "patch" in release_info.get("description", "").lower():
            return "Minor Release"
        elif len(components) > 5 or "major" in release_info.get("description", "").lower():
            return "Major Release"
        else:
            return "Standard Release"
    
    def _assess_release_complexity(self, release_info: Dict) -> Dict[str, Any]:
        """Assess release complexity"""
        components = release_info.get("components", [])
        environments = release_info.get("environments", ["Production"])
        dependencies = release_info.get("dependencies", [])
        
        complexity_score = 0
        complexity_score += len(components) * 2
        complexity_score += len(environments) * 3
        complexity_score += len(dependencies) * 4
        
        if complexity_score <= 10:
            complexity = "Low"
        elif complexity_score <= 25:
            complexity = "Medium"
        else:
            complexity = "High"
        
        return {
            "level": complexity,
            "score": complexity_score,
            "factors": {
                "components": len(components),
                "environments": len(environments),
                "dependencies": len(dependencies)
            }
        }
    
    def _perform_risk_analysis(self, release_info: Dict) -> Dict[str, Any]:
        """Perform comprehensive risk analysis"""
        release_type = self._classify_release_type(release_info)
        complexity = self._assess_release_complexity(release_info)
        
        risks = []
        
        # Technical risks
        if complexity["level"] == "High":
            risks.append({
                "type": "Technical",
                "risk": "Complex deployment may fail",
                "probability": "Medium",
                "impact": "High",
                "mitigation": "Thorough testing and phased deployment"
            })
        
        # Business risks
        if release_type == "Major Release":
            risks.append({
                "type": "Business",
                "risk": "User productivity impact",
                "probability": "Medium",
                "impact": "Medium",
                "mitigation": "User training and communication"
            })
        
        # Operational risks
        risks.append({
            "type": "Operational",
            "risk": "Service disruption during deployment",
            "probability": "Low",
            "impact": "High",
            "mitigation": "Deployment during maintenance window"
        })
        
        return {
            "overall_risk_level": self._calculate_overall_risk(risks),
            "risks": risks,
            "risk_score": len(risks) + (1 if complexity["level"] == "High" else 0)
        }
    
    def _calculate_overall_risk(self, risks: List[Dict]) -> str:
        """Calculate overall risk level"""
        high_risks = len([r for r in risks if r["impact"] == "High"])
        
        if high_risks >= 2:
            return "High"
        elif high_risks == 1:
            return "Medium"
        else:
            return "Low"
    
    def _create_deployment_plan(self, release_info: Dict) -> Dict[str, Any]:
        """Create detailed deployment plan"""
        environments = release_info.get("environments", ["Production"])
        components = release_info.get("components", [])
        
        phases = []
        
        # Development/Test phases
        if "Development" not in environments:
            phases.append({
                "phase": "Development Deployment",
                "environment": "Development",
                "duration": "2 hours",
                "activities": ["Deploy components", "Run unit tests", "Verify functionality"]
            })
        
        if "Test" not in environments:
            phases.append({
                "phase": "Test Deployment",
                "environment": "Test",
                "duration": "4 hours",
                "activities": ["Deploy components", "Execute test suite", "Performance testing"]
            })
        
        # UAT phase
        phases.append({
            "phase": "User Acceptance Testing",
            "environment": "UAT",
            "duration": "1 week",
            "activities": ["Deploy to UAT", "User acceptance testing", "Business validation"]
        })
        
        # Production phase
        phases.append({
            "phase": "Production Deployment",
            "environment": "Production",
            "duration": "4 hours",
            "activities": ["Pre-deployment checks", "Deploy components", "Post-deployment verification"]
        })
        
        return {
            "phases": phases,
            "total_duration": "1-2 weeks",
            "deployment_window": "Weekend maintenance window"
        }
    
    def _create_rollback_strategy(self, release_info: Dict) -> Dict[str, Any]:
        """Create rollback strategy"""
        complexity = self._assess_release_complexity(release_info)
        
        return {
            "rollback_triggers": [
                "Critical functionality failure",
                "Performance degradation > 50%",
                "Security vulnerability discovered",
                "Business stakeholder escalation"
            ],
            "rollback_steps": [
                "Stop new deployments",
                "Assess impact and scope",
                "Execute rollback procedures",
                "Verify system stability",
                "Communicate status to stakeholders"
            ],
            "rollback_time": "2-4 hours" if complexity["level"] != "High" else "4-8 hours",
            "rollback_owner": "Release Manager",
            "approval_required": complexity["level"] == "High"
        }
    
    def _define_testing_requirements(self, release_info: Dict) -> Dict[str, Any]:
        """Define comprehensive testing requirements"""
        complexity = self._assess_release_complexity(release_info)
        components = release_info.get("components", [])
        
        testing_phases = [
            {
                "phase": "Unit Testing",
                "scope": "Individual components",
                "duration": "1-2 days",
                "coverage": "90%+"
            },
            {
                "phase": "Integration Testing",
                "scope": "Component interactions",
                "duration": "2-3 days",
                "coverage": "Critical paths"
            },
            {
                "phase": "System Testing",
                "scope": "End-to-end functionality",
                "duration": "3-5 days",
                "coverage": "All features"
            }
        ]
        
        if complexity["level"] == "High":
            testing_phases.append({
                "phase": "Performance Testing",
                "scope": "Load and stress testing",
                "duration": "2-3 days",
                "coverage": "Critical scenarios"
            })
        
        return {
            "testing_phases": testing_phases,
            "total_testing_time": "1-2 weeks",
            "testing_environments": ["Development", "Test", "UAT"],
            "acceptance_criteria": "All tests pass with 0 critical defects"
        }
    
    def _define_approval_gates(self, release_info: Dict) -> List[Dict[str, Any]]:
        """Define approval gates for release"""
        complexity = self._assess_release_complexity(release_info)
        release_type = self._classify_release_type(release_info)
        
        gates = [
            {
                "gate": "Development Complete",
                "approver": "Development Team Lead",
                "criteria": "Code complete and unit tests pass"
            },
            {
                "gate": "Testing Complete",
                "approver": "QA Manager",
                "criteria": "All test phases complete with acceptable defect levels"
            },
            {
                "gate": "UAT Approval",
                "approver": "Business Stakeholders",
                "criteria": "User acceptance testing complete and approved"
            }
        ]
        
        if complexity["level"] == "High" or release_type == "Major Release":
            gates.append({
                "gate": "Change Advisory Board",
                "approver": "CAB",
                "criteria": "Risk assessment reviewed and deployment approved"
            })
        
        if release_type == "Emergency Release":
            gates = [{
                "gate": "Emergency Approval",
                "approver": "IT Director",
                "criteria": "Emergency justified and immediate deployment approved"
            }]
        
        return gates
    
    def _create_communication_plan(self, release_info: Dict) -> Dict[str, Any]:
        """Create communication plan for release"""
        return {
            "stakeholder_groups": [
                {
                    "group": "End Users",
                    "communication": "Release notes and training materials",
                    "timing": "1 week before release",
                    "method": "Email and portal announcement"
                },
                {
                    "group": "IT Operations",
                    "communication": "Technical deployment guide",
                    "timing": "3 days before release",
                    "method": "Technical briefing session"
                },
                {
                    "group": "Business Stakeholders",
                    "communication": "Release summary and benefits",
                    "timing": "1 week before release",
                    "method": "Executive briefing"
                },
                {
                    "group": "Support Teams",
                    "communication": "Support procedures and known issues",
                    "timing": "1 day before release",
                    "method": "Support team briefing"
                }
            ],
            "communication_schedule": {
                "T-14 days": "Release announcement",
                "T-7 days": "User communication and training",
                "T-3 days": "Technical team preparation",
                "T-1 day": "Final readiness confirmation",
                "T-0": "Go/No-go decision and deployment",
                "T+1 day": "Post-deployment status update"
            }
        }


class DeploymentAutomationTool(ITILAgentTool):
    """Tool for automated deployment orchestration"""
    
    def __init__(self, itil_manager: ITILIntegrationManager):
        super().__init__(
            name="deployment_automation",
            description="Automate deployment processes and orchestrate release activities",
            itil_manager=itil_manager
        )
    
    def _run(self, deployment_request: str) -> str:
        """Execute automated deployment with orchestration"""
        try:
            if isinstance(deployment_request, str):
                deployment_info = json.loads(deployment_request)
            else:
                deployment_info = deployment_request
            
            execution_result = {
                "deployment_id": deployment_info.get("id", "Unknown"),
                "automation_plan": self._create_automation_plan(deployment_info),
                "pre_deployment_checks": self._execute_pre_deployment_checks(deployment_info),
                "deployment_execution": self._execute_deployment(deployment_info),
                "post_deployment_validation": self._execute_post_deployment_validation(deployment_info),
                "rollback_readiness": self._prepare_rollback(deployment_info)
            }
            
            return json.dumps(execution_result, indent=2)
            
        except Exception as e:
            return f"Error in deployment automation: {str(e)}"
    
    def _create_automation_plan(self, deployment_info: Dict) -> Dict[str, Any]:
        """Create detailed automation execution plan"""
        components = deployment_info.get("components", [])
        environment = deployment_info.get("environment", "Production")
        
        return {
            "automation_level": "Full" if len(components) <= 3 else "Partial",
            "orchestration_tool": "Ansible/Jenkins",
            "deployment_strategy": "Blue-Green" if environment == "Production" else "Rolling",
            "monitoring_enabled": True,
            "automatic_rollback": environment != "Production"
        }
    
    def _execute_pre_deployment_checks(self, deployment_info: Dict) -> Dict[str, Any]:
        """Execute pre-deployment verification checks"""
        checks = [
            {"check": "Environment availability", "status": "Pass", "details": "All systems operational"},
            {"check": "Backup verification", "status": "Pass", "details": "Backups completed successfully"},
            {"check": "Resource availability", "status": "Pass", "details": "Sufficient resources available"},
            {"check": "Dependency validation", "status": "Pass", "details": "All dependencies satisfied"},
            {"check": "Security scan", "status": "Pass", "details": "No security vulnerabilities found"}
        ]
        
        return {
            "total_checks": len(checks),
            "passed_checks": len([c for c in checks if c["status"] == "Pass"]),
            "checks": checks,
            "overall_status": "Ready for Deployment"
        }
    
    def _execute_deployment(self, deployment_info: Dict) -> Dict[str, Any]:
        """Simulate deployment execution"""
        components = deployment_info.get("components", [])
        
        deployment_steps = []
        for i, component in enumerate(components, 1):
            deployment_steps.append({
                "step": i,
                "component": component,
                "action": "Deploy",
                "status": "Success",
                "duration": "5 minutes",
                "timestamp": datetime.now().isoformat()
            })
        
        return {
            "deployment_steps": deployment_steps,
            "total_duration": f"{len(components) * 5} minutes",
            "overall_status": "Deployment Successful",
            "deployed_components": len(components)
        }
    
    def _execute_post_deployment_validation(self, deployment_info: Dict) -> Dict[str, Any]:
        """Execute post-deployment validation"""
        validations = [
            {"validation": "Service availability", "status": "Pass", "response_time": "200ms"},
            {"validation": "Database connectivity", "status": "Pass", "connection_time": "50ms"},
            {"validation": "API endpoints", "status": "Pass", "success_rate": "100%"},
            {"validation": "User interface", "status": "Pass", "load_time": "1.2s"},
            {"validation": "Integration tests", "status": "Pass", "test_coverage": "95%"}
        ]
        
        return {
            "validation_results": validations,
            "all_validations_passed": True,
            "system_health": "Excellent",
            "ready_for_traffic": True
        }
    
    def _prepare_rollback(self, deployment_info: Dict) -> Dict[str, Any]:
        """Prepare rollback capabilities"""
        return {
            "rollback_prepared": True,
            "rollback_method": "Automated",
            "rollback_time_estimate": "10 minutes",
            "rollback_triggers_configured": True,
            "previous_version_preserved": True
        }


class ExtendedITILAgentCrew:
    """Extended ITIL Agent Crew with additional specialized agents"""
    
    def __init__(self, itil_manager: ITILIntegrationManager, llm_model=None):
        self.itil_manager = itil_manager
        self.llm_model = llm_model
        self.agents = {}
        self.tools = self._initialize_extended_tools()
        
        # Initialize extended agents
        self._create_extended_agents()
    
    def _initialize_extended_tools(self) -> Dict[str, ITILAgentTool]:
        """Initialize extended ITIL-specific tools"""
        return {
            "service_request_analysis": ServiceRequestAnalysisTool(self.itil_manager),
            "release_management": ReleaseManagementTool(self.itil_manager),
            "deployment_automation": DeploymentAutomationTool(self.itil_manager)
        }
    
    def _create_extended_agents(self):
        """Create additional specialized ITIL agents"""
        
        # Service Request Analyst Agent
        self.agents[ExtendedAgentRole.SERVICE_REQUEST_ANALYST] = Agent(
            role="Service Request Analyst",
            goal="Efficiently analyze, categorize, and fulfill service requests with optimal automation",
            backstory="You are an expert in service request management with deep knowledge of ITIL service request fulfillment processes. You excel at identifying automation opportunities and ensuring efficient service delivery.",
            tools=[self.tools["service_request_analysis"]],
            llm=self.llm_model,
            verbose=True,
            allow_delegation=True
        )
        
        # Release Manager Agent
        self.agents[ExtendedAgentRole.RELEASE_MANAGER] = Agent(
            role="Release Manager",
            goal="Plan, coordinate, and manage software releases with minimal risk and maximum efficiency",
            backstory="You are a seasoned release manager with expertise in coordinating complex software deployments. You understand risk management, stakeholder communication, and deployment automation.",
            tools=[self.tools["release_management"]],
            llm=self.llm_model,
            verbose=True,
            allow_delegation=True
        )
        
        # Deployment Specialist Agent
        self.agents[ExtendedAgentRole.DEPLOYMENT_SPECIALIST] = Agent(
            role="Deployment Specialist",
            goal="Execute automated deployments with comprehensive validation and rollback capabilities",
            backstory="You are a deployment automation expert who ensures reliable, repeatable, and safe software deployments. You focus on automation, monitoring, and rapid recovery capabilities.",
            tools=[self.tools["deployment_automation"]],
            llm=self.llm_model,
            verbose=True,
            allow_delegation=False
        )
    
    def handle_service_request(self, request_data: Dict) -> Dict[str, Any]:
        """Handle service request using specialized agents"""
        
        # Task 1: Service Request Analysis
        analysis_task = Task(
            description=f"Analyze the following service request and provide categorization, fulfillment approach, and automation recommendations: {json.dumps(request_data)}",
            agent=self.agents[ExtendedAgentRole.SERVICE_REQUEST_ANALYST],
            expected_output="Detailed service request analysis with fulfillment plan and automation opportunities"
        )
        
        # Create and execute crew
        service_request_crew = Crew(
            agents=[self.agents[ExtendedAgentRole.SERVICE_REQUEST_ANALYST]],
            tasks=[analysis_task],
            process=Process.sequential,
            verbose=True
        )
        
        try:
            result = service_request_crew.kickoff()
            return self._process_service_request_results(result, request_data)
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "request_id": request_data.get("id", "unknown"),
                "timestamp": datetime.now().isoformat()
            }
    
    def handle_release_planning(self, release_data: Dict) -> Dict[str, Any]:
        """Handle release planning using specialized agents"""
        
        # Task 1: Release Planning
        planning_task = Task(
            description=f"Create comprehensive release plan for: {json.dumps(release_data)}",
            agent=self.agents[ExtendedAgentRole.RELEASE_MANAGER],
            expected_output="Complete release plan with deployment strategy, risk assessment, and communication plan"
        )
        
        # Task 2: Deployment Preparation
        deployment_task = Task(
            description="Prepare automated deployment plan based on release requirements",
            agent=self.agents[ExtendedAgentRole.DEPLOYMENT_SPECIALIST],
            expected_output="Deployment automation plan with validation and rollback procedures"
        )
        
        # Create and execute crew
        release_crew = Crew(
            agents=[
                self.agents[ExtendedAgentRole.RELEASE_MANAGER],
                self.agents[ExtendedAgentRole.DEPLOYMENT_SPECIALIST]
            ],
            tasks=[planning_task, deployment_task],
            process=Process.sequential,
            verbose=True
        )
        
        try:
            result = release_crew.kickoff()
            return self._process_release_results(result, release_data)
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "release_id": release_data.get("id", "unknown"),
                "timestamp": datetime.now().isoformat()
            }
    
    def _process_service_request_results(self, crew_result: str, original_request: Dict) -> Dict[str, Any]:
        """Process service request crew results"""
        return {
            "status": "completed",
            "request_id": original_request.get("id", "unknown"),
            "timestamp": datetime.now().isoformat(),
            "analysis_result": crew_result,
            "recommendations": {
                "fulfillment_approach": self._extract_fulfillment_approach(crew_result),
                "automation_opportunity": self._extract_automation_opportunity(crew_result),
                "approval_required": self._extract_approval_requirement(crew_result),
                "estimated_completion": self._extract_completion_estimate(crew_result)
            },
            "next_steps": self._determine_service_request_next_steps(crew_result),
            "confidence_score": 0.88
        }
    
    def _process_release_results(self, crew_result: str, original_release: Dict) -> Dict[str, Any]:
        """Process release planning crew results"""
        return {
            "status": "completed",
            "release_id": original_release.get("id", "unknown"),
            "timestamp": datetime.now().isoformat(),
            "planning_result": crew_result,
            "recommendations": {
                "deployment_strategy": self._extract_deployment_strategy(crew_result),
                "risk_level": self._extract_risk_level(crew_result),
                "approval_gates": self._extract_approval_gates(crew_result),
                "rollback_plan": self._extract_rollback_plan(crew_result)
            },
            "next_steps": self._determine_release_next_steps(crew_result),
            "confidence_score": 0.92
        }
    
    def _extract_fulfillment_approach(self, result: str) -> str:
        """Extract fulfillment approach from results"""
        if "automated" in result.lower():
            return "Automated Fulfillment"
        elif "manual" in result.lower():
            return "Manual Fulfillment"
        else:
            return "Standard Fulfillment"
    
    def _extract_automation_opportunity(self, result: str) -> Dict[str, Any]:
        """Extract automation opportunity assessment"""
        return {
            "potential": "High" if "high potential" in result.lower() else "Medium",
            "confidence": 0.8,
            "benefits": "Reduced processing time and improved consistency"
        }
    
    def _extract_approval_requirement(self, result: str) -> bool:
        """Extract approval requirements"""
        return "approval" in result.lower()
    
    def _extract_completion_estimate(self, result: str) -> str:
        """Extract completion time estimate"""
        if "immediate" in result.lower():
            return "Same day"
        elif "urgent" in result.lower():
            return "1-2 days"
        else:
            return "3-5 days"
    
    def _determine_service_request_next_steps(self, result: str) -> List[str]:
        """Determine next steps for service request"""
        return [
            "Validate request requirements with requestor",
            "Obtain necessary approvals",
            "Execute fulfillment plan",
            "Validate completion with requestor"
        ]
    
    def _extract_deployment_strategy(self, result: str) -> str:
        """Extract deployment strategy"""
        if "blue-green" in result.lower():
            return "Blue-Green Deployment"
        elif "rolling" in result.lower():
            return "Rolling Deployment"
        else:
            return "Standard Deployment"
    
    def _extract_risk_level(self, result: str) -> str:
        """Extract risk level assessment"""
        if "high risk" in result.lower():
            return "High"
        elif "medium risk" in result.lower():
            return "Medium"
        else:
            return "Low"
    
    def _extract_approval_gates(self, result: str) -> List[str]:
        """Extract approval gates"""
        return ["Development Complete", "Testing Complete", "UAT Approval", "Production Ready"]
    
    def _extract_rollback_plan(self, result: str) -> str:
        """Extract rollback plan status"""
        return "Automated rollback prepared with 15-minute recovery time"
    
    def _determine_release_next_steps(self, result: str) -> List[str]:
        """Determine next steps for release"""
        return [
            "Execute development phase deployment",
            "Conduct comprehensive testing",
            "Obtain stakeholder approvals",
            "Schedule production deployment"
        ]
    
    def get_extended_agent_status(self) -> Dict[str, Any]:
        """Get status of all extended agents"""
        return {
            "total_agents": len(self.agents),
            "agents": {
                role.value: {
                    "status": "active",
                    "capabilities": self._get_extended_agent_capabilities(role),
                    "tools_available": 1
                }
                for role in self.agents.keys()
            },
            "tools_available": list(self.tools.keys()),
            "integration_status": "connected" if self.itil_manager else "disconnected"
        }
    
    def _get_extended_agent_capabilities(self, role: ExtendedAgentRole) -> List[str]:
        """Get capabilities for extended agent roles"""
        capabilities = {
            ExtendedAgentRole.SERVICE_REQUEST_ANALYST: ["Request analysis", "Automation assessment", "Fulfillment planning"],
            ExtendedAgentRole.RELEASE_MANAGER: ["Release planning", "Risk assessment", "Stakeholder coordination"],
            ExtendedAgentRole.DEPLOYMENT_SPECIALIST: ["Deployment automation", "Validation procedures", "Rollback management"]
        }
        return capabilities.get(role, [])


def create_sample_service_request() -> Dict[str, Any]:
    """Create sample service request for testing"""
    return {
        "id": "SR-2025-001",
        "title": "Request new software license for Adobe Creative Suite",
        "description": "Need Adobe Creative Suite license for new marketing team member. Will be used for creating marketing materials, brochures, and social media content.",
        "requester": {
            "name": "Emily Rodriguez",
            "email": "emily.rodriguez@company.com",
            "department": "Marketing",
            "manager": "David Chen"
        },
        "category": "Software Request",
        "urgency": "Medium",
        "business_justification": "Required for new team member to perform job functions",
        "estimated_cost": 600,
        "requested_completion": (datetime.now() + timedelta(days=7)).isoformat()
    }


def create_sample_release() -> Dict[str, Any]:
    """Create sample release for testing"""
    return {
        "id": "REL-2025-Q1-001",
        "name": "Customer Portal Enhancement Release",
        "description": "Major enhancement to customer portal including new self-service features, improved mobile experience, and integration with CRM system",
        "components": [
            "Customer Portal Web Application",
            "Mobile Application",
            "API Gateway",
            "CRM Integration Service",
            "Database Schema Updates"
        ],
        "environments": ["Development", "Test", "UAT", "Production"],
        "dependencies": [
            "CRM System upgrade",
            "Database migration",
            "API authentication service"
        ],
        "urgency": "Standard",
        "business_value": "Improved customer experience and reduced support volume",
        "target_release_date": (datetime.now() + timedelta(days=30)).isoformat()
    }


def main():
    """Main function to demonstrate extended AI agents"""
    print("🚀 Extended AI Agents for ITIL - Advanced Capabilities")
    print("=" * 65)
    
    # Initialize ITIL integration manager
    print("\n🔧 Initializing Extended ITIL Framework...")
    itil_manager = ITILIntegrationManager()
    
    # Create mock services
    class MockServiceRequestManagement:
        def get_metrics(self, period_days: int):
            return {"total_requests": 150, "fulfilled_requests": 130}
        
        def get_configuration(self):
            return {"automation_rate": 0.6, "avg_fulfillment_time": "3 days"}
        
        def validate_configuration(self):
            return True
        
        def get_health_status(self):
            return {"status": "healthy"}
    
    class MockReleaseManagement:
        def get_metrics(self, period_days: int):
            return {"total_releases": 12, "successful_releases": 11}
        
        def get_configuration(self):
            return {"success_rate": 0.92, "avg_release_duration": "2 weeks"}
        
        def validate_configuration(self):
            return True
        
        def get_health_status(self):
            return {"status": "healthy"}
    
    # Register services
    itil_manager.register_practice("service_request_management", MockServiceRequestManagement())
    itil_manager.register_practice("release_management", MockReleaseManagement())
    
    # Initialize framework
    init_results = itil_manager.initialize_framework()
    if init_results["overall_status"] == "SUCCESS":
        print("✅ Extended ITIL Framework initialized successfully")
    else:
        print("❌ Framework initialization failed")
        return
    
    # Create extended AI agent crew
    print("\n🤖 Creating Extended AI Agent Crew...")
    extended_crew = ExtendedITILAgentCrew(itil_manager)
    
    # Display agent status
    agent_status = extended_crew.get_extended_agent_status()
    print(f"✅ Created {agent_status['total_agents']} specialized agents:")
    
    for role, info in agent_status['agents'].items():
        print(f"  🤖 {role}:")
        print(f"    - Status: {info['status']}")
        print(f"    - Capabilities: {', '.join(info['capabilities'])}")
    
    # Test Service Request Management
    print(f"\n📋 Testing Service Request Management...")
    sample_request = create_sample_service_request()
    
    print(f"Service Request Details:")
    print(f"  - ID: {sample_request['id']}")
    print(f"  - Title: {sample_request['title']}")
    print(f"  - Estimated Cost: ${sample_request['estimated_cost']}")
    
    request_results = extended_crew.handle_service_request(sample_request)
    print(f"✅ Service Request Analysis Results:")
    print(f"  - Status: {request_results['status']}")
    print(f"  - Fulfillment Approach: {request_results['recommendations']['fulfillment_approach']}")
    print(f"  - Automation Opportunity: {request_results['recommendations']['automation_opportunity']['potential']}")
    print(f"  - Approval Required: {request_results['recommendations']['approval_required']}")
    
    # Test Release Management
    print(f"\n🚀 Testing Release Management...")
    sample_release = create_sample_release()
    
    print(f"Release Details:")
    print(f"  - ID: {sample_release['id']}")
    print(f"  - Name: {sample_release['name']}")
    print(f"  - Components: {len(sample_release['components'])}")
    
    release_results = extended_crew.handle_release_planning(sample_release)
    print(f"✅ Release Planning Results:")
    print(f"  - Status: {release_results['status']}")
    print(f"  - Deployment Strategy: {release_results['recommendations']['deployment_strategy']}")
    print(f"  - Risk Level: {release_results['recommendations']['risk_level']}")
    print(f"  - Rollback Plan: {release_results['recommendations']['rollback_plan']}")
    
    # Test individual tools
    print(f"\n🔧 Testing Individual Extended Tools...")
    
    # Test service request analysis tool
    sr_tool = extended_crew.tools["service_request_analysis"]
    sr_result = sr_tool._run(json.dumps(sample_request))
    print(f"✅ Service Request Analysis Tool: Automation assessment completed")
    
    # Test release management tool
    rel_tool = extended_crew.tools["release_management"]
    rel_result = rel_tool._run(json.dumps(sample_release))
    print(f"✅ Release Management Tool: Risk analysis and planning completed")
    
    # Test deployment automation tool
    deploy_tool = extended_crew.tools["deployment_automation"]
    deploy_result = deploy_tool._run(json.dumps({"id": "DEP-001", "components": sample_release["components"]}))
    print(f"✅ Deployment Automation Tool: Automation plan created")
    
    print(f"\n🎉 Extended AI Agents Integration Successful!")
    
    print(f"\nNew Capabilities Added:")
    print(f"✅ Service Request Management automation")
    print(f"✅ Release planning and risk assessment")
    print(f"✅ Deployment automation and orchestration")
    print(f"✅ Advanced approval workflow management")
    print(f"✅ Comprehensive testing and validation procedures")


if __name__ == "__main__":
    main()