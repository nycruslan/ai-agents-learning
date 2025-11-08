"""Framework Comparison - Quick guide to choosing the right framework (2025 Edition)"""


def main():
    print("\n" + "=" * 70)
    print("AI AGENT FRAMEWORK COMPARISON (2025 Edition)")
    print("=" * 70)

    print("\n📊 QUICK COMPARISON\n")
    print("OpenAI Agents SDK: ⭐ RECOMMENDED FOR PRODUCTION")
    print("  ✓ Best for: Production applications")
    print("  ✓ Control: High (official SDK)")
    print("  ✓ Learning: Easy (simplest API)")
    print("  ✓ Use when: Building real products, need official support")
    print("  ✓ Features: Built-in tracing, sessions, streaming, 100+ LLMs")

    print("\nLangGraph:")
    print("  ✓ Best for: Complex stateful workflows")
    print("  ✓ Control: Maximum (graph-based)")
    print("  ✓ Learning: Medium-High")
    print("  ✓ Use when: Need precise control & state management")

    print("\nCrewAI:")
    print("  ✓ Best for: Role-based team collaboration")
    print("  ✓ Control: High-level (simple)")
    print("  ✓ Learning: Easy (fastest to start)")
    print("  ✓ Use when: Quick prototyping, clear roles")

    print("\nAutoGen:")
    print("  ✓ Best for: Conversational agents & code execution")
    print("  ✓ Control: Medium (conversation-driven)")
    print("  ✓ Learning: Medium")
    print("  ✓ Use when: Need agent discussions or code generation")

    print("\n" + "=" * 70)
    print("DECISION GUIDE (2025)")
    print("=" * 70)

    print("\n⭐ Choose OpenAI Agents SDK if:")
    print("  • Building production applications (BEST CHOICE)")
    print("  • Want official OpenAI support & maintenance")
    print("  • Need built-in tracing, sessions, streaming")
    print("  • Want the simplest, cleanest API")
    print("  • Provider-agnostic (100+ LLMs via LiteLLM)")

    print("\n🎯 Choose LangGraph if:")
    print("  • You need complex state management")
    print("  • Precise control over workflow is critical")
    print("  • Building production systems with checkpoints")

    print("\n🚀 Choose CrewAI if:")
    print("  • You're new to AI agents (easiest!)")
    print("  • Want to prototype quickly")
    print("  • Need role-based collaboration")

    print("\n💬 Choose AutoGen if:")
    print("  • Need natural agent conversations")
    print("  • Code generation/execution is central")
    print("  • Want multi-agent group discussions")

    print("\n" + "=" * 70)
    print("\n💡 Tip: Start with OpenAI Agents SDK for production!")
    print("💡 Use CrewAI for quick experiments, LangGraph for complex flows\n")


if __name__ == "__main__":
    main()
