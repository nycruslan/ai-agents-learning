"""OpenAI Agents SDK - Streaming Responses Example"""

import asyncio
import os

from agents import Agent, Runner
from dotenv import load_dotenv

load_dotenv()


async def main():
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Set OPENAI_API_KEY in .env file")
        return

    agent = Agent(
        name="Story Teller",
        instructions="""You are a creative storyteller.
        Write engaging short stories with vivid descriptions.
        Keep stories under 200 words.""",
        model="gpt-4o-mini",
    )

    print("🎭 Streaming Story Generation\n")
    print("📖 Story: A Day in the Life of an AI Agent")
    print("=" * 70)
    print()

    # Stream the response token by token
    async for chunk in Runner.run(
        agent,
        input="Write a short story about an AI agent's first day helping humans",
        stream=True,
    ):
        # Print each token as it arrives for real-time display
        if hasattr(chunk, "content") and chunk.content:
            print(chunk.content, end="", flush=True)

    print("\n\n" + "=" * 70)
    print("✅ Story complete!\n")


if __name__ == "__main__":
    asyncio.run(main())
