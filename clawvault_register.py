#!/usr/bin/env python3
"""
ClawVault v1.0.0 — API Credential Manager for OpenClaw
The definitive API management system. 60 vendors. One command.

Cost optimization principle:
    ClawVault loads NOTHING at agent startup.
    Each vendor file is read ONLY when that vendor is actually called.
    60 vendors registered = 0 token overhead on turns that don't use them.

Usage:
    python3 clawvault_register.py --vendor anthropic --key sk-ant-xxx
    python3 clawvault_register.py --vendor kalshi --key your-key-id
    python3 clawvault_register.py --list
    python3 clawvault_register.py --check
    python3 clawvault_register.py --check --vendor openai
    python3 clawvault_register.py --heal --vendor kalshi
    python3 clawvault_register.py --vendors
    python3 clawvault_register.py --update

GitHub: https://github.com/abruso-DigitalMedia/clawvault
"""

import re
import sys
import json
import time
import argparse
import pathlib
import subprocess
import urllib.request
import urllib.error
from datetime import datetime

WORKSPACE    = pathlib.Path.home() / ".openclaw/workspace"
APIS_DIR     = WORKSPACE / "apis"
TESTS_DIR    = APIS_DIR / "tests"
VENDORS_FILE = pathlib.Path(__file__).parent / "vendors.json"
VENDORS_URL  = "https://raw.githubusercontent.com/abruso-DigitalMedia/clawvault/main/vendors.json"


def load_vendors() -> dict:
    if not VENDORS_FILE.exists():
        print(f"Error: vendors.json not found at {VENDORS_FILE}")
        sys.exit(1)
    with open(VENDORS_FILE) as f:
        data = json.load(f)
    return {k: v for k, v in data.items() if not k.startswith("_")}


def vendor_key(name: str) -> str:
    return re.sub(r'[^a-z0-9_]', '_', name.lower()).strip('_')


def create_dirs():
    APIS_DIR.mkdir(parents=True, exist_ok=True)
    TESTS_DIR.mkdir(parents=True, exist_ok=True)


def create_md_file(vkey: str, api_key: str, config: dict) -> pathlib.Path:
    md_path = APIS_DIR / f"{vkey}.md"
    now = datetime.now().strftime("%Y-%m-%d")
    name = config.get("name", vkey.title())
    note_line = f"\n- **Note:** {config['note']}" if config.get("note") else ""

    content = f"""# API — {name}

## Identity
- **Vendor:** {name}
- **Category:** {config.get('category', 'General')}
- **Product:** {config.get('product', name + ' API')}
- **Purpose:** [Describe what your agent uses this for]
- **Registered:** {now}
- **Last health check:** [UPDATED BY AGENT]
- **Status:** UNKNOWN

---

## Credentials

- **API Key:** {api_key}
- **Key type:** {config.get('key_type', 'Bearer')}
- **Header:** `{config.get('key_header', 'Authorization')}`
- **Auth format:** `{config.get('auth_format', 'Authorization: Bearer [KEY]')}`{note_line}

---

## Endpoints

- **Base URL:** `{config.get('base_url', '')}`
- **Primary:** `{config.get('primary_endpoint', '')}`
- **Test:** `{config.get('test_endpoint', '')}`

---

## Pricing

{config.get('pricing', 'See official documentation.')}

---

## Documentation

- {config.get('docs_url', '[Populate from vendor website]')}

---

## Error codes

| Code | Meaning | Fix |
|------|---------|-----|
| 401 | Unauthorized | Check API key in this file |
| 403 | Forbidden | Check key permissions |
| 429 | Rate limited | Implement exponential backoff |
| 500 | Server error | Retry — provider-side issue |

---

## Test script

- **Location:** `apis/tests/test_{vkey}.py`
- **Last run:** [UPDATED BY AGENT]
- **Last result:** [PASS / FAIL]
- **Last error:** none

---

## Runtime read pattern (ClawVault standard)

```python
import re, pathlib

def get_api_key(vendor: str) -> str:
    md = pathlib.Path.home() / f'.openclaw/workspace/apis/{{vendor}}.md'
    match = re.search(r'\\*\\*API Key:\\*\\*\\s*`?([^\\s`\\n\\[]+)`?', md.read_text())
    if not match or match.group(1).startswith('['):
        raise ValueError(f"Key not configured for {{vendor}}")
    return match.group(1).strip()

key = get_api_key('{vkey}')
```

**Cost note:** This file loads 0 tokens until {name} is actually called.

---

## Health check history

Format: `[DATETIME CT] — [PASS/FAIL] — [ms]ms — [note]`
"""
    md_path.write_text(content)
    return md_path


