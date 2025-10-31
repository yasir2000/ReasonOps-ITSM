"""
AI Agents Module for ITIL Framework

This module provides AI-powered automation for ITIL processes using
multi-agent systems that can analyze, reason, plan, and collaborate
to solve incidents and other ITIL processes autonomously.
"""

from .itil_crewai_integration import (
    ITILAgentCrew,
    AgentRole,
    AgentCapability,
    ITILAgentTool,
    IncidentAnalysisTool,
    ProblemAnalysisTool,
    ResolutionPlanningTool,
    create_sample_incident
)
from .matis_task_executor import MatisTaskExecutor, get_matis_executor

__all__ = [
    'ITILAgentCrew',
    'AgentRole', 
    'AgentCapability',
    'ITILAgentTool',
    'IncidentAnalysisTool',
    'ProblemAnalysisTool', 
    'ResolutionPlanningTool',
    'create_sample_incident',
    'MatisTaskExecutor',
    'get_matis_executor'
]

__version__ = '1.0.0'
__author__ = 'ITIL AI Agents Team'