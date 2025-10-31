import asyncio
from fastmcp import Client
from ultrathink.main import mcp


async def test_ultrathink() -> None:
    """Test the UltraThink MCP server"""

    # Connect to the server using in-memory transport
    async with Client(mcp) as client:
        print("🔌 Connected to UltraThink MCP server\n")

        # List available tools
        tools = await client.list_tools()
        print(f"📦 Available tools: {len(tools)}")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description[:80]}...")
        print()

        # Test ultrathink tool with a simple problem
        print("🧪 Testing ultrathink tool...")
        print("Problem: What is 15 + 27?\n")

        # Thought 1
        result1 = await client.call_tool(
            "ultrathink",
            {
                "thought": "I need to add 15 and 27. Let me break this down.",
                "thought_number": 1,
                "total_thoughts": 3,
                "next_thought_needed": True,
            },
        )
        response1 = result1.content[0].text
        print(f"  Thought 1/3: {response1}")

        # Thought 2
        result2 = await client.call_tool(
            "ultrathink",
            {
                "thought": "15 + 27 = 15 + 20 + 7 = 35 + 7",
                "thought_number": 2,
                "total_thoughts": 3,
                "next_thought_needed": True,
            },
        )
        response2 = result2.content[0].text
        print(f"  Thought 2/3: {response2}")

        # Thought 3 (final)
        result3 = await client.call_tool(
            "ultrathink",
            {
                "thought": "Therefore, 15 + 27 = 42",
                "thought_number": 3,
                "total_thoughts": 3,
                "next_thought_needed": False,
            },
        )
        response3 = result3.content[0].text
        print(f"  Thought 3/3: {response3}")
        print()

        # Test with revision
        print("🔄 Testing thought revision...")
        result_revision = await client.call_tool(
            "ultrathink",
            {
                "thought": "Wait, let me verify: 35 + 7 = 42 ✓",
                "thought_number": 4,
                "total_thoughts": 4,
                "next_thought_needed": False,
                "is_revision": True,
                "revises_thought": 2,
            },
        )
        response_revision = result_revision.content[0].text
        print(f"  Revision: {response_revision}")
        print()

        # Test with branching
        print("🌿 Testing thought branching...")
        result_branch = await client.call_tool(
            "ultrathink",
            {
                "thought": "Alternative approach: 27 + 15 = 27 + 10 + 5 = 42",
                "thought_number": 2,
                "total_thoughts": 2,
                "next_thought_needed": False,
                "branch_from_thought": 1,
                "branch_id": "alternative-method",
            },
        )
        response_branch = result_branch.content[0].text
        print(f"  Branch: {response_branch}")
        print()

        # Test with needs_more_thoughts
        print("🔢 Testing needs_more_thoughts (dynamic adjustment)...")
        print("Problem: Calculate 23 * 4\n")

        # Start with underestimated total
        result_nm1 = await client.call_tool(
            "ultrathink",
            {
                "thought": "I need to calculate 23 * 4",
                "thought_number": 1,
                "total_thoughts": 2,
                "next_thought_needed": True,
            },
        )
        response_nm1 = result_nm1.content[0].text
        print(f"  Thought 1/2: {response_nm1}")

        # Realize we need more thoughts
        result_nm2 = await client.call_tool(
            "ultrathink",
            {
                "thought": "Actually, let me break this down more: 23 * 4 = (20 + 3) * 4",
                "thought_number": 2,
                "total_thoughts": 2,
                "next_thought_needed": True,
                "needs_more_thoughts": True,
            },
        )
        response_nm2 = result_nm2.content[0].text
        print(f"  Thought 2/2 (requesting more): {response_nm2}")

        # Continue with adjusted total
        result_nm3 = await client.call_tool(
            "ultrathink",
            {
                "thought": "= (20 * 4) + (3 * 4) = 80 + 12",
                "thought_number": 3,
                "total_thoughts": 4,
                "next_thought_needed": True,
            },
        )
        response_nm3 = result_nm3.content[0].text
        print(f"  Thought 3/4: {response_nm3}")

        # Final answer
        result_nm4 = await client.call_tool(
            "ultrathink",
            {
                "thought": "= 92",
                "thought_number": 4,
                "total_thoughts": 4,
                "next_thought_needed": False,
            },
        )
        response_nm4 = result_nm4.content[0].text
        print(f"  Thought 4/4: {response_nm4}")
        print()

        # Test with confidence scoring
        print("🎯 Testing confidence scoring...")
        print("Problem: Is 97 a prime number?\n")

        # Low confidence - exploratory
        result_c1 = await client.call_tool(
            "ultrathink",
            {
                "thought": "I need to check if 97 is divisible by small primes. Not sure yet.",
                "thought_number": 1,
                "total_thoughts": 3,
                "next_thought_needed": True,
                "confidence": 0.5,
            },
        )
        response_c1 = result_c1.content[0].text
        print(f"  Low confidence (50%): {response_c1}")

        # Medium confidence - analyzing
        result_c2 = await client.call_tool(
            "ultrathink",
            {
                "thought": "Checked 2, 3, 5, 7. None divide 97. Looks prime but need to verify up to sqrt(97) ≈ 9.8",
                "thought_number": 2,
                "total_thoughts": 3,
                "next_thought_needed": True,
                "confidence": 0.75,
            },
        )
        response_c2 = result_c2.content[0].text
        print(f"  Medium confidence (75%): {response_c2}")

        # High confidence - conclusion
        result_c3 = await client.call_tool(
            "ultrathink",
            {
                "thought": "Verified: 97 is not divisible by any prime up to 9. Therefore, 97 is prime.",
                "thought_number": 3,
                "total_thoughts": 3,
                "next_thought_needed": False,
                "confidence": 0.95,
            },
        )
        response_c3 = result_c3.content[0].text
        print(f"  High confidence (95%): {response_c3}")
        print()

        print("✅ All tests passed!")


if __name__ == "__main__":
    asyncio.run(test_ultrathink())
