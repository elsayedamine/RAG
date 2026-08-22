from .loader import Loader
from .markdown_chunker import MDchunker
from .python_chunker import PYchunker


class Chunker:
    # dont forget to use the path of the files
    def __init__(self):
        loads = Loader()

        self.md_chunks = []
        for doc in loads.markdown_docs:
            self.md_chunks.append(MDchunker(doc))

        self.py_chunks = []
        for doc in loads.python_docs:
            self.py_chunks.append(PYchunker(doc))

    def __str__(self):
        output = []

        for file_index, file_chunks in enumerate(self.md_chunks, 1):
            output.append(f"\n{'=' * 70}")
            output.append(f"FILE {file_index}")
            output.append(f"{'=' * 70}")

            for chunk_index, chunk in enumerate(file_chunks, 1):
                output.append(f"\n--- Chunk {chunk_index} ---")
                output.append(f"Path   : {' > '.join(chunk['path']) or 'ROOT'}")
                output.append(f"Offset : {chunk['start']} → {chunk['end']}")
                output.append(f"Size   : {len(chunk['text'])} chars")
                output.append(f"Text   : {chunk['text']!r}")

        return "\n".join(output)        

if __name__ == "__main__":
    chunks = Chunker()
    print(chunks)