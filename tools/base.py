"""
Base tool interface — all tools inherit from this.
"""

from abc import ABC, abstractmethod


class BaseTool(ABC):
    """
    Base class for all agent tools.

    Subclasses must define:
        name: Unique identifier for the tool
        description: What the tool does (LLM reads this to decide when to use it)
        run(input): Execute the tool and return a string result
    """

    name: str = "base_tool"
    description: str = "Base tool — override this description"

    @abstractmethod
    def run(self, input: str) -> str:
        """Execute the tool with the given input and return a string result."""
        raise NotImplementedError

    def __repr__(self):
        return f"Tool(name={self.name})"
