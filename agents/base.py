"""
Base Agent — ReAct (Reason + Act) loop with tool use.

The agent follows this cycle:
1. THINK: Reason about what to do next
2. ACT: Choose and invoke a tool
3. OBSERVE: Process the tool's output
4. REPEAT until goal is achieved or max iterations reached
"""

import os
import json
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv

from tools.base import BaseTool
from memory.short_term import ShortTermMemory

load_dotenv()


REACT_SYSTEM_PROMPT = """You are an AI agent that solves tasks step by step.

You have access to these tools:
{tool_descriptions}

For each step, respond in this EXACT JSON format:
{{
    "thought": "Your reasoning about what to do next",
    "action": "tool_name",
    "action_input": "input for the tool"
}}

When you have the final answer, respond with:
{{
    "thought": "I now have enough information to answer",
    "action": "final_answer",
    "action_input": "Your complete final answer here"
}}

Rules:
1. Always think before acting
2. Use tools to gather information — don't guess
3. If a tool returns an error, try a different approach
4. Be concise in your thoughts
5. Provide a comprehensive final answer"""


class Agent:
    """
    Autonomous AI agent with ReAct reasoning and tool use.

    Args:
        name: Agent identifier
        role: System prompt describing the agent's role
        tools: List of Tool instances the agent can use
        model: LLM model name (default: gpt-4o)
        max_iterations: Maximum reasoning steps (default: 10)
        verbose: Print reasoning steps (default: True)
    """

    def __init__(
        self,
        name: str,
        role: str,
        tools: list[BaseTool] = None,
        model: str = None,
        max_iterations: int = None,
        verbose: bool = None,
    ):
        self.name = name
        self.role = role
        self.tools = {tool.name: tool for tool in (tools or [])}
        self.model = model or os.getenv("LLM_MODEL", "gpt-4o")
        self.max_iterations = max_iterations or int(os.getenv("MAX_ITERATIONS", "10"))
        self.verbose = verbose if verbose is not None else os.getenv("VERBOSE", "true").lower() == "true"
        self.memory = ShortTermMemory()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def run(self, goal: str) -> str:
        """
        Execute the ReAct loop to achieve the given goal.

        Args:
            goal: The task/question for the agent to solve

        Returns:
            The agent's final answer as a string
        """
        if self.verbose:
            print(f"\n{'='*60}")
            print(f"Agent: {self.name}")
            print(f"Goal: {goal}")
            print(f"{'='*60}\n")

        # Build system prompt with tool descriptions
        tool_desc = "\n".join([
            f"- {name}: {tool.description}"
            for name, tool in self.tools.items()
        ])
        system_prompt = f"{self.role}\n\n{REACT_SYSTEM_PROMPT.format(tool_descriptions=tool_desc)}"

        self.memory.clear()
        self.memory.add("system", system_prompt)
        self.memory.add("user", f"Goal: {goal}")

        for iteration in range(1, self.max_iterations + 1):
            if self.verbose:
                print(f"--- Step {iteration}/{self.max_iterations} ---")

            # Get LLM response
            response = self._call_llm()

            # Parse the response
            parsed = self._parse_response(response)
            if not parsed:
                self.memory.add("assistant", response)
                self.memory.add("user", "Please respond in the required JSON format.")
                continue

            thought = parsed.get("thought", "")
            action = parsed.get("action", "")
            action_input = parsed.get("action_input", "")

            if self.verbose:
                print(f"Thought: {thought}")
                print(f"Action: {action}")
                print(f"Input: {action_input[:200]}")

            # Check if agent is done
            if action == "final_answer":
                if self.verbose:
                    print(f"\nFinal Answer: {action_input}\n")
                return action_input

            # Execute tool
            observation = self._execute_tool(action, action_input)

            if self.verbose:
                print(f"Observation: {observation[:300]}\n")

            # Add to memory
            self.memory.add("assistant", response)
            self.memory.add("user", f"Observation: {observation}")

        return "I reached the maximum number of iterations without finding a complete answer."

    def _call_llm(self) -> str:
        """Call the LLM with current conversation history."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.memory.get_messages(),
            temperature=0.1,
            max_tokens=2000,
        )
        return response.choices[0].message.content or ""

    def _parse_response(self, response: str) -> Optional[dict]:
        """Extract JSON from the LLM response."""
        try:
            # Try direct JSON parse
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        # Try extracting JSON from markdown code block
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0].strip()
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass

        # Try finding JSON object in response
        start = response.find("{")
        end = response.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(response[start:end])
            except json.JSONDecodeError:
                pass

        return None

    def _execute_tool(self, tool_name: str, tool_input: str) -> str:
        """Execute a tool and return its output."""
        if tool_name not in self.tools:
            return f"Error: Tool '{tool_name}' not found. Available tools: {list(self.tools.keys())}"

        try:
            result = self.tools[tool_name].run(tool_input)
            return str(result)
        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"
