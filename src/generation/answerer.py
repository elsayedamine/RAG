from src.indexing import Indexer
from src.models import MinimalAnswer, MinimalSearchResults
from src.generation.context import ContextBuilder
from src.generation.generator import Generator


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