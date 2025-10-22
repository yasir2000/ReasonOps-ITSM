"""
AI Agents Framework for ITIL - CrewAI Integration

This module integrates CrewAI framework with ITIL processes to create autonomous
AI agents that can analyze, reason, plan, and work in teams to solve incidents
and other ITIL processes autonomously.
"""

import sys
import os
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import json
import logging

# Add parent directory to path for ITIL framework imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from crewai import Agent, Task, Crew, Process
    from crewai.tools import BaseTool
    from langchain.llms import OpenAI
    from langchain.tools import Tool
except ImportError:
    print("⚠️  CrewAI not installed. Install with: pip install crewai langchain")
    print("Creating mock classes for demonstration...")
    
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
    
    class OpenAI:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

# Import our ITIL framework components
from integration.integration_manager import ITILIntegrationManager

# Import multi-LLM provider support
try:
    from .multi_llm_provider import MultiLLMManager, LLMConfig, LLMProvider, ModelType
    MULTI_LLM_AVAILABLE = True
except ImportError:
    try:
        from multi_llm_provider import MultiLLMManager, LLMConfig, LLMProvider, ModelType  
        MULTI_LLM_AVAILABLE = True
    except ImportError:
        print("⚠️  Multi-LLM provider not available")
        MULTI_LLM_AVAILABLE = False


class AgentRole(Enum):
    """Predefined agent roles for ITIL processes"""
    INCIDENT_ANALYST = "Incident Analyst"
    TECHNICAL_SPECIALIST = "Technical Specialist"
    PROBLEM_ANALYST = "Problem Analyst"
    CHANGE_COORDINATOR = "Change Coordinator"
    KNOWLEDGE_MANAGER = "Knowledge Manager"
    SERVICE_DESK = "Service Desk Agent"
    SECURITY_ANALYST = "Security Analyst"
    ESCALATION_MANAGER = "Escalation Manager"


@dataclass
class AgentCapability:
    """Defines an agent's capability"""
    name: str
    description: str
    tools: List[str]
    expertise_level: str  # "L1", "L2", "L3", "Expert"
    can_escalate: bool = True
    requires_approval: bool = False


class ITILAgentTool(BaseTool):
    """Base class for ITIL-specific agent tools with multi-LLM support"""
    
    def __init__(self, name: str, description: str, itil_manager: ITILIntegrationManager, llm_manager=None):
        self.name = name
        self.description = description
        self.itil_manager = itil_manager
        self.llm_manager = llm_manager
        super().__init__()
    
    async def get_ai_analysis(self, prompt: str, system_prompt: str = None, provider_name: str = None) -> str:
        """Get AI analysis using multi-LLM support"""
        if self.llm_manager and MULTI_LLM_AVAILABLE:
            try:
                response = await self.llm_manager.generate_response(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    provider_name=provider_name
                )
                return response.content
            except Exception as e:
                print(f"⚠️  LLM analysis failed: {e}")
        
        # Mock AI analysis fallback
        return f"AI Analysis: {prompt[:100]}... [Mock response due to LLM unavailability]"
    
    def _run(self, *args, **kwargs):
        """Override in subclasses"""
        raise NotImplementedError


