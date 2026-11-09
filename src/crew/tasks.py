"""
CrewAI Multi-Agent Tasks Module.
Defines granular research and solution design tasks with strict
Pydantic output conformance for automated lead analysis.
"""

from crewai import Task

from src.crew.agents import LeadResearchAgents
from src.schemas.lead_validation import CrewAnalysisOutput


class LeadResearchTasks:
    """Factory class encapsulating specialized B2B research task definitions."""

    def __init__(self) -> None:
        self.agents = LeadResearchAgents()

    def audit_website_task(self, company_name: str, target_url: str) -> Task:
        """
        Defines the website auditing task for uncovering operational bottlenecks
        and manual friction points.
        Note (MVP Limit): Relies on agent contextual knowledge of the target URL
        pending external scraper integration.
        """
        agent = self.agents.website_analyzer_agent()
        return Task(
            description=(
                f"Conduct a rigorous technical and operational audit of {company_name} "
                f"via their official website at {target_url}. "
                "Identify manual bottlenecks, customer friction points, and legacy workflows "
                "that can be transformed through AI automation."
            ),
            expected_output=(
                "A comprehensive summary of identified operational bottlenecks, "
                "inefficiencies, and technical gaps discovered during the website review."
            ),
            agent=agent,
        )

    def design_solution_task(self, company_name: str) -> Task:
        """
        Defines the solution architecture task for drafting a tailored automation proposal
        and enforcing strict Pydantic output schema validation.
        """
        agent = self.agents.solution_architect_agent()
        return Task(
            description=(
                f"Synthesize the audit findings for {company_name} into a professional, high-impact "
                f"AI automation solution proposal. Calculate a precise confidence score (between 0.0 and 1.0) "
                f"reflecting feasibility and implementation ROI."
            ),
            expected_output=(
                "A structured JSON response conforming strictly to the CrewAnalysisOutput schema, "
                "containing the company name, identified bottlenecks, proposed solution, and confidence score."
            ),
            agent=agent,
            output_json=CrewAnalysisOutput,
        )
