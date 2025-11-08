"""OpenAI Agents SDK - Simple Agent Example"""

import asyncio
import os

from agents import Agent, Runner
from dotenv import load_dotenv

load_dotenv()


async def main():
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Set OPENAI_API_KEY in .env file")
        return

    # Create a simple agent
    agent = Agent(
        name="Assistant",
        instructions="You are a helpful AI assistant. Be concise and friendly.",
        model="gpt-4o-mini",
    )

    # Run the agent
    result = await Runner.run(agent, input="Explain what AI agents are in 2 sentences")

    print("\n🤖 Agent Response:")
    print(result.final_output)
    print(f"\n📊 Tokens used: {result.usage}")


if __name__ == "__main__":
    asyncio.run(main())
