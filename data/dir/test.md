# The Big Picture: Purpose & Core Concept

Large Language Models (LLMs) like Qwen3-0.6B have a fixed cutoff date and zero knowledge of private repositories like vLLM. Retraining an LLM every time a codebase changes is impractically expensive.

Retrieval-Augmented Generation (RAG) solves this by bridging information retrieval (search engines) with natural language generation. Instead of relying on the LLM's memory, your system acts like an automated open-book exam assistant:  

1. It searches thousands of codebase files to find exact relevant code/documentation snippets.
2. It injects those specific snippets into the small LLM's context window.
3. The LLM synthesizes a grounded answer based strictly on the provided snippets.  

# The 4 Key Pipeline Stages
1. Ingestion & Chunking: Loading .py and .md files and chopping them into smart, context-rich chunks (under 2000 characters).
2. Indexing: Building an inverted index (BM25 or TF-IDF) on your local disk so searches run in milliseconds across thousands of files.
3. Retrieval: Parsing user queries and extracting top-$k$ candidate source locations (file_path, start character, end character).
4. Generation & Grounding: Formatting retrieved snippets into a tight prompt for Qwen3-0.6B to generate JSON-formatted answers without hallucinating.

# What You Will Master After Completing This Project
- Search Engineering: How lexical ranking algorithms like BM25 work mathematically (TF-IDF vs BM25 term saturation and length normalization).
- Code Parsing Strategies: Why code requires structural AST (Abstract Syntax Tree) chunking while documentation requires markdown structure.
- Evaluation Metrics: How search accuracy is mathematically evaluated in industry using Recall@k and Intersection over Union (IoU).
- Production Python Architecture: Advanced strict typing (mypy), strict linter compliance (flake8), Pydantic validation schemas, dependency locking with uv, and CLI design.

