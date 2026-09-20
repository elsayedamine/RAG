from indexing import Indexer
from .context import ContextBuilder
from .generator import Generator
from models import (
    MinimalAnswer,
    MinimalSearchResults,
    StudentSearchResults,
    StudentSearchResultsAndAnswer,
)

class Answerer:
    """Generates answers from retrieved search results."""

    def __init__(self, index: Indexer):
        """Initialize the context builder and generator."""
        self.index = index
        self.generator = Generator()

    def answer(self, result: MinimalSearchResults) -> MinimalAnswer:
        """Generate an answer for one set of retrieved search results."""
        context = ContextBuilder(
            self.index,
            result.retrieved_sources,
        ).context

        answer = self.generator.generate(
            result.question,
            context,
        )

        return MinimalAnswer(
            question_id=result.question_id,
            question=result.question,
            retrieved_sources=result.retrieved_sources,
            answer=answer,
        )
    def answer_dataset(
        self,
        results: StudentSearchResults,
    ) -> StudentSearchResultsAndAnswer:
        """Generate answers for all search results."""
        answers: list[MinimalAnswer] = []

        for result in results.search_results:
            answers.append(self.answer(result))

        return StudentSearchResultsAndAnswer(
            search_results=answers,
            k=results.k,
        )