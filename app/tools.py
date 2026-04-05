"""Tools for the research pipeline agents."""

import os
import json
import requests
from agents import function_tool


@function_tool
def tavily_search(query: str, max_results: int = 5) -> str:
    """
    Search the web using Tavily API.

    Args:
        query: The search query
        max_results: Maximum number of results to return (default: 5)

    Returns:
        JSON string containing search results with titles, URLs, and content
    """
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    if not tavily_api_key:
        return json.dumps({"error": "TAVILY_API_KEY not found in environment"})

    url = "https://api.tavily.com/search"
    payload = {
        "api_key": tavily_api_key,
        "query": query,
        "max_results": max_results
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Format results
        results = []
        for result in data.get("results", []):
            results.append({
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "content": result.get("content", "")
            })

        return json.dumps(results, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})
