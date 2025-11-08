"""OpenAI Agents SDK - Structured Output Example"""

import asyncio
import os
from typing import List

from agents import Agent, Runner
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


# Define structured output schemas using Pydantic
class CodeReview(BaseModel):
    """Structured code review result."""

    overall_rating: int = Field(description="Overall rating from 1-10", ge=1, le=10)
    strengths: List[str] = Field(description="List of code strengths")
    issues: List[str] = Field(description="List of issues found")
    suggestions: List[str] = Field(description="List of improvement suggestions")
    security_concerns: List[str] = Field(description="Security issues (empty if none)")


class ProjectPlan(BaseModel):
    """Structured project plan."""

    title: str = Field(description="Project title")
    description: str = Field(description="Brief project description")
    technologies: List[str] = Field(description="Technologies to use")
    phases: List[str] = Field(description="Project phases/milestones")
    estimated_hours: int = Field(description="Estimated hours to complete", gt=0)
    difficulty: str = Field(
        description="Difficulty level: beginner/intermediate/advanced"
    )


class BugAnalysis(BaseModel):
    """Structured bug analysis."""

    bug_type: str = Field(description="Type of bug (logic, syntax, runtime, etc)")
    severity: str = Field(description="Severity: low/medium/high/critical")
    root_cause: str = Field(description="Root cause of the bug")
    affected_components: List[str] = Field(description="Which parts are affected")
    fix_steps: List[str] = Field(description="Steps to fix the bug")
    prevention: str = Field(description="How to prevent similar bugs")


async def demo_code_review():
    """Demo: Code review with structured output."""
    print("\n" + "=" * 70)
    print("🔍 CODE REVIEW DEMO")
    print("=" * 70)

    agent = Agent(
        name="Code Reviewer",
        instructions="""You are an expert code reviewer.
        Analyze code for quality, security, and best practices.
        Provide thorough, actionable feedback.""",
        output_type=CodeReview,  # Guaranteed structured output!
        model="gpt-4o-mini",
    )

    code = """
def process_user_input(data):
    result = eval(data)  # Security issue!
    return result

def calculate_total(items):
    total = 0
    for item in items:
        total = total + item['price']  # Could use sum()
    return total
"""

    result = await Runner.run(
        agent, input=f"Review this Python code:\n```python{code}```"
    )

    # result.final_output is a CodeReview object
    review: CodeReview = result.final_output

    print(f"\n⭐ Overall Rating: {review.overall_rating}/10\n")
    print(f"✅ Strengths:\n" + "\n".join(f"  • {s}" for s in review.strengths))
    print(f"\n⚠️  Issues:\n" + "\n".join(f"  • {i}" for i in review.issues))
    print(f"\n💡 Suggestions:\n" + "\n".join(f"  • {s}" for s in review.suggestions))

    if review.security_concerns:
        print(
            f"\n🚨 Security Concerns:\n"
            + "\n".join(f"  • {s}" for s in review.security_concerns)
        )


async def demo_project_planning():
    """Demo: Project planning with structured output."""
    print("\n" + "=" * 70)
    print("📋 PROJECT PLANNING DEMO")
    print("=" * 70)

    agent = Agent(
        name="Project Planner",
        instructions="""You are a project planning expert.
        Create detailed, realistic project plans with clear milestones.""",
        output_type=ProjectPlan,
        model="gpt-4o-mini",
    )

    result = await Runner.run(
        agent,
        input="Create a project plan for building a task management web app with user authentication",
    )

    plan: ProjectPlan = result.final_output

    print(f"\n📌 Title: {plan.title}")
    print(f"📝 Description: {plan.description}")
    print(f"\n🛠️  Technologies:\n" + "\n".join(f"  • {t}" for t in plan.technologies))
    print(
        f"\n🎯 Phases:\n"
        + "\n".join(f"  {i+1}. {p}" for i, p in enumerate(plan.phases))
    )
    print(f"\n⏱️  Estimated Hours: {plan.estimated_hours}")
    print(f"📊 Difficulty: {plan.difficulty.upper()}")


async def demo_bug_analysis():
    """Demo: Bug analysis with structured output."""
    print("\n" + "=" * 70)
    print("🐛 BUG ANALYSIS DEMO")
    print("=" * 70)

    agent = Agent(
        name="Bug Analyzer",
        instructions="""You are a debugging expert.
        Analyze bugs thoroughly and provide clear fix instructions.""",
        output_type=BugAnalysis,
        model="gpt-4o-mini",
    )

    bug_report = """
    Error: "TypeError: Cannot read property 'length' of undefined"

    Code:
    function getUserNames(users) {
        return users.map(u => u.name).length;
    }

    Context: This happens when the API returns null instead of an empty array.
    """

    result = await Runner.run(agent, input=f"Analyze this bug:\n{bug_report}")

    analysis: BugAnalysis = result.final_output

    print(f"\n🏷️  Type: {analysis.bug_type}")
    print(f"⚠️  Severity: {analysis.severity.upper()}")
    print(f"\n🔍 Root Cause:\n  {analysis.root_cause}")
    print(
        f"\n📦 Affected Components:\n"
        + "\n".join(f"  • {c}" for c in analysis.affected_components)
    )
    print(
        f"\n🔧 Fix Steps:\n"
        + "\n".join(f"  {i+1}. {s}" for i, s in enumerate(analysis.fix_steps))
    )
    print(f"\n🛡️  Prevention:\n  {analysis.prevention}")


async def main():
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Set OPENAI_API_KEY in .env file")
        return

    print("\n🎯 STRUCTURED OUTPUT EXAMPLES")
    print("Guaranteed output format using Pydantic models\n")

    await demo_code_review()
    await demo_project_planning()
    await demo_bug_analysis()

    print("\n" + "=" * 70)
    print("✅ All demos complete!")
    print("💡 Structured outputs guarantee consistent, parseable results\n")


if __name__ == "__main__":
    asyncio.run(main())