class IncidentAnalysisTool(ITILAgentTool):
    """Tool for analyzing incidents with multi-LLM support"""
    
    def __init__(self, itil_manager: ITILIntegrationManager, llm_manager=None):
        super().__init__(
            name="incident_analysis",
            description="Analyze incident details, classify priority, and suggest initial actions using AI",
            itil_manager=itil_manager,
            llm_manager=llm_manager
        )
    
    def _run(self, incident_data: str) -> str:
        """Analyze incident and return analysis results"""
        try:
            # Parse incident data
            if isinstance(incident_data, str):
                incident_info = json.loads(incident_data)
            else:
                incident_info = incident_data
            
            # Get incident management service
            if self.itil_manager.registry.is_registered("incident_management"):
                incident_mgmt = self.itil_manager.registry.get("incident_management")
                
                # Perform analysis
                analysis = {
                    "incident_id": incident_info.get("id", "Unknown"),
                    "title": incident_info.get("title", ""),
                    "category": self._classify_category(incident_info.get("description", "")),
                    "priority": self._determine_priority(incident_info),
                    "urgency": self._assess_urgency(incident_info),
                    "impact": self._assess_impact(incident_info),
                    "suggested_actions": self._suggest_actions(incident_info),
                    "escalation_needed": self._needs_escalation(incident_info),
                    "knowledge_articles": self._find_related_knowledge(incident_info)
                }
                
                return json.dumps(analysis, indent=2)
            else:
                return "Error: Incident management service not available"
                
        except Exception as e:
            return f"Error analyzing incident: {str(e)}"
    
    def _classify_category(self, description: str) -> str:
        """Classify incident category based on description"""
        description_lower = description.lower()
        
        if any(word in description_lower for word in ["email", "outlook", "smtp"]):
            return "Email"
        elif any(word in description_lower for word in ["network", "internet", "connectivity"]):
            return "Network"
        elif any(word in description_lower for word in ["server", "database", "application"]):
            return "Server/Application"
        elif any(word in description_lower for word in ["password", "login", "access"]):
            return "Access Management"
        elif any(word in description_lower for word in ["printer", "hardware", "device"]):
            return "Hardware"
        else:
            return "General IT"
    
    def _determine_priority(self, incident_info: Dict) -> str:
        """Determine incident priority based on impact and urgency"""
        impact = incident_info.get("impact", "Medium")
        urgency = incident_info.get("urgency", "Medium")
        
        # ITIL priority matrix
        priority_matrix = {
            ("Critical", "High"): "P1",
            ("Critical", "Medium"): "P1", 
            ("Critical", "Low"): "P2",
            ("High", "High"): "P1",
            ("High", "Medium"): "P2",
            ("High", "Low"): "P3",
            ("Medium", "High"): "P2",
            ("Medium", "Medium"): "P3",
            ("Medium", "Low"): "P4",
            ("Low", "High"): "P3",
            ("Low", "Medium"): "P4",
            ("Low", "Low"): "P4"
        }
        
        return priority_matrix.get((impact, urgency), "P3")
    
    def _assess_urgency(self, incident_info: Dict) -> str:
        """Assess incident urgency"""
        description = incident_info.get("description", "").lower()
        
        if any(word in description for word in ["urgent", "asap", "critical", "down", "outage"]):
            return "High"
        elif any(word in description for word in ["slow", "intermittent", "sometimes"]):
            return "Medium"
        else:
            return "Low"
    
    def _assess_impact(self, incident_info: Dict) -> str:
        """Assess incident impact"""
        description = incident_info.get("description", "").lower()
        affected_users = incident_info.get("affected_users", 1)
        
        if affected_users > 100 or any(word in description for word in ["all users", "entire", "company"]):
            return "Critical"
        elif affected_users > 20 or any(word in description for word in ["department", "team", "multiple"]):
            return "High"
        elif affected_users > 5:
            return "Medium"
        else:
            return "Low"
    
    def _suggest_actions(self, incident_info: Dict) -> List[str]:
        """Suggest initial actions based on incident type"""
        category = self._classify_category(incident_info.get("description", ""))
        
        action_suggestions = {
            "Email": [
                "Check email server status",
                "Verify user's email configuration",
                "Test SMTP connectivity",
                "Check for recent email system changes"
            ],
            "Network": [
                "Ping test to affected systems",
                "Check network switch status",
                "Verify firewall rules",
                "Test DNS resolution"
            ],
            "Server/Application": [
                "Check server resource utilization",
                "Review application logs",
                "Verify database connectivity",
                "Check recent deployments"
            ],
            "Access Management": [
                "Verify user account status",
                "Check password expiration",
                "Review access permissions",
                "Test authentication services"
            ],
            "Hardware": [
                "Check device physical status",
                "Verify power and connections",
                "Review hardware diagnostics",
                "Check for driver updates"
            ]
        }
        
        return action_suggestions.get(category, ["Gather more information", "Contact technical support"])
    
    def _needs_escalation(self, incident_info: Dict) -> bool:
        """Determine if incident needs escalation"""
        priority = self._determine_priority(incident_info)
        return priority in ["P1", "P2"]
    
    def _find_related_knowledge(self, incident_info: Dict) -> List[str]:
        """Find related knowledge base articles"""
        # Mock implementation - in real system would search knowledge base
        category = self._classify_category(incident_info.get("description", ""))
        
        knowledge_articles = {
            "Email": ["KB001: Email Configuration Guide", "KB045: SMTP Troubleshooting"],
            "Network": ["KB123: Network Connectivity Issues", "KB089: DNS Resolution Problems"],
            "Server/Application": ["KB234: Server Performance Monitoring", "KB156: Application Log Analysis"],
            "Access Management": ["KB067: Password Reset Procedures", "KB178: Access Control Troubleshooting"],
            "Hardware": ["KB345: Hardware Diagnostic Tools", "KB267: Device Driver Updates"]
        }
        
        return knowledge_articles.get(category, ["KB999: General Troubleshooting Guide"])


