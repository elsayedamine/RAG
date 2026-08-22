from typing import List, Tuple, Dict, Any

MAX_SIZE = 2000
SEPARATORS = [
    "\n\n",  # Paragraphs
    "\n",    # Lines
    ". ",    # Period
    "? ",    # Question mark
    "! ",    # Exclamation mark
    " ",     # Words / Spaces
    "",      # Hard character fallback
]


def MDchunker(doc: Tuple[str, str]) -> List[Dict[str, Any]] :
    content = doc[1]

    current_pos = 0
    current_start_index = 0
    header_stack = []
    in_code_block = False
    sections = []

    for line in content.splitlines(keepends=True):
        line_start_index = current_pos
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
        first_token = line.split(" ")[0] if line else ""
        is_header = not in_code_block and 1 <= len(first_token) <= 6 and \
            all(c == '#' for c in first_token)
        if is_header:
            # save prev section
            section_text = content[current_start_index:line_start_index]
            # titles hierarchy
            path = [title for _, title in header_stack]

            if section_text.strip():
                sections.append({
                    "text": section_text,
                    "start": current_start_index,
                    "end": line_start_index,
                    "path": path
                })

            level = len(first_token)
            title = line[level:].strip()

            while header_stack and header_stack[-1][0] >= level:
                header_stack.pop()
            header_stack.append((level, title))

            current_start_index = line_start_index
        current_pos += len(line)

    final_text = content[current_start_index:]
    if final_text.strip():
        sections.append({
            "text": final_text,
            "start": current_start_index,
            "end": len(content),
            "path": [title for _, title in header_stack]
        })
    return sections

def split(text: str, abs_offset: int, seperator: str, path: List[str], sections: List[Dict[str, Any]]):
    # text fits within the character limit
    if len(text) <= MAX_SIZE:
        sections.append({
            "text": text,
            "start": abs_offset,
            "end": abs_offset + len(text),
            "path": path,
        })
    # text exceeds limit and no separator remains -> hard-slice
    elif len(text) > MAX_SIZE and seperator == "":
        length = len(text)
        # Slice text directly into fixed-size chunks of MAX_SIZE
        for i in range(0, length, MAX_SIZE):
            block = text[i: i + MAX_SIZE]
            sections.append({
                "text": block,
                "start": abs_offset + i,
                "end": abs_offset + i + len(block),
                "path": path,
            })
    # text exceeds limit and active separator exists
    elif len(text) > MAX_SIZE and seperator:
        curr_rel_offset = 0
        buffer = []
        buffer_len = 0
        buffer_start = abs_offset
        sep_len = len(seperator)

        # split using active separator
        pieces = text.split(seperator)
        for i, piece in enumerate(pieces):
            # Calculate absolute starting offset
            piece_abs_start = abs_offset + curr_rel_offset
            piece_len = len(piece)

            # Piece itself exceeds limit -> Flush buffer and recursively split
            if piece_len > MAX_SIZE:
                # Flush accumulated pieces before diving deeper
                if buffer:
                    joined = seperator.join(buffer)
                    sections.append({
                        "text": joined,
                        "start": buffer_start,
                        "end": buffer_start + len(joined),
                        "path": path,
                    })
                    buffer = []
                    buffer_len = 0
                split(piece, piece_abs_start, SEPARATORS[SEPARATORS.index(seperator) + 1], path, sections)

            # Piece fits into current buffer without exceeding limit
            elif buffer_len + piece_len + (sep_len if buffer else 0) <= MAX_SIZE:
                # Set buffer start position on the first added piece
                if not buffer:
                    buffer_start = piece_abs_start
                # Append piece and update cumulative length including joining separators
                buffer.append(piece)
                buffer_len += piece_len + (sep_len if len(buffer) > 1 else 0)

            # Buffer limit reached -> Flush active buffer and start new buffer
            else:
                # Flush full buffer as a completed section
                joined = seperator.join(buffer)
                sections.append({
                    "text": joined,
                    "start": buffer_start,
                    "end": buffer_start + len(joined),
                    "path": path,
                })
                # Re-initialize buffer starting with the current piece
                buffer = [piece]
                buffer_len = piece_len
                buffer_start = piece_abs_start

            # Advance character offset tracking by piece size and separator length
            curr_rel_offset += piece_len + (sep_len if i < len(pieces) - 1 else 0)

        # Post-loop flush:
        if buffer:
            joined = seperator.join(buffer)
            sections.append({
                "text": joined,
                "start": buffer_start,
                "end": buffer_start + len(joined),
                "path": path,
            })


if __name__ == "__main__":
    doc: Tuple[str, str] = ("example.md", "# Title\nYour markdown content here...")
    macro_sections = MDchunker(doc)
    final_chunks: List[Dict[str, Any]] = []

    for section in macro_sections:
        if len(section["text"]) > MAX_SIZE:
            split(
                text=section["text"],
                abs_offset=section["start"],
                seperator=SEPARATORS[0],
                path=section["path"],
                sections=final_chunks,
            )
        else:
            final_chunks.append(section)

# steps

# save line start index at first
# check if u are in ``` block to ignore #
# check if u are in header
# do all this in header only
# take the sectiontext from the prev start index to the new saved one
# take the titles of the section as path from the headers stack
# append the sectiontext to the sections[] after stripping
# then find the new level u are in  by the len of the ###
# and the title after it 
# and pop up all the header_stack that are inside ur level (level >= curr_level)
# and append the current level and title to ur headerstack
# save the prev index start with the new start index
# and then ouside the isheader increment the current absolute pos with len(line) + 1 
# after the while append all the remaining text
