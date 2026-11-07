# Groww SIP Continuity Assistant — Groq Upgrade

> NextLeap graduation project prototype. This is an independent educational prototype, not an official Groww product and not a financial adviser.

## What this prototype demonstrates

The app preserves the original three-stage journey:

1. **Setup SIP** — choose an illustrative fund example, contribution amount and debit date.
2. **Active SIP Dashboard** — explore simulated cash-flow, salary-date and failed-debit scenarios.
3. **AI Retention Engine** — receive grounded, non-advisory explanations and explore continuity concepts.

The app also retains the flexibility simulator and AI quality/evidence tab.

## AI architecture

- **Provider:** Groq, through its OpenAI-compatible API.
- **Default model:** `openai/gpt-oss-20b`.
- **Endpoint:** `https://api.groq.com/openai/v1`.
- **Safety gate:** deterministic local checks run before any model request.
- **Grounded generation:** one Groq chat-completion request for an allowed query, using the project knowledge base and scenario context.
- **Fallback:** if the key is missing or Groq is unavailable, the deterministic local response path remains available.

The safety gate is a first-pass prototype control, not a certified compliance system. It should be evaluated with the supplied test set and adversarial prompts.

## Evidence and limitations

Project discovery included 32 survey responses and five qualitative interviews. These are exploratory inputs, not representative population estimates or proof of causality.

The knowledge base deliberately avoids unsupported universal claims about:
- Groww, AMC or bank penalties;
- CIBIL or credit-reporting outcomes;
- SIP pause/skip availability;
- minimum contribution amounts;
- mandate processing timelines.

Users are directed to verify platform-, AMC- and bank-specific rules with the relevant provider.

## Product concepts and demo boundaries

- **Step-Down + Auto-Step-Up** is presented as a proposed product innovation, not an existing Groww feature.
- Fund names in the setup screen are illustrative examples, not investment recommendations.
- The SIP, portfolio value, folio, mandate and debit history are simulated.
- Action confirmations are demo-only. No real SIP, NPCI mandate, bank payment or AMC instruction is submitted.
- Reminder interactions are session-level demonstrations. No WhatsApp, SMS or external reminder is sent.
- Simulator outputs are illustrative projections, not promised or expected returns.

## Run locally

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Configure Groq

Create a local `.streamlit/secrets.toml` file (do not commit it) or set environment variables:

```toml
GROQ_API_KEY = "your_groq_api_key"
GROQ_MODEL = "openai/gpt-oss-20b"
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
```

The key is read from Streamlit secrets or environment variables. Never put API keys in source code or GitHub.

## Tests

Run the deterministic/offline checks:

```bash
python test_app.py
```

These tests verify local guardrail and fallback behaviour. They do **not** measure live Groq accuracy or establish 100% AI accuracy. Live model evaluation should be reported separately with the tested prompts, results and date.

## Deployment for the isolated Groq version

Deploy this branch as a separate Streamlit app:

- Repository: `Omi2456/groww-sip-continuity-assistant`
- Branch: `groq-upgrade`
- Main file: `app.py`

Add the three Groq settings in the **new app's** Streamlit Secrets. Do not change the existing deployment's branch or secrets.
