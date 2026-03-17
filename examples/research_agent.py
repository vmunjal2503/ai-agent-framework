"""
Example: Research Agent — searches the web and summarizes findings.

Usage:
    python examples/research_agent.py
"""

import sys
sys.path.insert(0, ".")

from agents import Agent
from tools import WebSearchTool, WebScraperTool, CalculatorTool


def main():
    agent = Agent(
        name="Research Assistant",
        role=(
            "You are a research assistant. Your job is to find accurate, "
            "up-to-date information from the web and provide well-structured summaries. "
            "Always verify information from multiple sources when possible."
        ),
        tools=[WebSearchTool(), WebScraperTool(), CalculatorTool()],
        model="gpt-4o",
        max_iterations=8,
    )

    result = agent.run(
        "What are the top 3 Python web frameworks in 2024? "
        "Compare their GitHub stars, performance benchmarks, and best use cases."
    )

    print("\n" + "=" * 60)
    print("RESEARCH RESULT")
    print("=" * 60)
    print(result)


if __name__ == "__main__":
    main()
