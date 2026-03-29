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

**Cost optimization:** ClawVault loads NOTHING at agent startup. Each vendor file is read ONLY when that vendor is called. 60 vendors registered = 0 token overhead on turns that don't use them.

---

## Free tier (this repo)

Everything you need to get started:

| File | What it does |
|------|-------------|
| `SKILL.md` | ClawHub skill — install via `npx clawhub@latest install clawvault` |
| `AGENTS.md_addition.md` | Paste into your AGENTS.md to teach your agent the full workflow |
| `vendor_template.md` | Blank vendor credential file — copy and fill in for any API |
| `test_template.py` | Blank test script — copy and configure for any vendor |

### Quick start (free tier)

```bash
# 1. Copy the vendor template for any API you want to register
cp vendor_template.md ~/.openclaw/workspace/apis/openai.md

# 2. Edit the file and fill in your API key and endpoint details
open -e ~/.openclaw/workspace/apis/openai.md

# 3. Copy and configure the test script
cp test_template.py ~/.openclaw/workspace/apis/tests/test_openai.py
# Edit the CONFIGURATION section at the top of the file

# 4. Run the test
python3 ~/.openclaw/workspace/apis/tests/test_openai.py

# 5. Paste AGENTS.md_addition.md content into your workspace AGENTS.md
```

---

## Paid tier — $29 (the easy button)

Skip the manual setup entirely.

**What you get:**
- `clawvault_register.py` — auto-generator that does everything in one command
- `vendors.json` — 60 pre-configured vendor configs
- 60 ready-to-use vendor `.md` files
- 60 ready-to-run test scripts
- Complete self-heal workflow
- Discord support

**Register any of 60 vendors in one command:**

```bash
python3 clawvault_register.py --vendor anthropic --key sk-ant-xxx
python3 clawvault_register.py --vendor kalshi --key your-key-id
python3 clawvault_register.py --vendor stripe --key sk_live_xxx
python3 clawvault_register.py --check        # health check all vendors
python3 clawvault_register.py --vendors      # list all 60 supported vendors
python3 clawvault_register.py --update       # pull latest vendor configs from GitHub
```

**👉 Get the paid tier: [abrusomedia.gumroad.com/l/clawvault](https://abrusomedia.gumroad.com/l/clawvault)**

---

## 60 pre-configured vendors (paid tier)

| Category | Vendors |
|----------|---------|
| AI & Models (10) | Anthropic, OpenAI, xAI/Grok, Gemini, OpenRouter, Mistral, Perplexity, ElevenLabs, Replicate, Cohere |
| Trading (12) | Kalshi, Polymarket, Coinbase, Binance, Alpaca, Tradier, Kraken, Robinhood, Webull, Interactive Brokers, Alpha Vantage, Polygon.io |
| Marketplaces (10) | Amazon SP-API, eBay, Etsy, Walmart, Shopify, Stripe, PayPal, Poshmark, Printify, Merch by Amazon |
| Communication (8) | Discord, Telegram, Slack, Twilio, SendGrid, Mailgun, Postmark, Pushover |
| Data (5) | Brave Search, CoinGecko, Weatherstack, NWS (FREE), FRED (FREE) |
| Productivity (4) | GitHub, Notion, Airtable, Google Sheets |
| Infrastructure (3) | Cloudflare, DigitalOcean, AWS |
| Social (5) | Twitter/X, Reddit, LinkedIn, YouTube, TikTok |
| Trading extras (3) | Bybit, OKX, SerpAPI |

---

## The runtime read pattern

Every script reads credentials from the .md file at the moment of execution. Rotate a key, update one file, every automation instantly uses the new key.

```python
import re, pathlib

def get_api_key(vendor: str) -> str:
    """Read API key from ClawVault at runtime. Never hardcode."""
    md = pathlib.Path.home() / f'.openclaw/workspace/apis/{vendor}.md'
    match = re.search(r'\*\*API Key:\*\*\s*`?([^\s`\n\[]+)`?', md.read_text())
    if not match or match.group(1).startswith('['):
        raise ValueError(f"API key not configured for {vendor}")
    return match.group(1).strip()

key = get_api_key('anthropic')
```

---

## Self-heal flow

```
Connection failure detected
         ↓
Alert Discord #risk-alerts immediately
         ↓
Fetch latest vendor auth documentation
         ↓
Update .md if auth requirements changed
         ↓
Re-run test script
         ↓
PASS → "Self-heal successful"
FAIL → "Manual intervention needed"
```

For trading APIs: halt the affected desk immediately on failure.

---

## Agent commands

After adding the AGENTS.md addition to your workspace:

```
"Register Kalshi API, key is [your-key]"   → full registration flow (paid)
"Check all APIs"                            → health check all vendors
"Check OpenAI API"                          → check one vendor
"API status"                                → report all vendor status
```

---

## Health check schedule

- **Monthly:** 1st of each month — re-crawl vendor docs, check for breaking changes
- **On-demand:** any time via Discord command or automatic on failure
- **No daily checks** — monthly + reactive only (keeps token costs minimal)

---

## Security

```bash
chmod 700 ~/.openclaw/workspace/apis/
echo "apis/" >> ~/.openclaw/workspace/.gitignore
```

Keep your workspace `apis/` directory private. Never commit API keys to version control.

---

## What's included

| Feature | Free (this repo) | Paid ($29) |
|---------|-----------------|------------|
| AGENTS.md workflow | ✓ | ✓ |
| Generic .md template | ✓ | ✓ |
| Generic test template | ✓ | ✓ |
| SKILL.md (ClawHub) | ✓ | ✓ |
| Auto-generator script | — | ✓ |
| 60 pre-built vendors | — | ✓ |
| 60 pre-built test scripts | — | ✓ |
| Self-heal workflow (complete) | — | ✓ |
| Auto-update from GitHub | — | ✓ |
| Discord support | — | ✓ |

---

## Why this exists

Built after losing Kalshi trading credentials three times during an OpenClaw setup. Each time the agent went silent mid-session with no recovery path. No existing solution handled self-healing, runtime reads, or automatic doc updates.

ClawVault is the infrastructure layer OpenClaw should have shipped with.

---

## Support

- Email: abruso@brusodigitalmedia.com
- GitHub Issues: github.com/abruso-DigitalMedia/clawvault/issues
- Paid tier support: Discord (included with purchase)

---

*© 2026 Bruso Digital Media LLC — ClawVault is not affiliated with OpenClaw or Anthropic.*
*Built by the community, for the community.* 🦞
