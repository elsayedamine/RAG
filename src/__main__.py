import fire, os, json, uuid
from indexing import Indexer, Corpus, Chunker
from retrieval import Retriever
from generation import Answerer
from models import (
    MinimalSearchResults,
    StudentSearchResults,
)

def index(max_chunk_size=2000, output_path="data/processed/index.json"):
    indexer = Indexer(Corpus(Chunker(max_chunk_size)))
    indexer.save(output_path)


def search(query, k=5, index_path="data/processed/index.json"):
    indexer = Indexer.load(index_path)
    retriever = Retriever(indexer)

    results = retriever.retrieve(query, k)

    for source in results:
        print(source)


def search_dataset(dataset_path, k=5, save_directory="data/output/search_results", index_path="data/processed/index.json"):
    indexer = Indexer.load(index_path)
    retriever = Retriever(indexer)

    results = retriever.retrieve_dataset(dataset_path, k)

    os.makedirs(save_directory, exist_ok=True)
    output_path = os.path.join(
        save_directory,
        os.path.basename(dataset_path),
    )

    with open(output_path, "w") as js:
        json.dump(results.model_dump(), js, indent=2)

def answer(query, k=5, index_path="data/processed/index.json"):
    indexer = Indexer.load(index_path)
    retriever = Retriever(indexer)

    sources = retriever.retrieve(query, k)

    result = MinimalSearchResults(
        question_id=str(uuid.uuid4()),
        question=query,
        retrieved_sources=sources,
    )

    answerer = Answerer(indexer)
    result = answerer.answer(result)

    print(result.model_dump_json(indent=2))

def answer_dataset(student_search_results_path, save_directory="data/output/search_results_and_answer", index_path="data/processed/index.json"):
    """Generate answers for a search-results dataset."""
    indexer = Indexer.load(index_path)
    answerer = Answerer(indexer)

    with open(student_search_results_path, "r") as js:
        results = StudentSearchResults.model_validate_json(js.read())

    answered = answerer.answer_dataset(results)

    os.makedirs(save_directory, exist_ok=True)

    output_path = os.path.join(
        save_directory,
        os.path.basename(student_search_results_path),
    )

    with open(output_path, "w") as js:
        json.dump(answered.model_dump(), js, indent=2)

if __name__ == "__main__":
    fire.Fire()