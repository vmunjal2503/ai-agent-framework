"""
Web Search tool — search the internet using SerpAPI or Tavily.
"""

import os
import json
import httpx
from tools.base import BaseTool


class WebSearchTool(BaseTool):
    name = "web_search"
    description = (
        "Search the web for current information. Input should be a search query string. "
        "Returns top search results with titles, snippets, and URLs."
    )

    def __init__(self):
        self.provider = "serpapi" if os.getenv("SERPAPI_API_KEY") else "tavily"

    def run(self, input: str) -> str:
        """Search the web and return top results."""
        if self.provider == "serpapi":
            return self._search_serpapi(input)
        else:
            return self._search_tavily(input)

    def _search_serpapi(self, query: str) -> str:
        api_key = os.getenv("SERPAPI_API_KEY")
        if not api_key:
            return "Error: SERPAPI_API_KEY not set"

        response = httpx.get(
            "https://serpapi.com/search",
            params={"q": query, "api_key": api_key, "num": 5},
            timeout=15,
        )
        data = response.json()

        results = []
        for item in data.get("organic_results", [])[:5]:
            results.append({
                "title": item.get("title", ""),
                "snippet": item.get("snippet", ""),
                "url": item.get("link", ""),
            })

        return json.dumps(results, indent=2)

    def _search_tavily(self, query: str) -> str:
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            return "Error: No search API key configured. Set SERPAPI_API_KEY or TAVILY_API_KEY."

        response = httpx.post(
            "https://api.tavily.com/search",
            json={"query": query, "api_key": api_key, "max_results": 5},
            timeout=15,
        )
        data = response.json()

        results = []
        for item in data.get("results", [])[:5]:
            results.append({
                "title": item.get("title", ""),
                "snippet": item.get("content", "")[:300],
                "url": item.get("url", ""),
            })

        return json.dumps(results, indent=2)
