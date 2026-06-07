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

## Sample Chunks

**Chunk 1**
Source: rmp_bio_151.txt | Professor: Jeff Laney
[REVIEW 8]
Date: October 2022
Quality: 1/5 | Difficulty: 5/5
Grade: A- | Attendance: Mandatory
Tags: Tough grader, Lecture heavy
Content: Do not take this class. I spent upwards of 3 hours every day, weekends included,
trying to understand this material. Does not teach in a clear and understandable way.
If you're a hard worker you will be fine but if not, you will fail. Very hard class.

---

**Chunk 2**
Source: rmp_physics_151.txt | Professor: Jason Stevens
[REVIEW 4]
Date: October 2020
Quality: 1/5 | Difficulty: 5/5
Grade: F | Attendance: Not Mandatory
Tags: Graded by few things, Test heavy, Tough grader
Content: If you forgot Physics in high school, you're going to struggle badly.

---

**Chunk 3**
Source: rmp_cs_160.txt | Professor: Ella Tuson
[REVIEW 3]
Date: December 2025
Quality: 4/5 | Difficulty: 2/5
Grade: A | Attendance: Mandatory | Would Take Again: Yes
Tags: Hilarious, Caring
Content: It's clear she is very passionate about the topics she teaches in class, and I do
think she is a great lecturer when she teaches material. However, we did spend a lot of
lecture time going over stuff that didn't really matter, and lecture attendance was
unfortunately required. Overall, a top tier professor with some issues.

---

**Chunk 4**
Source: rmp_bio_151.txt | Professor: Amanda Cass
[REVIEW 8]
Date: December 2025
Quality: 5/5 | Difficulty: 1/5
Grade: A | Attendance: Mandatory | Would Take Again: Yes
Tags: Amazing lectures, Caring
Content: Great professor. I didn't have to study for any tests because all the lectures
had easily digestible information that stacked on top of each other. No complaints
except for the TAs, they were all snobs who never could accept being wrong.

---

**Chunk 5**
Source: rmp_cs_110.txt | Professor: Cole Reilly
[REVIEW 4]
Date: December 2024
Quality: 4/5 | Difficulty: 2/5
Grade: A | Attendance: Mandatory | Would Take Again: Yes
Tags: Clear grading criteria, Caring, Accessible outside class
Content: Cole is a good and caring professor. They are very accessible outside the class
and will help you if you show some effort.

## Retrieval Test Results

**Query 1: "Is David Hamilton a good professor for PHY 151?"**
Top 5 chunks returned:
- rmp_physics_151.txt — David Hamilton (distance: 0.8190)
- rmp_physics_151.txt — David Hamilton (distance: 0.8315)
- rmp_cs_160.txt — Jaime Davila (distance: 0.8589)
- rmp_physics_151.txt — David Hamilton (distance: 0.8611)
- rmp_physics_151.txt — Boris Svistunov (distance: 0.9164)

Why results 1, 2, and 4 are relevant: All three chunks contain the name "Hamilton"
and "PHY 151" which directly match the query. The embedding model correctly identified
semantic similarity between the query and reviews discussing Hamilton's teaching style,
lecture quality, and homework load.

---

**Query 2: "Which BIO 151 professor should I avoid?"**
Top 5 chunks returned:
- rmp_bio_151.txt — Randall Phillis (distance: 0.8628)
- rmp_bio_151.txt — Jeff Laney (distance: 0.8648)
- rmp_bio_151.txt — Caralyn Zehnder (distance: 0.9208)
- rmp_bio_151.txt — Amanda Cass (distance: 0.9454)
- rmp_bio_151.txt — Amanda Cass (distance: 1.1180)

Why results are relevant: All 5 chunks are from rmp_bio_151.txt, meaning retrieval
correctly scoped to the right course. Result 2 (Laney) and result 5 (Cass negative
review) are the most directly relevant — both contain strongly negative language
that semantically matched the "avoid" intent of the query.

---

**Query 3: "What is the workload like for CICS 160 with Professor Davila?"**
Top 5 chunks returned:
- rmp_cs_160.txt — Jaime Davila (distance: 0.9467)
- rmp_cs_160.txt — Jaime Davila (distance: 0.9560)
- rmp_cs_160.txt — Jaime Davila (distance: 1.0060)
- rmp_cs_110.txt — Cheryl Swanier (distance: 1.1181)
- rmp_bio_151.txt — Randall Phillis (distance: 1.1622)

Why results 1-3 are relevant: The top 3 chunks all come from rmp_cs_160.txt and
are attributed to Davila, directly matching both the course and professor in the
query. Results 4 and 5 are off-target but the LLM correctly ignored them when
generating the answer.

## Example Responses

**Query: "Which BIO 151 professor should I avoid?"**
Response: According to the reviews, there are two professors that students have
expressed negative experiences with: Jeff Laney and Amanda Cass. One reviewer
strongly advises against taking BIO 151 with Jeff Laney, stating that he is the
"worst professor to ever exist in the bio department" and that his classes are
"very poorly managed" (Professor: Jeff Laney, Source: rmp_bio_151.txt). Another
reviewer warns against Amanda Cass, citing heinous study guides and confusing
weekly quiz questions (Professor: Amanda Cass, Source: rmp_bio_151.txt). However,
there is a conflicting review from a student who had a very positive experience
with Cass. Based on the reviews, Jeff Laney is the professor students most strongly
advise against.

Sources:
- rmp_bio_151.txt — Randall Phillis
- rmp_bio_151.txt — Jeff Laney
- rmp_bio_151.txt — Caralyn Zehnder
- rmp_bio_151.txt — Amanda Cass

---

**Query: "What is the workload like for CICS 160 with Professor Davila?"**
Response: According to the reviews from Professor Jaime Davila's CICS 160 class,
the workload is described as easy with a difficulty rating of 2/5 by multiple
reviewers. One reviewer mentions that the class is easy and that Professor Davila
is always willing to help. Another reviewer notes that the lectures are amazing
and office hours are incredibly helpful. There is no mention of an excessive or
heavy workload in these reviews.

Sources:
- rmp_cs_160.txt — Jaime Davila
- rmp_cs_110.txt — Cheryl Swanier
- rmp_bio_151.txt — Randall Phillis

---

**Out-of-scope query: "What dining hall should I eat at?"**
Response: I don't have enough information in my documents to answer that.

Sources:
- rmp_bio_151.txt — Caralyn Zehnder
- rmp_cs_160.txt — Jaime Davila
- rmp_math_131.txt — Eric Heinzman


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

**Retrieval quality:** Relevant  
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
