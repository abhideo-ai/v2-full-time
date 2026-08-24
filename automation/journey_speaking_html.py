#!/usr/bin/env python3
"""Author professional-journey.html — the RECALL BOARD.

This is NOT a rendering of professional-journey.md. That was tried and it
produced junk: raw notes, half-stripped sections, client internals and
working commentary all leaking into a page meant for a live interview.

The markdown is the record. This page is the instrument: what to SAY,
keyed by what gets ASKED, answer first. It exists because on 17 Aug 2026
he lost a round not on knowledge but on retrieval -- asked for his total
Java experience he gave three date ranges and no number, and time ran out.

Content here is authored deliberately and every line is sayable out loud.
Nothing internal appears: no open questions, no resume conflicts, no client
system internals, no notes addressed to the file.

    python3 automation/journey_speaking_html.py
"""
import html as H
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "professional-journey.html"

# ── The recall board: what gets asked -> what he says ────────────────────
ASKS = [
    ("★", "What's your total Java experience?",
     "About eleven years, across three eras — El Paso 2008 to 2012, Rocket 2018 to 19, "
     "and Deque from December 2019 through February 2025. So the most recent is February last year.",
     ["El Paso — Java running under Citrix, rewritten to JSP and J2EE",
      "Rocket — first monolith broken into Java and Spring Boot microservices",
      "Deque — Spring Boot 2.x on Java 8/17, five years, multi-tenant platform"],
     "Say the number first. Three date ranges without a total makes the interviewer do arithmetic, and they won't."),

    ("★", "Tell me about your microservices experience.",
     "Two, and the second is the more interesting one. At Rocket I broke a Db2 tooling monolith into "
     "Java and Spring Boot services without customers seeing it. At Deque I built the cross-product "
     "platform services — authentication, billing and subscription, global configuration — that every "
     "product in the portfolio runs on.",
     ["Ten to fifteen services by the time I left Deque, starting from a monolith",
      "Rule for what earns its own service: it scales independently, or it owns its own data",
      "Auth was Java and Spring Boot; billing started in Node and TypeScript and we moved it to Java"],
     "\"We split a monolith\" is the common answer. \"I built the services every product authenticates and bills through\" is the platform-architect answer."),

    ("★", "How did you implement multi-tenancy at the database level?",
     "Organisation identifier on every table, tenant resolved from the token on every request — so there "
     "is exactly one code path. The banks that refused shared infrastructure kept their own database "
     "against that same code.",
     ["Two options weighed: database per customer, or a tenant column filtered on every query",
      "That split is a deployment difference, not a second codebase — holding that line kept it maintainable",
      "Isolation enforced by review plus automated tests; a cross-organisation leak is a compliance failure, not a bug"],
     "At CBRE the interviewer heard this as two implementations. Say \"one codebase, two deployment shapes\" early."),

    ("★", "One customer wants a custom field and the schema is shared. How?",
     "Additive only — a new column populated for that organisation and left null for the others, never "
     "changing or removing an existing one. Where the data was transactional we gave them a separate "
     "table so the values could be non-null. And we worked hard to avoid the situation in the first place.",
     ["The design position: per-tenant schema drift is what makes a shared platform unmaintainable",
      "Customer-specific frontends against one shared backend absorbed most customisation requests",
      "Give the principle first, then what actually shipped"],
     "This is the question that decided the CBRE round. Answer it in three sentences, then stop and let them push."),

    ("", "Walk me through the most complex system you've designed.",
     "A chat-based care platform where a single patient message fanned out into about fifty downstream "
     "calls. I rewrote the core service from Node.js to Go, and proved a hundred thousand concurrent "
     "connections in a burst test.",
     ["Fifty calls per message: the datastore write, membership lookup, per-member unread state, notification fan-out across every open tab and device",
      "Then a two-stream design for headroom against a real spike",
      "Observability first — Datadog — because nobody could tell me what was actually breaking"],
     "Open with the fifty-calls line. It states the problem in nine words and every follow-up writes itself."),

    ("", "What have you done with AI in production?",
     "We defined what we called killer queries with the client's chief executive — the questions that, if "
     "we could answer them properly, meant the AI was real rather than a demo. The first: a doctor on a "
     "call asks whether we've treated someone like this patient before, what protocol we followed, and "
     "what the outcome was.",
     ["An event spine projected through Lambda into Amazon Neptune",
      "Dense vectors and a retrieval pipeline, put in front of real clinicians",
      "Python — FastAPI, LangChain, LangGraph"],
     "Lead with the query, not the stack. The query is what shows you started from the business."),

    ("", "How are you using AI in how the team works?",
     "I embedded Claude Code and OpenAI Codex across the engineering team — daily architectural "
     "exploration, first-cut implementations and test scaffolding, all under hands-on review.",
     ["Agent proposes, human reviews — that is the boundary I have actually operated",
      "It changed what the team spent its time on, not how many people we needed"],
     "You named this at CBRE, said \"I'll elaborate on that\", and then never did. Either tell it or leave it out."),

    ("", "Are you still hands-on?",
     "Yes. I'm the go-to for proof-of-concepts, and I've never been the architect who draws diagrams "
     "without knowing the codebase. That was a deliberate choice early and it has held for nineteen years.",
     [], ""),

    ("", "What's the largest scale you've worked at?",
     "Two different shapes. At Teletext we served two to three million requests a day on the holiday "
     "search path. At VoltusWave I proved a hundred thousand concurrent connections in a burst test on "
     "the chat service.",
     ["Teletext: an Elasticsearch cache with a twenty-minute TTL in front of twenty-five to thirty suppliers",
      "VoltusWave: Go rewrite, then a two-stream architecture on Kinesis"],
     "Say \"burst test\" — it is accurate, and it survives the follow-up that \"sustained\" would not."),

    ("", "Tell me about your team leadership.",
     "Three times. I built VoltusWave's engineering team from zero to thirty-five as co-founder in 2017. "
     "At Rocket I supervised five engineers including their appraisals. And in the recent VoltusWave "
     "stint I grew the org from zero to twenty-plus across six sub-teams.",
     ["Six sub-teams: backend, React Native, web, AI, quality assurance and DevOps",
      "The two zero-to-N numbers are different teams eight years apart — always say which is which"], ""),

    ("", "Why so many companies?",
     "From 2013 to 2018 I was with the same leader across four of them — innRoad, Cura, Teletext, then "
     "co-founding VoltusWave together. It reads as four moves. It was one working relationship.",
     [], "Say it plainly and move on. It is the single best answer you have and it takes one sentence."),

    ("", "Why are you available now?",
     "VoltusWave and the client hit cash-flow problems — April and May went unpaid. So I'm available "
     "immediately, and I'm looking for something permanent.",
     [], "No apology, no elaboration. Then stop talking."),

    ("", "You've been a VP. Why an architect seat?",
     "Because the architect seat is the one I actually want. I've run the organisation, and I'd rather "
     "own the design and stay in the code.",
     [], ""),
]