def build_auth_code(config: dict) -> str:
    auth_type = config.get("auth_type", "bearer")
    key_header = config.get("key_header", "Authorization").split("+")[0].strip()
    extra = config.get("extra_headers", {})

    lines = []
    if auth_type == "bearer":
        lines.append('    headers["Authorization"] = f"Bearer {api_key}"')
    elif auth_type == "bot_token":
        lines.append('    headers["Authorization"] = f"Bot {api_key}"')
    elif auth_type in ("api_key", "custom_header"):
        lines.append(f'    headers["{key_header}"] = api_key')
    elif auth_type == "user_agent_only":
        lines.append('    headers["User-Agent"] = "(ClawVault, abruso@brusodigitalmedia.com)"')
    elif auth_type == "basic":
        lines.append('    import base64')
        lines.append('    creds = base64.b64encode(f"api:{api_key}".encode()).decode()')
        lines.append('    headers["Authorization"] = f"Basic {creds}"')
    elif auth_type in ("rsa_pss", "hmac_sha256", "hmac_sha512", "aws_sigv4", "lwa_sigv4"):
        lines.append(f'    # {auth_type.upper()} signing required — see vendor docs')
        lines.append('    # Implement vendor-specific signing before use')
    else:
        lines.append('    headers["Authorization"] = f"Bearer {api_key}"')

    for k, v in extra.items():
        lines.append(f'    headers["{k}"] = "{v}"')

    return "\n".join(lines)


def create_test_script(vkey: str, config: dict) -> pathlib.Path:
    test_path = TESTS_DIR / f"test_{vkey}.py"
    name = config.get("name", vkey.title())
    test_endpoint = config.get("test_endpoint", "")
    test_method = config.get("test_method", "GET")
    auth_code = build_auth_code(config)
    needs_config = any(p in test_endpoint for p in ["{AccountSid}", "{shop}", "{spreadsheetId}", "{TOKEN}"])

    url_line = f'    url = "{test_endpoint}"'
    if "{KEY}" in test_endpoint:
        url_line = f'    url = "{test_endpoint}".replace("{{KEY}}", api_key)'

    body_section = ""
    if config.get("test_body"):
        body_section = f'    body = {repr(config["test_body"].encode())}\n'
    elif test_method == "POST":
        body_section = '    body = b"{}"\n'

    body_arg = ", data=body" if body_section else ""

    if needs_config:
        connection_block = '''    print(f"SKIP — endpoint needs account-specific config: {url}")
    print("Update test_endpoint in this script with your account details.")
    return True, 0, "needs-account-config"'''
    else:
        connection_block = f'''    req = urllib.request.Request(url, headers=headers, method="{test_method}"{body_arg})
    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            ms = int((time.time() - start) * 1000)
            return True, ms, None
    except urllib.error.HTTPError as e:
        ms = int((time.time() - start) * 1000)
        body = e.read().decode()[:200] if e.fp else str(e)
        return False, ms, f"HTTP {{e.code}}: {{body}}"
    except Exception as e:
        ms = int((time.time() - start) * 1000)
        return False, ms, str(e)'''

    script = f'''#!/usr/bin/env python3
"""ClawVault — {name} health check
Reads credentials from: ~/.openclaw/workspace/apis/{vkey}.md
Cost: Runs on-demand or monthly only. Zero background token cost.
"""
import re, sys, time, pathlib, urllib.request, urllib.error
from datetime import datetime

MD_PATH = pathlib.Path.home() / ".openclaw/workspace/apis/{vkey}.md"


def read_api_key() -> str:
    if not MD_PATH.exists():
        raise FileNotFoundError(f"Not found: {{MD_PATH}}")
    content = MD_PATH.read_text()
    match = re.search(r\'\\*\\*API Key:\\*\\*\\s*`?([^\\s`\\n\\[]+)`?\', content)
    if not match or match.group(1).startswith(\'[\'):
        raise ValueError("Key not configured — edit {vkey}.md and add your key")
    return match.group(1).strip()


def test_connection(api_key: str) -> tuple:
{url_line}
{body_section}    headers = {{"Content-Type": "application/json", "Accept": "application/json"}}
{auth_code}
{connection_block}


def update_md(passed: bool, ms: int, error) -> None:
    if not MD_PATH.exists():
        return
    now = datetime.now().strftime("%Y-%m-%d %H:%M CT")
    content = MD_PATH.read_text()
    content = re.sub(r\'\\*\\*Last health check:\\*\\*.*\', f\'**Last health check:** {{now}}\', content)
    content = re.sub(r\'\\*\\*Status:\\*\\*.*\', f\'**Status:** {{"OK" if passed else "FAILED"}}\', content)
    content = re.sub(r\'\\*\\*Last run:\\*\\*.*\', f\'**Last run:** {{now}}\', content)
    content = re.sub(r\'\\*\\*Last result:\\*\\*.*\', f\'**Last result:** {{"PASS" if passed else "FAIL"}}\', content)
    content = re.sub(r\'\\*\\*Last error:\\*\\*.*\', f\'**Last error:** {{error or "none"}}\', content)
    log = f"\\n{{now}} — {{"PASS" if passed else "FAIL"}} — {{ms}}ms — {{error or \'none\'}}"
    marker = "Health check history"
    if marker in content:
        idx = content.find("Format:", content.find(marker))
        eol = content.find("\\n", idx)
        if eol != -1:
            content = content[:eol+1] + log + content[eol+1:]
    MD_PATH.write_text(content)


def main() -> None:
    print(f"ClawVault — {name} — {{datetime.now().strftime(\'%Y-%m-%d %H:%M CT\')}}")
    try:
        key = read_api_key()
        print(f"Key: {{key[:8]}}...{{key[-4:]}}")
    except Exception as e:
        print(f"FAIL — {{e}}")
        sys.exit(1)
    passed, ms, error = test_connection(key)
    print(f"{{"PASS" if True else "FAIL"}} — {{ms}}ms" if passed else f"FAIL — {{error}}")
    update_md(passed, ms, error)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
'''
    test_path.write_text(script)
    test_path.chmod(0o755)
    return test_path


