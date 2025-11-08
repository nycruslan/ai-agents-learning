# AI Agents Learning

Learn to build AI agent systems with **OpenAI Agents SDK**, **LangGraph**, **CrewAI**, and **AutoGen** through clean, simple examples.

## 🎯 What You'll Learn

- **OpenAI Agents SDK**: ⭐ Production-ready official framework (RECOMMENDED)
- **LangGraph**: Stateful workflows with graph-based control
- **CrewAI**: Role-based collaborative agent teams
- **AutoGen**: Conversational multi-agent systems

## 🚀 Quick Start

**Prerequisites:** Python 3.12+, API keys from [OpenAI](https://platform.openai.com/) or [Anthropic](https://www.anthropic.com/)

```bash
# 1. Install dependencies (using uv)
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync

# 2. Configure API keys
cp .env.example .env
# Edit .env: add OPENAI_API_KEY and/or ANTHROPIC_API_KEY

# 3. Run examples
uv run examples/comparisons/framework_comparison.py

# OpenAI Agents SDK (RECOMMENDED - start here!)
uv run examples/openai_agents/07_comprehensive_demo.py

# Other frameworks
uv run examples/crewai/01_simple_crew.py
uv run examples/langgraph/01_simple_agent.py
uv run examples/autogen/01_simple_conversation.py

```

## 📁 Examples

```
examples/
├── comparisons/
│   └── framework_comparison.py        # Decision guide (updated 2025)
├── openai_agents/                     # ⭐ NEW & RECOMMENDED
│   ├── 01_simple_agent.py            # Your first agent
│   ├── 02_agent_handoffs.py          # Multi-agent coordination
│   ├── 03_tools_and_functions.py     # Function calling
│   ├── 04_streaming.py               # Real-time responses
│   ├── 05_sessions.py                # Conversation memory
│   ├── 06_structured_output.py       # Guaranteed formats
│   ├── 07_comprehensive_demo.py      # ALL FEATURES ⭐
│   └── README.md                     # Full documentation
├── langgraph/
│   └── 01_simple_agent.py            # Stateful conversation
├── crewai/
│   ├── 01_simple_crew.py             # Role-based agents
│   └── 02_crew_with_tools.py         # Agents with web search
└── autogen/
    ├── 01_simple_conversation.py     # Agent chat
    ├── 02_code_execution.py          # Code generation
    └── 03_group_chat.py              # Multi-agent team

```

## 🎓 Learning Path

### Start Here (2025)

1. **⭐ BEST START**: `openai_agents/07_comprehensive_demo.py` - See production patterns
2. **Compare frameworks**: `comparisons/framework_comparison.py` - Updated for 2025
3. **Learn the basics**: `openai_agents/01_simple_agent.py` - Simplest example

### OpenAI Agents SDK (Recommended Path)

4. **Multi-agent**: `openai_agents/02_agent_handoffs.py` - Agent coordination
5. **Tools**: `openai_agents/03_tools_and_functions.py` - Function calling
6. **Streaming**: `openai_agents/04_streaming.py` - Real-time UX
7. **Sessions**: `openai_agents/05_sessions.py` - Conversation memory
8. **Structure**: `openai_agents/06_structured_output.py` - Guaranteed formats

### Explore Other Frameworks

9. **CrewAI**: `crewai/01_simple_crew.py` - Quick prototyping
10. **LangGraph**: `langgraph/01_simple_agent.py` - Complex workflows
11. **AutoGen**: `autogen/01_simple_conversation.py` - Code generation

## 🤔 Which Framework? (2025 Update)

**Choose LangGraph** if you need:## 🤔 Which Framework?

- Complex state management

- Precise workflow control**Choose LangGraph** if you need:

- Graph-based architectures

- Complex state management

**Choose CrewAI** if you want:- Precise workflow control

- Easiest learning curve ✨- Graph-based architectures

- Role-based collaboration

- Quick prototyping**Choose CrewAI** if you want:

**Choose AutoGen** if you need:- Easiest learning curve ✨

- Natural agent conversations- Role-based collaboration

- Code generation/execution- Quick prototyping

- Multi-agent discussions

**Choose AutoGen** if you need:

## 📚 Learn More

- [OpenAI Agents SDK Docs](https://openai.github.io/openai-agents-python/) ⭐
- [OpenAI Agents GitHub](https://github.com/openai/openai-agents-python)
- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [CrewAI Docs](https://docs.crewai.com/)
- [AutoGen Docs](https://microsoft.github.io/autogen/)

## Tips

- **Start with OpenAI Agents SDK**: Best for production (see `07_comprehensive_demo.py`)
- **Read the code**: Examples are clean and well-commented
- **Experiment**: Modify examples to learn
- **Monitor costs**: Set API rate limits
- **Check ANALYSIS.md**: Deep dive into framework comparison

## 🆕 What's New (2025)

- ✨ **OpenAI Agents SDK examples** - Official production framework
- 📊 Updated framework comparison with 2025 recommendations
- 🚀 Comprehensive demo with all features (multi-agent, tools, streaming, sessions)
- 📝 Detailed analysis document comparing all approaches

---

Built with [uv](https://github.com/astral-sh/uv) - the modern Python package manager

```

```
