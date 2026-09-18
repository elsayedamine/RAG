from typing import List, Set

from src.indexing import Indexer, Corpus
from src.models import (
    StudentSearchResults,
    MinimalSource,
    RagDataset,
    MinimalSearchResults,
)


STOPWORDS = {
    "a", "an", "the",
    "is", "are", "was", "were", "be", "been", "being",
    "of", "for", "in", "on", "at", "to", "from", "by",
    "with", "about", "against", "between", "into", "through",
    "and", "or", "but", "if",
    "what", "which", "where", "when", "how", "why", "who",
    "do", "does", "did",
    "can", "could", "would", "should",
    "you", "your", "s", "t", "re", "ve",
}


class Retriever:
    def __init__(self, index: Indexer):
        self.index = index

    def preprocess_query(self, query: str) -> List[str]:
        """Tokenize a query and remove stopwords."""
        return [
            token
            for token in Corpus.tokenize(query)
            if token not in STOPWORDS
        ]

    def _get_doc_candidates(self, query_tokens: List[str], extension: str | None = None) -> Set[int]:
        """Return documents containing at least one query token."""
        candidates: Set[int] = set()

        for token in query_tokens:
            if token not in self.index.TF:
                continue

            for doc_id in self.index.TF[token]:
                if (
                    extension is None
                    or self.index.corpus.corpus[doc_id]["file"].endswith(extension)
                ):
                    candidates.add(doc_id)

        return candidates

    def retrieve(self, query: str, k: int, extension: str | None = None) -> List[MinimalSource]:
        """Retrieve the top-k BM25 sources for a query."""
        tokens = self.preprocess_query(query)

        if not tokens or k <= 0:
            return []

        doc_ids = self._get_doc_candidates(tokens, extension)

        scores = {
            doc_id: self.index.bm25_score(tokens, doc_id)
            for doc_id in doc_ids
        }

        ranked = sorted(
            scores.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        results = []

        for doc_id, _ in ranked[:k]:
            chunk = self.index.corpus.corpus[doc_id]

            results.append(
                MinimalSource(
                    file_path=chunk["file"],
                    first_character_index=chunk["start"],
                    last_character_index=chunk["end"],
                )
            )

        return results

    def retrieve_dataset(self, path: str, k: int) -> StudentSearchResults:
        """Retrieve sources for every question in a RAG dataset."""
        with open(path, "r") as f:
            dataset = RagDataset.model_validate_json(f.read())

        results = []

        for question in dataset.rag_questions:
            result = MinimalSearchResults(
                question_id=question.question_id,
                question=question.question,
                retrieved_sources=self.retrieve(
                    question.question,
                    k,
                ),
            )
            results.append(result)

        return StudentSearchResults(
            search_results=results,
            k=k,
        )