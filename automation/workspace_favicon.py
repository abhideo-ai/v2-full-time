#!/usr/bin/env python3
"""Per-workspace favicon.

Each job-application workspace gets its own icon so several open tabs stay
tellable apart. Same visual language as static/favicon.svg (rounded tile,
serif initials, amber accent) with the colour derived from the slug, so a
company always gets the same colour.

    python automation/workspace_favicon.py --slug stripe-principal-architect
    python automation/workspace_favicon.py --slug databricks-staff-eng --initials DB
"""
import argparse
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Deep, legible tiles. Master (#0f766e teal) is deliberately absent so the
# master pages stay visually distinct from every workspace.
PALETTE = [
    "#9a3412", "#b91c1c", "#a21caf", "#6d28d9", "#4338ca", "#1d4ed8",
    "#0369a1", "#047857", "#4d7c0f", "#a16207", "#c2410c", "#831843",
]

TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <rect width="32" height="32" rx="6" fill="{bg}"/>
  <text x="16" y="22" font-family="Charter, 'Iowan Old Style', Georgia, serif" font-size="{size}" font-weight="700" text-anchor="middle" fill="#f7f4ee">{initials}</text>
</svg>
"""


def initials_for(slug: str) -> str:
    """First token of the slug, first two letters. `stripe-x` -> `ST`."""
    token = re.split(r"[-_]", slug.strip())[0]
    letters = re.sub(r"[^A-Za-z0-9]", "", token)
    if not letters:
        raise SystemExit(f"[favicon] slug {slug!r} has no usable letters")
    return letters[:2].upper()


def colour_for(slug: str) -> str:
    digest = hashlib.md5(slug.encode("utf-8")).digest()
    return PALETTE[digest[0] % len(PALETTE)]


def render(slug: str, initials: str | None = None) -> str:
    ini = (initials or initials_for(slug)).upper()
    # Two glyphs need to sit narrower than the master's single "A".
    return TEMPLATE.format(bg=colour_for(slug), initials=ini,
                           size=15 if len(ini) > 1 else 20)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--initials", help="override the derived two letters")
    ap.add_argument("--out", help="output path (default: <workspace>/favicon.svg)")
    ap.add_argument("--print", action="store_true", help="write to stdout instead")
    args = ap.parse_args()

    svg = render(args.slug, args.initials)
    if args.print:
        sys.stdout.write(svg)
        return

    if args.out:
        out = Path(args.out)
    else:
        import upgrad_resume_paste as urp
        dirs = urp._slug_dir_candidates(args.slug, ROOT)
        if not dirs:
            raise SystemExit(
                f"[favicon] no workspace found for slug {args.slug!r}; pass --out"
            )
        out = dirs[0] / "favicon.svg"

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(svg, encoding="utf-8")
    print(f"[favicon] {args.slug} -> {out}")


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    main()
