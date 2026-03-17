"""
Base orchestrator — coordinates multiple agents.
"""

from abc import ABC, abstractmethod
from agents.base import Agent


class BaseOrchestrator(ABC):
    """Base class for multi-agent orchestration strategies."""

    def __init__(self, agents: list[Agent], verbose: bool = True):
        self.agents = agents
        self.verbose = verbose

    @abstractmethod
    def run(self, goal: str) -> str:
        """Execute the orchestration strategy."""
        raise NotImplementedError

    def _log(self, msg: str):
        if self.verbose:
            print(f"[Orchestrator] {msg}")
