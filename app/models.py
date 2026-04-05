"""Data models for the research pipeline API."""

from pydantic import BaseModel
from typing import List


class ResearchRequest(BaseModel):
    """Request model for research endpoint."""
    query: str


class ResearchSummary(BaseModel):
    """Output from Researcher agent."""
    query: str
    summary: str
    sources: List[str]


class AnalysisInsights(BaseModel):
    """Output from Analyst agent."""
    trends: List[str]
    risks: List[str]
    key_insights: List[str]


class FinalReport(BaseModel):
    """Final report output from Writer agent."""
    executive_summary: str
    markdown_report: str
    follow_up_questions: List[str]
