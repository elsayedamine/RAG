from indexing import Indexer
from .context import Context
from .generator import Generator
from models import (
    MinimalAnswer,
    MinimalSearchResults,
    StudentSearchResults,
    StudentSearchResultsAndAnswer,
)

class Answerer:
    def __init__(self, index, ):
        self.index = index
        self.generator = Generator()
    
    def answer(self, result: MinimalSearchResults) -> MinimalAnswer:
        context = Context(self.index, result.retrieved_sources).context
        answer = self.generator.generate(result.question, context)
        return MinimalAnswer(
            answer=answer,
            question=result.question,
            question_id=result.question_id,
            retrieved_sources=result.retrieved_sources
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