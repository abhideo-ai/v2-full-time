#!/usr/bin/env python3
"""Hygiene gate for master/upgrad_resume.html.

Every rule in CLAUDE.md's "Resume hygiene" section, measured the way that section
says to measure it -- notably: a word counter must ignore punctuation tokens, and
same-root verb collisions must be checked across ALL ten roles plus mid-bullet text.

Usage: python3 automation/hygiene_check.py [path]
Exit 0 = clean, 1 = failures.
"""
import re, sys, html, collections

PATH = sys.argv[1] if len(sys.argv) > 1 else 'master/upgrad_resume.html'

EXPERIENCE_IDS = ['quick-vp', 'quick-deque', 'quick-rocket',
                  'quick-voltuswave-cofounder', 'quick-teletext',
                  'p-cura', 'p-innroad', 'p-mcd', 'p-elpaso', 'p-lynton']
PARSED_IDS = ['quick-headline', 'quick-summary', 'quick-skills-tls',
              'quick-skills-ee', 'quick-skills-bd'] + EXPERIENCE_IDS[:5]

BANNED_OPENERS = {'managed', 'replaced', 'responsible', 'worked', 'helped'}

def strip(h):
    return html.unescape(re.sub(r'<[^>]+>', '', h)).strip()

def words(t):
    """CLAUDE.md: count only tokens containing [A-Za-z0-9]. An em-dash is not a word."""
    return [w for w in re.split(r'\s+', t) if re.search(r'[A-Za-z0-9]', w)]

def sections(src):
    out = collections.OrderedDict()
    for m in re.finditer(r'<div class="section[^"]*" id="([a-z0-9_-]+)"(.*?)(?=<div class="section|</main>|\Z)',
                         src, re.S):
        sid, body = m.group(1), m.group(2)
        # headings sit before their div, so a trailing <h3> belongs to the NEXT section
        body = re.sub(r'<h[23][^>]*>.*?</h[23]>\s*$', '', body, flags=re.S)
        items = re.findall(r'<li[^>]*>(.*?)</li>', body, re.S) or \
                re.findall(r'<p[^>]*>(.*?)</p>', body, re.S)
        out[sid] = items
    return out

def stem(v):
    v = v.lower().rstrip(',')
    for suf in ('ised', 'ized', 'ed', 'd'):
        if v.endswith(suf) and len(v) - len(suf) >= 4:
            return v[:len(v) - len(suf)]
    return v


ACRO_RE = re.compile(r'\b(?:[A-Z]\.?){2,}[a-z]?(?:\.[A-Za-z]+)?\b|\b[A-Z][a-z]*[A-Z][A-Za-z]*\b')

def acronyms(text):
    """Initialisms only -- NOT CamelCase product names.

    The distinction matters: DynamoDB, PostgreSQL, GitHub, MuleSoft, LangChain,
    FastAPI, DuckDB and PayPal are product names a reader parses as words. ISO,
    JSON, JWT, SQL, MDM, WCF and RHEL are initialisms the ATS flags. A naive
    "2+ capitals" rule reports 40 acronyms where there are 7.

    Rule: strip separators; the remainder must be all-uppercase, optionally with
    one trailing lowercase plural 's' (URLs, APIs, APNs). A short allowlist
    covers the deliberately-lowercased forms.
    """
    ALLOW = {'z/OS', 'SaaS', 'aPaaS', 'CI/CD', 'AI/ML'}
    out = []
    for m in re.finditer(r'[A-Za-z][A-Za-z0-9./_]*', text):
        w = m.group(0).rstrip('.')
        if w in ALLOW:
            out.append(w)
            continue
        core = re.sub(r'[^A-Za-z]', '', w)
        if len(core) < 2:
            continue
        if core.endswith('s') and core[:-1].isupper() and len(core) > 2:
            out.append(w)                      # URLs, APIs, APNs
        elif core.isupper():
            out.append(w)                      # ISO, JSON, SQL, ASP.NET, .NET
    return out


