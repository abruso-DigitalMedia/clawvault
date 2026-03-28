# ClawVault — API Credential Management for OpenClaw

**Version:** 1.0.0  
**Author:** Aaron Bruso — Bruso Digital Media LLC  
**License:** MIT (free tier) / Commercial (paid tier)  
**ClawHub:** `npx clawhub@latest install clawvault`

---

## What ClawVault does

ClawVault is a self-healing API credential management system for OpenClaw.
It solves the single most common failure mode in OpenClaw deployments:
credentials breaking silently, agents losing access to external services,
and no recovery path when APIs stop working.

Every API your agent uses gets its own documented, tested, self-healing
credential file. When something breaks, ClawVault fixes it automatically.

---

## The problem it solves

Every OpenClaw user eventually hits this:

- Agent worked yesterday — silent failure today
- Credentials got overwritten during an update
- API changed their auth requirements
- Key rotated and a dozen scripts are now broken
- No way to know which APIs are healthy without manually testing each one

ClawVault eliminates all of these permanently.

---

## How it works

```
You provide: vendor name + API key
ClawVault creates: apis/[vendor].md with full documentation
ClawVault builds: apis/tests/test_[vendor].py
ClawVault runs: the test, logs the result, reports to Discord
ClawVault monitors: monthly doc refresh + on-demand health checks
ClawVault heals: fetches latest docs and retests on any failure
Your automations: read credentials from .md at runtime — never hardcoded
```

---

## Installation

### Free tier (ClawHub)
```bash
npx clawhub@latest install clawvault
```

Installs:
- AGENTS.md workflow addition
- Generic vendor .md template
- Generic test script template
- Setup instructions

### Paid tier (GitHub / Gumroad)
Full package includes:
- All 60 pre-built vendor registrations
- Auto-generator script (register any vendor in one command)
- Complete self-heal workflow
- Pre-built test scripts for all vendors
- Priority support via Discord

---

## File structure

```
~/.openclaw/workspace/
├── apis/
│   ├── anthropic.md          # Pre-built (paid tier)
│   ├── openai.md             # Pre-built (paid tier)
│   ├── kalshi.md             # Pre-built (paid tier)
│   ├── coinbase.md           # Pre-built (paid tier)
│   ├── binance.md            # Pre-built (paid tier)
│   ├── alpaca.md             # Pre-built (paid tier)
│   ├── tradier.md            # Pre-built (paid tier)
│   ├── brave.md              # Pre-built (paid tier)
│   ├── discord.md            # Pre-built (paid tier)
│   ├── telegram.md           # Pre-built (paid tier)
│   ├── slack.md              # Pre-built (paid tier)
│   ├── xai.md                # Pre-built (paid tier)
│   ├── gemini.md             # Pre-built (paid tier)
│   ├── openrouter.md         # Pre-built (paid tier)
│   ├── polymarket.md         # Pre-built (paid tier)
│   ├── kraken.md             # Pre-built (paid tier)
│   ├── github.md             # Pre-built (paid tier)
│   ├── stripe.md             # Pre-built (paid tier)
│   ├── twilio.md             # Pre-built (paid tier)
│   ├── twitter.md            # Pre-built (paid tier)
│   └── tests/
│       ├── test_anthropic.py
│       ├── test_openai.py
│       ├── test_kalshi.py
│       └── [one per vendor]
└── AGENTS.md                 # ClawVault workflow appended here
```

---

## The runtime read pattern (critical)

Every script that uses an API credential MUST read it from the .md file
at runtime. Never hardcode. Never cache at startup. Always read fresh.

