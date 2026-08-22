from .loader import Loader
import ast
from typing import List, Tuple, Dict, Any

def build_line_offsets(content: str) -> List[int]:
    lines = content.splitlines(keepends=True)
    offsets = [0]
    pos = 0
    for line in content.splitlines(keepends=True):
        pos += len(line)
        offsets.append(pos)
    return offsets

def PYchunker(doc: Tuple[str, str]) -> List[Dict[str, Any]] :
    offsets = build_line_offsets(doc[1])
    tree = ast.parse(doc[1])
    print(ast.dump(tree, indent=4))
    # for node in tree.body:
    #     print(f"Node type: {type(node).__name__}")
    # if isinstance(node, ast.Assign
    #     print(f"  Found assignment: {ast.dump(node)}")
    # elif isinstance(node, ast.FunctionDef):
    #     print(f"  Found function: {node.name}")
    # elif isinstance(node, ast.Expr):
    #     print(f"  Found expression: {ast.dump(node)}")

if __name__ == "__main__":
    with open("./src/indexing/chunker.py") as f:
        content  = f.read()
    PYchunker(content)
