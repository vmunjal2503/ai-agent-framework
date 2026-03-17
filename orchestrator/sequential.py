"""
Sequential orchestrator — agents execute in order, each receiving
the output of the previous agent.

Use case: Research → Code → Write pipeline
"""

from orchestrator.base import BaseOrchestrator


class SequentialOrchestrator(BaseOrchestrator):
    """Run agents in sequence, piping outputs forward."""

    def run(self, goal: str) -> str:
        """
        Execute agents sequentially.
        Each agent receives the original goal + previous agent's output.
        """
        self._log(f"Starting sequential execution with {len(self.agents)} agents")
        self._log(f"Goal: {goal}\n")

        current_context = ""

        for i, agent in enumerate(self.agents):
            self._log(f"Step {i+1}/{len(self.agents)}: Agent '{agent.name}'")

            # Build prompt with accumulated context
            if current_context:
                prompt = f"""Original goal: {goal}

Previous agent output:
{current_context}

Your task: Continue working on the goal using the information above."""
            else:
                prompt = goal

            # Run agent
            result = agent.run(prompt)
            current_context = result

            self._log(f"Agent '{agent.name}' completed.\n")

        self._log("Sequential execution complete.")
        return current_context