# ── Every metric he can defend, in one place ─────────────────────────────
NUMBERS = [
    ("19+ years", "Apr 2007 → Apr 2026", ""),
    ("~11 years", "Java, across three eras", "most recent Feb 2025"),
    ("~300", "enterprise customers on axe Monitor", "each its own instance, version and Keycloak"),
    ("10–15", "services at Deque by the time he left", "from a monolith"),
    ("50", "downstream calls per chat message", "code-verified at 48–58"),
    ("100,000", "concurrent connections", "proved in a burst test"),
    ("under 3%", "production error rate after observability", "VoltusWave"),
    ("10,000+", "patients onboarded onto the platform", "off a third-party messaging product"),
    ("2–3 million", "requests per day at peak", "Teletext holiday search"),
    ("46%", "operational cost reduction", "replacing a third-party search provider with in-house Elasticsearch"),
    ("25–30", "hotel suppliers integrated", "MuleSoft scatter-gather"),
    ("12", "new customers in two months", "Cura, after the Linux deployment path"),
    ("8", "early enterprise clients", "VoltusWave first stint"),
    ("0 → 35", "engineers, VoltusWave 2017–18", "as co-founder"),
    ("0 → 20+", "engineers across 6 sub-teams, 2025–26", ""),
    ("5", "engineers supervised at Rocket", "including appraisals"),
    ("60–70%", "faster screen load times", "innRoad re-architecture"),
    ("~11,800 miles", "Tennessee Gas Pipeline, Gulf Coast to Northeast", "El Paso"),
]

