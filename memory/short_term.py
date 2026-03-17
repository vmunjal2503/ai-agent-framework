"""
Short-term memory — conversation buffer for the current task.
"""


class ShortTermMemory:
    """Manages the conversation history within a single agent run."""

    def __init__(self, max_messages: int = 50):
        self.messages: list[dict] = []
        self.max_messages = max_messages

    def add(self, role: str, content: str):
        """Add a message to memory."""
        self.messages.append({"role": role, "content": content})

        # Keep memory bounded (preserve system prompt)
        if len(self.messages) > self.max_messages:
            system = [m for m in self.messages if m["role"] == "system"]
            recent = self.messages[-(self.max_messages - len(system)):]
            self.messages = system + recent

    def get_messages(self) -> list[dict]:
        """Get all messages for LLM context."""
        return self.messages.copy()

    def get_last(self, n: int = 5) -> list[dict]:
        """Get the last N messages."""
        return self.messages[-n:]

    def clear(self):
        """Clear all messages."""
        self.messages = []

    def __len__(self):
        return len(self.messages)
