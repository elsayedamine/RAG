import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


class Generator:
    def __init__(self, model_name="Qwen/Qwen3-0.6B"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)

    def generate(self, question: str, context: str) -> str:
        prompt = f"""
You are a question-answering assistant.

Answer the question using only the information contained in the provided context.

Rules:
- Use only the provided context to answer.
- Do not use outside knowledge.
- Do not invent or assume information that is not in the context.
- Give a direct and concise answer.
- If the context does not contain enough information to answer the question, say:
  "I cannot answer this question from the provided context."

Context:
{context}

Question:
{question}

Answer:
"""
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(**inputs, max_new_tokens=200)
        generated = outputs[0][inputs["input_ids"].shape[1]:]
        answer = self.tokenizer.decode(generated, skip_special_tokens=True)
        return answer.strip()
