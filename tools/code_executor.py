"""
Code Executor tool — run Python code in a sandboxed subprocess.
"""

import subprocess
import tempfile
import os
from tools.base import BaseTool


class CodeExecutorTool(BaseTool):
    name = "code_executor"
    description = (
        "Execute Python code and return the output. "
        "Input should be valid Python code. "
        "Use print() to output results. Code runs in an isolated subprocess."
    )

    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    def run(self, input: str) -> str:
        """Execute Python code in a sandboxed subprocess."""
        code = input.strip()

        # Remove markdown code blocks if present
        if code.startswith("```python"):
            code = code[9:]
        if code.startswith("```"):
            code = code[3:]
        if code.endswith("```"):
            code = code[:-3]
        code = code.strip()

        # Write to temp file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as f:
            f.write(code)
            temp_path = f.name

        try:
            result = subprocess.run(
                ["python3", temp_path],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            )

            output = ""
            if result.stdout:
                output += result.stdout
            if result.stderr:
                output += f"\nSTDERR:\n{result.stderr}"
            if result.returncode != 0:
                output += f"\nExit code: {result.returncode}"

            return output.strip() or "(no output)"

        except subprocess.TimeoutExpired:
            return f"Error: Code execution timed out after {self.timeout}s"
        except Exception as e:
            return f"Error executing code: {str(e)}"
        finally:
            os.unlink(temp_path)
