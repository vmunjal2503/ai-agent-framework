"""
Planner Agent — Breaks complex goals into executable step-by-step plans.
"""

import json
from agents.base import Agent


PLANNER_ROLE = """You are a planning agent. Your job is to break down complex goals
into clear, actionable steps that other agents can execute.

When creating a plan:
1. Identify all sub-tasks needed to achieve the goal
2. Order them by dependency (what must happen first)
3. Specify which type of agent/tool is needed for each step
4. Include verification steps to check progress

Output plans as JSON with this structure:
{
    "goal": "The original goal",
    "steps": [
        {
            "id": 1,
            "description": "What to do",
            "agent_type": "researcher|coder|writer",
            "depends_on": [],
            "expected_output": "What this step should produce"
        }
    ]
}"""


class PlannerAgent(Agent):
    """Agent that creates execution plans for complex tasks."""

    def __init__(self, **kwargs):
        super().__init__(
            name=kwargs.get("name", "Planner"),
            role=PLANNER_ROLE,
            tools=kwargs.get("tools", []),
            model=kwargs.get("model"),
            verbose=kwargs.get("verbose"),
        )

    def create_plan(self, goal: str) -> dict:
        """Create a structured execution plan for a goal."""
        result = self.run(f"Create a detailed execution plan for: {goal}")

        try:
            # Try to parse as JSON
            plan = json.loads(result)
            return plan
        except json.JSONDecodeError:
            # Extract JSON from response
            start = result.find("{")
            end = result.rfind("}") + 1
            if start >= 0 and end > start:
                try:
                    return json.loads(result[start:end])
                except json.JSONDecodeError:
                    pass

        # Fallback: single-step plan
        return {
            "goal": goal,
            "steps": [{"id": 1, "description": result, "agent_type": "general", "depends_on": []}],
        }
