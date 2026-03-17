# AI Agent Framework — Build Autonomous LLM Agents with Tools

A lightweight Python framework for building AI agents that can reason, plan, use tools, and collaborate. Inspired by ReAct, AutoGPT, and CrewAI — but simple enough to understand and extend.

## Why I Built This

**The Problem:** Existing AI agent frameworks (LangChain, AutoGPT, CrewAI) are either massively over-engineered with hundreds of abstractions, or too simplistic for real use. LangChain has 3,000+ files and changes its API every week. AutoGPT burns through tokens with unfocused reasoning. Teams want to build AI agents that can search the web, write code, call APIs, and collaborate — but they don't want to learn a 50,000-line framework to do it.

**The Solution:** A clean, understandable agent framework in ~1,500 lines of Python. Each component does one thing well: the `Agent` class implements the ReAct (Reason → Act → Observe) loop, `Tools` are simple classes with a `run()` method, `Memory` stores conversation history and past learnings, and `Orchestrators` coordinate multiple agents (sequential, parallel, or hierarchical). Want to add a custom tool? Write 10 lines of code. Want to understand how the agent reasons? Read one file.

**Built because I needed agents for real projects** — automating research, code generation, report writing — and found that existing frameworks either do too much or too little. This hits the sweet spot: powerful enough for production, simple enough to understand in an afternoon.

```
┌──────────────────────────────────────────────────────────────────────┐
│                       Agent Architecture                             │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                     Orchestrator                             │    │
│  │                                                              │    │
│  │  User Goal ──▶ Plan ──▶ Execute ──▶ Observe ──▶ Repeat     │    │
│  │                 │          │           │                      │    │
│  └─────────────────┼──────────┼───────────┼─────────────────────┘    │
│                    │          │           │                           │
│       ┌────────────▼──┐  ┌───▼────┐  ┌───▼──────────┐              │
│       │   Planning     │  │ Agent  │  │  Observation  │              │
│       │                │  │        │  │               │              │
│       │ • Break goal   │  │ • LLM  │  │ • Tool output │              │
│       │   into steps   │  │ • Tools│  │ • Validation  │              │
│       │ • Prioritize   │  │ • Mem  │  │ • Next step   │              │
│       │ • Dependencies │  │        │  │   decision    │              │
│       └────────────────┘  └───┬────┘  └───────────────┘              │
│                               │                                      │
│           ┌───────────────────┼───────────────────┐                  │
│           │                   │                   │                  │
│     ┌─────▼─────┐     ┌──────▼──────┐    ┌──────▼──────┐          │
│     │  Web       │     │  Code       │    │  File       │          │
│     │  Search    │     │  Executor   │    │  System     │          │
│     │  Tool      │     │  Tool       │    │  Tool       │          │
│     └───────────┘     └─────────────┘    └─────────────┘          │
│                                                                      │
│     ┌───────────┐     ┌─────────────┐    ┌─────────────┐          │
│     │  API       │     │  Database   │    │  Custom     │          │
│     │  Client    │     │  Query      │    │  Tools      │          │
│     │  Tool      │     │  Tool       │    │  (yours)    │          │
│     └───────────┘     └─────────────┘    └─────────────┘          │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    Memory System                              │   │
│  │  Short-term (conversation) │ Long-term (vector DB) │ Episodic│   │
│  └──────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────┘
```

## Features

### Core Agent
- **ReAct Loop** — Reason → Act → Observe cycle until goal is achieved
- **Tool Use** — Agents dynamically choose and invoke tools based on the task
- **Planning** — Break complex goals into step-by-step execution plans
- **Self-Correction** — Detect errors and retry with adjusted approach
- **Max iterations guard** — Prevent infinite loops with configurable limits

### Tools (Built-in)
- **Web Search** — Search the web via SerpAPI or Tavily
- **Web Scraper** — Fetch and parse web pages
- **Code Executor** — Run Python code in a sandboxed environment
- **File System** — Read, write, and list files
- **API Client** — Make HTTP requests to any REST API
- **Calculator** — Evaluate mathematical expressions
- **Shell** — Execute shell commands (sandboxed)

