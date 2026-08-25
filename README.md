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

# ---------------------------------------------------------------------------------------------

1. What is BM25?

BM25 = Best Matching 25.

It is a lexical information-retrieval ranking algorithm.

Its job is:

Given a query and a collection of documents, assign a relevance score to every document and rank them.

For your RAG:

User query
    ↓
BM25
    ↓
score every chunk
    ↓
rank chunks
    ↓
take top-k
    ↓
LLM

It does not understand meaning.

If the query is:

how does epoll handle non blocking sockets

BM25 looks for terms such as:

epoll
handle
non
blocking
sockets

and determines which chunks are statistically most relevant.

2. Why did we need something like BM25?

Before modern embeddings and LLMs, search engines still had to answer:

"Which documents are most relevant to this query?"

The simplest possible approach would be:

Does the document contain the query word?

But that's not enough.

Consider:

Document A:
epoll epoll epoll epoll

Document B:
epoll is used to monitor file descriptors for I/O events.

A naive system might think A is better because it contains epoll four times.

But obviously B is probably more useful.

So information retrieval needed a better way to quantify:

How often does the term occur?
How rare is the term across the collection?
Is the document unusually long?
How much should repeated occurrences matter?

That led to increasingly sophisticated ranking models.

3. The history

BM25 didn't appear from nowhere.

A simplified history is:

Boolean retrieval
      ↓
TF-IDF
      ↓
Probabilistic Retrieval Model
      ↓
BM25
Boolean retrieval

The earliest systems essentially worked like:

"find documents containing X"

You could do:

epoll AND socket

Very rigid.

You get matching documents, but no good notion of degree of relevance.

4. TF-IDF

Then came one of the most important ideas in information retrieval:

TF-IDF

It combines:

TF — Term Frequency

How often does a term appear in this document?

document:
epoll socket epoll server epoll

TF(epoll) = 3

Generally:

More occurrences → stronger evidence that the document is about that term.

But there's a problem.

IDF — Inverse Document Frequency

Suppose your corpus has 10,000 documents.

the appears in:

9,900 documents

while:

epoll

appears in:

30 documents

Finding the tells us almost nothing.

Finding epoll tells us a lot.

So:

Rare terms are more informative than common terms.

That's what IDF captures.

Conceptually:

common term → low IDF
rare term   → high IDF

5. But TF-IDF still has problems

Imagine:

Document A:
epoll

Document B:
epoll epoll epoll epoll epoll epoll epoll epoll

Should B really be 8× more relevant?

Probably not.

Once a document contains a term several times, additional occurrences provide diminishing evidence.

You want something like:

1 occurrence → significant increase
2 occurrences → another increase
5 occurrences → some increase
50 occurrences → definitely NOT 50× better

This is called term-frequency saturation.

BM25 handles this.

# ---------------------------------------------------------------------------------------------
6. BM25's core idea

BM25 essentially asks:

How strong is the evidence that this document is relevant to this query?

For each query term, it considers three major things:

① Term frequency

How many times does the term occur?

TF

More occurrences help.

But with diminishing returns.

② Inverse document frequency

How rare is this term in the entire corpus?

IDF

Rare terms matter more.

Common terms matter less.

③ Document length

How long is the document compared with the average document?

A 10-word document containing epoll 3 times is very different from a 10,000-word document containing epoll 3 times.

BM25 normalizes for document length.

7. The actual formula

The standard BM25 score looks roughly like:

score(D,Q)= t∈Q ∑ IDF(t) * (f(t,D)*(k1 + 1)) / f(t,D) + k1(1-b + b *(|D|/avgdl))



Don't worry about memorizing it yet.

Break it apart:

BM25 score
    │
    ├── IDF
    │
    └── TF component
          │
          ├── term frequency
          ├── k1
          ├── document length
          ├── average document length
          └── b
8. What does k1 do?

k1 controls term-frequency saturation.

Think:

term appears:
1 time  → useful
2 times → more useful
3 times → more useful
...
100 times → not dramatically more useful

