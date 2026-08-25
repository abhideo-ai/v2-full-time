# Pending at context clear — 2026-08-25 ~22:15

## All three scored — full rubrics in each `<workspace>/score.json`

| Seat | Technical | Comp | Mode | The cap |
|---|---|---|---|---|
| **AI-Native & Agentic Architect** — Bengaluru | **83.3** | not disclosed | hybrid | No dedicated vector-DB product; ANN internals absent |
| **Yes Madam** — Lead Architect, Noida | **83.0** | ₹60–80L | **in-office** | **Kubernetes** and **Grafana/Prometheus** absent, both *required* |
| **o9 Solutions** — Senior Architect, Bengaluru | **80.4** | **₹60–100L** | hybrid | **"5+ years deep learning"** — he has ~14 months applied |

**None reaches 95, and none is closable by re-vectoring** — each is capped by absent experience,
not by wording. Say so plainly rather than implying a rewrite fixes it.

**The three sharpest findings, one per seat:**

- **Yes Madam** — he left Deque on **Spring Boot 2.x**, so it is *never shipped on Spring Boot 3*,
  not *behind on it*. Jakarta namespace, SB3 observability, Java 21 virtual threads all unevidenced.
  His concurrency proof is **Go**, so a JVM follow-up has no JVM answer behind it.
- **AI-Native** — his own KQ1 Q&A already answers the vector-DB objection: Elasticsearch
  `dense_vector` is *"the implementation default behind an index abstraction"* and a dedicated store
  is *"a still-open bake-off"*. He architected the **vector data access layer** — the JD's exact
  phrase. But Pinecone/Weaviate/Milvus/pgvector/Qdrant and HNSW internals are zero hands-on.
- **o9** — the requirement is a compound OR and the halves must not be averaged. **Data
  engineering: met deeply**, 2012 → 2026, nine-year hydration with byte-identical replay.
  **Deep learning: ~14 months**, one stint. The IIIT diploma (Jan 2021) adds credibility, not years.
  And his portfolio's stated through-line is *"knowing when not to use an LLM"* — an architecture
  virtue that reads as one, but it means no fine-tuning, no pre-training, no CV, no RL anywhere.
  MLOps partly rescues it: retraining pipelines and drift detection are directly evidenced; a
  **model registry is never named**.

## Still outstanding, his hand

- **El Paso's three bullets on the Hiration card still read .NET.** The title is corrected to
  *Senior Java Developer*; the bullets revert on save. Correct text: `master/upgrad_resume.html` §14.
- **His live card's 17 VoltusWave bullets are not merged into the master** — Kubernetes, Terraform,
  ECS Fargate at 70% Spot, k6-validated, React Native across 2 app stores, the 4 reusable
  archetypes, `TraversalSource` wrapper, Rosenbaum γ + E-value. Biggest unfinished résumé work.
  **Note:** his live card claims Kubernetes and Terraform. If that is real, Yes Madam's binding
  constraint disappears and the score moves. **Ask him.**
- **The +65% hotel conversions** — unresolved, stays per the no-scrub rule.

## Next command

```
automation/.venv/bin/python automation/resume.py new --slug <slug> --company X --role Y
```
Then delegate the whole build. Master PDF is done: `master/Abhisheik_Deo_Resume.pdf`, 3 pages, ATS 85.

## His read on the vector-DB gap — 2026-08-25, and it stands

> *"Vector databases — it's a relatively simple thing for a person with my experience to learn/master."*

**Correct, and the rubric already agrees**: it is classified a **RAMP ITEM, not a capability cap.**
He did not fail to use a vector database — he architected around one deliberately, and KQ1's Q&A
makes the case: Elasticsearch `dense_vector` is *"the implementation default behind an index
abstraction… so the store can be swapped without touching the serving contract."*

Someone who already reasons about hybrid filter-plus-kNN in one engine, tenant filters **inside**
the query, embedding-version pinning across index and query, and blue-green index rebuilds with
shadow evaluation learns a specific store's API in an afternoon.

**The caveat that still holds:** "I could learn it quickly" does not score in a room. Fluency in the
trade-offs *now* does — HNSW `ef_construction` vs `M`, recall-versus-latency, quantisation cost,
when a dedicated store actually beats a hybrid engine. A week of reading, not a quarter. **Do not
re-litigate this gap as a capability cap.**

## Gap prep running

`wf_58f6f5c4-caa` → `~/Documents/interview-prep/gap-prep/index.html`. Seven gaps, ordered by how
CERTAIN the question is. Each gets: the honest concession first, the nearest real thing, the bridge
and where it stops, what to learn this week, and three likely questions with one-sentence headlines.

**The graph neural network is first and is the highest-risk item in his whole profile** — he
confirmed it is real, it sits in word-position four of his headline, and the phrase appears **zero
times across all 22 case-study files** because it attaches to the Context Graph, which those ten
killer queries do not document. A headline claim with no artefact to rehearse from. Only he can
fill in the node/edge schema, the task, the framework, the training data and how it was served.
