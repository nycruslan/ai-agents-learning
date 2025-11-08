"""AutoGen Group Chat - Multiple specialized agents collaborating"""

import asyncio
import os

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

load_dotenv()


async def main():
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Set OPENAI_API_KEY in .env file")
        return

    model = OpenAIChatCompletionClient(model="gpt-4o-mini")

    # Create specialized agents
    pm = AssistantAgent(
        "product_manager",
        model_client=model,
        system_message="You define requirements and priorities",
    )

    engineer = AssistantAgent(
        "engineer",
        model_client=model,
        system_message="You assess technical feasibility",
    )

    designer = AssistantAgent(
        "designer",
        model_client=model,
        system_message="You focus on user experience",
    )

    # Create team
    termination = MaxMessageTermination(6)
    team = RoundRobinGroupChat(
        [pm, engineer, designer], termination_condition=termination
    )

    # Run collaboration
    task = "Design a simple AI code review feature. Each person share one insight."
    result = await team.run(task=task)

    print("\n👥 Team Discussion:")
    for msg in result.messages:
        content = str(getattr(msg, "content", msg))
        print(f"\n{msg.source}: {content[:150]}...")


if __name__ == "__main__":
    asyncio.run(main())