k1 controls how quickly that saturation happens.

Typical values are around:

k1 ≈ 1.2–2.0

You don't need to invent a value initially. A conventional value such as 1.2 or 1.5 is a reasonable starting point.

9. What does b do?

b controls document-length normalization.

Usually:

b = 0.75

Conceptually:

b = 0

→ don't care about document length

b = 1

→ strongly normalize according to document length

b = 0.75

→ compromise

For your RAG chunks, this parameter is particularly interesting because your documents are already chunks of relatively controlled size.

That means BM25's document-length normalization may behave somewhat differently than it does on arbitrary webpages or books.

# ---------------------------------------------------------------------------------------------

10. Why BM25 is excellent for your RAG

This is where BM25 becomes particularly useful.

Suppose your repository contains:

epoll_ctl(epoll_fd, EPOLL_CTL_ADD, fd, &event);

User asks:

where is epoll_ctl used?

An embedding model might understand the semantic concept.

But BM25 sees:

epoll_ctl

which is an extremely distinctive token.

That's powerful.

Another example:

getaddrinfo
ServerConfig
EPOLL_CTL_ADD
SO_REUSEPORT
CGI

These are identifiers and technical terms.

Semantic embeddings aren't always the best mechanism for exact identifier retrieval.

BM25 is extremely good at this.

11. What BM25 does NOT solve

This is important.

BM25 doesn't understand:

"How does the server wait for socket events?"

and:

"How does epoll_wait monitor file descriptors?"

as necessarily being semantically related unless the relevant words overlap.

It fundamentally operates on terms.

So:

"car"

and:

"automobile"

are different terms.

BM25 doesn't inherently know they're synonyms.

12. That's where embeddings enter

Embeddings solve almost the opposite problem.

They capture:

semantic similarity

So:

"How does the server monitor socket events?"

can retrieve something discussing:

epoll_wait monitors registered file descriptors...

even if the exact words don't match.

But embeddings have their own weaknesses.

They can struggle with:

getaddrinfo
EPOLL_CTL_ADD
ft_vault_security.py
ServerConfig

where exact lexical matching is extremely important.

13. Therefore: Hybrid Retrieval

This is where your RAG architecture gets interesting.

Instead of:

BM25 OR embeddings

you can do:

                 Query
                   │
          ┌────────┴────────┐
          ↓                 ↓
        BM25             Embeddings
          ↓                 ↓
     lexical rank      semantic rank
          │                 │
          └────────┬────────┘
                   ↓
              combination
                   ↓
               reranking
                   ↓
                top-k

This is called hybrid retrieval.

And for a repository/document RAG system, this is usually much more compelling than relying exclusively on either mechanism.

# ---------------------------------------------------------------------------------------------

14. One more important distinction

You asked earlier about indexing vs retrieval.

BM25 has both.

Indexing

Before the user asks anything:

chunks
  ↓
tokenize
  ↓
build inverted index

For example:

"epoll"
    → document 3
    → document 17
    → document 42

The index stores the information needed to calculate BM25 efficiently.

Retrieval

Then the user asks:

"epoll socket"

We:

query
 ↓
tokenize
 ↓
lookup terms in index
 ↓
calculate BM25 scores
 ↓
rank documents
 ↓
top-k

So BM25 is the ranking model, while the inverted index is the data structure that makes lexical retrieval efficient.

Those are related but not the same thing.

# ---------------------------------------------------------------------------------------------

The mental model I want you to have

Don't think of BM25 as:

"an algorithm that searches text."

Think of it as:

a probabilistic-ish relevance scoring model that estimates how strongly each document matches a query using term frequency, term rarity, and document-length normalization.

And the surrounding system is:

                DOCUMENT SIDE
                     │
                  chunks
                     ↓
                 tokenize
                     ↓
              inverted index
                     ↓
                  BM25
                     ↑
                     │
                  tokenize
                     ↑
                   query

              QUERY / RETRIEVAL SIDE

The next thing worth learning is the inverted index, because once you understand that data structure, BM25's implementation becomes much less mysterious.