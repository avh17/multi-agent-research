"""Research pipeline orchestration with async streaming."""

import uuid
import asyncio
from typing import AsyncGenerator
from agents import Runner, SQLiteSession
from app.agents import create_researcher_agent, create_analyst_agent, create_writer_agent
from app.models import FinalReport


async def run_pipeline_stream(user_query: str) -> AsyncGenerator[dict, None]:
    """
    Async generator that yields stage events during pipeline execution.

    Args:
        user_query: The research question/topic

    Yields:
        dict: Event objects with type and data
    """
    session_id = str(uuid.uuid4())

    try:
        # Start event
        yield {
            "type": "start",
            "data": {
                "session_id": session_id,
                "query": user_query
            }
        }

        # Create session
        session = SQLiteSession(session_id=session_id)

        # Stage 1: Research
        yield {
            "type": "stage",
            "data": {
                "stage": "research",
                "status": "started",
                "message": "Searching the web for information..."
            }
        }

        researcher = create_researcher_agent()

        # Run research using the static method
        research_result = await Runner.run(researcher, user_query, session=session)
        research_summary = research_result.final_output

        yield {
            "type": "stage",
            "data": {
                "stage": "research",
                "status": "completed",
                "message": f"Found {len(research_summary.sources)} sources",
                "result": {
                    "summary": research_summary.summary,
                    "sources": research_summary.sources
                }
            }
        }

        # Stage 2: Analysis
        yield {
            "type": "stage",
            "data": {
                "stage": "analysis",
                "status": "started",
                "message": "Analyzing findings..."
            }
        }

        analyst = create_analyst_agent()
        analysis_prompt = f"""
Analyze this research summary:

Query: {research_summary.query}
Summary: {research_summary.summary}
Sources: {', '.join(research_summary.sources)}
"""

        analysis_result = await Runner.run(analyst, analysis_prompt, session=session)
        analysis_insights = analysis_result.final_output

        yield {
            "type": "stage",
            "data": {
                "stage": "analysis",
                "status": "completed",
                "message": f"Identified {len(analysis_insights.trends)} trends and {len(analysis_insights.risks)} risks",
                "result": {
                    "trends": analysis_insights.trends,
                    "risks": analysis_insights.risks,
                    "key_insights": analysis_insights.key_insights
                }
            }
        }

        # Stage 3: Report Writing
        yield {
            "type": "stage",
            "data": {
                "stage": "writing",
                "status": "started",
                "message": "Generating final report..."
            }
        }

        writer = create_writer_agent()
        writer_prompt = f"""
Create a comprehensive report based on:

RESEARCH:
- Query: {research_summary.query}
- Summary: {research_summary.summary}
- Sources: {', '.join(research_summary.sources)}

ANALYSIS:
- Trends: {', '.join(analysis_insights.trends)}
- Risks: {', '.join(analysis_insights.risks)}
- Key Insights: {', '.join(analysis_insights.key_insights)}
"""

        final_result = await Runner.run(writer, writer_prompt, session=session)
        final_report = final_result.final_output

        yield {
            "type": "stage",
            "data": {
                "stage": "writing",
                "status": "completed",
                "message": "Report completed"
            }
        }

        # Final result
        yield {
            "type": "complete",
            "data": {
                "executive_summary": final_report.executive_summary,
                "markdown_report": final_report.markdown_report,
                "follow_up_questions": final_report.follow_up_questions
            }
        }

    except Exception as e:
        yield {
            "type": "error",
            "data": {
                "message": str(e)
            }
        }
