import os
from typing import List, Tuple

class Loader:
    def __init__(self, data_dir="data/raw"):
        if not os.path.exists(data_dir) or not os.path.isdir(data_dir):
            raise ValueError(f"Target directory '{data_dir}' does not exist or is not a valid directory.")

        self.markdown_docs = []
        self.python_docs = []
        for dirpath, _, filenames in os.walk(data_dir):
            for filename in filenames:
                ext = os.path.splitext(filename)[1].lower()
                if ext in (".md", ".txt", ".py"):
                    fullpath = os.path.join(dirpath, filename)
                    cleanpath = fullpath.replace("\\", "/")
                    try:
                        with open(fullpath, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                        if ext in (".md", ".txt"):
                            self.markdown_docs.append((cleanpath, content))
                        elif ext == ".py":
                            self.python_docs.append((cleanpath, content))
                    except OSError as e:
                        print(f"Warning: Could not read file {cleanpath}: {e}")