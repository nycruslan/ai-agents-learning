"""CrewAI Simple Crew - Role-based collaborative agents"""

import os

from crewai import Agent, Crew, Process, Task
from dotenv import load_dotenv

load_dotenv()


def main():
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Set OPENAI_API_KEY in .env file")
        return

    # Create agents with roles
    researcher = Agent(
        role="Researcher",
        goal="Find key information about AI agents",
        backstory="Expert at finding and organizing information",
        verbose=True,
    )

    writer = Agent(
        role="Writer",
        goal="Write clear, engaging content",
        backstory="Skilled at making complex topics accessible",
        verbose=True,
    )

    # Define tasks
    research = Task(
        description="Research 3 benefits of AI agent frameworks",
        expected_output="List of 3 benefits with brief explanations",
        agent=researcher,
    )

    write = Task(
        description="Write a short blog post about the benefits researched",
        expected_output="A 200-word blog post",
        agent=writer,
        context=[research],
    )

    # Create and run crew
    crew = Crew(
        agents=[researcher, writer],
        tasks=[research, write],
        process=Process.sequential,
    )

    result = crew.kickoff()
    print(f"\n📝 Final Output:\n{result}\n")


if __name__ == "__main__":
    main()
