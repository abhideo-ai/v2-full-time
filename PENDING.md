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