# ── One card per role: what it was, what he did, why it ended ────────────
ROLES = [
    ("VoltusWave Technologies", "Principal Software Architect", "Mar 2025 – Apr 2026", "Hyderabad",
     "A chat-based healthcare platform, embedded with a client in Chennai. The business wanted AI in the "
     "product to raise investment — which needed patients, which needed reliability, which needed someone "
     "to find out what was actually broken.",
     ["Rewrote the core chat service from Node.js to Go; 100,000 concurrent connections proved under burst",
      "Designed a two-stream architecture on Kinesis for headroom",
      "Datadog in first — production errors under 3%",
      "Killer-query AI programme: event spine → Lambda → Amazon Neptune, dense vectors, retrieval, in front of clinicians",
      "Embedded Claude Code and OpenAI Codex across the engineering team",
      "Grew engineering 0 → 20+ across six sub-teams"],
     "Cash-flow problems at VoltusWave and the client. April and May went unpaid."),

    ("Deque Software", "Lead SDE / Senior Staff Engineer", "Dec 2019 – Feb 2025", "Hyderabad",
     "Accessibility testing software. The flagship, axe Monitor, crawls an enterprise's whole web estate "
     "and reports where it fails accessibility standards. Around 300 enterprise customers — each on their "
     "own instance, own database, own Keycloak, own version.",
     ["Consolidated them onto a shared multi-tenant platform on Spring Boot and Java 8/17",
      "Organisation ID on every table, tenant from the token, one code path; banks kept dedicated databases",
      "Built the cross-product services: authentication, billing and subscription, global configuration",
      "Migrated every customer off local Keycloak to central Red Hat single sign-on with zero end-user disruption",
      "OpenID Connect and OAuth 2.0 across realms, clients, roles and groups",
      "PostgreSQL 9.6 → Aurora 13.x across every instance, no downtime",
      "axe DevTools: finding violations inside cross-origin iframes"],
     ""),

    ("Rocket Software", "Software Engineer III", "Aug 2018 – Jul 2019", "Bangalore",
     "IBM Db2 Configuration Manager for z/OS — a web tool built on IBM Data Server Manager, for managing "
     "Db2 database and client configuration across mainframe and the Linux, UNIX and Windows platforms.",
     ["First monolith-to-microservices decomposition — Java and Spring Boot, no customer-visible impact",
      "Reported bugs down over 50%",
      "Product adoption up over 20% through REST APIs",
      "Supervised five engineers including performance appraisals"],
     "The product and the team were dissolved in Bangalore and we weren't absorbed."),

    ("VoltusWave Technologies", "Co-Founder & VP of Technology", "Mar 2017 – Apr 2018", "Hyderabad",
     "Co-founded the company and built its first application platform-as-a-service product for web and "
     "Android from nothing.",
     ["Engineering team 0 → 35 in thirteen months",
      "End-to-end delivery on AWS Elastic Container Service",
      "Eight early enterprise clients",
      "Set the architectural roadmap the later products were built from"],
     ""),

    ("Teletext India", "Senior Software Engineer", "Mar 2016 – Mar 2017", "Hyderabad",
     "Holiday search and booking. Sales reps had to check twenty-five to thirty suppliers by hand to quote "
     "a customer, on a .NET 2.0 system a previous team had failed to modernise. Pricing itself came from a "
     "third party who charged by load.",
     ["MuleSoft Anypoint scatter-gather to call all suppliers in parallel",
      "Replaced the third-party pricing service with an in-house Elasticsearch tier, 20-minute TTL — costs down 46%",
      "2–3 million requests a day at peak",
      "Licensed GIATA MultiCodes to map supplier hotel codes onto our own records, and automated the reconciliation pipeline on AWS Lambda \u2014 approval stayed in-house"],
     ""),

    ("CURA Software Solutions", "Technical Architect", "May 2015 – Nov 2015", "Hyderabad",
     "A governance, risk and compliance platform. Windows Server and SQL Server licence costs were losing "
     "deals before the software was even evaluated.",
     ["Built a Linux deployment path on Node and MySQL for new enterprise customers",
      "Twelve new customers in two months"],
     "The building was sealed and the office closed. It was decided for me."),

    ("innRoad", "Technical Lead", "Jul 2013 – May 2015", "Hyderabad",
     "Hotel management software. A legacy ASP.NET product that reloaded the page for every interaction.",
     ["Modernised it into a single-page application against a WCF backend",
      "Screen load times improved 60–70%",
      "Stored procedure, indexing and table design work underneath it"],
     ""),

    ("McDonald's Corporation", "Software Architect", "Jun 2012 – May 2013", "Oak Brook, IL",
     "Master data management. Leadership had no single view of employee data across the stores; the North "
     "America pilot covered the US and Canada.",
     ["Modelled the schema and the governance framework",
      "Rebuilt the interface so leadership could actually read the records — drill-down, row-level editing",
      "Field-level lineage: when each value was first seen and last changed. In 2012, before anyone called it data provenance"],
     ""),

    ("El Paso Corporation", "Senior Java Developer", "Apr 2008 – May 2012", "Houston, TX",
     "The Tennessee Gas Pipeline systems — roughly 11,800 miles from the Gulf Coast to the Northeast. "
     "Nominations, flowing gas and contracts: the transactional core of scheduling gas across an "
     "interstate network, under federal deadlines.",
     ["Took a Java application running inside Citrix out to JSP and J2EE on the web",
      "SQL Server 2000 → 2005 migration",
      "Stored procedure optimisation and database design"],
     "Kinder Morgan closed its acquisition of El Paso in May 2012 and the organisation changed shape."),

    ("LyntonWeb", ".NET Developer", "Apr 2007 – Apr 2008", "Houston, TX",
     "A portal connecting suppliers and buyers, with a payments application for a Mexican financial "
     "institution.",
     ["Built the payments product on .NET and SQL Server 2005",
      "A Windows service that picked up invoices from a watched folder and pushed them to the portal"],
     ""),
]