def run_test(vkey: str) -> tuple:
    test_path = TESTS_DIR / f"test_{vkey}.py"
    if not test_path.exists():
        return None, 0, "no test script"
    try:
        result = subprocess.run([sys.executable, str(test_path)], capture_output=True, text=True, timeout=30)
        output = result.stdout.strip()
        match = re.search(r'(\d+)ms', output)
        ms = int(match.group(1)) if match else 0
        return result.returncode == 0, ms, output
    except subprocess.TimeoutExpired:
        return False, 30000, "timed out"
    except Exception as e:
        return False, 0, str(e)


def register(vendor_input: str, api_key: str, docs_url: str = None) -> bool:
    vendors = load_vendors()
    vkey = vendor_key(vendor_input)
    config = vendors.get(vkey)

    if not config:
        matches = [k for k in vendors if vendor_input.lower() in k or k in vendor_input.lower()]
        if len(matches) == 1:
            vkey, config = matches[0], vendors[matches[0]]
            print(f"Matched '{vendor_input}' → '{vkey}'")
        elif len(matches) > 1:
            print(f"Ambiguous: {', '.join(matches)}")
            sys.exit(1)
        else:
            print(f"'{vendor_input}' not in vendors.json — using generic template.")
            config = {"name": vendor_input.title(), "category": "Custom", "auth_type": "bearer",
                      "key_header": "Authorization", "auth_format": "Authorization: Bearer [KEY]",
                      "key_type": "Bearer", "docs_url": docs_url or "[configure]",
                      "pricing": "See vendor docs", "test_endpoint": "[configure]", "test_method": "GET"}

    if docs_url:
        config["docs_url"] = docs_url

    create_dirs()
    name = config.get("name", vkey.title())
    print(f"\nClawVault — Registering {name}\n{'='*50}")
    print(f"[1/3] Creating apis/{vkey}.md ...")
    create_md_file(vkey, api_key, config)
    print(f"      Done")
    print(f"[2/3] Building test script ...")
    create_test_script(vkey, config)
    print(f"      Done")
    print(f"[3/3] Running health check ...")
    passed, ms, output = run_test(vkey)
    if passed is None:
        print(f"      SKIPPED — {output}")
        passed = True
    elif passed:
        print(f"      PASS — {ms}ms")
    else:
        print(f"      FAIL — {output}")
    print(f"\n{'─'*50}")
    print(f"  Vendor : {name}")
    print(f"  Status : {'OK' if passed else 'FAILED'}")
    print(f"  File   : ~/.openclaw/workspace/apis/{vkey}.md")
    print(f"  Cost   : 0 tokens until {name} is called")
    print(f"{'─'*50}")
    return passed


def check_all() -> None:
    print(f"\nClawVault — Health check — {datetime.now().strftime('%Y-%m-%d %H:%M CT')}\n{'='*55}")
    if not APIS_DIR.exists() or not list(APIS_DIR.glob("*.md")):
        print("No vendors registered. Run: python3 clawvault_register.py --vendor VENDOR --key KEY")
        return
    results = []
    for md in sorted(APIS_DIR.glob("*.md")):
        v = md.stem
        passed, ms, _ = run_test(v)
        icon = "✓" if passed else "✗" if passed is False else "?"
        status = "PASS" if passed else "FAIL" if passed is False else "NO TEST"
        results.append((v, passed, ms))
        print(f"  {icon} {v:<30} {status:<8} {ms}ms")
    ok = sum(1 for _, p, _ in results if p)
    print(f"\n{'─'*55}\n  {ok}/{len(results)} APIs healthy")


