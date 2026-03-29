#!/usr/bin/env python3
"""
ClawVault health check template — [Vendor Name]
Copy this file to: apis/tests/test_[vendor].py
Fill in the configuration section below.

Reads credentials from: ~/.openclaw/workspace/apis/[vendor].md
Cost: Runs on-demand or monthly only. Zero background token cost.
"""

import re
import sys
import time
import pathlib
import urllib.request
import urllib.error
from datetime import datetime

# ─────────────────────────────────────────────
# CONFIGURATION — fill these in for your vendor
# ─────────────────────────────────────────────

VENDOR_NAME  = "[Vendor Name]"
VENDOR_KEY   = "[vendor_key]"          # lowercase, no spaces e.g. "openai", "stripe"
TEST_URL     = "[https://api.vendor.com/v1/test-endpoint]"
TEST_METHOD  = "GET"                   # GET or POST
AUTH_TYPE    = "bearer"                # bearer / api_key / bot_token / basic / custom

# For custom auth types, set the exact header name and format:
CUSTOM_HEADER = "[Authorization]"      # e.g. "x-api-key", "X-Subscription-Token"
CUSTOM_FORMAT = "Bearer"              # e.g. "Bearer", "Bot", ""

# Extra headers required by this vendor (e.g. versioning headers)
EXTRA_HEADERS = {
    # "anthropic-version": "2023-06-01",  # example
}

# ─────────────────────────────────────────────
# DO NOT EDIT BELOW THIS LINE
# ─────────────────────────────────────────────

MD_PATH = pathlib.Path.home() / f".openclaw/workspace/apis/{VENDOR_KEY}.md"


def read_api_key() -> str:
    """Read API key from ClawVault .md file at runtime."""
    if not MD_PATH.exists():
        raise FileNotFoundError(
            f"API file not found: {MD_PATH}\n"
            f"Create it first using the vendor_template.md"
        )
    content = MD_PATH.read_text()
    match = re.search(r'\*\*API Key:\*\*\s*`?([^\s`\n\[]+)`?', content)
    if not match or match.group(1).startswith('['):
        raise ValueError(
            f"API key not configured in {VENDOR_KEY}.md\n"
            f"Edit the file and replace [YOUR API KEY HERE] with your actual key"
        )
    return match.group(1).strip()


def build_headers(api_key: str) -> dict:
    """Build request headers based on auth type."""
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    if AUTH_TYPE == "bearer":
        headers["Authorization"] = f"Bearer {api_key}"
    elif AUTH_TYPE == "api_key":
        headers[CUSTOM_HEADER] = api_key
    elif AUTH_TYPE == "bot_token":
        headers["Authorization"] = f"Bot {api_key}"
    elif AUTH_TYPE == "basic":
        import base64
        credentials = base64.b64encode(f"api:{api_key}".encode()).decode()
        headers["Authorization"] = f"Basic {credentials}"
    elif AUTH_TYPE == "custom":
        if CUSTOM_FORMAT:
            headers[CUSTOM_HEADER] = f"{CUSTOM_FORMAT} {api_key}"
        else:
            headers[CUSTOM_HEADER] = api_key

    # Add any extra required headers
    headers.update(EXTRA_HEADERS)

    return headers


def test_connection(api_key: str) -> tuple:
    """Test the API connection and return (passed, elapsed_ms, error)."""
    headers = build_headers(api_key)
    req = urllib.request.Request(
        TEST_URL,
        headers=headers,
        method=TEST_METHOD
    )
    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            elapsed_ms = int((time.time() - start) * 1000)
            return True, elapsed_ms, None
    except urllib.error.HTTPError as e:
        elapsed_ms = int((time.time() - start) * 1000)
        body = e.read().decode()[:200] if e.fp else str(e)
        return False, elapsed_ms, f"HTTP {e.code}: {body}"
    except Exception as e:
        elapsed_ms = int((time.time() - start) * 1000)
        return False, elapsed_ms, str(e)


def update_md_file(passed: bool, elapsed_ms: int, error: str) -> None:
    """Update the .md file with test results."""
    if not MD_PATH.exists():
        return

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M CT")
    status = "OK" if passed else "FAILED"
    result = "PASS" if passed else "FAIL"
    error_note = error if error else "none"

    content = MD_PATH.read_text()
    content = re.sub(
        r'\*\*Last health check:\*\*.*',
        f'**Last health check:** {now_str}',
        content
    )
    content = re.sub(
        r'\*\*Status:\*\*.*',
        f'**Status:** {status}',
        content
    )
    content = re.sub(
        r'\*\*Last run:\*\*.*',
        f'**Last run:** {now_str}',
        content
    )
    content = re.sub(
        r'\*\*Last result:\*\*.*',
        f'**Last result:** {result}',
        content
    )
    content = re.sub(
        r'\*\*Last error:\*\*.*',
        f'**Last error:** {error_note}',
        content
    )

    # Append to health check history
    log_entry = f"\n{now_str} — {result} — {elapsed_ms}ms — {error_note}"
    marker = "Health check history"
    if marker in content:
        fmt_idx = content.find("Format:", content.find(marker))
        eol = content.find("\n", fmt_idx)
        if eol != -1:
            content = content[:eol+1] + log_entry + content[eol+1:]

    MD_PATH.write_text(content)


def main() -> None:
    print(f"ClawVault — {VENDOR_NAME} health check")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M CT')}")
    print(f"File: {MD_PATH}")
    print()

    # Read API key
    try:
        api_key = read_api_key()
        print(f"Key found: {api_key[:8]}...{api_key[-4:]}")
    except (FileNotFoundError, ValueError) as e:
        print(f"FAIL — {e}")
        sys.exit(1)

    # Test connection
    print(f"Testing: {TEST_URL}")
    passed, elapsed_ms, error = test_connection(api_key)

    if passed:
        print(f"PASS — Connected successfully ({elapsed_ms}ms)")
    else:
        print(f"FAIL — {error}")

    # Update .md file
    update_md_file(passed, elapsed_ms, error)
    print(f"Results written to {MD_PATH.name}")

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