```python
import re, pathlib

def get_api_key(vendor: str) -> str:
    """Read API key from ClawVault .md file at runtime."""
    md = pathlib.Path.home() / f'.openclaw/workspace/apis/{vendor}.md'
    content = md.read_text()
    match = re.search(r'\*\*API Key:\*\*\s*`?([^\s`\n\[]+)`?', content)
    if not match or match.group(1).startswith('['):
        raise ValueError(f"API key not configured for {vendor}")
    return match.group(1).strip()

# Usage
api_key = get_api_key('anthropic')
api_key = get_api_key('kalshi')
api_key = get_api_key('openai')
```

Rotate a key? Update one .md file. Every automation instantly uses
the new key. No hunting through scripts, environment variables, or
config files.

---

## Vendor .md file standard format

Every vendor file follows this exact structure so automations can
parse them consistently:

```markdown
# API — [Vendor Name]

## Identity
- **Vendor:** [Name]
- **Product:** [API product name]
- **Purpose:** [What the agent uses this for]
- **Registered:** [DATE]
- **Last health check:** [UPDATED BY AGENT]
- **Status:** [UNKNOWN / OK / DEGRADED / FAILED]

## Credentials
- **API Key:** [KEY VALUE]
- **Key type:** [Bearer / Basic / RSA / Custom]
- **Header name:** [exact header]
- **Auth format:** [exact format]

## Endpoints
- **Base URL:** [url]
- **Primary endpoint:** [url]

## Rate limits & pricing
- [From official docs]

## Official documentation links
- [Populated by ClawVault doc crawl]

## Common error codes
| Code | Meaning | Fix |
|------|---------|-----|

## Test script
- **Location:** apis/tests/test_[vendor].py
- **Last run:** [UPDATED BY AGENT]
- **Last result:** [PASS / FAIL]
- **Last error:** [none if passing]

## Usage rules
[Vendor-specific auth patterns and gotchas]

## Health check history
[DATETIME] — [PASS/FAIL] — [ms]ms — [note]
```

---

## Agent commands

Once ClawVault is installed, your agent understands these commands:

- `"Register [vendor] API, key is [key]"` — full registration flow
- `"Check [vendor] API"` — run health check, report result
- `"Check all APIs"` — health check all registered vendors
- `"API status"` — report current status of all vendors
- `"Update [vendor] docs"` — re-crawl vendor documentation

---

## Self-heal flow

When any API fails during operation:

```
Connection failure detected
         ↓
Post to Discord #risk-alerts immediately
         ↓
Fetch latest vendor auth documentation
         ↓
Compare to current .md file
         ↓
Update .md if auth requirements changed
         ↓
Re-run test script
         ↓
PASS → "Self-heal successful" to Discord
FAIL → "Manual intervention needed" to Discord
```

For trading APIs: halt the affected desk immediately on failure.
Never attempt trades on a desk with a failed API connection.

---

## Health check schedule

- **Monthly doc refresh:** 1st of each month, 09:00 local time
  Re-crawl all vendor documentation, check for breaking changes
- **On-demand:** any time via Discord command or automatic on failure
- **No daily scheduled checks** — monthly + reactive only

---

## Security rules

- API keys stored in plaintext .md files — keep workspace directory private
- Never commit apis/ folder to public git repositories
- Add `apis/` to your .gitignore if using version control
- RSA private keys (e.g. Kalshi) stored as PEM blocks in the .md file
- The workspace directory should have restricted permissions:
  ```bash
  chmod 700 ~/.openclaw/workspace/apis/
  ```

---

## What's included in each tier

| Feature | Free | Paid ($29) |
|---------|------|-----------|
| AGENTS.md workflow | ✓ | ✓ |
| Generic .md template | ✓ | ✓ |
| Generic test template | ✓ | ✓ |
| Auto-generator script | — | ✓ |
| 60 pre-built vendors | — | ✓ |
| Pre-built test scripts | — | ✓ |
| Self-heal workflow | Partial | Complete |
| GitHub repo access | — | ✓ |
| Discord support | — | ✓ |

---

## Support

- GitHub Issues: github.com/abruso-DigitalMedia/clawvault
- OpenClaw Discord: #clawvault channel
- Documentation: github.com/abruso-DigitalMedia/clawvault/wiki

---

## Why ClawVault exists

Built by an OpenClaw user who lost API credentials in production —
repeatedly — until building a system that makes it impossible.

Every design decision comes from a real failure:
- The self-heal flow: because silent failures cost real money
- The runtime read pattern: because hardcoded keys break on rotation
- The monthly doc refresh: because APIs change their auth quietly
- The test scripts: because "it worked yesterday" isn't good enough

ClawVault is the infrastructure layer OpenClaw should have shipped with.
