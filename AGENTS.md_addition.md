# API_MANAGEMENT.md — Full API management workflow

*Read this file on demand only — not loaded on every turn.*
*Reference from AGENTS.md when API management tasks are needed.*

---

## Registering a new API

When user says "register [vendor] API, key is [key]":

1. Create ~/.openclaw/workspace/apis/[vendor].md using standard template
2. Populate with vendor name, key, endpoint info
3. Search vendor website for API documentation — save doc links to .md file
4. Build test script at apis/tests/test_[vendor].py
   - Reads credentials from .md at runtime (never hardcoded)
   - Tests most basic authenticated endpoint
   - Updates .md with last run time, result, error
5. Run test script immediately
6. Post to Discord #api-status:
   ```
   API registered: [Vendor]
   Test: PASS/FAIL | Response: Xms
   Docs saved: N links
   ```

---

## Standard vendor .md template

```markdown
# API — [Vendor]

## Identity
- **Vendor:** [Name]
- **Category:** [type]
- **Purpose:** [what agent uses this for]
- **Registered:** [DATE]
- **Last health check:** [UPDATED BY AGENT]
- **Status:** UNKNOWN

## Credentials
- **API Key:** [KEY]
- **Key type:** [type]
- **Header:** [header name]
- **Auth format:** [exact format]

## Endpoints
- **Base URL:** [url]
- **Primary:** [url]
- **Test:** [url]

## Pricing
[From docs]

## Documentation
[Links from doc crawl]

## Test script
- **Location:** apis/tests/test_[vendor].py
- **Last run:** [UPDATED]
- **Last result:** [PASS/FAIL]
- **Last error:** none

## Health check history
Format: [DATETIME CT] — [PASS/FAIL] — [ms]ms — [note]
```

---

## Runtime read pattern

```python
import re, pathlib

def get_api_key(vendor: str) -> str:
    md = pathlib.Path.home() / f'.openclaw/workspace/apis/{vendor}.md'
    match = re.search(r'\*\*API Key:\*\*\s*`?([^\s`\n\[]+)`?', md.read_text())
    if not match or match.group(1).startswith('['):
        raise ValueError(f"Key not configured for {vendor}")
    return match.group(1).strip()
```

Never hardcode. Always read from file at runtime.

---

## Health check schedule

- Monthly doc refresh: 1st of month, 09:00 CT — re-crawl vendor docs
- On-demand: when connection fails or user requests
- No daily scheduled checks

---

## Self-heal flow

1. Connection failure detected
2. Post to #risk-alerts immediately
3. Fetch latest vendor auth documentation
4. Update .md if auth requirements changed
5. Re-run test script
6. PASS → "Self-heal successful" to #api-status
7. FAIL → "Manual intervention needed" to #risk-alerts
8. Trading APIs: halt affected desk immediately on failure

---

## On-demand commands

- "Register [vendor] API, key is [key]" → full registration flow
- "Check [vendor] API" → run test script
- "Check all APIs" → health check all vendors
- "API status" → report status from all .md files
- "Update [vendor] docs" → re-crawl vendor documentation
