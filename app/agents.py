"""Agent definitions for the research pipeline."""

from agents import Agent
from app.tools import tavily_search
from app.models import ResearchSummary, AnalysisInsights, FinalReport


def create_researcher_agent():
    """Create the Researcher agent with Tavily search capability."""
    return Agent(
        name="Researcher",
        model="gpt-4o-mini",  # Using cheaper model to conserve credits
        instructions="""
You are a thorough research assistant.

Your job is to:
1. Use the tavily_search tool to gather information from the web
2. Search multiple times with different queries if needed to get comprehensive information
3. Compile a detailed summary of your findings
4. List all sources you used

IMPORTANT: Always use the tavily_search tool before providing your summary.
Do not make up information - only use what you find from searches.
""",
        tools=[tavily_search],
        output_type=ResearchSummary
    )


def create_analyst_agent():
    """Create the Analyst agent."""
    return Agent(
        name="Analyst",
        model="gpt-4o-mini",
        instructions="""
You are an analytical expert who reviews research findings.

Your job is to:
1. Review the research summary provided
2. Identify emerging trends
3. Highlight potential risks or concerns
4. Extract key insights that are actionable

Be concise but thorough. Focus on what matters most.
""",
        output_type=AnalysisInsights
    )


def create_writer_agent():
    """Create the Writer agent."""
    return Agent(
        name="Writer",
        model="gpt-4o-mini",
        instructions="""
You are a professional report writer.

Your job is to:
1. Create a concise executive summary (2-3 paragraphs)
2. Write a well-formatted markdown report with:
   - Introduction
   - Key Findings (from research)
   - Analysis (trends, risks, insights)
   - Conclusion
3. Generate 3-5 follow-up questions for deeper investigation

Use clear headings, bullet points, and proper markdown formatting.
Make the report professional and easy to read.
""",
        output_type=FinalReport
    )
