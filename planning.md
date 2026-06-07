# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

I decided to choose RMP ratings for first year courses, because a lot of incoming freshman may be unfamiliar with how choosing professors matters, and be eager to take on rigorous course work, or maybe just say that any option that they have for a course is fine as long as it's not too early in the day. The truth is when you have options you want to be all the more careful and involved with your decision making.

---

## Documents

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 |Rate My Professors|Reviews for CICS 110 professors: Cole Reilly, Ella Tuson, Cheryl Swanier |docs/cics110_rmp_reviews.txt |
| 2 |Rate My Professors |Reviews for CICS 160 professors: Jaime Davila, Ella Tuson |docs/cics160_rmp_reviews.txt |
| 3 |Rate My Professors | Reviews for MATH 131 professors: Eric Heinzman, Angelica Simonetti, Brody Lynch|docs/math131_rmp_reviews.txt |
| 4 |Rate My Professors | Reviews for PHY 151 professors: David Hamilton, Jason Stevens, Boris Svistunov|docs/phy151_rmp_reviews.txt |
| 5 |Rate My Professors |Reviews for BIO 151 professors: Randall Phillis, Jeff Laney, Caralyn Zehnder, Amanda Cass |docs/bio151_rmp_reviews.txt |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:** 200 characters

**Overlap:** 0 characters

**Reasoning:** The reviews are separated by --- so individual reviews that have a high similarity score should be able to match the question well. Overlap here would mix two different reviews up, which is not needed since the .txts are cleaned up already.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** all-MiniLM-L6-v2 via sentence transformers  

**Top-k:** 5

**Production tradeoff reflection:** because the chunks are small enough that we dont require large context windows, and it can run locally which keeps it free! If I had to use OpenAI's text-embedding instead, it would be more accurate but we'd pay per token.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 |"Who is the most recommended professor for PHY 151?"|David Hamilton |
| 2 |"Which BIO 151 professor should I avoid?" | Jeff Laney (overwhelmingly negative reviews)|
| 3 |"Which CICS 110 professor should I avoid?" | Cheryl Swanier (rude, disorganized, negative reviews)|
| 4 | "What is the workload like for CICS 160 with Professor Davila?"| No exams, graded on projects/quizzes/labs, manageable workload|
| 5 |"What is the workload like for MATH 131 with Eric Heinzman?" |Expected: Homework is challenging but prepares you for exams, practice exams match real exams closely, participation questions on Canvas |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. Since the chunks are review based, it could find chunks that allign with some keywords of the question in a completely unrelated class. Like where do I study optimization could be in both Physics, CS or Math classes and come up in different contexts.

2. It could also just be a bunch of trolling in the reviews glazing professors for the fun of it, where a professor who has a 1 overall but one 5 rating gets bumped up because a keyword in the trolling comment gets matched heavily.

---

## Architecture

```+------------------+       +------------------+       +---------------------------+
|                  |       |                  |       |                           |
| Document         |  -->  |   Chunking       |  -->  |  Embedding + Vector Store |
| Ingestion        |       |                  |       |                           |
|                  |       |                  |       |                           |
| os / pathlib     |       | Split on "---"   |       | all-MiniLM-L6-v2          |
| (reads .txt      |       | separator        |       | (sentence-transformers)   |
| files from       |       | ~200-350 chars   |       |                           |
| docs/)           |       | per chunk        |       | ChromaDB vector store     |
|                  |       | 0 overlap        |       |                           |
+------------------+       +------------------+       +---------------------------+
                                                                    |
                                                                    v
                                                       +---------------------------+
                                                       |                           |
                                                       |       Retrieval           |
                                                       |                           |
                                                       | Semantic search, top-5    |
                                                       | chunks by cosine          |
                                                       | similarity                |
                                                       |                           |
                                                       +---------------------------+
                                                                    |
                                                                    v
                                                       +---------------------------+
                                                       |                           |
                                                       |       Generation          |
                                                       |                           |
                                                       | LLM synthesizes answer    |
                                                       | from retrieved chunks     |
                                                       | with citations            |
                                                       |                           |
                                                       +---------------------------+ ```

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
