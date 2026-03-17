"""
Critic Agent — Evaluates agent outputs for quality and correctness.
"""

from agents.base import Agent


CRITIC_ROLE = """You are a critic agent. Your job is to evaluate the quality
and correctness of work produced by other agents.

When evaluating, consider:
1. Accuracy — Is the information correct?
2. Completeness — Does it fully address the goal?
3. Quality — Is it well-structured and clear?
4. Actionability — Can the user act on this?

Provide your evaluation as:
{
    "score": 1-10,
    "passed": true/false,
    "issues": ["list of problems found"],
    "suggestions": ["list of improvements"],
    "summary": "Brief overall assessment"
}"""


class CriticAgent(Agent):
    """Agent that evaluates and critiques outputs from other agents."""

    def __init__(self, **kwargs):
        super().__init__(
            name=kwargs.get("name", "Critic"),
            role=CRITIC_ROLE,
            tools=[],
            model=kwargs.get("model"),
            verbose=kwargs.get("verbose", False),
        )

    def evaluate(self, goal: str, output: str, min_score: int = 7) -> dict:
        """
        Evaluate an agent's output against the original goal.

        Returns dict with score, passed, issues, and suggestions.
        """
        prompt = f"""Evaluate this output:

Original Goal: {goal}

Agent Output:
{output}

Minimum acceptable score: {min_score}/10
"""
        result = self.run(prompt)

        import json
        try:
            evaluation = json.loads(result)
            evaluation["passed"] = evaluation.get("score", 0) >= min_score
            return evaluation
        except (json.JSONDecodeError, TypeError):
            return {
                "score": 5,
                "passed": False,
                "issues": ["Could not parse evaluation"],
                "suggestions": ["Re-run evaluation"],
                "summary": result,
            }
