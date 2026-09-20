from indexing import Indexer
from models import MinimalSource


class ContextBuilder:
    """Builds generation context from retrieved sources."""

    def __init__(self, index: Indexer, sources: list[MinimalSource]):
        self.index = index
        self.sources = {
            (
                chunk["file"],
                chunk["start"],
                chunk["end"],
            ): chunk["text"]
            for chunk in index.corpus.corpus
        }

        self.context = "\n\n".join(
            self.sources.get(
                (
                    source.file_path,
                    source.first_character_index,
                    source.last_character_index,
                ),
                "",
            )
            for source in sources
        )