def check_acronym_expansion(secs, order):
    """Reading order: headline -> summary -> skills -> experience.

    Reports (a) acronyms never expanded anywhere, and (b) acronyms whose bare
    first use PRECEDES their expansion -- the rule is expand on FIRST use.
    The headline is exempt: CLAUDE.md's tagline exception lets it stay bare
    provided the summary expands it immediately after.
    """
    # Universally understood, or product names that have no expansion. Neither
    # CLAUDE.md's list nor resume-issues-to-avoid asks for these.
    NO_EXPANSION_NEEDED = {'IBM', 'UNIX', 'SQL', 'MySQL', 'ID', 'NET', '.NET',
                           'ASP.NET', 'z/OS', 'OS', 'AA', 'III', 'PDF', 'HTML',
                           # components of proper standard names -- expanding
                           # "ISO 27001" or "JSON Web Token" reads worse than not
                           'ISO', 'JSON',
                           # brand names, not initialisms -- GIATA MultiCodes is a
                           # product the way Datadog or MuleSoft is
                           'GIATA'}
    def norm(a):
        """APIs and API are the same acronym; URLs and URL likewise."""
        return a[:-1] if (len(a) > 2 and a.endswith('s') and a[:-1].isupper()) else a

    never, wrong_order = [], []
    seen_bare = {}          # acronym -> first (position, section) used bare
    expanded_at = {}        # acronym -> position where "Expansion (ACRO)" appears
    pos = 0
    for sid in order:
        for item in secs.get(sid, []):
            t = strip(item)
            pos += 1
            # Form 1: "Master Data Management (MDM)" -- paren holds ONLY the acronym.
            for m in re.finditer(r'\(([A-Za-z0-9./]{2,})\)', t):
                for a in acronyms(m.group(1)):
                    expanded_at.setdefault(norm(a), (pos, sid))
            # Form 2: "MDM (Master Data Management)" -- acronym immediately before
            # a multi-word parenthetical.
            for m in re.finditer(r'\b([A-Za-z0-9./]{2,})\s*\(([^)]{6,})\)', t):
                if ' ' in m.group(2).strip():
                    for a in acronyms(m.group(1)):
                        expanded_at.setdefault(norm(a), (pos, sid))
            # Form 3: expansion immediately precedes a parenthetical that merely
            # CONTAINS the acronym -- "Command Query Responsibility Segregation
            # (CQRS, DynamoDB Single-Table, ...)". Confirmed by initials match.
            for m in re.finditer(r'([A-Za-z][A-Za-z\- ]{5,})\(([^)]*)\)', t):
                before = [w for w in re.findall(r"[A-Za-z][A-Za-z\-]*", m.group(1))]
                for a in acronyms(m.group(2)):
                    letters = [c for c in a if c.isalpha()]
                    if len(letters) >= 2 and len(before) >= len(letters):
                        tail = before[-len(letters):]
                        if all(w[0].lower() == c.lower() for w, c in zip(tail, letters)):
                            expanded_at.setdefault(norm(a), (pos, sid))
            # "ELK: Elasticsearch, Logstash, Kibana" -- gloss after a colon
            for m in re.finditer(r'\b([A-Z][A-Za-z/.]*)\s*:\s*[A-Z]', t):
                for a in acronyms(m.group(1)):
                    expanded_at.setdefault(norm(a), (pos, sid))
            for a in acronyms(t):
                if a in ('AND', 'THE', 'III', 'II', 'IV', 'AA', 'AAA'):
                    continue
                # bare = not immediately preceded by its expansion in this same item
                if f'({a})' in t:
                    continue
                seen_bare.setdefault(norm(a), (pos, sid))
    for a, (bpos, bsid) in sorted(seen_bare.items()):
        if a in NO_EXPANSION_NEEDED:
            continue
        if a not in expanded_at:
            never.append((a, bsid))
        else:
            epos, esid = expanded_at[a]
            if epos > bpos and bsid != 'quick-headline':
                wrong_order.append((a, bsid, esid))
    return never, wrong_order


