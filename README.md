# ClawVault 🔐🦞

**Self-healing API credential management for OpenClaw**

> Built by an OpenClaw user who lost API credentials in production — repeatedly — until building a system that makes it impossible.

---

## The problem

Every OpenClaw user eventually hits this:

- ✗ Agent worked yesterday — silent failure today
- ✗ Credentials got overwritten during an update  
- ✗ API changed their auth requirements quietly
- ✗ Key rotated and a dozen scripts are now broken
- ✗ No way to know which APIs are healthy without testing each one manually

ClawVault eliminates all of these permanently.

---

## How it works

```
You provide: vendor name + API key
ClawVault:   creates apis/[vendor].md with full documentation
             builds  apis/tests/test_[vendor].py
             runs    the test, logs result, reports status
             heals   automatically when connections break
Your code:   reads credentials from .md at runtime — never hardcoded
```

---

## Quick start

### Free tier (ClawHub)
```bash
npx clawhub@latest install clawvault
```

### Paid tier (all 60 vendors + auto-generator)
```bash
git clone https://github.com/abruso-DigitalMedia/clawvault
cd clawvault
python3 clawvault_register.py --vendor Anthropic --key sk-ant-xxx
```

---

## Register any API in one command

```bash
# Pre-configured vendors (no docs URL needed)
python3 clawvault_register.py --vendor Anthropic --key sk-ant-xxx
python3 clawvault_register.py --vendor OpenAI --key sk-xxx
python3 clawvault_register.py --vendor Kalshi --key your-key-id
python3 clawvault_register.py --vendor Coinbase --key your-key
python3 clawvault_register.py --vendor Discord --key your-bot-token

# Any vendor (provide docs URL)
python3 clawvault_register.py --vendor Stripe --key sk_live_xxx --docs stripe.com/docs/api

# Health checks
python3 clawvault_register.py --check              # all vendors
python3 clawvault_register.py --check --vendor openai  # one vendor
python3 clawvault_register.py --list               # show all status
```

---

## 20 pre-configured vendors

### AI Providers
| Vendor | Auth Type | Notes |
|--------|-----------|-------|
| Anthropic | API Key | x-api-key header |
| OpenAI | Bearer | Standard OAuth |
| xAI / Grok | Bearer | Standard OAuth |
| Gemini | API Key | x-goog-api-key |
| OpenRouter | Bearer | Multi-model routing |

### Trading & Markets
| Vendor | Auth Type | Notes |
|--------|-----------|-------|
| Kalshi | RSA-PSS | Asymmetric signing required |
| Polymarket | Bearer | CLOB API |
| Coinbase | Bearer/JWT | Public price endpoint is auth-free |
| Binance | HMAC | US accounts use Binance.US |
| Alpaca | Key + Secret | Both required |
| Tradier | Bearer | Commission-free options |
| Kraken | HMAC | Non-standard pair naming |

### Infrastructure & Comms
| Vendor | Auth Type | Notes |
|--------|-----------|-------|
| Discord | Bot Token | Enable Message Content Intent |
| Telegram | URL Token | Token embedded in URL path |
| Slack | OAuth Token | xoxb- prefix |
| Brave Search | Subscription Token | 2k free queries/month |
| GitHub | Personal Token | Fine-grained tokens recommended |
| Stripe | Secret Key | Use sk_test_ for dev |
| Twilio | SID + Token | Both required |
| Twitter/X | Bearer | Free tier: 1,500 tweets/month |

---

## The runtime read pattern

Every script reads credentials from the .md file at the moment of
execution. Rotate a key, update one file, every automation instantly
uses the new key.

```python
import re, pathlib

def get_api_key(vendor: str) -> str:
    """Read API key from ClawVault at runtime. Never hardcode."""
    md = pathlib.Path.home() / f'.openclaw/workspace/apis/{vendor}.md'
    content = md.read_text()
    match = re.search(r'\*\*API Key:\*\*\s*`?([^\s`\n\[]+)`?', content)
    if not match or match.group(1).startswith('['):
        raise ValueError(f"API key not configured for {vendor}")
    return match.group(1).strip()

# Usage in any script
anthropic_key = get_api_key('anthropic')
kalshi_key = get_api_key('kalshi')
openai_key = get_api_key('openai')
```

---

## Self-heal flow

When any API fails during operation:

```
Connection failure detected
         ↓
Alert Discord #risk-alerts immediately
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

For trading APIs: **halt the affected desk immediately on failure.**

---

## Agent commands (after installing AGENTS.md addition)

Tell your OpenClaw agent in Discord:

```
"Register Kalshi API, key is [your-key]"
"Check all APIs"
"Check OpenAI API"  
"API status"
"Update Anthropic docs"
```

---

## Health check schedule

- **Monthly:** 1st of each month — re-crawl vendor docs, check for breaking changes
- **On-demand:** any time via Discord command
- **Automatic:** triggers immediately on any connection failure
- **No daily checks** — monthly + reactive only (keeps costs minimal)

---

## File structure

```
~/.openclaw/workspace/
└── apis/
    ├── anthropic.md
    ├── openai.md
    ├── kalshi.md
    ├── [vendor].md
    └── tests/
        ├── test_anthropic.py
        ├── test_openai.py
        ├── test_kalshi.py
        └── test_[vendor].py
```

---

## Security

```bash
# Restrict permissions on your apis directory
chmod 700 ~/.openclaw/workspace/apis/

# Never commit to public repos
echo "apis/" >> ~/.openclaw/workspace/.gitignore
```

Keys are stored in plaintext .md files for human readability and
agent accessibility. Keep your workspace directory private.

---

## What's included

| Feature | Free (ClawHub) | Paid ($29) |
|---------|---------------|------------|
| AGENTS.md workflow | ✓ | ✓ |
| Generic .md template | ✓ | ✓ |
| Generic test template | ✓ | ✓ |
| Auto-generator script | — | ✓ |
| 60 pre-built vendors | — | ✓ |
| Pre-built test scripts | — | ✓ |
| Self-heal workflow | Partial | Complete |
| GitHub repo | — | ✓ |
| Discord support | — | ✓ |

---

## Get the paid tier

**Gumroad:** [link]  
**Includes:** Full source, all 60 vendors, auto-generator, Discord support

---

## Why this exists

Built after losing Kalshi trading credentials three times during an
OpenClaw setup. Each time the agent went silent mid-session with no
recovery path. No existing solution handled self-healing, runtime
reads, or automatic doc updates.

ClawVault is the infrastructure layer OpenClaw should have shipped with.

---

## License

MIT — free tier  
Commercial — paid tier (includes all vendor registrations and auto-generator)

---

*© 2026 Bruso Digital Media LLC — ClawVault is not affiliated with OpenClaw or Anthropic.*  
*Built by the community, for the community.* 🦞
