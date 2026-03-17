"""
File System tool — read, write, and list files.
"""

import os
import json
from tools.base import BaseTool


class FileSystemTool(BaseTool):
    name = "file_system"
    description = (
        "Read, write, or list files. Input should be JSON with 'action' and 'path'. "
        "Actions: 'read' (read file), 'write' (write file, include 'content'), "
        "'list' (list directory), 'exists' (check if file exists). "
        'Example: {"action": "read", "path": "data.txt"}'
    )

    def __init__(self, base_dir: str = "./workspace"):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)

    def run(self, input: str) -> str:
        """Execute a file system operation."""
        try:
            params = json.loads(input)
        except json.JSONDecodeError:
            return "Error: Input must be valid JSON with 'action' and 'path'"

        action = params.get("action", "")
        path = params.get("path", "")

        # Sandbox: prevent path traversal
        safe_path = os.path.normpath(os.path.join(self.base_dir, path))
        if not safe_path.startswith(os.path.normpath(self.base_dir)):
            return "Error: Path traversal not allowed"

        if action == "read":
            return self._read(safe_path)
        elif action == "write":
            content = params.get("content", "")
            return self._write(safe_path, content)
        elif action == "list":
            return self._list(safe_path)
        elif action == "exists":
            return str(os.path.exists(safe_path))
        else:
            return f"Error: Unknown action '{action}'. Use: read, write, list, exists"

    def _read(self, path: str) -> str:
        try:
            with open(path, "r") as f:
                content = f.read()
            if len(content) > 5000:
                return content[:5000] + "\n...[truncated]"
            return content
        except FileNotFoundError:
            return f"Error: File not found: {path}"

    def _write(self, path: str, content: str) -> str:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(content)
        return f"Successfully wrote {len(content)} characters to {path}"

    def _list(self, path: str) -> str:
        try:
            entries = os.listdir(path)
            return "\n".join(sorted(entries))
        except FileNotFoundError:
            return f"Error: Directory not found: {path}"