### Memory
- **Short-term** — Conversation history within current task
- **Long-term** — Persistent knowledge via ChromaDB vector store
- **Episodic** — Past task results for learning from experience

### Multi-Agent
- **Sequential** — Agents execute in order, passing results forward
- **Parallel** — Independent agents run concurrently
- **Hierarchical** — Manager agent delegates to worker agents
- **Debate** — Multiple agents discuss and reach consensus

## Quick Start

```python
from agents import Agent
from tools import WebSearchTool, CodeExecutorTool

# Create an agent with tools
agent = Agent(
    name="Research Assistant",
    role="You are a research assistant that finds and summarizes information.",
    tools=[WebSearchTool(), CodeExecutorTool()],
    model="gpt-4o",
)

# Run with a goal
result = agent.run("Find the top 3 Python web frameworks in 2024 and compare their performance benchmarks")
print(result)
```

### Multi-Agent Example

```python
from orchestrator import Orchestrator
from agents import Agent
from tools import WebSearchTool, CodeExecutorTool, FileSystemTool

# Define specialized agents
researcher = Agent(
    name="Researcher",
    role="Find and verify information from the web",
    tools=[WebSearchTool()],
)

coder = Agent(
    name="Developer",
    role="Write and test Python code",
    tools=[CodeExecutorTool(), FileSystemTool()],
)

writer = Agent(
    name="Writer",
    role="Create clear, well-structured reports",
    tools=[FileSystemTool()],
)

# Orchestrate
orchestrator = Orchestrator(
    agents=[researcher, coder, writer],
    strategy="sequential",  # or "parallel", "hierarchical"
)

result = orchestrator.run(
    "Research FastAPI vs Django performance, write benchmark code, and create a report"
)
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM | OpenAI GPT-4o / GPT-3.5 / Ollama |
| Framework | Python 3.12, asyncio |
| Vector Memory | ChromaDB |
| Web Search | SerpAPI / Tavily |
| Code Sandbox | RestrictedPython / subprocess |

## Installation

```bash
git clone https://github.com/vmunjal2503/ai-agent-framework.git
cd ai-agent-framework
pip install -r requirements.txt
cp .env.example .env
# Add your API keys

# Run an example
python examples/research_agent.py
python examples/code_agent.py
python examples/multi_agent_report.py
```

## Project Structure

```
ai-agent-framework/
├── agents/
│   ├── base.py              # Base Agent class with ReAct loop
│   ├── planner.py           # Planning agent (breaks goals into steps)
│   └── critic.py            # Self-evaluation agent
├── tools/
│   ├── base.py              # BaseTool interface
│   ├── web_search.py        # Web search (SerpAPI/Tavily)
│   ├── web_scraper.py       # Web page scraping
│   ├── code_executor.py     # Sandboxed Python execution
│   ├── file_system.py       # File read/write operations
│   ├── api_client.py        # HTTP REST API client
│   ├── calculator.py        # Math expression evaluator
│   └── shell.py             # Shell command execution
├── memory/
│   ├── short_term.py        # Conversation buffer
│   ├── long_term.py         # Vector store (ChromaDB)
│   └── episodic.py          # Task result history
├── orchestrator/
│   ├── base.py              # Orchestrator base class
│   ├── sequential.py        # Sequential execution
│   ├── parallel.py          # Parallel execution
│   └── hierarchical.py      # Manager-worker pattern
├── examples/
│   ├── research_agent.py    # Single agent: web research
│   ├── code_agent.py        # Single agent: code generation
│   └── multi_agent_report.py # Multi-agent collaboration
├── tests/
├── requirements.txt
└── .env.example
```

## Creating Custom Tools

```python
from tools.base import BaseTool

class MyCustomTool(BaseTool):
    name = "my_tool"
    description = "Describe what this tool does — the LLM reads this to decide when to use it"

    def run(self, input: str) -> str:
        # Your tool logic here
        result = do_something(input)
        return str(result)
```

---

Built by **Vikas Munjal** | Open source under MIT License
