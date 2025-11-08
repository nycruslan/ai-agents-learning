"""OpenAI Agents SDK - Tools and Function Calling Example"""

import asyncio
import os
from datetime import datetime

from agents import Agent, Runner, function_tool
from dotenv import load_dotenv

load_dotenv()


# Define custom tools using @function_tool decorator
@function_tool
def get_current_time(timezone: str = "UTC") -> str:
    """Get the current time in a specific timezone.

    Args:
        timezone: The timezone name (e.g., 'UTC', 'US/Pacific', 'Europe/London')
    """
    # In a real app, use pytz for proper timezone handling
    current_time = datetime.now()
    return f"Current time in {timezone}: {current_time.strftime('%Y-%m-%d %H:%M:%S')}"


@function_tool
def calculate_cost(tokens: int, model: str = "gpt-4o-mini") -> str:
    """Calculate the cost of an API call based on token usage.

    Args:
        tokens: Number of tokens used
        model: The model name (e.g., 'gpt-4o', 'gpt-4o-mini')
    """
    # Approximate pricing (as of 2025)
    pricing = {
        "gpt-4o": {"input": 2.50, "output": 10.00},  # per 1M tokens
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "gpt-4-turbo": {"input": 10.00, "output": 30.00},
    }

    if model not in pricing:
        return f"Unknown model: {model}"

    # Assume equal split for simplicity
    input_tokens = tokens // 2
    output_tokens = tokens // 2

    cost = (
        input_tokens * pricing[model]["input"] / 1_000_000
        + output_tokens * pricing[model]["output"] / 1_000_000
    )

    return f"Cost estimate: ${cost:.6f} for {tokens:,} tokens on {model}"


@function_tool
def search_documentation(query: str, framework: str) -> str:
    """Search documentation for a specific framework.

    Args:
        query: What to search for
        framework: Which framework ('openai-agents', 'langgraph', 'crewai', 'autogen')
    """
    # Mock documentation search - in real app, use vector search or API
    docs = {
        "openai-agents": "OpenAI Agents SDK provides Agent, Runner, handoffs, and tools. Visit: https://openai.github.io/openai-agents-python/",
        "langgraph": "LangGraph offers graph-based workflows with StateGraph and checkpointing. Visit: https://langchain-ai.github.io/langgraph/",
        "crewai": "CrewAI enables role-based agent teams with sequential/hierarchical processes. Visit: https://docs.crewai.com/",
        "autogen": "AutoGen facilitates multi-agent conversations and code execution. Visit: https://microsoft.github.io/autogen/",
    }

    if framework.lower() not in docs:
        return f"Framework '{framework}' not found. Available: {', '.join(docs.keys())}"

    return f"Documentation for '{query}' in {framework}:\n{docs[framework.lower()]}"


async def main():
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Set OPENAI_API_KEY in .env file")
        return

    # Create agent with tools
    agent = Agent(
        name="AI Developer Assistant",
        instructions="""You are an AI development assistant with access to helpful tools.

        Use the available tools to:
        - Check current time for logging and scheduling
        - Calculate API costs to help users budget
        - Search documentation to provide accurate information

        Always use tools when appropriate to provide accurate, real-time information.""",
        tools=[get_current_time, calculate_cost, search_documentation],
        model="gpt-4o-mini",
    )

    # Test queries that trigger different tools
    queries = [
        "What time is it in UTC?",
        "How much would 50,000 tokens cost on gpt-4o-mini?",
        "Where can I learn about handoffs in openai-agents?",
        "I used 150000 tokens on gpt-4o today. What's the cost and what time is it now?",
    ]

    for query in queries:
        print(f"\n{'='*70}")
        print(f"❓ Query: {query}")
        print(f"{'='*70}\n")

        result = await Runner.run(agent, input=query)

        print(f"🤖 Response: {result.final_output}\n")
        print(f"📊 Tokens: {result.usage}")

        # Show which tools were called
        if hasattr(result, "tool_calls") and result.tool_calls:
            print(f"🔧 Tools used: {[tc['name'] for tc in result.tool_calls]}")


if __name__ == "__main__":
    asyncio.run(main())
