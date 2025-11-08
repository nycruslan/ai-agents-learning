"""AutoGen Simple Conversation - Two agents chatting automatically"""

import asyncio
import os

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

load_dotenv()


async def main():
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Set OPENAI_API_KEY in .env file")
        return

    # Create model client
    model = OpenAIChatCompletionClient(model="gpt-4o-mini")

    # Create two agents
    assistant = AssistantAgent(
        "assistant",
        model_client=model,
        system_message="You explain AI concepts clearly. Say TERMINATE when done.",
    )

    critic = AssistantAgent(
        "critic",
        model_client=model,
        system_message="You ask follow-up questions. Say TERMINATE when satisfied.",
    )

    # Create team with termination condition
    termination = TextMentionTermination("TERMINATE")
    team = RoundRobinGroupChat([assistant, critic], termination_condition=termination)

    # Run conversation
    result = await team.run(task="Explain AutoGen in 2 sentences")

    print("\n💬 Conversation:")
    for msg in result.messages:
        content = getattr(msg, "content", str(msg))
        print(f"\n{msg.source}: {content}")


if __name__ == "__main__":
    asyncio.run(main())