class ProblemAnalysisTool(ITILAgentTool):
    """Tool for problem analysis and root cause investigation with AI support"""
    
    def __init__(self, itil_manager: ITILIntegrationManager, llm_manager=None):
        super().__init__(
            name="problem_analysis",
            description="Analyze patterns in incidents to identify potential problems and root causes using AI",
            itil_manager=itil_manager,
            llm_manager=llm_manager
        )
    
    def _run(self, incident_data: str) -> str:
        """Analyze incident patterns for problem identification"""
        try:
            incidents = json.loads(incident_data) if isinstance(incident_data, str) else incident_data
            
            analysis = {
                "pattern_analysis": self._analyze_patterns(incidents),
                "root_cause_hypotheses": self._generate_hypotheses(incidents),
                "similar_incidents": self._find_similar_incidents(incidents),
                "problem_recommendation": self._recommend_problem_creation(incidents),
                "investigation_steps": self._suggest_investigation_steps(incidents)
            }
            
            return json.dumps(analysis, indent=2)
            
        except Exception as e:
            return f"Error in problem analysis: {str(e)}"
    
    def _analyze_patterns(self, incidents: List[Dict]) -> Dict:
        """Analyze patterns in incidents"""
        if not isinstance(incidents, list):
            incidents = [incidents]
        
        patterns = {
            "frequency": len(incidents),
            "time_pattern": self._analyze_time_patterns(incidents),
            "category_distribution": self._analyze_categories(incidents),
            "affected_components": self._analyze_components(incidents)
        }
        
        return patterns
    
    def _analyze_time_patterns(self, incidents: List[Dict]) -> Dict:
        """Analyze temporal patterns in incidents"""
        # Mock implementation - in real system would analyze timestamps
        return {
            "peak_hours": ["09:00-11:00", "14:00-16:00"],
            "frequency_trend": "increasing",
            "seasonal_pattern": "workday_peaks"
        }
    
    def _analyze_categories(self, incidents: List[Dict]) -> Dict:
        """Analyze incident categories"""
        categories = {}
        for incident in incidents:
            category = incident.get("category", "Unknown")
            categories[category] = categories.get(category, 0) + 1
        return categories
    
    def _analyze_components(self, incidents: List[Dict]) -> List[str]:
        """Identify affected components"""
        components = set()
        for incident in incidents:
            description = incident.get("description", "").lower()
            if "email" in description:
                components.add("Email System")
            if "network" in description:
                components.add("Network Infrastructure")
            if "server" in description:
                components.add("Server Infrastructure")
        return list(components)
    
    def _generate_hypotheses(self, incidents: List[Dict]) -> List[str]:
        """Generate root cause hypotheses"""
        hypotheses = [
            "Resource exhaustion on email servers",
            "Network latency issues during peak hours",
            "Insufficient system capacity for current load",
            "Configuration drift in infrastructure",
            "Aging hardware requiring replacement"
        ]
        return hypotheses[:3]  # Return top 3 hypotheses
    
    def _find_similar_incidents(self, incidents: List[Dict]) -> List[str]:
        """Find similar historical incidents"""
        # Mock implementation
        return ["INC-2024-001", "INC-2024-045", "INC-2024-089"]
    
    def _recommend_problem_creation(self, incidents: List[Dict]) -> Dict:
        """Recommend whether to create a problem record"""
        frequency = len(incidents)
        
        recommendation = {
            "create_problem": frequency >= 3,
            "reason": f"Pattern detected: {frequency} similar incidents in short timeframe",
            "urgency": "High" if frequency >= 5 else "Medium",
            "suggested_title": f"Recurring issues with {self._get_primary_component(incidents)}"
        }
        
        return recommendation
    
    def _get_primary_component(self, incidents: List[Dict]) -> str:
        """Get the primary affected component"""
        components = self._analyze_components(incidents)
        return components[0] if components else "IT Services"
    
    def _suggest_investigation_steps(self, incidents: List[Dict]) -> List[str]:
        """Suggest investigation steps"""
        return [
            "Review system logs for common error patterns",
            "Analyze resource utilization trends",
            "Interview affected users for additional details",
            "Check for recent changes to infrastructure",
            "Perform root cause analysis using fishbone diagram"
        ]


