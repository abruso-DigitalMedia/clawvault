# API — [Vendor Name]

## Identity
- **Vendor:** [Vendor Name]
- **Category:** [AI / Trading / Marketplace / Communication / Data / Productivity / Infrastructure / Social]
- **Product:** [API product name]
- **Purpose:** [What your agent uses this for]
- **Registered:** [DATE]
- **Last health check:** [UPDATED BY AGENT]
- **Status:** UNKNOWN

---

## Credentials

- **API Key:** [YOUR API KEY HERE]
- **Key type:** [Bearer / API Key / RSA-PSS / HMAC / OAuth / Basic]
- **Header:** [Authorization / x-api-key / custom header name]
- **Auth format:** [e.g. Authorization: Bearer [KEY]]
- **Note:** [Any special auth requirements — leave blank if none]

---

## Endpoints

- **Base URL:** [https://api.vendor.com/v1]
- **Primary endpoint:** [https://api.vendor.com/v1/main-resource]
- **Test endpoint:** [https://api.vendor.com/v1/status or /ping or /me]
- **Test method:** [GET / POST]

---

## Pricing

[Free tier details / paid tier pricing — from vendor docs]

---

## Documentation

- Primary docs: [https://docs.vendor.com]
- Authentication: [https://docs.vendor.com/auth]
- API reference: [https://docs.vendor.com/api]
- Rate limits: [https://docs.vendor.com/rate-limits]
- Error codes: [https://docs.vendor.com/errors]

---

## Common error codes

| Code | Meaning | Fix |
|------|---------|-----|
| 401 | Unauthorized | Check API key value in this file |
| 403 | Forbidden | Check key permissions |
| 429 | Rate limited | Implement exponential backoff |
| 500 | Server error | Retry — provider-side issue |

---

## Test script

- **Location:** `apis/tests/test_[vendor].py`
- **Last run:** [UPDATED BY AGENT]
- **Last result:** [PASS / FAIL]
- **Last error:** none

---

## Runtime read pattern (ClawVault standard)

Use this exact pattern in any script that calls this API.
Never hardcode the key. Always read from this file at runtime.

```python
import re, pathlib

def get_api_key(vendor: str) -> str:
    """Read API key from ClawVault at runtime. Never hardcode."""
    md = pathlib.Path.home() / f'.openclaw/workspace/apis/{vendor}.md'
    match = re.search(r'\*\*API Key:\*\*\s*`?([^\s`\n\[]+)`?', md.read_text())
    if not match or match.group(1).startswith('['):
        raise ValueError(f"Key not configured for {vendor}")
    return match.group(1).strip()

# Usage
key = get_api_key('[vendor_name]')
```

**Cost note:** This file is NOT loaded at agent startup.
It is read ONLY when your agent calls this vendor's API.
Zero token overhead on turns that don't use this vendor.

---

## Health check history

*Append one line after every health check:*

Format: `[DATETIME CT] — [PASS/FAIL] — [ms]ms — [note]`
