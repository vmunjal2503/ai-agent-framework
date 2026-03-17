"""
Example: Multi-Agent Report — 3 agents collaborate sequentially.

Pipeline: Researcher → Developer → Writer

Usage:
    python examples/multi_agent_report.py
"""

import sys
sys.path.insert(0, ".")

from agents import Agent
from tools import WebSearchTool, WebScraperTool, CodeExecutorTool, FileSystemTool
from orchestrator import SequentialOrchestrator


def main():
    # Agent 1: Researcher
    researcher = Agent(
        name="Researcher",
        role=(
            "You are a technical researcher. Search the web for information "
            "and provide detailed, factual findings with sources."
        ),
        tools=[WebSearchTool(), WebScraperTool()],
    )

    # Agent 2: Developer
    developer = Agent(
        name="Developer",
        role=(
            "You are a Python developer. Take research findings and create "
            "working code examples, benchmarks, or data analysis scripts."
        ),
        tools=[CodeExecutorTool(), FileSystemTool()],
    )

    # Agent 3: Writer
    writer = Agent(
        name="Writer",
        role=(
            "You are a technical writer. Take research and code from other agents "
            "and create a polished, well-structured report with sections, "
            "key findings, and recommendations."
        ),
        tools=[FileSystemTool()],
    )

    # Orchestrate
    orchestrator = SequentialOrchestrator(
        agents=[researcher, developer, writer],
        verbose=True,
    )

    result = orchestrator.run(
        "Create a comprehensive comparison of FastAPI vs Django for building REST APIs. "
        "Include performance benchmarks, code examples, and recommendations."
    )

    print("\n" + "=" * 60)
    print("MULTI-AGENT REPORT")
    print("=" * 60)
    print(result)


if __name__ == "__main__":
    main()