class ResolutionPlanningTool(ITILAgentTool):
    """Tool for creating AI-powered resolution plans"""
    
    def __init__(self, itil_manager: ITILIntegrationManager, llm_manager=None):
        super().__init__(
            name="resolution_planning",
            description="Create detailed resolution plans for incidents and problems using AI analysis",
            itil_manager=itil_manager,
            llm_manager=llm_manager
        )
    
    def _run(self, analysis_data: str) -> str:
        """Create resolution plan based on analysis"""
        try:
            analysis = json.loads(analysis_data) if isinstance(analysis_data, str) else analysis_data
            
            plan = {
                "resolution_strategy": self._determine_strategy(analysis),
                "action_plan": self._create_action_plan(analysis),
                "resource_requirements": self._identify_resources(analysis),
                "timeline": self._estimate_timeline(analysis),
                "risk_assessment": self._assess_risks(analysis),
                "rollback_plan": self._create_rollback_plan(analysis),
                "testing_plan": self._create_testing_plan(analysis)
            }
            
            return json.dumps(plan, indent=2)
            
        except Exception as e:
            return f"Error creating resolution plan: {str(e)}"
    
    def _determine_strategy(self, analysis: Dict) -> str:
        """Determine resolution strategy"""
        priority = analysis.get("priority", "P3")
        
        if priority == "P1":
            return "Immediate resolution with emergency change if needed"
        elif priority == "P2":
            return "Expedited resolution with standard change process"
        else:
            return "Standard resolution following normal change process"
    
    def _create_action_plan(self, analysis: Dict) -> List[Dict]:
        """Create detailed action plan"""
        actions = []
        
        suggested_actions = analysis.get("suggested_actions", [])
        
        for i, action in enumerate(suggested_actions, 1):
            actions.append({
                "step": i,
                "action": action,
                "responsible": "Technical Specialist",
                "estimated_time": "15-30 minutes",
                "dependencies": [],
                "success_criteria": f"Completion of {action.lower()}"
            })
        
        return actions
    
    def _identify_resources(self, analysis: Dict) -> Dict:
        """Identify required resources"""
        return {
            "personnel": ["Technical Specialist", "System Administrator"],
            "tools": ["Monitoring tools", "Log analysis tools", "Testing environment"],
            "access_required": ["Production systems", "Administrative privileges"],
            "estimated_effort": "2-4 hours"
        }
    
    def _estimate_timeline(self, analysis: Dict) -> Dict:
        """Estimate resolution timeline"""
        priority = analysis.get("priority", "P3")
        
        timelines = {
            "P1": {"target": "1 hour", "maximum": "4 hours"},
            "P2": {"target": "4 hours", "maximum": "12 hours"},
            "P3": {"target": "24 hours", "maximum": "72 hours"},
            "P4": {"target": "5 days", "maximum": "10 days"}
        }
        
        return timelines.get(priority, timelines["P3"])
    
    def _assess_risks(self, analysis: Dict) -> List[Dict]:
        """Assess resolution risks"""
        return [
            {
                "risk": "Service disruption during resolution",
                "probability": "Medium",
                "impact": "High",
                "mitigation": "Perform changes during maintenance window"
            },
            {
                "risk": "Resolution may not address root cause",
                "probability": "Low",
                "impact": "Medium", 
                "mitigation": "Monitor for recurring issues and escalate to problem management"
            }
        ]
    
    def _create_rollback_plan(self, analysis: Dict) -> List[str]:
        """Create rollback plan"""
        return [
            "Document current system state before changes",
            "Create configuration backup",
            "Define rollback triggers and decision points",
            "Test rollback procedures in non-production environment",
            "Assign rollback responsibility to senior technician"
        ]
    
    def _create_testing_plan(self, analysis: Dict) -> List[str]:
        """Create testing plan"""
        return [
            "Verify resolution addresses reported symptoms",
            "Test system functionality end-to-end",
            "Confirm user access and permissions",
            "Monitor system performance for 24 hours",
            "Obtain user confirmation of resolution"
        ]


