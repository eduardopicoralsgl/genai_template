from genai_template.orchestration.runtime import run_pipeline


def test_graph_without_llm() -> None:
    result = run_pipeline({"message": "hello", "use_llm": False})

    assert result["processed"] is True
    assert result.get("result") is None


def test_graph_with_llm() -> None:
    result = run_pipeline({"message": "hello", "use_llm": True})

    assert result["processed"] is True
    assert isinstance(result["result"], str)
    assert len(result["result"]) > 0
