# Finishing the story-clusters résumé: your answers

**File being finished:** `master/Abhisheik_Deo_Resume_story_clusters.docx`, built from the database as
`variant:story-clusters`. **Full evidence** for every question: `master/story-clusters-review.html`.
"Journey 88" means line 88 of `professional-journey.md`.

**How to fill this in**

- Write under each **Your answer:** line. One short line is enough.
- "I don't know" or "not sure" is a perfectly good answer. Anything you are not sure of stays off
  the résumé; nothing gets guessed.
- No new outcome numbers are asked for here. The questions only check the numbers and claims that
  are already on the résumé.
- Part 1 and Part 2 are needed before this résumé can become the master. Part 3 only makes the
  stories richer, so skip it if you are short of time.

---

## Part 1. Must answer (these change what the résumé claims)

### 1. The killer-query AI work: pilot or production?
Journey 88 says the work was "piloted to doctors and sales". The case studies say "Live in production". The draft says "production".
Which is right: piloted, in production, or piloted first and then in production?

**Your answer:**
- Production.
- I don't have the numbers since it's been running after I left the organization

### 2. Amazon Neptune per tenant
The master says the healthcare data tier had a separate Amazon Neptune (graph database) per tenant (per customer). No case study mentions this, so the draft removes it.
Was there really a separate Neptune per tenant? (If yes, it goes back in.)

**Your answer:**
- hybrid approach
- for certain tenants, we used separate Amazon Neptune but for others, we used the shared database