def main():
    src = open(PATH).read()
    secs = sections(src)
    fails, warns = [], []

    missing = [i for i in PARSED_IDS if i not in secs]
    if missing:
        fails.append(f"PARSER CONTRACT: missing section id(s) {missing} -- these are silently skipped on export")

    bullets = []          # (sid, idx, raw, text)
    for sid in EXPERIENCE_IDS:
        for i, raw in enumerate(secs.get(sid, []), 1):
            bullets.append((sid, i, raw, strip(raw)))

    # ---- per-bullet rules -------------------------------------------------
    for sid, i, raw, t in bullets:
        w = words(t)
        tag = f"{sid}#{i}"
        if len(w) > 25:
            fails.append(f"{tag}: {len(w)} words (max 25) -- {t[:70]}...")
        if w and w[0].lower().rstrip(',') in BANNED_OPENERS:
            fails.append(f"{tag}: banned opener '{w[0]}'")
        # spelled-out numbers count -- 'ten production analytics services' HAS a number.
        NUMWORD = (r'\b(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|'
                   r'twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|'
                   r'dozen|single|every|all|zero|no\s|first|second|third)\b')
        has_digit = bool(re.search(r'\d|%', t))
        has_numword = bool(re.search(NUMWORD, t, re.I))
        # 'every'/'all' are soft quantifiers, not magnitudes. They satisfy CLAUDE.md's
        # "scale marker" wording but the ATS reference wants a measurable outcome, so
        # they earn a warning rather than a silent pass.
        soft_only = (not has_digit
                     and re.search(r'\b(every|all|no|zero)\b', t, re.I)
                     and not re.search(r'\b(one|two|three|four|five|six|seven|eight|nine|ten|'
                                       r'eleven|twelve|twenty|thirty|forty|fifty|hundred|thousand)\b', t, re.I))
        if not has_digit and not has_numword:
            fails.append(f"{tag}: no number, %, or scale marker -- {t[:70]}...")
        elif soft_only:
            warns.append(f"{tag}: only a soft quantifier ('every'/'all') -- no magnitude")
        if '<strong>' not in raw:
            fails.append(f"{tag}: no bolded fact")
        if t.endswith('.'):
            fails.append(f"{tag}: trailing period")
        if '[fill in metric]' in t:
            warns.append(f"{tag}: carries a [fill in metric] placeholder")

    # ---- leading-verb uniqueness across ALL ten roles ---------------------
    verbs = collections.defaultdict(list)
    for sid, i, raw, t in bullets:
        w = words(t)
        if w:
            verbs[w[0].rstrip(',')].append(f"{sid}#{i}")
    for v, where in sorted(verbs.items()):
        if len(where) > 1:
            fails.append(f"LEADING-VERB COLLISION '{v}': {where}")

    # ---- same-root collisions, including mid-bullet -----------------------
    by_stem = collections.defaultdict(set)
    for v in verbs:
        by_stem[stem(v)].add(v)
    for st, vs in sorted(by_stem.items()):
        if len(vs) > 1:
            fails.append(f"SAME-ROOT LEADING VERBS {sorted(vs)} (stem '{st}')")

    doc = strip(src).lower()
    for v in sorted(verbs):
        st = stem(v)
        hits = len(re.findall(r'\b' + re.escape(st), doc))
        if hits > len(verbs[v]):
            warns.append(f"stem '{st}' (verb {v}) appears {hits}x in the document vs {len(verbs[v])} as a leading verb -- check for a mid-bullet collision")


    # ---- resume-issues-to-avoid: at most ONE acronym per bullet -----------
    # "Per-bullet hygiene is evaluated independently... one acronym per bullet
    #  is the practical cap." The ATS rescans per bullet, so an acronym expanded
    #  in bullet 2 is still flagged in bullet 12.
    # Mixed-case acronyms count too -- SaaS, APNs, URLs, APIs, MySQL, ASP.NET were
    # all invisible to an [A-Z]{2,} pattern. Roman numerals and conformance levels
    # are NOT acronyms.
    NOT_ACRO = {'III', 'II', 'IV', 'AA', 'AAA', 'AND', 'THE', 'A', 'I'}
    for sid, i, raw, t in bullets:
        uniq = sorted({a for a in acronyms(t) if a not in NOT_ACRO})
        if len(uniq) > 1:
            fails.append(f"{sid}#{i}: {len(uniq)} acronyms {uniq} -- reference caps at 1 per bullet")

    # ---- resume-issues-to-avoid rule 10: every skills line needs bold ------
    for s_id in ['quick-skills-tls', 'quick-skills-ee', 'quick-skills-bd']:
        for i, raw in enumerate(secs.get(s_id, []), 1):
            if '<strong>' not in raw:
                fails.append(f"{s_id}#{i}: skills line has no bolded fact -- {strip(raw)[:60]}")

    # ---- resume-issues-to-avoid rule 7: power verbs on the prominent roles -
    POWER = {'established','built','launched','instituted','delivered','spearheaded',
             'drove','owned','architected','designed','scaled','engineered','implemented',
             'led','drove','secured','optimized','strengthened','improved','increased'}
    SAVE_FOR_OLDER = {'codified','productized','anchored','helmed','stewarded'}
    for sid in ['quick-vp', 'quick-deque']:
        for i, raw in enumerate(secs.get(sid, []), 1):
            w = words(strip(raw))
            if not w: continue
            v = w[0].lower().rstrip(',')
            if v in SAVE_FOR_OLDER:
                warns.append(f"{sid}#{i}: '{w[0]}' is an uncommon-fresh verb the ATS reference says to save for OLDER roles")

    # ---- banned technology ------------------------------------------------
    BANNED = ['Kafka', 'NATS', 'MongoDB', 'ClickHouse', 'Azure', 'Google Cloud',
              'SOC 2', 'Spring Cloud', 'Spring WebFlux', 'Spring Batch',
              'Grafana', 'Prometheus', 'Hazelcast', 'Ignite', 'Coherence']
    plain = strip(src)
    for b in BANNED:
        if re.search(r'\b' + re.escape(b) + r'\b', plain, re.I):
            fails.append(f"BANNED TECHNOLOGY present: '{b}'")
    if re.search(r'six\s+continuous\s+years', plain, re.I):
        fails.append("FALSE CLAIM: 'six continuous years' of Spring Boot -- there is a five-month gap")

    # ---- acronym expansion, in reading order ------------------------------
    READING_ORDER = ['quick-headline', 'quick-summary', 'quick-skills-tls',
                     'quick-skills-ee', 'quick-skills-bd'] + EXPERIENCE_IDS
    never, wrong_order = check_acronym_expansion(secs, READING_ORDER)
    for a, sid in never:
        fails.append(f"ACRONYM NEVER EXPANDED: '{a}' (first bare use in {sid})")
    for a, bsid, esid in wrong_order:
        fails.append(f"ACRONYM EXPANDED TOO LATE: '{a}' used bare in {bsid}, expanded in {esid}")

    # ---- the headline and summary are sections too ------------------------
    for sid in ['quick-headline', 'quick-summary']:
        for i, raw in enumerate(secs.get(sid, []), 1):
            t = strip(raw)
            if t.endswith('.') and sid == 'quick-headline':
                fails.append(f"{sid}: trailing period")
            if '<strong>' not in raw and sid == 'quick-summary':
                fails.append(f"{sid}: no bolded fact")
            if '<strong>' not in raw and sid == 'quick-headline':
                warns.append("quick-headline: no bolded fact (Hiration title field -- "
                             "bold may not render there, but nothing else checks this)")

    # ---- page budget ------------------------------------------------------
    chars = sum(len(t) for _, _, _, t in bullets)
    skills = sum(len(secs.get(s, [])) for s in ['quick-skills-tls', 'quick-skills-ee', 'quick-skills-bd'])

    print(f"{'='*68}\n  {PATH}\n{'='*68}")
    for sid in EXPERIENCE_IDS:
        print(f"  {sid:30} {len(secs.get(sid, [])):3} bullets")
    print(f"  {'skills items':30} {skills:3}")
    print(f"\n  experience bullets : {len(bullets)}")
    print(f"  distinct verbs     : {len(verbs)}")
    print(f"  bullet text        : {chars:,} chars")
    print(f"  BASELINE           : 39 bullets / 5,752 chars exported to 3 pages,")
    print(f"                       page 3 only 381 chars of ~5,200 -> ~4,800 chars headroom")
    margin = 4800 - (chars - 5752)
    print(f"  projected margin   : {margin:+,} chars  "
          f"({'likely fits' if margin > 0 else 'LIKELY SPILLS'}) "
          f"-- ESTIMATE from a hand-measured headroom constant, {abs(margin)/4800*100:.1f}% of budget.")
    print(f"  ** only the exported PDF settles 3 pages. This is not a pass. **")

    print(f"\n  FAILURES: {len(fails)}")
    for f in fails: print(f"    x {f}")
    print(f"\n  WARNINGS: {len(warns)}")
    for w in warns: print(f"    ! {w}")
    return 1 if fails else 0

if __name__ == '__main__':
    sys.exit(main())
