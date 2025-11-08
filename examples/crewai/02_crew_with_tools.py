"""CrewAI with Tools - Agents using web search capabilities"""

import os

from crewai import Agent, Crew, Task
from dotenv import load_dotenv
from langchain_community.tools import DuckDuckGoSearchRun

load_dotenv()


def main():
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Set OPENAI_API_KEY in .env file")
        return

    # Initialize search tool
    search = DuckDuckGoSearchRun()

    # Researcher with web search
    researcher = Agent(
        role="Web Researcher",
        goal="Find latest info about AI frameworks",
        backstory="Expert at web research",
        tools=[search],
        verbose=True,
    )

    analyst = Agent(
        role="Analyst",
        goal="Analyze findings and extract insights",
        backstory="Expert at analysis",
        verbose=True,
    )

    # Tasks
    research_task = Task(
        description="Search for latest news on LangGraph or CrewAI",
        expected_output="Summary of 2-3 recent updates",
        agent=researcher,
    )

    analysis_task = Task(
        description="Analyze the research and provide key insights",
        expected_output="2-3 key takeaways",
        agent=analyst,
        context=[research_task],
    )

    # Run crew
    crew = Crew(agents=[researcher, analyst], tasks=[research_task, analysis_task])
    result = crew.kickoff()
    print(f"\n🔍 Final Report:\n{result}\n")


if __name__ == "__main__":
    main()
