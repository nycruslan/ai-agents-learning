"""AutoGen Code Execution - Agent writes and runs Python code"""

import asyncio
import os

from autogen_agentchat.agents import AssistantAgent, CodeExecutorAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

load_dotenv()


async def main():
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Set OPENAI_API_KEY in .env file")
        return

    # Create code executor
    executor = LocalCommandLineCodeExecutor(work_dir="coding_output")

    # Create agents
    coder = AssistantAgent(
        "coder",
        model_client=OpenAIChatCompletionClient(model="gpt-4o"),
        system_message="Write Python code to solve tasks. Use ```python blocks.",
    )

    runner = CodeExecutorAgent("runner", code_executor=executor)

    # Create team
    termination = TextMentionTermination("TERMINATE")
    team = RoundRobinGroupChat([coder, runner], termination_condition=termination)

    # Run task
    task = "Write code to calculate fibonacci(10). Say TERMINATE when done."
    result = await team.run(task=task)

    print("\n💻 Code Execution:")
    for msg in result.messages:
        content = str(getattr(msg, "content", msg))
        print(f"\n{msg.source}: {content[:200]}...")


if __name__ == "__main__":
    asyncio.run(main())
