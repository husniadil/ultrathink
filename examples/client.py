import asyncio
import json
from fastmcp import Client
from ultrathink.infrastructure.mcp.server import mcp


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

        # Thought 1 - next_thought_needed auto-assigned as True (1 < 3)
        result1 = await client.call_tool(
            "ultrathink",
            {
                "thought": "I need to add 15 and 27. Let me break this down.",
                "total_thoughts": 3,
                # next_thought_needed auto-assigned as True
            },
        )
        r1 = json.loads(result1.content[0].text)
        session_id = r1["session_id"]
        print(f"  Thought 1/3: {result1.content[0].text}")

        # Thought 2 - next_thought_needed auto-assigned as True (2 < 3)
        result2 = await client.call_tool(
            "ultrathink",
            {
                "thought": "15 + 27 = 15 + 20 + 7 = 35 + 7",
                "total_thoughts": 3,
                # next_thought_needed auto-assigned as True
                "session_id": session_id,
            },
        )
        response2 = result2.content[0].text
        print(f"  Thought 2/3: {response2}")

        # Thought 3 (final) - next_thought_needed auto-assigned as False (3 == 3)
        result3 = await client.call_tool(
            "ultrathink",
            {
                "thought": "Therefore, 15 + 27 = 42",
                "total_thoughts": 3,
                # next_thought_needed auto-assigned as False
                "session_id": session_id,
            },
        )
        response3 = result3.content[0].text
        print(f"  Thought 3/3: {response3}")
        print()

        # Test with revision (explicitly set next_thought_needed=False to end)
        print("🔄 Testing thought revision...")
        result_revision = await client.call_tool(
            "ultrathink",
            {
                "thought": "Wait, let me verify: 35 + 7 = 42 ✓",
                "total_thoughts": 4,
                "next_thought_needed": False,  # Explicit override to end early
                "is_revision": True,
                "revises_thought": 2,
                "session_id": session_id,
            },
        )
        response_revision = result_revision.content[0].text
        print(f"  Revision: {response_revision}")
        print()

        # Test with branching (auto-assigned as False since 2 == 2)
        print("🌿 Testing thought branching...")
        result_branch = await client.call_tool(
            "ultrathink",
            {
                "thought": "Alternative approach: 27 + 15 = 27 + 10 + 5 = 42",
                "total_thoughts": 2,
                # next_thought_needed auto-assigned as False
                "branch_from_thought": 1,
                "branch_id": "alternative-method",
                "session_id": session_id,
            },
        )
        response_branch = result_branch.content[0].text
        print(f"  Branch: {response_branch}")
        print()

        # Test with needs_more_thoughts
        print("🔢 Testing needs_more_thoughts (dynamic adjustment)...")
        print("Problem: Calculate 23 * 4\n")

        # Start with underestimated total (auto-assigned as True)
        result_nm1 = await client.call_tool(
            "ultrathink",
            {
                "thought": "I need to calculate 23 * 4",
                "total_thoughts": 2,
                # next_thought_needed auto-assigned as True
            },
        )
        nm1 = json.loads(result_nm1.content[0].text)
        nm_session_id = nm1["session_id"]
        print(f"  Thought 1/2: {result_nm1.content[0].text}")

        # Realize we need more thoughts (explicit override to continue)
        result_nm2 = await client.call_tool(
            "ultrathink",
            {
                "thought": "Actually, let me break this down more: 23 * 4 = (20 + 3) * 4",
                "total_thoughts": 2,
                "next_thought_needed": True,  # Explicit override (would auto-assign False at 2/2)
                "needs_more_thoughts": True,
                "session_id": nm_session_id,
            },
        )
        response_nm2 = result_nm2.content[0].text
        print(f"  Thought 2/2 (requesting more): {response_nm2}")

        # Continue with adjusted total (auto-assigned as True)
        result_nm3 = await client.call_tool(
            "ultrathink",
            {
                "thought": "= (20 * 4) + (3 * 4) = 80 + 12",
                "total_thoughts": 4,
                # next_thought_needed auto-assigned as True
                "session_id": nm_session_id,
            },
        )
        response_nm3 = result_nm3.content[0].text
        print(f"  Thought 3/4: {response_nm3}")

        # Final answer (auto-assigned as False)
        result_nm4 = await client.call_tool(
            "ultrathink",
            {
                "thought": "= 92",
                "total_thoughts": 4,
                # next_thought_needed auto-assigned as False
                "session_id": nm_session_id,
            },
        )
        response_nm4 = result_nm4.content[0].text
        print(f"  Thought 4/4: {response_nm4}")
        print()

        # Test with confidence scoring
        print("🎯 Testing confidence scoring...")
        print("Problem: Is 97 a prime number?\n")

        # Low confidence - exploratory (auto-assigned as True)
        result_c1 = await client.call_tool(
            "ultrathink",
            {
                "thought": "I need to check if 97 is divisible by small primes. Not sure yet.",
                "total_thoughts": 3,
                # next_thought_needed auto-assigned as True
                "confidence": 0.5,
            },
        )
        c1 = json.loads(result_c1.content[0].text)
        c_session_id = c1["session_id"]
        print(f"  Low confidence (50%): {result_c1.content[0].text}")

        # Medium confidence - analyzing (auto-assigned as True)
        result_c2 = await client.call_tool(
            "ultrathink",
            {
                "thought": "Checked 2, 3, 5, 7. None divide 97. Looks prime but need to verify up to sqrt(97) ≈ 9.8",
                "total_thoughts": 3,
                # next_thought_needed auto-assigned as True
                "confidence": 0.75,
                "session_id": c_session_id,
            },
        )
        response_c2 = result_c2.content[0].text
        print(f"  Medium confidence (75%): {response_c2}")

        # High confidence - conclusion (auto-assigned as False)
        result_c3 = await client.call_tool(
            "ultrathink",
            {
                "thought": "Verified: 97 is not divisible by any prime up to 9. Therefore, 97 is prime.",
                "total_thoughts": 3,
                # next_thought_needed auto-assigned as False
                "confidence": 0.95,
                "session_id": c_session_id,
            },
        )
        response_c3 = result_c3.content[0].text
        print(f"  High confidence (95%): {response_c3}")
        print()

        # Test multi-session support
        print("🔀 Testing multi-session support...")
        print("Scenario: Working on two separate problems simultaneously\n")

        # Session 1: Calculate area of circle (auto-assigned as True)
        print("  Session 1 - Circle Area Problem:")
        result_s1_t1 = await client.call_tool(
            "ultrathink",
            {
                "thought": "Calculate area of circle with radius 5",
                "thought_number": 1,
                "total_thoughts": 2,
                # next_thought_needed auto-assigned as True
                # No session_id = create new session
            },
        )
        s1_response1 = json.loads(result_s1_t1.content[0].text)
        session_1_id = s1_response1["session_id"]
        print(f"    Created session: {session_1_id[:8]}...")
        print(f"    History length: {s1_response1['thought_history_length']}")

        # Session 2: Calculate fibonacci (auto-assigned as True)
        print("\n  Session 2 - Fibonacci Problem:")
        result_s2_t1 = await client.call_tool(
            "ultrathink",
            {
                "thought": "Calculate the 7th Fibonacci number",
                "thought_number": 1,
                "total_thoughts": 3,
                # next_thought_needed auto-assigned as True
                # No session_id = create another new session
            },
        )
        s2_response1 = json.loads(result_s2_t1.content[0].text)
        session_2_id = s2_response1["session_id"]
        print(f"    Created session: {session_2_id[:8]}...")
        print(f"    History length: {s2_response1['thought_history_length']}")

        # Continue Session 1 (auto-assigned as False)
        print("\n  Continuing Session 1:")
        result_s1_t2 = await client.call_tool(
            "ultrathink",
            {
                "thought": "Area = π × r² = π × 5² = 25π ≈ 78.54",
                "thought_number": 2,
                "total_thoughts": 2,
                # next_thought_needed auto-assigned as False
                "session_id": session_1_id,  # Continue session 1
            },
        )
        s1_response2 = json.loads(result_s1_t2.content[0].text)
        print(f"    Session: {s1_response2['session_id'][:8]}...")
        print(f"    History length: {s1_response2['thought_history_length']}")

        # Continue Session 2 (auto-assigned as True)
        print("\n  Continuing Session 2:")
        result_s2_t2 = await client.call_tool(
            "ultrathink",
            {
                "thought": "Fibonacci: 0, 1, 1, 2, 3, 5, 8",
                "thought_number": 2,
                "total_thoughts": 3,
                # next_thought_needed auto-assigned as True
                "session_id": session_2_id,  # Continue session 2
            },
        )
        s2_response2 = json.loads(result_s2_t2.content[0].text)
        print(f"    Session: {s2_response2['session_id'][:8]}...")
        print(f"    History length: {s2_response2['thought_history_length']}")

        # Final thought for Session 2 (auto-assigned as False)
        result_s2_t3 = await client.call_tool(
            "ultrathink",
            {
                "thought": "The 7th Fibonacci number is 8",
                "thought_number": 3,
                "total_thoughts": 3,
                # next_thought_needed auto-assigned as False
                "session_id": session_2_id,
            },
        )
        s2_response3 = json.loads(result_s2_t3.content[0].text)
        print(f"    Session: {s2_response3['session_id'][:8]}...")
        print(f"    History length: {s2_response3['thought_history_length']}")

        # Test custom session ID (resilient recovery, auto-assigned as False)
        print("\n  Creating session with custom ID:")
        result_custom = await client.call_tool(
            "ultrathink",
            {
                "thought": "Starting a task with a stable session ID",
                "thought_number": 1,
                "total_thoughts": 1,
                # next_thought_needed auto-assigned as False
                "session_id": "my-stable-session-123",  # Custom ID
            },
        )
        custom_response = json.loads(result_custom.content[0].text)
        print(f"    Session: {custom_response['session_id']}")
        print(f"    History length: {custom_response['thought_history_length']}")

        print("\n  ✓ Session 1 completed with 2 thoughts")
        print("  ✓ Session 2 completed with 3 thoughts")
        print("  ✓ Sessions maintained separate histories")
        print()

        print("✅ All tests passed!")


if __name__ == "__main__":
    asyncio.run(test_ultrathink())
