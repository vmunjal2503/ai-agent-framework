# AI Agent Framework

**Give an AI agent a goal and tools — it figures out how to achieve it step by step. Like giving a smart assistant access to Google, a code editor, and file system, then saying "go research X and write a report."**

---

## What is this?

An AI agent is an LLM (like GPT-4) that can **do things**, not just chat. You give it a goal and tools, and it:

1. **Thinks** about what to do
2. **Uses a tool** (search the web, run code, read a file)
3. **Looks at the result**
4. **Repeats** until the goal is done

```
You: "Find the top 3 Python web frameworks and compare their speed"

Agent thinking:
  Step 1: "I need to search the web for Python framework benchmarks"
          → Uses web_search tool → Gets results

  Step 2: "Let me get more details from this benchmark article"
          → Uses web_scraper tool → Gets the page content

  Step 3: "I should verify with another source"
          → Uses web_search tool → Gets more results

  Step 4: "I have enough info. Let me compile the comparison."
          → Returns final answer with data from 3 sources
```

You can also have **multiple agents work together** — one researches, one writes code, one writes the report.

---

## What problem does this solve?

**Without this:** You manually do multi-step tasks: search Google, read articles, copy data, write code to analyze it, then write a summary. Or you use ChatGPT but it can't actually search the web, run code, or save files — it can only talk.

**With this:** You describe what you want, and the agent does the legwork. It searches the web, writes and runs code, reads and writes files, calls APIs — autonomously. You get the final result.

**Why not use LangChain or AutoGPT?** LangChain has 3,000+ files and changes every week. AutoGPT wastes tokens going in circles. This framework is ~1,500 lines of Python — you can read and understand the entire thing in an afternoon.

---

## What can the agent do?

The agent has **tools** it can choose from:

| Tool | What it does | Example |
|------|-------------|---------|
| **Web Search** | Searches Google/Bing for current information | "Find the latest Python release" |
| **Web Scraper** | Reads a web page and extracts the text | "Read the content of this URL" |
| **Code Executor** | Writes and runs Python code | "Calculate the average of this data" |
| **File System** | Reads, writes, and lists files | "Save this report to report.md" |
| **API Client** | Calls any REST API | "Get the current Bitcoin price from CoinGecko" |
| **Calculator** | Does math | "What is 15% of 2,340?" |

You can also **create your own tools** in 10 lines of code.

---

## How to use it

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
print(result)
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

### Multi-Agent Strategies

| Strategy | How it works | Good for |
|----------|-------------|----------|
| **Sequential** | Agent 1 finishes → passes result to Agent 2 → Agent 2 passes to Agent 3 | Research → Analyze → Report pipelines |
| **Parallel** | All agents work on the same goal at the same time, results are merged | Getting multiple perspectives quickly |
| **Hierarchical** | A "manager" agent creates a plan and assigns tasks to "worker" agents | Complex projects with many subtasks |

---

## How to create your own tool

```python
from tools.base import BaseTool

class StockPriceTool(BaseTool):
    name = "stock_price"
    description = "Get the current price of a stock. Input: ticker symbol (e.g., AAPL)"

    def run(self, input: str) -> str:
        # Your logic here — call an API, query a database, etc.
        import httpx
        response = httpx.get(f"https://api.example.com/price/{input}")
        return f"${response.json()['price']}"

# Now your agent can check stock prices
agent = Agent(
    name="Finance Bot",
    role="Answer questions about stocks",
    tools=[StockPriceTool()],
)
```

---

## How is the code organized?

```
ai-agent-framework/
│
├── agents/                    # The brains
│   ├── base.py                # Core agent: Think → Act → Observe loop
│   ├── planner.py             # Breaks big goals into smaller steps
│   └── critic.py              # Checks if an agent's output is good enough
│
├── tools/                     # Things the agent can do
│   ├── base.py                # Template for creating new tools
│   ├── web_search.py          # Search the web
│   ├── web_scraper.py         # Read web pages
│   ├── code_executor.py       # Run Python code
│   ├── file_system.py         # Read/write files
│   ├── api_client.py          # Call REST APIs
│   └── calculator.py          # Do math
│
├── memory/                    # What the agent remembers
│   ├── short_term.py          # Current conversation (cleared after each task)
│   ├── long_term.py           # Permanent knowledge stored in a vector database
│   └── episodic.py            # Past task results (learns from experience)
│
├── orchestrator/              # Coordinate multiple agents
│   ├── sequential.py          # One after another
│   ├── parallel.py            # All at the same time
│   └── hierarchical.py        # Manager assigns work to workers
│
├── examples/                  # Working examples you can run
│   ├── research_agent.py      # Single agent: web research
│   ├── code_agent.py          # Single agent: writes and runs code
│   └── multi_agent_report.py  # 3 agents collaborate on a report
│
└── tests/                     # Unit tests
```

---

## Installation

```bash
git clone https://github.com/vmunjal2503/ai-agent-framework.git
cd ai-agent-framework
pip install -r requirements.txt

cp .env.example .env
# Add your OpenAI API key

# Try an example
python examples/research_agent.py
```

---

## Who is this for?

- Developers who want to build AI agents without learning a massive framework
- Teams automating research, code generation, or report writing
- Anyone who looked at LangChain and thought "this is way too complicated for what I need"

---

Built by **Vikas Munjal** | Open source under MIT License
