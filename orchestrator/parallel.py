"""
Parallel orchestrator — agents execute concurrently on the same goal,
results are merged.

Use case: Multiple researchers investigating different aspects simultaneously.
"""

import concurrent.futures
from orchestrator.base import BaseOrchestrator


class ParallelOrchestrator(BaseOrchestrator):
    """Run agents in parallel, then merge results."""

    def __init__(self, agents, verbose=True, max_workers=None):
        super().__init__(agents, verbose)
        self.max_workers = max_workers or len(agents)

    def run(self, goal: str) -> str:
        """
        Execute all agents concurrently on the same goal.
        Returns merged results from all agents.
        """
        self._log(f"Starting parallel execution with {len(self.agents)} agents")

        results = {}

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_agent = {
                executor.submit(agent.run, goal): agent
                for agent in self.agents
            }

            for future in concurrent.futures.as_completed(future_to_agent):
                agent = future_to_agent[future]
                try:
                    result = future.result()
                    results[agent.name] = result
                    self._log(f"Agent '{agent.name}' completed.")
                except Exception as e:
                    results[agent.name] = f"Error: {str(e)}"
                    self._log(f"Agent '{agent.name}' failed: {e}")

        # Merge results
        merged = f"Goal: {goal}\n\n"
        for agent_name, result in results.items():
            merged += f"=== {agent_name} ===\n{result}\n\n"

        self._log("Parallel execution complete.")
        return merged
