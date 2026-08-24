"""Local encrypted credential store + auto-login for upGrad.

Creds live in two LOCAL, git-ignored files next to this module:
  .upgrad_key        — Fernet symmetric key (generated once, chmod 600)
  .upgrad_creds.enc  — Fernet-encrypted JSON {"username", "password"} (chmod 600)

Neither is committed (see repo .gitignore). The key is what decrypts the creds,
so it is deliberately kept out of git — this protects against accidental
check-in, not against a local attacker who already has the key file.

Set the creds once (username on line 1, password on line 2, via STDIN so the
password never appears in argv / shell history / process list):

    printf '%s\\n%s\\n' "user@example.com" 'the-password' \\
      | automation/.venv/bin/python automation/upgrad_creds.py set

Check (prints the username only, never the password):

    automation/.venv/bin/python automation/upgrad_creds.py check
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

from cryptography.fernet import Fernet

_HERE = Path(__file__).resolve().parent
KEY_FILE = _HERE / ".upgrad_key"
ENC_FILE = _HERE / ".upgrad_creds.enc"

# upGrad "Career Centre" login form (Ant Design) selectors.
USER_SEL = "#basic_username"
PASS_SEL = "#basic_password"
SUBMIT_SEL = "button[type=submit]"


def _load_key() -> bytes | None:
    if KEY_FILE.exists():
        return KEY_FILE.read_bytes().strip()
    return None


def set_creds(username: str, password: str) -> None:
    key = _load_key()
    if key is None:
        key = Fernet.generate_key()
        KEY_FILE.write_bytes(key)
        os.chmod(KEY_FILE, 0o600)
    blob = json.dumps({"username": username, "password": password}).encode()
    ENC_FILE.write_bytes(Fernet(key).encrypt(blob))
    os.chmod(ENC_FILE, 0o600)


def get_creds() -> tuple[str, str] | None:
    key = _load_key()
    if key is None or not ENC_FILE.exists():
        return None
    try:
        data = json.loads(Fernet(key).decrypt(ENC_FILE.read_bytes()))
        return data["username"], data["password"]
    except Exception:
        return None


def auto_login(page, timeout_s: int = 40) -> bool:
    """Fill + submit the upGrad login form using stored creds.

    Returns True once the URL leaves '/login' (signed in), False if creds are
    missing or the login did not complete (caller should fall back to manual).
    """
    creds = get_creds()
    if creds is None:
        return False
    username, password = creds
    try:
        page.wait_for_selector(USER_SEL, timeout=10_000)
        page.fill(USER_SEL, username)
        page.fill(PASS_SEL, password)
        try:
            page.click(SUBMIT_SEL, timeout=5_000)
        except Exception:
            page.press(PASS_SEL, "Enter")
    except Exception as exc:  # noqa: BLE001
        print(f"[auto-login] could not fill the login form: {exc}", file=sys.stderr)
        return False

    start = time.time()
    while time.time() - start < timeout_s:
        page.wait_for_timeout(1000)
        if "/login" not in page.url.lower():
            page.wait_for_timeout(2000)  # let cookies flush to the profile
            print(f"[auto-login] signed in -- now at {page.url}", file=sys.stderr)
            return True
    print(
        "[auto-login] submitted but still on /login -- wrong creds, or a "
        "captcha/2FA challenge appeared. Falling back to manual.",
        file=sys.stderr,
    )
    return False


def _cli() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "set":
        lines = sys.stdin.read().splitlines()
        if len(lines) < 2:
            sys.exit("set: provide username on line 1 and password on line 2 via stdin")
        set_creds(lines[0].strip(), lines[1])
        print(
            f"stored encrypted creds for {lines[0].strip()} -> "
            f"{ENC_FILE.name} + {KEY_FILE.name} (both git-ignored, chmod 600)"
        )
    elif cmd == "check":
        creds = get_creds()
        print(f"creds: {'OK, username=' + creds[0] if creds else 'NOT set'}")
    else:
        sys.exit(f"unknown command: {cmd!r} (use: set | check)")


if __name__ == "__main__":
    _cli()
