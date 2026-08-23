from .loader import Loader
from .markdown_chunker import MDchunker
from .python_chunker import PYchunker

"""Coordinates loading and chunking of Markdown and Python documents."""
"""It has a list of dict that has the filenmae and its chunks for both py and md"""
class Chunker:
    def __init__(self):
        loads = Loader("data/dir")

        self.md_chunks = [{"file": doc[0], "chunks": MDchunker(doc[1])} for doc in loads.markdown_docs]
        self.py_chunks = [{"file": doc[0], "chunks": PYchunker(doc[1])} for doc in loads.python_docs]

    def __str__(self):
        output = []

        # for name, files in [("PYTHON", self.py_chunks)]:
        for name, files in [("MARKDOWN", self.md_chunks), ("PYTHON", self.py_chunks)]:
            output.append(name)
            for file_index, file in enumerate(files, 1):
                output.append(f"\n{'=' * 70}")
                output.append(f"--- FILE {file_index}: {file['file']} ---")
                output.append(f"{'=' * 70}")

                for chunk_index, chunk in enumerate(file['chunks'], 1):
                    output.extend([
                        f"\n--- Chunk {chunk_index} ---",
                        f"Path   : {' > '.join(chunk['path']) or 'ROOT'}",
                        f"Offset : {chunk['start']} → {chunk['end']}",
                        f"Size   : {len(chunk['text'])} chars",
                        f"Text   : {chunk['text']!r}",
                    ])

        return "\n".join(output)

if __name__ == "__main__":
    print(Chunker())