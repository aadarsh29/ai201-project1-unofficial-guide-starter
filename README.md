# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

I decided to go with RMP reviews for first semester courses at UMass Amherst. It is a valuable source of information when narrowing down which classes to take, especially most freshmen underestimate how important a good prof is. Official channels usually glaze professors based on personal accomplishments much more than teaching style, curriculum, etc.

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 |Rate My Professors|Reviews for CICS 110 professors: Cole Reilly, Ella Tuson, Cheryl Swanier |docs/cics110_rmp_reviews.txt |
| 2 |Rate My Professors |Reviews for CICS 160 professors: Jaime Davila, Ella Tuson |docs/cics160_rmp_reviews.txt |
| 3 |Rate My Professors | Reviews for MATH 131 professors: Eric Heinzman, Angelica Simonetti, Brody Lynch|docs/math131_rmp_reviews.txt |
| 4 |Rate My Professors | Reviews for PHY 151 professors: David Hamilton, Jason Stevens, Boris Svistunov|docs/phy151_rmp_reviews.txt |
| 5 |Rate My Professors |Reviews for BIO 151 professors: Randall Phillis, Jeff Laney, Caralyn Zehnder, Amanda Cass |docs/bio151_rmp_reviews.txt |
---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** Size of each review

**Overlap:** 0

**Why these choices fit your documents:** easy to extract since the preprocessed documents had reviews separated by "---"


**Final chunk count:** 120

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** all-MiniLM-L6-v2 via sentence transformers

**Production tradeoff reflection:** Because the chunks are small enough that we dont require large context windows, and it can run locally which keeps it free! If I had to use OpenAI's text-embedding instead, it would be more accurate but we'd pay per token.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:** 
1. Answer ONLY using information from the provided review excerpts. Do not use any outside knowledge.
2. If the provided reviews do not contain enough information to answer the question, say exactly: "I don't have enough information in my documents to answer that.
This forced the LLM to use only the provided information, and reinforced the fact that if it wasnt in the provided information the LLM couldn't abitrarily generate a response based on memory.

**How source attribution is surfaced in the response:**
The LLM cites its sources explaining where each review is found in each txt document. It literally says it found "review 6" under "physics151.txt" for professor "davila" etc, which allows the user to verify the source.
---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

+----+--------------------------------------------------+--------------------------------+--------------------------------------------------+------------------+
| #  | Question                                         | Expected Answer                | System Response Summary                          | Accuracy         |
+----+--------------------------------------------------+--------------------------------+--------------------------------------------------+------------------+
| 1  | "Who is the most recommended professor for       | David Hamilton                 | System said it didn't have enough information    | Inaccurate       |
|    | PHY 151?"                                        |                                | and only found a negative Stevens review —       |                  |
|    |                                                  |                                | failed to retrieve Hamilton chunks               |                  |
+----+--------------------------------------------------+--------------------------------+--------------------------------------------------+------------------+
| 2  | "Which BIO 151 professor should I avoid?"        | Jeff Laney (overwhelmingly     | Correctly identified Laney as strongest avoid,   | Accurate         |
|    |                                                  | negative reviews)              | flagged Cass with conflicting reviews, cited     |                  |
|    |                                                  |                                | sources                                          |                  |
+----+--------------------------------------------------+--------------------------------+--------------------------------------------------+------------------+
| 3  | "Which CICS 110 professor should I avoid?"       | Cheryl Swanier (rude,          | Correctly identified Swanier as disorganized,    | Accurate         |
|    |                                                  | disorganized, negative)        | explicitly recommended avoiding her, contrasted  |                  |
|    |                                                  |                                | with Reilly                                      |                  |
+----+--------------------------------------------------+--------------------------------+--------------------------------------------------+------------------+
| 4  | "What is the workload like for CICS 160          | No exams, graded on            | Correctly described workload as easy (2/5        | Partially        |
|    | with Professor Davila?"                          | projects/quizzes/labs,         | difficulty) but missed specific no-exams /       | Accurate         |
|    |                                                  | manageable                     | projects/quizzes breakdown                       |                  |
+----+--------------------------------------------------+--------------------------------+--------------------------------------------------+------------------+
| 5  | "What is the workload like for MATH 131          | Challenging homework,          | Mentioned lots of homework and extensions but    | Partially        |
|    | with Eric Heinzman?"                             | practice exams match real      | missed that practice exams closely match real    | Accurate         |
|    |                                                  | exams, Canvas participation    | exams and Canvas participation questions         |                  |
+----+--------------------------------------------------+--------------------------------+--------------------------------------------------+------------------+

**Retrieval quality:** Relvant  
**Response accuracy:** Partially accurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:** Who is the most recommended professor for Phyics 151.

**What the system returned:** I don't have enough information in my documents to answer that.

**Root cause (tied to a specific pipeline stage):** The vector embedding model is not trained on review text specifically so it isn't tuned to prioritize courses over key words, so it's looking to match keywords directly to its data. Here are the documents it retrieved which match the highly recommended sentiment but for different subjects completely.
• rmp_math_131.txt — Eric Heinzman
• rmp_bio_151.txt — Caralyn Zehnder
• rmp_cs_160.txt — Jaime Davila

**What you would change to fix it:**  The vector embedding model focused on finding reviews that reflected the recommended sentiment more than anything else. It went looking for similar results in different places completely ignorning the physics 151 mention in the prompt. Better prompts, explicitly mentioning professors will perform better.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:** The specs kept me on track. It was my first time doing anything like this, so it gave me a structed way to go about it and showed my how important planning really is for a project like this. Planning helped me always look back and realize what exactly I was trying to do and change with each iteration.

**One way your implementation diverged from the spec, and why:** I did not end up using a fixed chunking strategy because my data was preprocessed by Claude so it was easy to extract relevant information. Reviews were separated by "---" so it was easy to extract reviews as a whole.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:* The raw text from the websites
- *What it produced:* Polished formatted review texts
- *What I changed or overrode:* Didn't change anything, it gave me the txts as expected.

**Instance 2**

- *What I gave the AI:* Debated between chunking strategy of 200 chars w 50 chars overlap like in class and the chunking strategy to split by "---" and my decision to take 5 chunks at a time with zero overlap.
- *What it produced:* Told me the data is clean enough where we can look at individual chunks ourselves without any overlap strategy.
- *What I changed or overrode:* I noticed it was truncating at 400 chars and wondered if the reviews were being cut off. Then verified that it was only truncated in the print statement and not the actual code.