### 3. The infrastructure figures: where do they come from?
The master says 70% of the servers ran on AWS Spot (Amazon's cheaper, interruptible servers), deploys took under 10 minutes, and costs dropped 
25–30%. The journey records none of these three. 
What is the source of each one? Should any of them be removed?

**Your answer:**

- I measured ALL of these myself.

### 4. The "5 sub-teams" adoption figure
The master mentions an adoption figure across 5 sub-teams. The journey records 6 sub-teams (journey 104) and no adoption figure.
Where does the "5 sub-teams" figure come from?

**Your answer:**
- The "5 sub-teams" figure comes from the master résumé which is incorrect. It should be "6 sub-teams".

### 5. The React Native apps and the 10,000+ patients
The draft puts two facts in one bullet: you published React Native apps, and 10,000+ patients moved onto "our app" (journey 628, 659).
Were the React Native apps the same app the patients moved to? (If not, the draft splits them.)

**Your answer:**

- that's correct


### 6. The statistics tests: how many pipelines?
The master says "across 6 production pipelines" for the bootstrap resampling and the Rosenbaum γ and E-value sensitivity tests. The case studies  
show the sensitivity tests only in KQ6. Does "6 pipelines" cover the whole set of tests, or only the bootstrap?

**Your answer:**

- The whole set of tests

### 7. Deque databases: one migration or two?
Journey 606 describes a move to Amazon RDS (Relational Database Service): backups took 3–4 hours and deploy errors were 40%. Separately, 
axe Auditor moved from PostgreSQL 9.6 to Aurora 13.x.
Was the RDS move the same migration as the Aurora upgrade, or a separate one? Which product was it for?

**Your answer:**

there were actually two moves:

1. PostgreSQL 9.6 to Amazon RDS 13.x
2. Amazon RDS 13.x to Aurora

### 8. Teletext: how many suppliers?
The résumé says 25 hotel suppliers. Journey 415 says 25–30.
Which should it say?

**Your answer:**

- ~30

### 9. Teletext: the 46%
Does the 46% belong to replacing Artirix (the outside pricing service)? Does it match the public figure of about $1.4M a year? (journey 431)

**Your answer:**

- where's this public figure of $1.4M a year at?

### 10. Teletext: the 8% month over month
Was the 8% month-over-month revenue growth kept up over time, or was it a one-time lift? (journey 452)

**Your answer:**

- over my time period there

The entire situation:

- a user fires a search for both flights & hotels on a particular destination
- we then use the scatter-gather to call specific supplier endpoints
- the suppliers then returned hotels 
- if the returned hotel wasn't mapped with Teletext, we couldn't show that hotel even though that supplier/hotel combination is the lowest/best rate
- improving this mapping helped us increase our sales
- AND this is a continuous effort. We sent out an email to the supplier to also correct mapping on their end.

### 11. Teletext: the 65% conversion lift
Which work does the 65% conversion lift belong to: the GIATA hotel-identity reconciliation, the direct-contract ranking, or both? (journey 450, 454)

**Your answer:**

- This 65% was related to the above part.

### 12. innRoad: AngularJS or Knockout.js?
The master says AngularJS. The journey says Knockout.js and marks it open (journey 364).
Which framework was it?

**Your answer:**

- POC was knockout.js
- production we sent out AngularJS

---

## Part 2. Keep or cut (the 12 open claims)

For each claim, write **Keep**, **Cut** or **Change to: …**. Add a note if you like. Nothing here is decided without you.

### 13. Graph neural network (GNN)
The Context Graph bullet says "Context Graph on Amazon Neptune with graph neural network (GNN) models". The headline says "Graph + GNN" and the 
summary says "a graph neural network (GNN) context graph". (journey 682)
Was the GNN ever trained and served, or was it still in training?


**Keep / Cut / Change to:**
**Note:**

**My Answer:** It was trained & served for patients who were identified as low/medium risk. 

### 14. "100,000 concurrent connections at P95 under 16 ms"
This is in the Spearheaded bullet (P95 means 95 out of 100 requests were at least this fast). 

**Heads-up:** your interview-prep notes say "P95 16 ms" is "not true of any run". In `img.png`, one run at 100,000 shows P95 19.05 ms.

**Keep / Cut / Change to:**
**Note:**
**My Answer:** p95 is under 16 ms

### 15. "P95 under 30 ms at 100,000-user load" (the data-layer bullet)
The master attaches this to PostgreSQL. Your prep notes say the figure belongs to the DynamoDB write path.
Which database does it belong to, and should the 100,000 stay?

**Keep / Cut / Change to:**
**Note:**
**My Answer:** p95 is under 16 ms for DynamoDB write paths

### 16. Kubernetes
You confirmed Kubernetes in August 2026. Your interview-prep notes list it as "never claim" and say the code shows AWS ECS Fargate (Amazon's own container service). It appears in the Provisioned bullet, the headline and the summary.

**Keep / Cut / Change to:**
**Note:**
**My Answer:** Kubernetes was confirmed in August 2026, but the code shows AWS ECS Fargate.

### 17. Kinesis "4 to 1,200 shards"
Was this a shard count you set yourself, or Kinesis on-demand mode scaling automatically?

**Keep / Cut / Change to:**
**Note:**
**My Answer:** on-demand scale automatically. During load tests, it moved to ~1,200 shards. I did not capture the results though.

### 18. LLM (large language model) narrative guardrails
The bullet says the guardrails were "designed to reject 100% of uncited claims". It does not say they ran in production. The case-study index 
marks the shared contract as pending (journey 684).
Did they ship?

**Keep / Cut / Change to:**
**Note:**
**My Answer:** production

### 19. Deque: "Steered 70–80% of customers onto shared axe Monitor instances"
**Heads-up:** on 14 September 2026 your interview-prep notes recorded this as never yours ("No idea about this 70%-80% consolidated"). The draft  
still carries it word for word. (journey 604)

**Keep / Cut / Change to:**
**Note:**
**My Answer:** 70–80% of customers were steered onto shared axe Monitor instances.

### 20. Rocket: "Coached a 5-engineer team…"
One of the four Rocket numbers (journey 492, 503).

**Keep / Cut / Change to:**
**Note:** that's correct.

### 21. Rocket: "reducing reported bugs over 50%"
One of the four Rocket numbers (journey 493).

**Keep / Cut / Change to:**
**Note:** that's correct

### 22. Rocket: "raising sales over 20%"
One of the four Rocket numbers (journey 495). The fourth, "adoption +20%", is not on the résumé and was not added.

**Keep / Cut / Change to:**
**Note:** Keep

### 23. VoltusWave: "cutting errors to under 3%"
Journey 216 and 658 record it, although the working rules say you have no VoltusWave outcome numbers.

**Keep / Cut / Change to:**
**Note:** Keep

### 24. HIPAA wording, and failover and disaster recovery
The summary now says HIPAA "compliance", not "certification", because HIPAA (the US health-privacy law) has no formal certification. The multi-availability-zone failover and disaster recovery come from your August 2026 confirmations, not from the journey.

**Keep / Cut / Change to:**
**Note:** Keep

---

## Part 3. Nice to have (these make the stories richer; skip any)

Each one asks for the business reason or the user, never a new number.

### 25. VoltusWave team building
What business need drove hiring from 0 to 20+ across 6 sub-teams, and standardizing on Go and DynamoDB?

**Your answer:** that's correct.

### 26. Claude Code and OpenAI Codex rollout
What process did it replace or improve? What changed for the team afterwards? (No numbers needed; journey 672.)

**Your answer:** 

- we used to take a lot of time to onboard new developers, QA team, product team, etc
- Claude & Codex bought a certain set of standards across the team by using "CLAUDE.md" & "AGENTS.md" files across the repositories

### 27. Deque, axe Monitor consolidation
How was each customer's customization handled on the shared database? Was "customer-specific front ends on one backend" the real mechanism? 
(journey 602)

**Your answer:**

- this was done in rarest of rare cases
- DO NOT remember it 100% but if I remember it correctly, we had a "custom_fields" table which had "tenant_id", "table_name", etc which helped in 
  customization

### 28. Deque, billing
Why was billing and subscription moved from Node.js/TypeScript to Java and Spring Boot? (journey 576)

**Your answer:**

- better debugging. 
- more tools. 
- the company was more comfortable with Java/Spring Boot

### 29. Deque, choosing Aurora
What drove the choice of Aurora? (journey 606)

**Your answer:**

- Infinite scaling capability
- If I remember correctly, we got a deal from AWS for Aurora. BUT I may be wrong here.

### 30. Deque, release pipeline
What problem drove the move from Jenkins to GitHub Actions and the ISO 27001 (security standard) work? Who used the Puppeteer regression suite?

**Your answer:**

- Jenkins was painful when we scaled. That scaling took place when we used Claude for our development
- The Jenkins pipeline was failing , jobs were pending, etc
- GHA scaled automatically & it worked out well for us.

### 31. Deque, axe DevTools
How did phase 1 of the cross-origin iframe work get past the browser's security model, and did it reach users? (journey 561)

**Your answer:**

- DO NOT remember this

### 32. Rocket
Why decompose Configuration Manager? How many services came out, and how were the boundaries drawn? Did the new services reach customers before the product and team were dissolved? (journey 505, 50)

**Your answer:**

- DO NOT remember this

### 33. VoltusWave co-founder years
What was the no-code aPaaS (application platform as a service) for? Who were the 8 early enterprise clients, or at least what did they build with it? (journey 472)

**Your answer:**

- No Code Platform
- The clients build Leave Management System, etc
- Apart from this, I do not remember much

### 34. CURA
Was the Node.js piece a rewrite or a port of the existing product? (journey 389)

**Your answer:**

- It was a LITE version of the existing product to increase sales

### 35. innRoad
Who used the application, for example hotel property staff? (journey 364)

**Your answer:**

- we sold this to motels across US / Canada and charged them per room

### 36. McDonald's
How many stores and employee records were involved? Did the MDM (master data management) work go beyond the 2-country pilot? Did the field-level  
history ship, did leadership use it, and were there more timestamps than "first seen" and "last updated"? (journey 344, 346)

**Your answer:**

- When I was there, we started getting requirements for EU (Germany) & China.
- Design was ongoing and some dev had started. BUT not beyond this

### 37. El Paso
Which of Nominations, Flowing Gas and Contracts did you own? Who used the rewritten application: shippers or internal schedulers? (journey 324, 326)

**Your answer:**

- I worked on ALL these depending on the requirements

### 38. LyntonWeb
Is Paymaster the same thing as the Mexican PayPal payments piece? Did suppliers and buyers actually move onto the portal? (journey 287)

**Your answer:**

- Paymaster was indeed the Mexican PayPal payments piece
- Suppliers and buyers did move onto the portal

---

## When you are done

Tell me "answers are in". I will then:

1. apply your answers to the draft only (the current master stays untouched until the switch);
2. put back the 6 dropped keywords: Aggregation, Mining, Sequence, Traversal, P99, URLs;
3. re-run the bullet rules, the 35 format checks and the keyword check;
4. make it the master, keeping a copy of today's master. Sent résumés stay frozen; Lilly's unsent résumé gets rebuilt.

Then you check the page count in Word.
