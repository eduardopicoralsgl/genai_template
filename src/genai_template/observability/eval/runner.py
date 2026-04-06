from typing import Any

from genai_template.orchestration.runtime import run_pipeline


def run_eval(dataset: list[dict[str, Any]]) -> float:
    """
    Simple evaluation runner.

    Each dataset item should have:
    {
        "input": {...},
        "expected": {...}
    }
    """

    scores: list[float] = []

    for case in dataset:
        output = run_pipeline(case["input"])

        expected = case.get("expected", {})
        expected_processed = expected.get("processed")

        # Basic scoring: check processed flag
        if expected_processed is None:
            scores.append(1.0)
        else:
            score = 1.0 if output.get("processed") == expected_processed else 0.0
            scores.append(score)

    if not scores:
        return 0.0

    return sum(scores) / len(scores)