def list_registered() -> None:
    print(f"\nClawVault — Registered vendors\n{'='*55}")
    if not APIS_DIR.exists():
        print("No vendors registered.")
        return
    for md in sorted(APIS_DIR.glob("*.md")):
        content = md.read_text()
        status = re.search(r'\*\*Status:\*\*\s*(\S+)', content)
        last = re.search(r'\*\*Last health check:\*\*\s*(.+)', content)
        s = status.group(1) if status else "UNKNOWN"
        l = last.group(1).strip() if last else "Never"
        icon = "✓" if s == "OK" else "✗" if s == "FAILED" else "?"
        print(f"  {icon} {md.stem:<30} {s:<10} {l}")


def list_all_supported() -> None:
    vendors = load_vendors()
    cats = {}
    for vkey, cfg in vendors.items():
        cat = cfg.get("category", "Other")
        cats.setdefault(cat, []).append((vkey, cfg.get("name", vkey)))
    print(f"\nClawVault — {len(vendors)} supported vendors\n{'='*55}")
    for cat in sorted(cats):
        print(f"\n  {cat}")
        for vkey, name in sorted(cats[cat], key=lambda x: x[1]):
            print(f"    {name:<28} --vendor {vkey}")
    print(f"\n  Register: python3 clawvault_register.py --vendor VENDOR --key YOUR_KEY")


def update_vendors() -> None:
    print("ClawVault — Updating vendors.json from GitHub ...")
    try:
        with urllib.request.urlopen(VENDORS_URL, timeout=15) as resp:
            data = json.loads(resp.read())
        count = len([k for k in data if not k.startswith("_")])
        with open(VENDORS_FILE, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Updated — {count} vendors")
    except Exception as e:
        print(f"Update failed: {e}")


def self_heal(vkey: str) -> None:
    vendors = load_vendors()
    config = vendors.get(vkey)
    if not config:
        print(f"Vendor '{vkey}' not in vendors.json")
        return
    name = config.get("name", vkey)
    print(f"\nClawVault — Self-heal {name}\n{'='*50}")
    md_path = APIS_DIR / f"{vkey}.md"
    if not md_path.exists():
        print(f"No {vkey}.md — register first: --vendor {vkey} --key YOUR_KEY")
        return
    content = md_path.read_text()
    match = re.search(r'\*\*API Key:\*\*\s*`?([^\s`\n\[]+)`?', content)
    if not match or match.group(1).startswith('['):
        print("No key configured. Add your key to the .md file.")
        return
    key = match.group(1).strip()
    print(f"[1/3] Key: {key[:8]}...{key[-4:]}")
    print(f"[2/3] Rebuilding test script from latest config ...")
    create_test_script(vkey, config)
    print(f"[3/3] Retesting ...")
    passed, ms, output = run_test(vkey)
    if passed:
        print(f"      PASS — {ms}ms — Self-heal successful")
    else:
        print(f"      FAIL — {output}")
        print(f"      Docs: {config.get('docs_url', 'see vendor website')}")


def main():
    p = argparse.ArgumentParser(
        description="ClawVault — API credential manager for OpenClaw (60 vendors)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  --vendor anthropic --key sk-ant-xxx
  --vendor kalshi --key your-key-id
  --list          registered vendors + status
  --check         health check all
  --check --vendor openai
  --heal --vendor kalshi
  --vendors       all 60 supported vendors
  --update        pull latest vendors.json
        """
    )
    p.add_argument("--vendor")
    p.add_argument("--key")
    p.add_argument("--docs")
    p.add_argument("--list",    action="store_true")
    p.add_argument("--check",   action="store_true")
    p.add_argument("--heal",    action="store_true")
    p.add_argument("--vendors", action="store_true")
    p.add_argument("--update",  action="store_true")
    args = p.parse_args()

    if args.update:               update_vendors()
    elif args.vendors:            list_all_supported()
    elif args.list:               list_registered()
    elif args.heal and args.vendor: self_heal(vendor_key(args.vendor))
    elif args.check and args.vendor:
        vk = vendor_key(args.vendor)
        passed, ms, out = run_test(vk)
        print(f"{'PASS' if passed else 'FAIL'} — {args.vendor} — {ms}ms")
        if not passed:
            print(f"Error: {out}")
            print(f"Try: python3 clawvault_register.py --heal --vendor {args.vendor}")
    elif args.check:              check_all()
    elif args.vendor and args.key: register(args.vendor, args.key, args.docs)
    else:
        p.print_help()


if __name__ == "__main__":
    main()
