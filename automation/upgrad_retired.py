#!/usr/bin/env python3
"""The upGrad / Hiration path is RETIRED. This module makes that a hard stop.

⛔ HIS ACCESS TO UPGRAD WAS REVOKED ON 2026-08-27. The résumé builder, both
Hiration cards (`august_ic_master_resume`, `august_master_resume`) and every
credential in this directory are unreachable. Nothing here can succeed any more;
without this guard each script would fail somewhere deep in Playwright with a
timeout or a login error, and cost real time being diagnosed as a bug.

⛔ THE FILES STAY. He set that explicitly, before access was revoked:
   "do not remove the files. just remove the step from the automation workflow."
They are history, not garbage — `upgrad_apply.py` in particular records how the
synthetic ClipboardEvent carried bold and bullets into Draft.js, which is the
only reason v1's formatting survived. Deleting that costs the explanation.

⛔ DO NOT DISABLE `upgrad_resume_paste.py`. Despite its name it is the shared
résumé PARSER, imported by resume_db.py, jobs_sync.py, daily.py, resume.py and
workspace_favicon.py. It is load-bearing for the CURRENT path. Only the seven
entry points that actually drive a browser at upgrad.com are guarded.

WHAT REPLACED IT: the master résumé lives in `jobs_tracker_v2` and is rendered
by `automation/resume_db.py`. Layout and PDF export are done by hand in Canva.
"""
import sys

REASON = "his upGrad access was revoked on 2026-08-27"

def refuse(tool: str) -> None:
    """Print why, and exit non-zero. Never returns."""
    print(
        f"\n  ⛔ {tool} is RETIRED — {REASON}.\n\n"
        "  The upGrad résumé builder and both Hiration cards are unreachable, so\n"
        "  this script cannot succeed. It is kept for its history, not for use.\n\n"
        "  What to use instead:\n"
        "    master résumé   : automation/resume_db.py  (load | generate | verify)\n"
        "                      content lives in jobs_tracker_v2; HTML is generated\n"
        "    layout + PDF    : by hand, in Canva Pro\n"
        "    the PDF gate    : ./todo  ->  canva-export, then verify-pdf\n\n"
        "  ⚠ master/Abhisheik_Deo_Resume.pdf is the LAST upGrad export (25 Aug) and\n"
        "    is now WRONG: it says Knockout.js and 300, and predates AngularJS, 280,\n"
        "    Kubernetes, Terraform and the axe DevTools bullets. Do not send it.\n",
        file=sys.stderr)
    raise SystemExit(3)
