"""OpenAI Agents SDK - Session Management Example"""

import asyncio
import os

from agents import Agent, Runner, SQLiteSession
from dotenv import load_dotenv

load_dotenv()


async def main():
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Set OPENAI_API_KEY in .env file")
        return

    # Create agent
    agent = Agent(
        name="Personal Assistant",
        instructions="""You are a helpful personal assistant with memory.
        Remember user preferences, past conversations, and context.
        Be conversational and reference previous interactions.""",
        model="gpt-4o-mini",
    )

    # Create session for user "alice"
    session = SQLiteSession("user_alice", "conversations.db")

    print("💬 Multi-turn conversation with memory\n")
    print("=" * 70)

    # Conversation turns
    conversations = [
        "Hi! My name is Alice and I love Python programming.",
        "What's my name?",  # Agent should remember
        "What programming language do I like?",  # Agent should remember
        "Can you suggest a Python project for me based on what you know?",
    ]

    for turn, message in enumerate(conversations, 1):
        print(f"\n👤 User: {message}")

        # Run with session - automatically maintains history
        result = await Runner.run(agent, input=message, session=session)

        print(f"🤖 Assistant: {result.final_output}")

        if turn < len(conversations):
            print(f"\n{'─' * 70}")

    print("\n" + "=" * 70)
    print("\n✨ Session Demo Complete!")
    print("💡 Try running again - the agent remembers Alice!\n")

    # Demo: Create a different session for another user
    print("\n🔄 Switching to a different user session...\n")
    print("=" * 70)

    session_bob = SQLiteSession("user_bob", "conversations.db")

    result = await Runner.run(
        agent, input="Hi! What's my name and what do I like?", session=session_bob
    )

    print(f"\n👤 User (Bob): Hi! What's my name and what do I like?")
    print(f"🤖 Assistant: {result.final_output}")
    print("\n💡 Notice: Different session = different memory!")


if __name__ == "__main__":
    asyncio.run(main())
