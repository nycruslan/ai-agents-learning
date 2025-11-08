"""OpenAI Agents SDK - Comprehensive Demo
Showcases: Multi-agent handoffs, tools, sessions, streaming, and structured output
"""

import asyncio
import os
from datetime import datetime
from typing import List

from agents import Agent, Runner, SQLiteSession, function_tool
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


# ==================== TOOLS ====================
@function_tool
def search_web(query: str) -> str:
    """Search the web for information (mock).

    Args:
        query: Search query
    """
    # Mock search results
    results = {
        "python best practices": "Top Python practices: use type hints, follow PEP 8, write tests, use virtual environments",
        "react hooks": "React Hooks: useState, useEffect, useContext, useReducer, useMemo, useCallback",
        "docker deployment": "Docker best practices: multi-stage builds, .dockerignore, health checks, security scanning",
    }

    for key in results:
        if key in query.lower():
            return f"Search results for '{query}':\n{results[key]}"

    return f"No specific results for '{query}'. General info available."


@function_tool
def get_code_example(language: str, concept: str) -> str:
    """Get a code example for a specific concept.

    Args:
        language: Programming language
        concept: What to demonstrate
    """
    examples = {
        (
            "python",
            "async",
        ): """
```python
import asyncio

async def fetch_data(url):
    # Simulate async operation
    await asyncio.sleep(1)
    return f"Data from {url}"

async def main():
    results = await asyncio.gather(
        fetch_data("api1.com"),
        fetch_data("api2.com")
    )
    print(results)
```""",
        (
            "javascript",
            "promise",
        ): """
```javascript
async function fetchData(url) {
    const response = await fetch(url);
    return response.json();
}

Promise.all([
    fetchData('api1.com'),
    fetchData('api2.com')
]).then(results => console.log(results));
```""",
    }

    key = (language.lower(), concept.lower())
    return examples.get(key, f"No example found for {language} {concept}")


@function_tool
def analyze_performance(code_snippet: str) -> str:
    """Analyze code performance and suggest optimizations.

    Args:
        code_snippet: Code to analyze
    """
    # Mock performance analysis
    return """Performance Analysis:
    - Time Complexity: O(n²) - nested loops detected
    - Space Complexity: O(n) - linear space usage
    - Suggestions:
      1. Consider using a hash map to reduce lookup time
      2. Break early if condition is met
      3. Use generator expressions for memory efficiency"""


# ==================== STRUCTURED OUTPUTS ====================
class TechnicalAnswer(BaseModel):
    """Structured technical answer."""

    summary: str = Field(description="Brief summary of the answer")
    detailed_explanation: str = Field(description="Detailed explanation")
    code_examples: List[str] = Field(
        description="Code examples (empty if not applicable)"
    )
    best_practices: List[str] = Field(description="Best practices to follow")
    common_pitfalls: List[str] = Field(description="Common mistakes to avoid")
    related_topics: List[str] = Field(description="Related topics to explore")


# ==================== SPECIALIZED AGENTS ====================
def create_research_agent() -> Agent:
    """Research agent with web search capabilities."""
    return Agent(
        name="Research Agent",
        instructions="""You are a research specialist with web search capabilities.

        Your role:
        - Search for latest information and best practices
        - Provide well-researched, accurate answers
        - Cite sources when available

        Use the search_web tool to find current information.""",
        tools=[search_web],
        model="gpt-4o-mini",
    )


def create_code_expert() -> Agent:
    """Code expert with code examples and analysis tools."""
    return Agent(
        name="Code Expert",
        instructions="""You are a coding expert with access to code examples and analysis tools.

        Your role:
        - Provide practical code examples
        - Analyze code performance
        - Explain technical concepts clearly

        Use get_code_example for demonstrations and analyze_performance for optimization advice.""",
        tools=[get_code_example, analyze_performance],
        output_type=TechnicalAnswer,  # Structured output
        model="gpt-4o-mini",
    )


