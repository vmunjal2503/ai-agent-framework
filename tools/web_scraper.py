"""
Web Scraper tool — fetch and extract text from web pages.
"""

import httpx
from bs4 import BeautifulSoup
from tools.base import BaseTool


class WebScraperTool(BaseTool):
    name = "web_scraper"
    description = (
        "Fetch a web page and extract its text content. "
        "Input should be a URL. Returns the page text (truncated to 3000 chars)."
    )

    def run(self, input: str) -> str:
        """Fetch a URL and return its text content."""
        url = input.strip()
        if not url.startswith("http"):
            url = "https://" + url

        try:
            response = httpx.get(
                url,
                headers={"User-Agent": "Mozilla/5.0 (compatible; AIAgent/1.0)"},
                timeout=15,
                follow_redirects=True,
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove script and style elements
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()

            text = soup.get_text(separator="\n", strip=True)

            # Clean up whitespace
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            clean_text = "\n".join(lines)

            # Truncate
            if len(clean_text) > 3000:
                clean_text = clean_text[:3000] + "\n...[truncated]"

            return clean_text

        except Exception as e:
            return f"Error fetching {url}: {str(e)}"
