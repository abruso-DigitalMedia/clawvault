# ClawVault — Gumroad Product Listing

## Product title
ClawVault — Self-Healing API Management for OpenClaw (20 Vendors)

## Price
$29 (one-time)

## Short description (shown in search)
Stop losing API credentials. ClawVault gives every OpenClaw API its own 
documented, tested, self-healing credential file. 60 vendors pre-built. 
Register any new vendor in one command.

## Full description

---

**The #1 reason OpenClaw setups fail silently is broken API credentials.**

You set everything up perfectly. The agent runs for a few days. Then something 
changes — a key rotates, an API updates their auth requirements, an OpenClaw 
update overwrites your config — and the agent goes silent. No error. No alert. 
Just silence.

I lost my Kalshi trading credentials three times before building ClawVault.

**ClawVault solves this permanently.**

---

### What you get

**The auto-generator** — register any API in one command:
```
python3 clawvault_register.py --vendor Anthropic --key sk-ant-xxx
```
It creates the credential file, crawls the vendor docs, builds a test script, 
runs it, and reports back. Done in 60 seconds.

**60 pre-built vendor registrations** — ready to use immediately:

AI Providers: Anthropic, OpenAI, xAI/Grok, Gemini, OpenRouter

Trading: Kalshi, Polymarket, Coinbase, Binance, Alpaca, Tradier, Kraken

Infrastructure: Discord, Telegram, Slack, Brave Search, GitHub, Stripe, 
Twilio, Twitter/X

**The self-heal workflow** — when an API breaks at 3am during a trading 
session, ClawVault fetches the latest vendor documentation, updates the 
credential file, retests, and alerts you in Discord. Automatically.

**The runtime read pattern** — every automation reads credentials from the 
.md file at the moment of execution. Rotate a key, update one file, every 
script in your entire system instantly uses the new key. No hunting through 
environment variables, hardcoded values, or config files.

**The AGENTS.md addition** — teach your OpenClaw agent the full ClawVault 
workflow. Tell it in Discord: "Register Stripe API, key is sk_live_xxx" and 
it handles everything.

---

### Why it's designed this way

Every design decision came from a real failure:

- **Self-heal:** because silent failures cost real money (especially in trading)
- **Runtime reads:** because hardcoded keys break silently on rotation
- **Monthly doc refresh:** because APIs change their auth requirements without announcements
- **Test scripts:** because "it worked yesterday" isn't a monitoring strategy
- **One file per vendor:** because you should be able to see every credential 
  in your system at a glance

---

### The Kalshi RSA-PSS gotcha (why this matters)

Kalshi uses RSA-PSS asymmetric signing — not a simple API key. Every request 
must be signed with a private key using a specific path format. The legacy 
trading-api.kalshi.com URL returns 401. The correct endpoint is 
api.elections.kalshi.com/trade-api/v2.

ClawVault's Kalshi registration handles all of this. The PEM private key 
is stored safely in the .md file and read at runtime by the signing function. 
No separate keyfiles. No environment variables. One file, everything you need.

---

### Health check schedule (token-efficient)

- **Monthly:** 1st of each month — re-crawl vendor docs, check for breaking changes
- **On-demand:** any time via Discord command or automatic on failure
- **No daily checks** — keeps your API costs minimal

---

### What's NOT included in the free ClawHub tier

The free tier gives you the template and workflow. The paid tier gives you 
20 working vendor registrations, the auto-generator that builds new ones, 
and complete test scripts for every vendor.

If you've ever spent an afternoon debugging why your OpenClaw agent suddenly 
can't reach Anthropic, Kalshi, or Discord — this pays for itself immediately.

---

### What you receive

- `clawvault_register.py` — the auto-generator (works for any vendor)
- `SKILL.md` — full ClawHub skill definition
- `README.md` — complete documentation
- `AGENTS.md` addition — paste into your existing AGENTS.md
- 60 pre-built `apis/[vendor].md` files
- 60 pre-built `apis/tests/test_[vendor].py` scripts
- Access to the GitHub repo for updates
- Discord support channel

---

### Requirements

- OpenClaw installed and running
- Python 3.8+
- The API keys you want to register (you provide these — ClawVault just manages them)

---

### Refund policy

If ClawVault doesn't work with your OpenClaw setup, contact me at abruso@brusodigitalmedia.com or in Discord 
and I'll either fix it or refund you. No questions asked within 14 days.

---

*Built by a 20-year automation engineer who got tired of losing credentials.*  
*ClawVault is community software — not affiliated with OpenClaw or Anthropic.* 🦞
