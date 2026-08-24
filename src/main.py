import argparse
from .indexing.chunker import Chunker


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--max_chunk_size",
        type=int,
        default=2000,
    )
    args = parser.parse_args()

    chunks = Chunker(args.max_chunk_size)
    print(chunks)


if __name__ == "__main__":
    main()