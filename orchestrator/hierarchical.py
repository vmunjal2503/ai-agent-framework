"""
Hierarchical orchestrator — a manager agent delegates tasks to worker agents.

Use case: Complex projects where a coordinator breaks work into subtasks
and assigns them to specialized agents.
"""

from agents.base import Agent
from agents.planner import PlannerAgent
from orchestrator.base import BaseOrchestrator


class HierarchicalOrchestrator(BaseOrchestrator):
    """Manager-worker pattern: planner creates tasks, workers execute them."""

    def __init__(self, agents, verbose=True, planner=None):
        super().__init__(agents, verbose)
        self.planner = planner or PlannerAgent(verbose=verbose)
        self.agent_map = {agent.name.lower(): agent for agent in agents}

    def run(self, goal: str) -> str:
        """
        1. Planner creates a step-by-step plan
        2. Each step is assigned to the most suitable agent
        3. Results are collected and synthesized
        """
        self._log(f"Manager creating execution plan...")

        # Step 1: Create plan
        plan = self.planner.create_plan(goal)
        steps = plan.get("steps", [])

        self._log(f"Plan created with {len(steps)} steps:")
        for step in steps:
            self._log(f"  {step.get('id', '?')}. {step.get('description', '')}")

        # Step 2: Execute each step
        results = {}
        for step in steps:
            step_id = step.get("id", 0)
            description = step.get("description", "")
            agent_type = step.get("agent_type", "").lower()

            # Find matching agent
            agent = self._find_agent(agent_type)
            if not agent:
                self._log(f"  No agent found for type '{agent_type}', using first available")
                agent = self.agents[0]

            self._log(f"\nExecuting step {step_id} with agent '{agent.name}'...")

            # Include context from previous steps
            context = "\n".join([
                f"Step {k} result: {v}" for k, v in results.items()
            ])

            prompt = f"""Task: {description}

Previous results:
{context if context else 'None yet'}

Execute this step and provide a clear result."""

            result = agent.run(prompt)
            results[step_id] = result

        # Step 3: Compile final result
        final = f"Goal: {goal}\n\n"
        for step_id, result in results.items():
            final += f"Step {step_id}:\n{result}\n\n"

        self._log("Hierarchical execution complete.")
        return final

    def _find_agent(self, agent_type: str) -> Agent:
        """Find the best matching agent for a step type."""
        # Direct name match
        if agent_type in self.agent_map:
            return self.agent_map[agent_type]

        # Fuzzy match
        for name, agent in self.agent_map.items():
            if agent_type in name or name in agent_type:
                return agent

        return None
