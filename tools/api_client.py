"""
API Client tool — make HTTP requests to REST APIs.
"""

import json
import httpx
from tools.base import BaseTool


class APIClientTool(BaseTool):
    name = "api_client"
    description = (
        "Make HTTP requests to REST APIs. Input should be JSON with: "
        "'method' (GET/POST/PUT/DELETE), 'url', optional 'headers' and 'body'. "
        'Example: {"method": "GET", "url": "https://api.example.com/data"}'
    )

    def run(self, input: str) -> str:
        """Make an HTTP request and return the response."""
        try:
            params = json.loads(input)
        except json.JSONDecodeError:
            return "Error: Input must be valid JSON"

        method = params.get("method", "GET").upper()
        url = params.get("url", "")
        headers = params.get("headers", {})
        body = params.get("body")

        if not url:
            return "Error: 'url' is required"

        try:
            response = httpx.request(
                method=method,
                url=url,
                headers=headers,
                json=body if body else None,
                timeout=15,
            )

            result = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
            }

            # Try to parse as JSON
            try:
                result["body"] = response.json()
            except Exception:
                result["body"] = response.text[:2000]

            return json.dumps(result, indent=2)

        except Exception as e:
            return f"Error: {str(e)}"
