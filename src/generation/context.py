from indexing import Indexer
from models import MinimalSource

class Context:
    def __init__(self, index: Indexer, sources: list[MinimalSource]):
        self.context = ""
        self.lookup = {(chunk["file"], chunk["start"], chunk["end"]): chunk["text"] for chunk in index.corpus.corpus}
        self.context = "\n\n".join(self.lookup[(source.file_path, source.first_character_index, source.last_character_index)] for source in sources)
