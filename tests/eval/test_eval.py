from genai_template.observability.eval.runner import run_eval


def test_eval_pipeline() -> None:
    dataset = [
        {
            "input": {"message": "hello", "use_llm": False},
            "expected": {"processed": True},
        },
        {
            "input": {"message": "world", "use_llm": True},
            "expected": {"processed": True},
        },
    ]

    score = run_eval(dataset)

    assert score >= 0.9
