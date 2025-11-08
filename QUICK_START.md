# 🚀 Quick Start Guide - OpenAI Agents SDK

**Updated:** November 8, 2025

## The Fastest Way to Production-Ready AI Agents

If you're building AI agents in 2025, **start here**.

## ⚡ Install & Run in 2 Minutes

```bash
# 1. Install OpenAI Agents SDK
uv add openai-agents

# 2. Set your API key
export OPENAI_API_KEY="your-key-here"

# 3. Run the comprehensive demo
uv run examples/openai_agents/07_comprehensive_demo.py
```

## 🎯 Why OpenAI Agents SDK?

✅ **Official** - Maintained by OpenAI team
✅ **Simple** - Cleanest API of all frameworks
✅ **Complete** - Multi-agent, tools, sessions, streaming
✅ **Production** - Built-in tracing, error handling
✅ **Flexible** - Works with 100+ LLMs via LiteLLM

## 📊 Quick Comparison

| What You Need              | Use This             |
| -------------------------- | -------------------- |
| **Production app**         | OpenAI Agents SDK ⭐ |
| **Complex state machines** | LangGraph            |
| **Quick prototype**        | CrewAI               |
| **Code generation**        | AutoGen              |

## 🔥 Feature Highlights

### 1. Simple Agent (3 lines!)

```python
from agents import Agent, Runner

agent = Agent(name="Assistant", instructions="You are helpful")
result = Runner.run_sync(agent, "Write a haiku about AI")
print(result.final_output)
```

### 2. Multi-Agent Coordination

```python
specialist = Agent(name="Specialist", instructions="...")
coordinator = Agent(
    name="Coordinator",
    handoffs=[specialist]  # Automatic routing!
)
```

### 3. Tools & Functions

```python
from agents import function_tool

@function_tool
def search(query: str) -> str:
    """Search the web."""
    return f"Results for {query}"

agent = Agent(name="Agent", tools=[search])
```

### 4. Conversation Memory

```python
from agents import SQLiteSession

session = SQLiteSession("user_123")
result = await Runner.run(agent, "Hello", session=session)
# Automatic history management!
```

### 5. Streaming Responses

```python
async for chunk in Runner.run(agent, "Story time", stream=True):
    print(chunk.content, end="", flush=True)
```

### 6. Structured Output

```python
from pydantic import BaseModel

class Answer(BaseModel):
    summary: str
    details: list[str]

agent = Agent(name="Agent", output_type=Answer)
# Guaranteed structure!
```

## 📁 Example Files

| File                          | What It Shows       | Run Time |
| ----------------------------- | ------------------- | -------- |
| `01_simple_agent.py`          | Basic agent         | 5 sec    |
| `02_agent_handoffs.py`        | Multi-agent         | 15 sec   |
| `03_tools_and_functions.py`   | Function calling    | 20 sec   |
| `04_streaming.py`             | Real-time output    | 10 sec   |
| `05_sessions.py`              | Conversation memory | 15 sec   |
| `06_structured_output.py`     | Guaranteed formats  | 25 sec   |
| `07_comprehensive_demo.py` ⭐ | **ALL FEATURES**    | 30 sec   |

## 🎓 Learning Path

**Absolute Beginner?**

1. Run `07_comprehensive_demo.py` to see everything
2. Read `01_simple_agent.py` to understand basics
3. Try modifying examples

**Have Experience?**

1. Read `openai_agents/README.md` for full docs
2. Check `ANALYSIS.md` for deep comparison
3. Build your own agent!

## 🆚 vs. Your Current Framework

### From AutoGen?

```python
# AutoGen: 30+ lines setup
# OpenAI Agents: 3 lines
agent = Agent(name="Agent", instructions="...")
result = await Runner.run(agent, "task")
```

### From CrewAI?

```python
# CrewAI: Define crew, agents, tasks
# OpenAI Agents: Define agent, run
agent = Agent(name="Agent", tools=[...])
result = await Runner.run(agent, "task")
```

### From LangGraph?

```python
# LangGraph: Build graph, add nodes
# OpenAI Agents: Built-in state management
session = SQLiteSession("user")
result = await Runner.run(agent, "task", session=session)
```

## 🔧 Production Patterns

### Error Handling

```python
try:
    result = await Runner.run(
        agent,
        "task",
        max_turns=10,  # Prevent loops
        timeout=30     # Prevent hanging
    )
except TimeoutError:
    # Graceful fallback
    pass
```

### Cost Monitoring

```python
result = await Runner.run(agent, "task")
print(f"Tokens: {result.usage}")
print(f"Cost: ${result.usage.total_tokens * 0.15 / 1_000_000}")
```

### Multi-User Sessions

```python
# Different users = different memory
alice = SQLiteSession("alice", "users.db")
bob = SQLiteSession("bob", "users.db")

await Runner.run(agent, "Hi", session=alice)
await Runner.run(agent, "Hi", session=bob)
# Completely separate conversations!
```

## 💡 Pro Tips

1. **Always use sessions** for multi-turn conversations
2. **Stream responses** for better UX (users see progress)
3. **Set max_turns** to prevent infinite loops
4. **Use structured outputs** when you need consistent formats
5. **Monitor token usage** to control costs
6. **Start with gpt-4o-mini** (cheaper, faster)

## 🐛 Common Issues

### Import Error?

```bash
uv add openai-agents  # Make sure it's installed
```

### API Key Error?

```bash
export OPENAI_API_KEY="sk-..."  # Set your key
```

### Session Database Locked?

```python
# Use different database files for different apps
session = SQLiteSession("user", "my_app.db")
```

## 🔗 Next Steps

1. ✅ Run the examples
2. ✅ Read `openai_agents/README.md`
3. ✅ Check `ANALYSIS.md` for deep dive
4. ✅ Build your first agent!

## 📚 Resources

- [Official Docs](https://openai.github.io/openai-agents-python/)
- [GitHub](https://github.com/openai/openai-agents-python)
- [Examples](https://github.com/openai/openai-agents-python/tree/main/examples)

---

**🎯 Bottom Line:** If you're building AI agents in 2025, OpenAI Agents SDK is the best starting point. It's official, simple, and production-ready.

**Start here:** `uv run examples/openai_agents/07_comprehensive_demo.py`