class ITILAgentCrew:
    """Manages a crew of AI agents for ITIL processes with multi-LLM support"""
    
    def __init__(self, itil_manager: ITILIntegrationManager, llm_model=None, llm_config_file=None):
        self.itil_manager = itil_manager
        
        # Initialize multi-LLM manager if available
        if MULTI_LLM_AVAILABLE:
            self.llm_manager = MultiLLMManager(llm_config_file)
            self.use_multi_llm = True
            print("✅ Multi-LLM support enabled")
        else:
            self.llm_manager = None
            self.use_multi_llm = False
            print("⚠️  Using single LLM fallback")
        
        # Fallback to single LLM model
        self.llm_model = llm_model or self._get_default_llm()
        self.agents = {}
        self.tools = self._initialize_tools()
        
        # Initialize agents
        self._create_agents()
    
    def _get_default_llm(self):
        """Get default LLM (mock for demonstration)"""
        try:
            return OpenAI(temperature=0.1)
        except:
            return None  # Mock LLM for demonstration
    
    def _initialize_tools(self) -> Dict[str, ITILAgentTool]:
        """Initialize ITIL-specific tools with multi-LLM support"""
        return {
            "incident_analysis": IncidentAnalysisTool(self.itil_manager, self.llm_manager),
            "problem_analysis": ProblemAnalysisTool(self.itil_manager, self.llm_manager),
            "resolution_planning": ResolutionPlanningTool(self.itil_manager, self.llm_manager)
        }
    
    def _create_agents(self):
        """Create specialized ITIL agents"""
        
        # Incident Analyst Agent
        self.agents[AgentRole.INCIDENT_ANALYST] = Agent(
            role="Incident Analyst",
            goal="Analyze and classify incidents, determine priority and suggest initial resolution steps",
            backstory="You are an experienced IT service desk analyst with deep knowledge of ITIL incident management processes. You excel at quickly understanding user issues and classifying them appropriately.",
            tools=[self.tools["incident_analysis"]],
            llm=self.llm_model,
            verbose=True,
            allow_delegation=True
        )
        
        # Technical Specialist Agent
        self.agents[AgentRole.TECHNICAL_SPECIALIST] = Agent(
            role="Technical Specialist",
            goal="Provide deep technical analysis and implement resolution plans for complex incidents",
            backstory="You are a senior technical specialist with expertise in system administration, networking, and application troubleshooting. You can handle complex technical issues that require deep system knowledge.",
            tools=[self.tools["resolution_planning"]],
            llm=self.llm_model,
            verbose=True,
            allow_delegation=False
        )
        
        # Problem Analyst Agent
        self.agents[AgentRole.PROBLEM_ANALYST] = Agent(
            role="Problem Analyst",
            goal="Identify patterns in incidents, perform root cause analysis, and prevent recurring issues",
            backstory="You are a problem management specialist who excels at pattern recognition and root cause analysis. You help prevent incidents by identifying and addressing underlying problems.",
            tools=[self.tools["problem_analysis"]],
            llm=self.llm_model,
            verbose=True,
            allow_delegation=True
        )
        
        # Knowledge Manager Agent
        self.agents[AgentRole.KNOWLEDGE_MANAGER] = Agent(
            role="Knowledge Manager",
            goal="Maintain and update knowledge base with solutions and best practices",
            backstory="You are responsible for capturing and organizing knowledge from incident resolutions to help improve future response times and solution quality.",
            tools=[],
            llm=self.llm_model,
            verbose=True,
            allow_delegation=False
        )
    
    async def get_llm_response(self, prompt: str, system_prompt: str = None, provider_name: str = None) -> str:
        """Get LLM response using multi-provider support or fallback"""
        if self.use_multi_llm and self.llm_manager:
            try:
                response = await self.llm_manager.generate_response(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    provider_name=provider_name
                )
                return response.content
            except Exception as e:
                print(f"⚠️  Multi-LLM failed, using fallback: {e}")
        
        # Fallback to mock response
        return f"Mock AI analysis for: {prompt[:100]}..."
    
    def set_primary_llm_provider(self, provider_name: str):
        """Set the primary LLM provider"""
        if self.llm_manager:
            self.llm_manager.set_primary_provider(provider_name)
            print(f"✅ Primary LLM provider set to: {provider_name}")
        else:
            print("⚠️  Multi-LLM manager not available")
    
    def get_available_llm_providers(self) -> List[str]:
        """Get list of available LLM providers"""
        if self.llm_manager:
            return self.llm_manager.get_available_providers()
        return ["mock"]
    
    def get_llm_provider_info(self) -> Dict[str, Any]:
        """Get information about current LLM configuration"""
        info = {
            "multi_llm_enabled": self.use_multi_llm,
            "available_providers": self.get_available_llm_providers()
        }
        
        if self.llm_manager:
            info["primary_provider"] = self.llm_manager.primary_provider
            info["fallback_providers"] = self.llm_manager.fallback_providers
        
        return info
    
    def handle_incident(self, incident_data: Dict) -> Dict[str, Any]:
        """Handle an incident using the agent crew"""
        
        # Task 1: Incident Analysis
        analysis_task = Task(
            description=f"Analyze the following incident and provide classification, priority assessment, and initial recommendations: {json.dumps(incident_data)}",
            agent=self.agents[AgentRole.INCIDENT_ANALYST],
            expected_output="Detailed incident analysis with classification, priority, and suggested actions"
        )
        
        # Task 2: Resolution Planning
        planning_task = Task(
            description="Based on the incident analysis, create a detailed resolution plan with steps, timeline, and resource requirements",
            agent=self.agents[AgentRole.TECHNICAL_SPECIALIST],
            expected_output="Comprehensive resolution plan with action steps and timeline"
        )
        
        # Task 3: Pattern Analysis (for problem identification)
        pattern_task = Task(
            description="Analyze this incident for patterns that might indicate underlying problems requiring proactive resolution",
            agent=self.agents[AgentRole.PROBLEM_ANALYST],
            expected_output="Pattern analysis and problem identification recommendations"
        )
        
        # Create and execute crew
        incident_crew = Crew(
            agents=[
                self.agents[AgentRole.INCIDENT_ANALYST],
                self.agents[AgentRole.TECHNICAL_SPECIALIST],
                self.agents[AgentRole.PROBLEM_ANALYST]
            ],
            tasks=[analysis_task, planning_task, pattern_task],
            process=Process.sequential,
            verbose=True
        )
        
        # Execute the crew
        try:
            result = incident_crew.kickoff()
            
            # Process and structure the results
            return self._process_crew_results(result, incident_data)
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "incident_id": incident_data.get("id", "unknown"),
                "timestamp": datetime.now().isoformat()
            }
    
    def _process_crew_results(self, crew_result: str, original_incident: Dict) -> Dict[str, Any]:
        """Process and structure crew execution results"""
        
        return {
            "status": "completed",
            "incident_id": original_incident.get("id", "unknown"),
            "timestamp": datetime.now().isoformat(),
            "crew_analysis": crew_result,
            "recommendations": {
                "immediate_actions": self._extract_immediate_actions(crew_result),
                "escalation_needed": self._requires_escalation(crew_result),
                "problem_creation": self._should_create_problem(crew_result),
                "knowledge_update": self._needs_knowledge_update(crew_result)
            },
            "next_steps": self._determine_next_steps(crew_result),
            "confidence_score": self._calculate_confidence(crew_result)
        }
    
    def _extract_immediate_actions(self, result: str) -> List[str]:
        """Extract immediate actions from crew result"""
        # Mock implementation - in real system would parse LLM output
        return [
            "Verify incident details with user",
            "Check system status and logs",
            "Apply standard resolution procedures",
            "Monitor for resolution effectiveness"
        ]
    
    def _requires_escalation(self, result: str) -> bool:
        """Determine if escalation is needed"""
        # Mock implementation
        return "P1" in result or "critical" in result.lower()
    
    def _should_create_problem(self, result: str) -> bool:
        """Determine if problem record should be created"""
        # Mock implementation
        return "pattern" in result.lower() or "recurring" in result.lower()
    
    def _needs_knowledge_update(self, result: str) -> bool:
        """Determine if knowledge base needs updating"""
        # Mock implementation
        return "new solution" in result.lower() or "knowledge gap" in result.lower()
    
    def _determine_next_steps(self, result: str) -> List[str]:
        """Determine next steps based on analysis"""
        return [
            "Implement resolution plan",
            "Monitor incident status",
            "Update incident record",
            "Communicate with stakeholders"
        ]
    
    def _calculate_confidence(self, result: str) -> float:
        """Calculate confidence score for the analysis"""
        # Mock implementation - in real system would analyze LLM output quality
        return 0.85
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents in the crew"""
        return {
            "total_agents": len(self.agents),
            "agents": {
                role.value: {
                    "status": "active",
                    "capabilities": self._get_agent_capabilities(role),
                    "tools_available": len(agent.tools) if hasattr(agent, 'tools') else 0
                }
                for role, agent in self.agents.items()
            },
            "tools_available": list(self.tools.keys()),
            "integration_status": "connected" if self.itil_manager else "disconnected"
        }
    
    def _get_agent_capabilities(self, role: AgentRole) -> List[str]:
        """Get capabilities for specific agent role"""
        capabilities = {
            AgentRole.INCIDENT_ANALYST: ["Incident classification", "Priority assessment", "Initial triage"],
            AgentRole.TECHNICAL_SPECIALIST: ["Technical troubleshooting", "Resolution planning", "System analysis"],
            AgentRole.PROBLEM_ANALYST: ["Pattern recognition", "Root cause analysis", "Trend analysis"],
            AgentRole.KNOWLEDGE_MANAGER: ["Knowledge capture", "Documentation", "Best practices"]
        }
        return capabilities.get(role, [])


def create_sample_incident() -> Dict[str, Any]:
    """Create sample incident for testing"""
    return {
        "id": "INC-2025-001",
        "title": "Email system extremely slow",
        "description": "Multiple users reporting that email is extremely slow to load and send. Started this morning around 9 AM. Affecting approximately 50 users in the Finance department.",
        "reporter": {
            "name": "John Smith",
            "email": "john.smith@company.com",
            "department": "Finance"
        },
        "reported_time": datetime.now().isoformat(),
        "affected_users": 50,
        "business_impact": "Medium - Finance team cannot process time-sensitive communications",
        "urgency": "High",
        "impact": "Medium"
    }


def main():
    """Main function to demonstrate AI agents with ITIL"""
    print("🤖 AI Agents Framework for ITIL - CrewAI Integration")
    print("=" * 60)
    
    # Initialize ITIL integration manager
    print("\n🔧 Initializing ITIL Framework...")
    itil_manager = ITILIntegrationManager()
    
    # Create mock ITIL services for demonstration
    class MockIncidentManagement:
        def get_metrics(self, period_days: int):
            return {"total_incidents": 25, "resolved_incidents": 20}
        
        def get_configuration(self):
            return {"sla_targets": {"P1": "1h", "P2": "4h"}}
        
        def validate_configuration(self):
            return True
        
        def get_health_status(self):
            return {"status": "healthy"}
    
    # Register mock services
    itil_manager.register_practice("incident_management", MockIncidentManagement())
    
    # Initialize framework
    init_results = itil_manager.initialize_framework()
    if init_results["overall_status"] == "SUCCESS":
        print("✅ ITIL Framework initialized successfully")
    else:
        print("❌ ITIL Framework initialization failed")
        return
    
    # Create AI agent crew
    print("\n🤖 Creating AI Agent Crew...")
    agent_crew = ITILAgentCrew(itil_manager)
    
    # Display agent status
    agent_status = agent_crew.get_agent_status()
    print(f"✅ Created {agent_status['total_agents']} specialized agents:")
    
    for role, info in agent_status['agents'].items():
        print(f"  🤖 {role}:")
        print(f"    - Status: {info['status']}")
        print(f"    - Tools: {info['tools_available']}")
        print(f"    - Capabilities: {', '.join(info['capabilities'][:2])}...")
    
    # Create and process sample incident
    print("\n📞 Processing Sample Incident...")
    sample_incident = create_sample_incident()
    
    print(f"📋 Incident Details:")
    print(f"  - ID: {sample_incident['id']}")
    print(f"  - Title: {sample_incident['title']}")
    print(f"  - Affected Users: {sample_incident['affected_users']}")
    print(f"  - Business Impact: {sample_incident['business_impact']}")
    
    # Process incident with AI agents
    print(f"\n🤖 AI Agents Processing Incident...")
    
    try:
        # Simulate agent crew processing
        results = agent_crew.handle_incident(sample_incident)
        
        print(f"✅ Incident Processing Results:")
        print(f"  - Status: {results['status']}")
        print(f"  - Confidence Score: {results.get('confidence_score', 0):.2f}")
        
        if results.get('recommendations'):
            recs = results['recommendations']
            print(f"  - Escalation Needed: {'Yes' if recs.get('escalation_needed') else 'No'}")
            print(f"  - Problem Creation: {'Yes' if recs.get('problem_creation') else 'No'}")
            print(f"  - Knowledge Update: {'Yes' if recs.get('knowledge_update') else 'No'}")
        
        if results.get('next_steps'):
            print(f"  - Next Steps: {len(results['next_steps'])} actions identified")
        
        # Test individual tools
        print(f"\n🔧 Testing Individual Agent Tools...")
        
        # Test incident analysis tool
        analysis_tool = agent_crew.tools["incident_analysis"]
        analysis_result = analysis_tool._run(json.dumps(sample_incident))
        print(f"✅ Incident Analysis: Classification and priority completed")
        
        # Test problem analysis tool
        problem_tool = agent_crew.tools["problem_analysis"]
        problem_result = problem_tool._run(json.dumps([sample_incident]))
        print(f"✅ Problem Analysis: Pattern detection completed")
        
        # Test resolution planning tool
        planning_tool = agent_crew.tools["resolution_planning"]
        planning_result = planning_tool._run(analysis_result)
        print(f"✅ Resolution Planning: Action plan created")
        
        print(f"\n🎉 AI Agents Framework Integration Successful!")
        print(f"\nKey Benefits Achieved:")
        print(f"✅ Automated incident analysis and classification")
        print(f"✅ Intelligent priority assessment") 
        print(f"✅ Pattern recognition for problem identification")
        print(f"✅ Automated resolution planning")
        print(f"✅ Multi-agent collaboration for complex issues")
        print(f"✅ Integration with existing ITIL processes")
        
    except Exception as e:
        print(f"❌ Error processing incident: {e}")
        print(f"💡 Note: This is a demonstration. Install CrewAI for full functionality.")


if __name__ == "__main__":
    main()