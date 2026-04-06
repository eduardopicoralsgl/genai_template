from genai_template.orchestration.nodes.example_node import example_node


def test_example_node():
    state = {"input": {}}
    result = example_node(state)
    assert result["processed"] is True
