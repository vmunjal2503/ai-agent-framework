"""
Example: Code Agent — writes and executes Python code to solve problems.

Usage:
    python examples/code_agent.py
"""

import sys
sys.path.insert(0, ".")

from agents import Agent
from tools import CodeExecutorTool, FileSystemTool, CalculatorTool


def main():
    agent = Agent(
        name="Code Developer",
        role=(
            "You are a Python developer. You write clean, well-documented code "
            "and test it by executing it. When asked to solve a problem, write "
            "the code, run it to verify it works, then save the final version."
        ),
        tools=[CodeExecutorTool(), FileSystemTool(), CalculatorTool()],
        model="gpt-4o",
        max_iterations=10,
    )

    result = agent.run(
        "Write a Python script that fetches the current Bitcoin price from a public API, "
        "calculates the 24-hour change percentage, and formats it as a clean report. "
        "Execute the code to verify it works, then save it to 'crypto_report.py'."
    )

    print("\n" + "=" * 60)
    print("CODE AGENT RESULT")
    print("=" * 60)
    print(result)


if __name__ == "__main__":
    main()
