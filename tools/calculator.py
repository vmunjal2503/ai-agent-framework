"""
Calculator tool — evaluate mathematical expressions safely.
"""

import ast
import operator
from tools.base import BaseTool


class CalculatorTool(BaseTool):
    name = "calculator"
    description = (
        "Evaluate mathematical expressions. Input should be a math expression. "
        "Supports: +, -, *, /, **, %, parentheses. "
        "Example: '(15 * 3) + (200 / 4)'"
    )

    # Safe operators
    OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod,
        ast.USub: operator.neg,
    }

    def run(self, input: str) -> str:
        """Safely evaluate a mathematical expression."""
        expr = input.strip()
        try:
            tree = ast.parse(expr, mode="eval")
            result = self._eval_node(tree.body)
            return str(result)
        except (ValueError, TypeError, SyntaxError, ZeroDivisionError) as e:
            return f"Error: {str(e)}"

    def _eval_node(self, node):
        """Recursively evaluate AST nodes."""
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError(f"Unsupported constant: {node.value}")

        elif isinstance(node, ast.BinOp):
            op = self.OPERATORS.get(type(node.op))
            if not op:
                raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            return op(left, right)

        elif isinstance(node, ast.UnaryOp):
            op = self.OPERATORS.get(type(node.op))
            if not op:
                raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
            return op(self._eval_node(node.operand))

        else:
            raise ValueError(f"Unsupported expression type: {type(node).__name__}")
