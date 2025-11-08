# OpenAI Agents SDK Examples

**Production-ready** examples using the official [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/).

## 🎯 Why OpenAI Agents SDK?

- ✅ **Official** - Supported by OpenAI team
- ✅ **Production-ready** - Built-in best practices
- ✅ **Simple** - Cleaner than AutoGen/CrewAI/LangGraph
- ✅ **Powerful** - Multi-agent, tools, streaming, sessions
- ✅ **Provider-agnostic** - Works with 100+ LLMs via LiteLLM

## 🚀 Installation

```bash
# Install OpenAI Agents SDK
uv add openai-agents

# Or with pip
pip install openai-agents
```

## 📚 Examples

### Basic

**01_simple_agent.py** - Your first agent

```bash
uv run examples/openai_agents/01_simple_agent.py
```

- Single agent
- Basic interaction
- Token usage tracking

### Multi-Agent

**02_agent_handoffs.py** - Agent coordination

```bash
uv run examples/openai_agents/02_agent_handoffs.py
```

- Multiple specialized agents (Python, JavaScript, DevOps experts)
- Automatic routing via triage agent
- Handoffs between agents

### Tools

**03_tools_and_functions.py** - Function calling

```bash
uv run examples/openai_agents/03_tools_and_functions.py
```

- Custom tool definitions
- Time queries, cost calculation, doc search
- Multi-tool orchestration

### Streaming

**04_streaming.py** - Real-time responses

```bash
uv run examples/openai_agents/04_streaming.py
```

- Token-by-token streaming
- Better UX for long responses
- Live output display

### Sessions

**05_sessions.py** - Conversation memory

```bash
uv run examples/openai_agents/05_sessions.py
```

- Multi-turn conversations
- Automatic history management
- SQLite-backed persistence
- Multiple user sessions

### Structured Output

**06_structured_output.py** - Guaranteed formats

```bash
uv run examples/openai_agents/06_structured_output.py
```

- Pydantic schemas for outputs
- Code reviews, project plans, bug analysis
- Type-safe responses

### Complete Demo

**07_comprehensive_demo.py** ⭐ **START HERE**

```bash
uv run examples/openai_agents/07_comprehensive_demo.py
```

- **Everything combined!**
- Multi-agent with handoffs
- Multiple tools
- Session management
- Streaming responses
- Structured outputs
- Production patterns

## 🎓 Learning Path

1. **Start here**: `07_comprehensive_demo.py` - See everything in action
2. **Basics**: `01_simple_agent.py` - Understand core concepts
3. **Multi-agent**: `02_agent_handoffs.py` - Learn coordination
4. **Tools**: `03_tools_and_functions.py` - Add capabilities
5. **UX**: `04_streaming.py` - Improve user experience
6. **State**: `05_sessions.py` - Add memory
7. **Structure**: `06_structured_output.py` - Guarantee formats

## 🆚 Comparison with Other Frameworks

| Feature                | OpenAI Agents | AutoGen        | CrewAI      | LangGraph        |
| ---------------------- | ------------- | -------------- | ----------- | ---------------- |
| **Setup complexity**   | ⭐ Simple     | ⭐⭐ Medium    | ⭐ Simple   | ⭐⭐⭐ Complex   |
| **Built-in tracing**   | ✅ Yes        | ❌ No          | ❌ No       | ⚠️ Via LangSmith |
| **Session management** | ✅ Built-in   | ❌ Manual      | ❌ Manual   | ⚠️ Manual        |
| **Streaming**          | ✅ Native     | ✅ Yes         | ✅ Yes      | ✅ Yes           |
| **Structured output**  | ✅ Pydantic   | ⚠️ Limited     | ⚠️ Limited  | ✅ Yes           |
| **Provider support**   | ✅ 100+       | ❌ OpenAI only | ✅ Many     | ✅ Many          |
| **Production ready**   | ✅ Official   | ⚠️ Evolving    | ⚠️ Evolving | ✅ Yes           |

## 🔧 Key Concepts

### Agents

```python
agent = Agent(
    name="Assistant",
    instructions="You are helpful",
    tools=[my_tool],
    handoffs=[other_agent],
    model="gpt-4o-mini"
)
```

### Runner

```python
# Sync
result = Runner.run_sync(agent, "Your query")

# Async
result = await Runner.run(agent, "Your query")

# Streaming
async for chunk in Runner.run(agent, "Query", stream=True):
    print(chunk.content)
```

### Tools

```python
from agents import function_tool

@function_tool
def get_weather(city: str) -> str:
    """Get weather for a city."""
    return f"Weather in {city}: Sunny"
```

### Handoffs

```python
specialist = Agent(name="Specialist", instructions="...")
coordinator = Agent(
    name="Coordinator",
    handoffs=[specialist]  # Can transfer to specialist
)
```

### Sessions

```python
from agents import SQLiteSession

session = SQLiteSession("user_123", "chats.db")
result = await Runner.run(agent, "Query", session=session)
# Automatic conversation history!
```

### Structured Output

```python
from pydantic import BaseModel

class Answer(BaseModel):
    summary: str
    details: List[str]

agent = Agent(
    name="Agent",
    output_type=Answer  # Guaranteed structure
)
```

## 💡 Best Practices

1. **Use sessions** for multi-turn conversations (don't manage history manually)
2. **Stream responses** for better UX on long outputs
3. **Define tools clearly** with good docstrings and type hints
4. **Use structured outputs** when you need consistent formats
5. **Set max_turns** to prevent infinite loops
6. **Monitor token usage** via `result.usage`
7. **Use handoffs** for specialization instead of one mega-agent

## 🔗 Resources

- [Official Docs](https://openai.github.io/openai-agents-python/)
- [GitHub Repo](https://github.com/openai/openai-agents-python)
- [Examples](https://github.com/openai/openai-agents-python/tree/main/examples)
- [API Reference](https://openai.github.io/openai-agents-python/api/)

## 🤔 When to Use What?

**Choose OpenAI Agents SDK** when:

- Building production applications ✅
- Want official support and maintenance ✅
- Need built-in tracing and debugging ✅
- Want simple, clean code ✅

**Choose LangGraph** when:

- Need complex state machines
- Require branching/conditional logic
- Want graph visualization

**Choose CrewAI** when:

- Rapid prototyping
- Simple role-based teams
- Learning agent basics

**Choose AutoGen** when:

- Focus on code generation
- Need group chat dynamics
- Already invested in AutoGen

## 🆕 Migration from Other Frameworks

### From AutoGen:

```python
# AutoGen (complex)
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
# ... 30+ lines of setup

# OpenAI Agents (simple)
from agents import Agent, Runner
agent = Agent(name="Assistant", instructions="...")
result = await Runner.run(agent, "query")
```

### From CrewAI:

```python
# CrewAI
from crewai import Agent, Crew, Task
# ... define agents, tasks, crew

# OpenAI Agents
from agents import Agent, Runner
agent = Agent(name="Agent", instructions="...", tools=[...])
result = await Runner.run(agent, "task")
```

### From LangGraph:

```python
# LangGraph (complex state management)
from langgraph.graph import StateGraph
# ... build graph

# OpenAI Agents (auto state management)
from agents import Agent, Runner, SQLiteSession
session = SQLiteSession("user")
result = await Runner.run(agent, "query", session=session)
```

---

**💡 Tip**: Start with `07_comprehensive_demo.py` to see all features in action!
