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

## ⚠ THE THREE WORKSPACES ARE SCORED BUT NOT TAILORED AND NOT EXPORTED

```
o9-senior-architect-agentic      pdf=no  score=yes  resume=UNCHANGED COPY OF MASTER
principal-architect-ai-native    pdf=no  score=yes  resume=UNCHANGED COPY OF MASTER
yes-madam-lead-architect         pdf=no  score=yes  resume=UNCHANGED COPY OF MASTER
```

Only `master/Abhisheik_Deo_Resume.pdf` exists — 3 pages, ATS 85, verified.

**Do NOT export these as they stand.** Each `upgrad_resume.html` is byte-identical to the master,
so three exports would produce three identical PDFs — which is precisely the top-of-résumé-only
tailoring that produced **zero calls in June 2026**.

### The missing step: Rule 7 re-vectoring, per seat, delegated to subagents

VoltusWave carries **ten bullets** and must come down to six or seven for the three-page limit —
a *different* four dropped for each seat.

| Seat | Lead with | Cut |
|---|---|---|
| **AI-Native** | Elasticsearch `dense_vector` retrieval · the LangGraph orchestrator · self-hosted models in-VPC | Kinesis shards, Datadog, patient onboarding |
| **Yes Madam** | Java + Spring Boot · monolith → 10–15 services · Keycloak → Red Hat SSO · the Go concurrency work | most of the Amura AI bullets |
| **o9** | data-engineering depth — event spine, Parquet/DuckDB, nine-year hydration — plus SageMaker retraining and drift | the chat-platform bullets |

Then, per workspace:
```
automation/.venv/bin/python automation/resume.py sheet --slug <slug>
UPGRAD_HEADLESS=1 automation/.venv/bin/python automation/upgrad_apply.py \
    --slug <slug> --no-pause --reset
```
The exporter runs serially on one shared browser. It is unblocked and proven end to end.

### Starting a new seat
```
automation/.venv/bin/python automation/resume.py new --slug <slug> --company X --role Y
```
Then delegate the whole build — jd.md included. **Nothing has been SENT yet.**

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

## ⛔ Gap prep is STOPPED — do not rebuild it unprompted

Killed by him 2026-08-25: **"DO NOT build the prep now… we wait until I hear back from the
company."** Correct, and it is the v1 lesson repeating — preparing for rooms he has not been
invited to is the same failure as building workspaces he does not send. **Nothing has been
submitted yet.**

**The trigger is a company responding.** Not a score, not a workspace being ready, not a hunch.
When one replies, build the prep for THAT seat's gaps, not for all seven at once.

The stopped run is `wf_58f6f5c4-caa` and is resumable with `resumeFromRunId` — completed agents
replay from cache, so nothing is wasted if it is picked up later. The gap analysis itself is
already banked in the three `score.json` files; only the prep *page* was deferred.

**The seven gaps, ranked by how certain the question is** (from the rubrics, kept here so the
analysis is not lost):

1. **Graph neural network** — highest risk in his whole profile. Real and confirmed, sits in
   word-position four of his headline, and appears **zero times across all 22 case-study files**.
   A headline claim with no artefact to rehearse from. Only he can supply the node/edge schema,
   the task, the framework, the training data and how it was served.
2. **Kubernetes** — absent from the master, but **his live card claims it**. Needs his answer.
3. **Spring Boot 3 / Java 21** — never shipped, not rusty. Concurrency proof is Go.
4. **Grafana / Prometheus** — absent. Datadog and ELK transfer conceptually; PromQL does not.
5. **Deep-learning years** — ~14 months applied against o9's "5+ years".
6. **Model registry, Spark** — retraining and drift ARE evidenced; a registry is never named.
7. **Vector DB internals** — ramp item. His read stands; see above.

**The graph neural network is first and is the highest-risk item in his whole profile** — he
confirmed it is real, it sits in word-position four of his headline, and the phrase appears **zero
times across all 22 case-study files** because it attaches to the Context Graph, which those ten
killer queries do not document. A headline claim with no artefact to rehearse from. Only he can
fill in the node/edge schema, the task, the framework, the training data and how it was served.
