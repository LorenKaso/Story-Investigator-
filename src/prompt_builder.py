from __future__ import annotations


class PromptTooLongError(Exception):
    """Raised when the constructed prompt exceeds the allowed length."""


class PromptBuilder:
    def build(self, question: str, evidence_chunks: list[str]) -> str:
        evidence = "\n\n".join(evidence_chunks)
        prompt = (
            f"Question: {question}\n\n"
            f"Evidence:\n"
            f"{evidence}\n\n"
            "Instructions:\n"
            "Answer ONLY using the evidence above. Quote the exact lines you "
            "used as evidence. If the evidence is insufficient, say why."
        )
        if len(prompt) > 3000:
            raise PromptTooLongError("Prompt exceeds 3000 characters.")
        return prompt