def create_mentor_agent(research_agent: Agent, code_expert: Agent) -> Agent:
    """Mentor agent that coordinates with specialists."""
    return Agent(
        name="Tech Mentor",
        instructions="""You are a friendly technical mentor coordinating a team of specialists.

        Your role:
        - Understand user questions and needs
        - Route to appropriate specialist:
          * Research Agent: For finding best practices, comparisons, latest trends
          * Code Expert: For code examples, performance analysis, implementation details
        - Synthesize information from specialists

        Always be encouraging and explain concepts clearly.""",
        handoffs=[research_agent, code_expert],
        model="gpt-4o-mini",
    )


# ==================== MAIN DEMO ====================
async def run_comprehensive_demo():
    """Run a comprehensive demo with all features."""
    print("\n" + "=" * 80)
    print("🚀 OPENAI AGENTS SDK - COMPREHENSIVE DEMO")
    print("=" * 80)
    print(
        "\nFeatures: Multi-agent handoffs, tools, sessions, streaming, structured output"
    )
    print()

    # Create agent hierarchy
    research_agent = create_research_agent()
    code_expert = create_code_expert()
    mentor_agent = create_mentor_agent(research_agent, code_expert)

    # Create session for conversation memory
    session = SQLiteSession("demo_user", "demo_conversations.db")

    # Demo scenarios
    scenarios = [
        {
            "title": "Research Question",
            "query": "What are the current best practices for Python async programming?",
            "stream": False,
        },
        {
            "title": "Code Example Request",
            "query": "Show me how to use async/await in Python with practical examples",
            "stream": False,
        },
        {
            "title": "Streaming Response",
            "query": "Based on what we discussed, create a learning roadmap for mastering async programming",
            "stream": True,
        },
    ]

    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'─' * 80}")
        print(f"📝 SCENARIO {i}: {scenario['title']}")
        print(f"{'─' * 80}")
        print(f"\n❓ Query: {scenario['query']}\n")

        if scenario["stream"]:
            print("📡 Streaming response:\n")
            async for chunk in Runner.run(
                mentor_agent, input=scenario["query"], session=session, stream=True
            ):
                if hasattr(chunk, "content") and chunk.content:
                    print(chunk.content, end="", flush=True)
            print("\n")
        else:
            result = await Runner.run(
                mentor_agent, input=scenario["query"], session=session
            )

            print(f"🎯 Handled by: {result.agent.name}\n")

            # If structured output, display it formatted
            if isinstance(result.final_output, TechnicalAnswer):
                answer: TechnicalAnswer = result.final_output
                print(f"📌 Summary:\n{answer.summary}\n")
                print(f"📖 Explanation:\n{answer.detailed_explanation}\n")

                if answer.code_examples:
                    print("💻 Code Examples:")
                    for example in answer.code_examples:
                        print(example)

                if answer.best_practices:
                    print("\n✅ Best Practices:")
                    for bp in answer.best_practices:
                        print(f"  • {bp}")

                if answer.common_pitfalls:
                    print("\n⚠️  Common Pitfalls:")
                    for cp in answer.common_pitfalls:
                        print(f"  • {cp}")

                if answer.related_topics:
                    print("\n🔗 Related Topics:")
                    for rt in answer.related_topics:
                        print(f"  • {rt}")
            else:
                print(f"💬 Response:\n{result.final_output}")

            print(f"\n📊 Usage: {result.usage}")

    print("\n" + "=" * 80)
    print("✅ DEMO COMPLETE!")
    print("\n💡 Key Features Demonstrated:")
    print("  ✓ Multi-agent handoffs (Mentor → Research/Code Expert)")
    print("  ✓ Tool calling (search_web, get_code_example, analyze_performance)")
    print("  ✓ Session management (conversation memory across turns)")
    print("  ✓ Streaming responses (real-time output)")
    print("  ✓ Structured outputs (TechnicalAnswer schema)")
    print("\n🎯 This demonstrates production-ready patterns for building AI agents!")
    print("=" * 80 + "\n")


async def main():
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Set OPENAI_API_KEY in .env file")
        return

    await run_comprehensive_demo()


if __name__ == "__main__":
    asyncio.run(main())
