# AI Agent Framework

**Give an AI agent a goal and tools — it figures out how to achieve it step by step. Like giving a smart assistant access to Google, a code editor, and file system, then saying "go research X and write a report."**

---

## What is this?

An AI agent is an LLM (like GPT-4) that can **do things**, not just chat. You give it a goal and tools, and it runs a reasoning loop:

```
You: "Find the top 3 Python web frameworks and compare their speed"

Agent reasoning loop (ReAct pattern):

  THINK:  "I need to search the web for Python framework benchmarks"
  ACT:    web_search("python web framework benchmarks 2024")
  OBSERVE: [Results from Google: TechEmpower benchmarks, blog posts...]

  THINK:  "Let me get the actual benchmark numbers from this article"
  ACT:    web_scraper("https://techempower.com/benchmarks/...")
  OBSERVE: [FastAPI: 42k req/s, Django: 8k req/s, Flask: 12k req/s]

  THINK:  "I should verify with another source"
  ACT:    web_search("fastapi vs django vs flask performance comparison")
  OBSERVE: [More data confirming the numbers]

  THINK:  "I have enough data. Let me compile the comparison."
  RETURN: Final answer with data from 3 sources
```

The agent decides **which tool to use**, **what input to pass**, and **when it has enough information to stop**. You can also have **multiple agents work together** — one researches, one writes code, one writes the report.

---

## What problem does this solve?

**Without this:** You manually do multi-step tasks: search Google, read articles, copy data, write code to analyze it, then write a summary. Or you use ChatGPT but it can't actually search the web, run code, or save files — it can only talk.

**With this:** You describe what you want, and the agent does the legwork. It searches the web, writes and runs code, reads and writes files, calls APIs — autonomously. You get the final result.

**Why not use LangChain or AutoGPT?** LangChain has 3,000+ files and changes every week. AutoGPT wastes tokens going in circles. This framework is ~1,500 lines of Python — you can read and understand the entire thing in an afternoon.

---

## The ReAct reasoning loop

This is the core algorithm that makes an agent work:

```
┌─────────────────────────────────────────────────┐
│                  Agent Loop                      │
│                                                  │
│  ┌──────────┐                                    │
│  │  THINK   │ LLM decides what to do next        │
│  │          │ Output: reasoning + chosen tool     │
│  └────┬─────┘                                    │
│       │                                          │
│       ▼                                          │
│  ┌──────────┐                                    │
│  │   ACT    │ Execute the chosen tool             │
│  │          │ Input: tool name + parameters       │
│  └────┬─────┘                                    │
│       │                                          │
│       ▼                                          │
│  ┌──────────┐                                    │
│  │ OBSERVE  │ Append tool result to context       │
│  │          │ LLM sees what happened              │
│  └────┬─────┘                                    │
│       │                                          │
│       ▼                                          │
│  ┌──────────┐    No                              │
│  │  DONE?   │────────▶ Back to THINK             │
│  │          │                                    │
│  └────┬─────┘                                    │
│       │ Yes                                      │
│       ▼                                          │
│  Return final answer                             │
│  (max 10 iterations as safety limit)             │
└─────────────────────────────────────────────────┘
```

### How the LLM decides

```python
# The agent sends this to the LLM at each step:
{
  "system": "You are an agent. Respond with JSON: {thought, tool, tool_input} or {thought, final_answer}",
  "messages": [
    {"role": "user", "content": "Find top 3 Python frameworks..."},
    {"role": "assistant", "content": "{thought: 'I need to search...', tool: 'web_search', tool_input: '...'}"},
    {"role": "user", "content": "Tool result: [search results here]"},
    # ... conversation grows with each Think→Act→Observe cycle
  ]
}

# The LLM sees its own previous reasoning + tool results
# and decides the next action. When it has enough info,
# it returns {final_answer: "..."} instead of another tool call.
```

---

## What can the agent do?

The agent has **tools** it can choose from:

| Tool | What it does | Implementation |
|------|-------------|----------------|
| **Web Search** | Searches Google/Bing for current information | `httpx` call to search API, returns top 10 results with title + snippet + URL |
| **Web Scraper** | Reads a web page and extracts text | `httpx` + `BeautifulSoup`. Strips HTML tags, scripts, styles. Returns clean text. |
| **Code Executor** | Writes and runs Python code | Executes in a sandboxed `subprocess` with 30s timeout. Captures stdout + stderr. |
| **File System** | Reads, writes, and lists files | Scoped to a working directory. Path traversal protection (`..` blocked). |
| **API Client** | Calls any REST API | `httpx` with configurable method, headers, body. Parses JSON response. |
| **Calculator** | Evaluates math expressions | Python `ast.literal_eval` for safety — no arbitrary code execution via eval(). |

### Create your own tool (10 lines)

```python
from tools.base import BaseTool

class StockPriceTool(BaseTool):
    name = "stock_price"
    description = "Get the current price of a stock. Input: ticker symbol (e.g., AAPL)"

    def run(self, input: str) -> str:
        import httpx
        response = httpx.get(f"https://api.example.com/price/{input}")
        return f"${response.json()['price']}"

# The LLM reads the tool's `name` and `description` to decide when to use it.
# That's the entire interface — name, description, run(input) → string.
```

---

## Single agent vs. multi-agent

### Single Agent

```python
from agents import Agent
from tools import WebSearchTool, CodeExecutorTool

agent = Agent(
    name="Research Assistant",
    role="You find and summarize information from the web.",
    tools=[WebSearchTool(), CodeExecutorTool()],
)

result = agent.run("What are the top 3 Python web frameworks in 2024?")
```

