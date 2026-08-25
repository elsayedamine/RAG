import ast
from typing import List, Tuple, Dict, Any


def build_line_offsets(content: str) -> List[int]:
    offsets = [0]
    pos = 0
    for line in content.splitlines(keepends=True):
        pos += len(line)
        offsets.append(pos)
    return offsets


def fallback_line_chunker(text: str, start, path, chunks: List, max_chunk_size: int = 2000):
    pos = start
    buffer = ""
    buffer_start = start

    for line in text.splitlines(keepends=True):
        # if line too long we flush the buffer
        # and split the line by max_chunk_size
        if len(line) > max_chunk_size:
            if buffer:
                chunks.append({"text": buffer, "start": buffer_start,
                                "end": pos, "path": path})
                buffer = ""

            for i in range(0, len(line), max_chunk_size):
                chunk = line[i:i + max_chunk_size]
                chunks.append({"text": chunk, "start": pos + i,
                    "end": pos + i + len(chunk), "path": path})

            pos += len(line)
            buffer = ""
            buffer_start = pos
        # we append until we reach max_chunk_size to flush
        elif len(buffer) + len(line) <= max_chunk_size:
            buffer += line
            pos += len(line)
        # we flush when max_chunk_size is reached
        else:
            chunks.append({"text": buffer, "start": buffer_start,
                           "end": pos, "path": path})
            buffer = line
            buffer_start = pos
            pos += len(line)
    # post loop flush
    if buffer:
        chunks.append({"text": buffer, "start": buffer_start,
                       "end": pos, "path": path})


def is_main_guard(node):
    return (
        isinstance(node, ast.If)
        and isinstance(node.test, ast.Compare)
        and isinstance(node.test.left, ast.Name)
        and node.test.left.id == "__name__"
        and len(node.test.ops) == 1
        and isinstance(node.test.ops[0], ast.Eq)
        and len(node.test.comparators) == 1
        and isinstance(node.test.comparators[0], ast.Constant)
        and node.test.comparators[0].value == "__main__"
    )


def tree_walk(node, content: str, offsets: List[int], path: List[str], chunks: List, max_chunk_size: int = 2000):
    nodes = node if isinstance(node, list) else (
    node.body if hasattr(node, "body") else [node]
)
    buffer = ""
    buffer_start = None
    buffer_end = None
    buffer_path = None

    for nd in nodes:
        start = offsets[nd.lineno - 1] + nd.col_offset
        end = offsets[nd.end_lineno - 1] + nd.end_col_offset

        current_path = path
        if is_main_guard(nd):
            current_path = path + ["__main__"]
        elif isinstance(nd, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            current_path = path + [nd.name]
        text = content[start:end]

        is_scope = (is_main_guard(nd) or isinstance(nd, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)))

        if is_scope and buffer:
            chunks.append({
                "text": buffer,
                "start": buffer_start,
                "end": buffer_end,
                "path": buffer_path,
            })
            buffer = ""
            buffer_start = None
            buffer_end = None
            buffer_path = None
        if end - start > max_chunk_size:
            if buffer:
                chunks.append({"text": buffer, "start": buffer_start,
                    "end": buffer_end, "path": buffer_path,})
                buffer = ""
                buffer_start = None
                buffer_end = None
                buffer_path = None
            found_child = False
            children = [child for child in ast.iter_child_nodes(nd) if isinstance(child, ast.stmt)]
            if children:
                found_child = True
                tree_walk(children, content, offsets, current_path, chunks, max_chunk_size)
            if not found_child:
                fallback_line_chunker(text, start, current_path, chunks, max_chunk_size)
            continue
        if not buffer:
            buffer = text
            buffer_start = start
            buffer_end = end
            buffer_path = current_path
        elif end - buffer_start <= max_chunk_size:
            buffer += content[buffer_end:start] + text
            buffer_end = end
        else:
            chunks.append({"text": buffer, "start": buffer_start,
                           "end": buffer_start, "path": buffer_path})
            buffer = text
            buffer_start = start
            buffer_end = end
            buffer_path = current_path
    if buffer:
        chunks.append({"text": buffer, "start": buffer_start,
                       "end": buffer_end, "path": buffer_path})

def PYchunker(content: str, max_chunk_size: int = 2000) -> List[Dict[str, Any]] :
    offsets = build_line_offsets(content)
    chunks = []
    try:
        tree = ast.parse(content)
    except SyntaxError:
        fallback_line_chunker(content, 0, [], chunks, max_chunk_size)
        return chunks
    tree_walk(tree, content, offsets, [], chunks, max_chunk_size)
    return chunks

if __name__ == "__main__":
    content = "# test content"
    chunks = PYchunker(content, max_chunk_size=2000)

    for i, chunk in enumerate(chunks, 1):
        print(f"\n--- Chunk {i} ---")
        print(f"Path   : {chunk['path']}")
        print(f"Offset : {chunk['start']} → {chunk['end']}")
        print(f"Size   : {len(chunk['text'])}")
        print(f"Text   : {chunk['text']!r}")