import pytest

from src.prompt_builder import PromptBuilder, PromptTooLongError


def test_build_under_limit_ok() -> None:
    builder = PromptBuilder()
    prompt = builder.build("Q?", ["short evidence"])

    assert isinstance(prompt, str)
    assert "Question:" in prompt
    assert "Evidence:" in prompt
    assert "short evidence" in prompt


def test_build_over_limit_raises() -> None:
    builder = PromptBuilder()
    long_evidence = "x" * 4000

    with pytest.raises(PromptTooLongError):
        builder.build("Q?", [long_evidence])
