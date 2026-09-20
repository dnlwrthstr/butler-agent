from hstest import StageTest, TestedProgram, CheckResult, dynamic_test


class AgentTests(StageTest):

    @dynamic_test
    def test_basic_output_format(self):
        """Test that agent produces correct output format with basic tags"""
        pr = TestedProgram()
        pr.start()
        output = pr.execute("What's in my wardrobe?").lower().strip()
        _ = pr.execute("q")

        expected_tags = [
            "[entering agent loop]",
            "[think]",
            "[act]",
            "[observe]",
            "[exiting agent loop]",
            "[assistant]"
        ]

        if all(tag in output for tag in expected_tags):
            return CheckResult(True, 'Correct output format found.')
        else:
            missing = [tag for tag in expected_tags if tag not in output]
            return CheckResult(False, f"Output should contain all of the following tags: {missing}. Please don't modify the agent output format.")

    @dynamic_test
    def test_single_tool_call(self):
        """Test that agent can call a single tool"""
        pr = TestedProgram()
        pr.start()
        output = pr.execute("What's in my wardrobe?").lower().strip()
        _ = pr.execute("q")

        expected_patterns = [
            "calling",
            "get_wardrobe_items",
            "with arguments",
            "result",
            "blue sweater",
            "brown jacket"
        ]

        if all(pattern in output for pattern in expected_patterns):
            return CheckResult(True, 'Agent correctly called get_wardrobe_items tool.')
        else:
            missing = [p for p in expected_patterns if p not in output]
            return CheckResult(False, f"Output doesn't contain expected patterns: {missing}")

    @dynamic_test
    def test_multiple_tool_calls(self):
        """Test that agent can perform multiple sequential tool calls"""
        pr = TestedProgram()
        pr.start()
        output = pr.execute("What should I wear today?").lower().strip()
        _ = pr.execute("q")

        # Should call check_weather, get_wardrobe_items, and wash_clothing
        expected_tools = [
            "check_weather",
            "get_wardrobe_items",
            "wash_clothing"
        ]

        # Count how many times [ACT] appears to verify multiple tool calls
        act_count = output.count("[act]")

        if all(tool in output for tool in expected_tools) and act_count >= 3:
            return CheckResult(True, 'Agent correctly performed multiple tool calls.')
        else:
            return CheckResult(False, f"Agent should call multiple tools (check_weather, get_wardrobe_items, wash_clothing). Found {act_count} [ACT] tags.")

    @dynamic_test
    def test_think_observe_cycle(self):
        """Test that agent follows THINK -> ACT -> OBSERVE cycle"""
        pr = TestedProgram()
        pr.start()
        output = pr.execute("What should I wear today?")
        _ = pr.execute("q")

        # Check for proper ordering of tags
        think_pos = output.lower().find("[think]")
        act_pos = output.lower().find("[act]")
        observe_pos = output.lower().find("[observe]")

        if think_pos < act_pos < observe_pos:
            return CheckResult(True, 'Agent follows correct THINK -> ACT -> OBSERVE cycle.')
        else:
            return CheckResult(False, "Agent should follow THINK -> ACT -> OBSERVE cycle in correct order.")

    @dynamic_test
    def test_handles_missing_item(self):
        """Test that agent handles requests for items not in wardrobe"""
        pr = TestedProgram()
        pr.start()
        output = pr.execute("Wash my red shirt").lower().strip()
        _ = pr.execute("q")

        # Should indicate item not found with various negative patterns
        negative_patterns = [
            "not found",
            "no red shirt",
            "couldn't",
            "could not",
            "can't",
            "can not",
            "didn't",
            "did not",
            "doesn't",
            "does not"
            "is not",
            "isn't",
            "not"
        ]

        if any(pattern in output for pattern in negative_patterns):
            return CheckResult(True, 'Agent correctly handles missing items.')
        else:
            return CheckResult(False, "Agent should indicate when an item is not found in the wardrobe (e.g., 'not found', 'couldn't', 'doesn't exist').")


if __name__ == '__main__':
    AgentTests().run_tests()