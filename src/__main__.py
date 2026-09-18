import fire, os, json
from indexing import Indexer, Corpus, Chunker
from retrieval import Retriever


def index(max_chunk_size=2000):
    indexer = Indexer(Corpus(Chunker(max_chunk_size)))
    indexer.save("index.json")


def search(query, k=5):
    indexer = Indexer.load("data/processed/index.json")
    retriever = Retriever(indexer)

    results = retriever.retrieve(query, k)

    for source in results:
        print(source)


def search_dataset(dataset_path, k=5, save_directory="data/output/search_results"):
    indexer = Indexer.load("data/processed/index.json")
    retriever = Retriever(indexer)

    results = retriever.retrieve_dataset(dataset_path, k)

    os.makedirs(save_directory, exist_ok=True)
    output_path = os.path.join(
        save_directory,
        os.path.basename(dataset_path),
    )

    with open(output_path, "w") as js:
        json.dump(results.model_dump(), js, indent=2)
    


if __name__ == "__main__":
    fire.Fire()