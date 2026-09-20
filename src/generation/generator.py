import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


class Generator:
    """Generates grounded answers using Qwen3-0.6B."""

    def __init__(self, model_name: str = "Qwen/Qwen3-0.6B"):
        """Load the tokenizer and language model."""
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.model.eval()

    def generate(self, question: str, context: str) -> str:
        """Generate one concise answer using only the provided context."""
        prompt = f"""Answer the question using only the provided context.

Give ONE concise answer. Do not repeat yourself. Do not write "Answer:".
If the context does not contain enough information, say:
"I cannot answer this from the provided context."

Context:
{context}

Question:
{question}

Answer:"""

        inputs = self.tokenizer(prompt, return_tensors="pt")

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=100,
                do_sample=False,
                eos_token_id=self.tokenizer.eos_token_id,
            )

        generated = outputs[0][inputs["input_ids"].shape[1]:]

        return self.tokenizer.decode(
            generated,
            skip_special_tokens=True,
        ).strip()