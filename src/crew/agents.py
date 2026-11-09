"""
CrewAI Multi-Agent Definitions Module.
Instantiates specialized AI agents configured with OpenAI models,
custom system prompts, and strict operational tools for B2B lead research.
"""

import os
from crewai import Agent

from config.settings import settings


class LeadResearchAgents:
    """Factory class encapsulating specialized B2B research agent definitions."""

    def __init__(self) -> None:
        # Ensure OpenAI API key is exported in environment for CrewAI underlying LLM calls
        os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY

    def website_analyzer_agent(self) -> Agent:
        """
        Instantiates the Lead Researcher & Website Auditor agent.
        Responsible for crawling target URLs, identifying operational bottlenecks,
        and analyzing technical gaps.
        """
        return Agent(
            role="Senior B2B Technical Auditor & Lead Researcher",
            goal=(
                "Thoroughly analyze the target company's website and public footprint "
                "to uncover critical operational bottlenecks, manual friction points, and automation opportunities."
            ),
            backstory=(
                "You are an elite technical auditor for boutique US AI automation agencies. "
                "You have years of experience dissecting business workflows, spotting inefficiencies, "
                "and identifying where LLMs, workflow automation, and custom backends can drive massive ROI."
            ),
            verbose=True,
            memory=True,
            max_iter=3,
            allow_delegation=False,
        )

    def solution_architect_agent(self) -> Agent:
        """
        Instantiates the AI Solution Architect & Proposal Writer agent.
        Responsible for designing tailored automation solutions and calculating confidence scores.
        """
        return Agent(
            role="Principal AI Solutions Architect",
            goal=(
                "Synthesize audit findings into high-impact, professional AI automation proposals "
                "with concrete architectural solutions and calculated confidence ratings."
            ),
            backstory=(
                "You are a seasoned AI solution architect who bridges the gap between complex client "
                "workflows and high-performance automation stacks. You draft concise, persuasive, "
                "and technically rigorous proposals that appeal directly to engineering leaders and founders."
            ),
            verbose=True,
            memory=True,
            max_iter=2,
            allow_delegation=False,
        )