### Multiple Agents Working Together

```python
from agents import Agent
from tools import WebSearchTool, CodeExecutorTool, FileSystemTool
from orchestrator import Orchestrator

# Agent 1: Finds information
researcher = Agent(
    name="Researcher",
    role="Search the web and gather facts",
    tools=[WebSearchTool()],
)

# Agent 2: Writes and tests code
developer = Agent(
    name="Developer",
    role="Write Python code to analyze data",
    tools=[CodeExecutorTool(), FileSystemTool()],
)

# Agent 3: Writes the final report
writer = Agent(
    name="Writer",
    role="Create a clear, well-organized report",
    tools=[FileSystemTool()],
)

# They work in sequence: Research → Code → Write
orchestrator = Orchestrator(agents=[researcher, developer, writer])
result = orchestrator.run("Compare FastAPI vs Django performance and write a report")
```

---

## Multi-agent orchestration strategies

| Strategy | How it works | When to use | Implementation |
|----------|-------------|-------------|----------------|
| **Sequential** | Agent 1 → passes output → Agent 2 → Agent 3 | Research → Analyze → Report pipelines | Each agent's `final_answer` becomes the next agent's input. Chain of responsibility. |
| **Parallel** | All agents work on the same goal simultaneously | Getting multiple perspectives quickly | `asyncio.gather()` runs all agents concurrently. Results merged by a synthesis step. |
| **Hierarchical** | A "manager" agent creates a plan and delegates to "worker" agents | Complex projects with many subtasks | Manager uses `PlannerAgent` to break goal into steps, assigns each step to a specialist agent. |

---

## Memory systems

| Memory Type | What it stores | How it works | Lifetime |
|-------------|---------------|-------------|----------|
| **Short-term** | Current conversation | List of messages (user prompts + tool results) | Cleared after each task |
| **Long-term** | Permanent knowledge | Vector embeddings in ChromaDB. Semantic search to recall relevant past knowledge. | Persistent across tasks |
| **Episodic** | Past task results | Task description + outcome pairs. Agent checks "have I done something like this before?" | Persistent, grows over time |

```
Agent receives new task: "Compare React vs Vue"
     │
     ├── Check episodic memory: "Did I do a similar comparison before?"
     │   → Found: "Compare FastAPI vs Django" task from last week
     │   → Uses same research strategy (search → scrape benchmarks → compare)
     │
     ├── Check long-term memory: "Do I know anything about React/Vue?"
     │   → Found: stored knowledge about React hooks, Vue composition API
     │   → Skips searching for basics, goes straight to comparison
     │
     └── Short-term memory: tracks this conversation's tool results
```

---

## Safety and guardrails

- **Max iterations (10)** — Agent can't loop forever. If it hasn't found an answer in 10 Think→Act→Observe cycles, it returns what it has.
- **Tool sandboxing** — Code executor runs in a subprocess with a 30-second timeout. File system is scoped to a working directory.
- **Structured output** — Agent must respond in JSON format (`{thought, tool, tool_input}` or `{thought, final_answer}`). Invalid JSON triggers a retry with an error message.
- **No arbitrary eval()** — Calculator uses `ast.literal_eval`, not `eval()`. Prevents code injection via math expressions.

---

## How is the code organized?

```
ai-agent-framework/
│
├── agents/                    # The brains
│   ├── base.py                # Core Agent: ReAct loop (Think → Act → Observe), JSON parsing, tool dispatch
│   ├── planner.py             # PlannerAgent: breaks goals into structured step-by-step plans (JSON output)
│   └── critic.py              # CriticAgent: evaluates outputs → {score, passed, issues[], suggestions[]}
│
├── tools/                     # Things the agent can do
│   ├── base.py                # BaseTool abstract class: name, description, run(input) → string
│   ├── web_search.py          # Search API wrapper (httpx, returns top 10 results)
│   ├── web_scraper.py         # HTML → clean text (BeautifulSoup, strips scripts/styles)
│   ├── code_executor.py       # Sandboxed Python execution (subprocess, 30s timeout)
│   ├── file_system.py         # Scoped file I/O (read/write/list, path traversal blocked)
│   ├── api_client.py          # REST API caller (configurable method/headers/body)
│   └── calculator.py          # Safe math evaluation (ast.literal_eval, not eval)
│
├── memory/                    # What the agent remembers
│   ├── short_term.py          # Current conversation messages (list, cleared per task)
│   ├── long_term.py           # Vector DB knowledge store (ChromaDB, semantic search)
│   └── episodic.py            # Past task results (task → outcome pairs, pattern matching)
│
├── orchestrator/              # Coordinate multiple agents
│   ├── sequential.py          # Chain: agent1.output → agent2.input → agent3.input
│   ├── parallel.py            # Concurrent: asyncio.gather(), results merged
│   └── hierarchical.py       # Manager creates plan, delegates steps to worker agents
│
├── examples/                  # Working examples you can run
│   ├── research_agent.py      # Single agent: web research task
│   ├── code_agent.py          # Single agent: writes and runs Python code
│   └── multi_agent_report.py  # 3 agents collaborate: research → code → report
│
└── tests/                     # Unit tests (pytest)
    └── test_tools.py          # Tests for Calculator (safe eval) and FileSystem (path safety)
```

---

## Who is this for?

- Developers who want to build AI agents without learning a massive framework
- Teams automating research, code generation, or report writing
- Anyone who looked at LangChain and thought "this is way too complicated for what I need"

---

Built by **Vikas Munjal** | Open source under MIT License
