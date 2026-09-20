from transformers import AutoModelForCausalLM, AutoTokenizer


class Generator:
    """Generates grounded answers using Qwen3-0.6B."""

    def __init__(self, model_name: str = "Qwen/Qwen3-0.6B"):
        """Load the tokenizer and language model."""
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)

    def generate(self, question: str, context: str) -> str:
        """Generate an answer using only the provided context."""
        prompt = f"""Answer the question using only the provided context.

Context:
{context}

Question:
{question}

If the context does not contain enough information, say that you
cannot answer from the provided context.
"""

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
        )

        outputs = self.model.generate(
            **inputs,
            max_new_tokens=300,
        )

        generated = outputs[0][inputs["input_ids"].shape[1]:]

        return self.tokenizer.decode(
            generated,
            skip_special_tokens=True,
        ).strip()