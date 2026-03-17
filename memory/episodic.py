"""
Episodic memory — remembers past task results for learning.
"""

import json
from datetime import datetime, timezone
from typing import Optional


class EpisodicMemory:
    """
    Stores past task results so agents can learn from experience.
    Similar tasks can reference previous successes and failures.
    """

    def __init__(self, max_episodes: int = 100):
        self.episodes: list[dict] = []
        self.max_episodes = max_episodes

    def record(self, goal: str, result: str, success: bool, metadata: dict = None):
        """Record a completed task episode."""
        episode = {
            "goal": goal,
            "result": result,
            "success": success,
            "metadata": metadata or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.episodes.append(episode)

        # Keep bounded
        if len(self.episodes) > self.max_episodes:
            self.episodes = self.episodes[-self.max_episodes:]

    def find_similar(self, goal: str, limit: int = 3) -> list[dict]:
        """
        Find past episodes similar to the current goal.
        Uses simple keyword matching (upgrade to embeddings for production).
        """
        goal_words = set(goal.lower().split())

        scored = []
        for ep in self.episodes:
            ep_words = set(ep["goal"].lower().split())
            overlap = len(goal_words & ep_words)
            if overlap > 0:
                scored.append((overlap, ep))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [ep for _, ep in scored[:limit]]

    def get_successes(self, limit: int = 5) -> list[dict]:
        """Get recent successful episodes."""
        successes = [ep for ep in self.episodes if ep["success"]]
        return successes[-limit:]

    def get_failures(self, limit: int = 5) -> list[dict]:
        """Get recent failed episodes."""
        failures = [ep for ep in self.episodes if not ep["success"]]
        return failures[-limit:]
