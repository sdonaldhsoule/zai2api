from zai2api.prompt_assembly import assemble_prompt, normalize_argument_string


def test_developer_role_is_treated_as_system() -> None:
    prompt = assemble_prompt(
        [
            {"role": "developer", "content": "You are helpful."},
            {"role": "user", "content": "Hello"},
        ]
    )
    assert prompt == "You are helpful.\n\n<｜User｜>Hello"


def test_assistant_tool_history_and_tool_result_are_preserved() -> None:
    prompt = assemble_prompt(
        [
            {"role": "user", "content": "What's the weather?"},
            {
                "role": "assistant",
                "content": "Calling a tool.",
                "tool_calls": [
                    {
                        "id": "call_1",
                        "type": "function",
                        "function": {
                            "name": "get_weather",
                            "arguments": '{"city":"beijing"}',
                        },
                    }
                ],
            },
            {
                "role": "tool",
                "tool_call_id": "call_1",
                "name": "get_weather",
                "content": '{"temp":18}',
            },
        ]
    )
    assert "[TOOL_CALL_HISTORY]" in prompt
    assert "function.name: get_weather" in prompt
    assert "[TOOL_RESULT_HISTORY]" in prompt
    assert "content: {\"temp\":18}" in prompt


def test_concatenated_json_arguments_are_preserved_raw() -> None:
    raw = ' {"a":1}{"b":2} '
    assert normalize_argument_string(raw) == raw


def test_regular_json_arguments_are_trimmed() -> None:
    assert normalize_argument_string('  {"city":"beijing"}  ') == '{"city":"beijing"}'