def esc(t):
    return H.escape(t, quote=False)


def render_asks():
    out = []
    for star, q, say, depth, note in ASKS:
        cls = "rb-ask rb-star" if star else "rb-ask"
        out.append('<article class="%s">' % cls)
        out.append('<h3 class="rb-q">%s%s</h3>' % (
            '<span class="rb-pin" aria-hidden="true">★</span> ' if star else "", esc(q)))
        out.append('<p class="rb-say"><span class="rb-lbl">Say</span>%s</p>' % esc(say))
        if depth:
            out.append('<div class="rb-depth"><span class="rb-lbl">Hold in reserve</span><ul>%s</ul></div>'
                       % "".join("<li>%s</li>" % esc(d) for d in depth))
        if note:
            out.append('<p class="rb-note">%s</p>' % esc(note))
        out.append("</article>")
    return "\n".join(out)


def render_numbers():
    rows = "".join(
        '<tr><td class="rb-fig">%s</td><td>%s</td><td class="rb-qual">%s</td></tr>'
        % (esc(f), esc(w), esc(q)) for f, w, q in NUMBERS)
    return '<table class="rb-numbers"><tbody>%s</tbody></table>' % rows


def render_roles():
    out = []
    for co, title, dates, loc, what, did, left in ROLES:
        out.append('<article class="rb-role">')
        out.append('<h3>%s <span class="rb-role-title">%s</span></h3>' % (esc(co), esc(title)))
        out.append('<p class="rb-meta">%s &middot; %s</p>' % (esc(dates), esc(loc)))
        out.append('<p class="rb-what">%s</p>' % esc(what))
        out.append("<ul>%s</ul>" % "".join("<li>%s</li>" % esc(d) for d in did))
        if left:
            out.append('<p class="rb-left"><span class="rb-lbl">Why it ended</span>%s</p>' % esc(left))
        out.append("</article>")
    return "\n".join(out)


page = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Recall board — what to say</title>
  <link rel="icon" type="image/svg+xml" href="./static/favicon.svg" />
  <link rel="stylesheet" href="./style.css" />
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>

<nav class="toolbar no-print" aria-label="Primary">
  <span class="breadcrumb" aria-label="Breadcrumb">
    <a href="./index.html">Full-time v1</a>
    <span class="sep">/</span>
    <strong aria-current="page">Recall board</strong>
  </span>
  <span class="spacer"></span>
  <a class="button" href="./professional-journey-narration.html">Narration</a>
  <a class="button" href="./master/">Master resume</a>
  <a class="button" href="./professional-journey.md">Full record</a>
</nav>

<main class="page" id="main">
  <header>
    <h1>Recall board</h1>
    <p class="pj-lede">Open this during the call. Questions on the left of your attention, the answer to say
    first, and the depth held in reserve for the follow-up. <strong>Answer, then stop</strong> &mdash; let them
    choose how deep to go.</p>
    <p class="pj-stats">
      <span class="pj-stat"><strong>19+</strong> years</span>
      <span class="pj-stat"><strong>~11</strong> years Java</span>
      <span class="pj-stat"><strong>10</strong> roles</span>
      <span class="pj-stat pj-stat-default"><strong>Available</strong> immediately</span>
    </p>
    <p class="rb-jump no-print">
      <a href="#asks">Ask &rarr; Say</a> &middot;
      <a href="#numbers">The numbers</a> &middot;
      <a href="#roles">Role cards</a> &middot;
      <a href="./professional-journey-narration.html">Narration &rarr;</a>
    </p>
  </header>

  <section id="asks">
    <h2>Ask &rarr; Say</h2>
    <p class="rb-sub">The starred four are the ones that decide architect rounds.</p>
%(asks)s
  </section>

  <section id="numbers">
    <h2>The numbers</h2>
    <p class="rb-sub">Every figure here is defensible. If it is not on this list, do not put a number on it.</p>
%(numbers)s
  </section>

  <section id="roles">
    <h2>Role cards</h2>
    <p class="rb-sub">Most recent first &mdash; the order you should talk in.</p>
%(roles)s
  </section>
</main>
</body>
</html>
""" % {"asks": render_asks(), "numbers": render_numbers(), "roles": render_roles()}

OUT.write_text(page, encoding="utf-8")
print("wrote %s (%d bytes) — %d asks, %d numbers, %d role cards"
      % (OUT.name, len(page), len(ASKS), len(NUMBERS), len(ROLES)))
