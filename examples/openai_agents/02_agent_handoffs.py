"""OpenAI Agents SDK - Multi-Agent Handoffs Example"""

import asyncio
import os

from agents import Agent, Runner
from dotenv import load_dotenv

load_dotenv()


async def main():
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Set OPENAI_API_KEY in .env file")
        return

    # Create specialized agents
    python_expert = Agent(
        name="Python Expert",
        instructions="""You are a Python programming expert.
        Help users with Python code, best practices, and libraries.
        Be specific and provide code examples.""",
        model="gpt-4o-mini",
    )

    javascript_expert = Agent(
        name="JavaScript Expert",
        instructions="""You are a JavaScript/TypeScript expert.
        Help users with JS/TS code, frameworks like React/Node.js.
        Provide modern ES6+ examples.""",
        model="gpt-4o-mini",
    )

    devops_expert = Agent(
        name="DevOps Expert",
        instructions="""You are a DevOps and cloud infrastructure expert.
        Help with Docker, Kubernetes, CI/CD, AWS/GCP/Azure.
        Focus on best practices and security.""",
        model="gpt-4o-mini",
    )

    # Triage agent that routes to specialists
    triage_agent = Agent(
        name="Tech Support Triage",
        instructions="""You are a technical support triage agent.

        Route questions to the appropriate expert:
        - Python Expert: For Python programming questions
        - JavaScript Expert: For JS/TS/Node/React questions
        - DevOps Expert: For deployment, infrastructure, Docker, cloud questions

        Analyze the user's question and hand off to the right specialist.
        If the question spans multiple areas, choose the most relevant expert.""",
        handoffs=[python_expert, javascript_expert, devops_expert],
        model="gpt-4o-mini",
    )

    # Test cases
    questions = [
        "How do I create a FastAPI endpoint with async database queries?",
        "What's the best way to manage state in React with TypeScript?",
        "How do I set up a CI/CD pipeline with GitHub Actions and Docker?",
    ]

    for question in questions:
        print(f"\n{'='*70}")
        print(f"❓ Question: {question}")
        print(f"{'='*70}")

        result = await Runner.run(triage_agent, input=question)

        print(f"\n🎯 Handled by: {result.agent.name}")
        print(f"\n💡 Answer:\n{result.final_output}")


if __name__ == "__main__":
    asyncio.run(main())
