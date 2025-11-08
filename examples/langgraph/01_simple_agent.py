"""LangGraph Simple Agent - Stateful conversation with graph-based workflow"""

import os
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

load_dotenv()


class State(TypedDict):
    messages: Annotated[list, add_messages]


def chatbot(state: State):
    """Process messages with Claude"""
    llm = ChatAnthropic(model_name="claude-3-5-sonnet-20241022", timeout=60, stop=None)
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


def main():
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ Set ANTHROPIC_API_KEY in .env file")
        return

    # Build graph: START -> chatbot -> END
    graph = StateGraph(State)
    graph.add_node("chatbot", chatbot)
    graph.add_edge(START, "chatbot")
    graph.add_edge("chatbot", END)
    agent = graph.compile()

    # Run conversation
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "Explain LangGraph in 2 sentences"}]}
    )

    print(f"\n🤖 {result['messages'][-1].content}\n")


if __name__ == "__main__":
    main()
