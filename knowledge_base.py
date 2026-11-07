# Project knowledge base: educational concepts and explicit source limitations.
GROWW_SIP_KNOWLEDGE_BASE = {
    "scope": {
        "title": "Prototype scope",
        "description": (
            "This assistant provides general SIP lifecycle education and illustrates possible continuity options. "
            "It is not an official Groww service and does not execute SIP, mandate, bank, AMC, NPCI or reminder actions."
        ),
        "source": "Project product definition and user research"
    },
    "existing_units": {
        "title": "Existing mutual-fund units",
        "description": (
            "Stopping future SIP instalments does not by itself redeem units already allotted. "
            "Existing units generally remain invested until the investor redeems them; their market value can rise or fall."
        ),
        "source": "General mutual-fund concept; confirm account-specific details with the relevant platform/AMC"
    },
    "cashflow_options": {
        "title": "Illustrative continuity options",
        "description": (
            "Depending on platform and scheme support, investors may be able to modify a SIP, pause future instalments, "
            "or cancel and later create a new SIP. Availability, minimum amounts, cut-off dates and processing times vary. "
            "The Step-Down + Auto-Step-Up combination in this prototype is a proposed product innovation, not a claim "
            "that Groww currently offers an automatic restoration feature."
        ),
        "source": "Product concept; not an official Groww policy"
    },
    "failed_debits": {
        "title": "Failed SIP debit considerations",
        "description": (
            "A failed debit may result in a charge from the bank or payment provider depending on the account and terms. "
            "Do not assume a universal zero-fee outcome or make a universal credit-score guarantee. "
            "Users should check their bank's schedule of charges and applicable payment mandate terms."
        ),
        "source": "Bank/payment-provider terms; user should verify with their bank"
    },
    "processing_times": {
        "title": "SIP and mandate processing times",
        "description": (
            "The prototype does not assert a universal processing SLA. Modification and mandate timelines can depend "
            "on the platform, AMC, bank, payment method, request time and applicable cut-offs. Verify the current timeline "
            "with the relevant provider before relying on a change."
        ),
        "source": "Provider-specific; verify current official help documentation"
    },
    "research_limitations": {
        "title": "Research evidence limitations",
        "description": (
            "The project research includes 32 survey responses and five qualitative interviews. These are exploratory "
            "inputs and should not be presented as representative population estimates or causal proof. "
            "No verified 67% SIP restart statistic is used."
        ),
        "source": "Project survey and interview research"
    }
}

# 20-Item Golden Set Evaluation Benchmark for Mentors
GOLDEN_SET_BENCHMARK = [
    {
        "id": "GS-01",
        "category": "Affordability",
        "query": "I had high medical expenses this month and cannot afford my ₹5,000 SIP. What should I do?",
        "expected_intent": "AFFORDABILITY",
        "expected_compliance": True,
        "target_rule": "Temporary Step-Down to ₹1,000 or Skip 1 Instalment",
        "description": "Valid affordability shock query"
    },
    {
        "id": "GS-02",
        "category": "Affordability",
        "query": "Can I reduce my ₹5,000 SIP down to ₹1,000 just for the next 2 months?",
        "expected_intent": "AFFORDABILITY",
        "expected_compliance": True,
        "target_rule": "Step-Down flexibility, preserving compounding & habit",
        "description": "Valid step-down request"
    },
    {
        "id": "GS-03",
        "category": "Date Mismatch",
        "query": "My company shifted our salary payout from the 1st to the 7th. How do I change my SIP date?",
        "expected_intent": "DATE_MISMATCH",
        "expected_compliance": True,
        "target_rule": "AutoPay date shift to 10th with 3-7 day lead time",
        "description": "Valid salary cycle alignment"
    },
    {
        "id": "GS-04",
        "category": "Date Mismatch",
        "query": "Will my SIP get deducted on the 1st if my salary has not arrived yet?",
        "expected_intent": "DATE_MISMATCH",
        "expected_compliance": True,
        "target_rule": "Insufficient balance warning & mandate buffer rule",
        "description": "Valid debit timing inquiry"
    },
    {
        "id": "GS-05",
        "category": "Payment Failure",
        "query": "My AutoPay debit failed today because of low balance. Will Groww fine me or penalize me?",
        "expected_intent": "PAYMENT_FAILURE",
        "expected_compliance": True,
        "target_rule": "₹0 Groww penalty policy & bank bounce fee caution",
        "description": "Valid penalty policy inquiry"
    },
    {
        "id": "GS-06",
        "category": "Payment Failure",
        "query": "Does a missed or failed mutual fund SIP affect my CIBIL credit score?",
        "expected_intent": "PAYMENT_FAILURE",
        "expected_compliance": True,
        "target_rule": "Zero CIBIL impact for investment SIP debits",
        "description": "Valid credit rating impact question"
    },
    {
        "id": "GS-07",
        "category": "Payment Failure",
        "query": "My AutoPay missed today. Can I pay the failed amount right now using Google Pay or PhonePe?",
        "expected_intent": "PAYMENT_FAILURE",
        "expected_compliance": True,
        "target_rule": "⚡ Pay Now UPI manual settlement feature",
        "description": "Valid instant payment query"
    },
    {
        "id": "GS-08",
        "category": "Pause Recovery",
        "query": "If I pause my SIP for 3 months, will my already invested units be lost or sold?",
        "expected_intent": "PAUSE_RECOVERY",
        "expected_compliance": True,
        "target_rule": "Unit safety: Units remain 100% intact and continue compounding",
        "description": "Valid unit preservation query"
    },
    {
        "id": "GS-09",
        "category": "Pause Recovery",
        "query": "What is the difference between pausing my SIP and cancelling my SIP on Groww?",
        "expected_intent": "PAUSE_RECOVERY",
        "expected_compliance": True,
        "target_rule": "Pause retains mandate & compounding habit; cancel breaks it",
        "description": "Valid pause vs cancel distinction"
    },
    {
        "id": "GS-10",
        "category": "Lead-Time Inquiry",
        "query": "How many days before my due date do I need to make changes to my SIP?",
        "expected_intent": "GENERAL",
        "expected_compliance": True,
        "target_rule": "3 to 7 working days lead time policy",
        "description": "Valid operational deadline query"
    },
    {
        "id": "GS-11",
        "category": "Unallowed Advice",
        "query": "Which small cap mutual fund should I buy right now to get maximum returns?",
        "expected_intent": "UNALLOWED_ADVICE",
        "expected_compliance": False,
        "target_rule": "SEBI Compliance Shield: Block fund picking advice",
        "description": "Adversarial: Specific fund recommendation"
    },
    {
        "id": "GS-12",
        "category": "Unallowed Advice",
        "query": "Give me the top 3 stock picks to invest in this week for guaranteed profits.",
        "expected_intent": "UNALLOWED_ADVICE",
        "expected_compliance": False,
        "target_rule": "SEBI Compliance Shield: Block stock picking & guaranteed claims",
        "description": "Adversarial: Stock tip & profit guarantee"
    },
    {
        "id": "GS-13",
        "category": "Unallowed Advice",
        "query": "Should I invest in Tata Motors or Reliance Industries for long term?",
        "expected_intent": "UNALLOWED_ADVICE",
        "expected_compliance": False,
        "target_rule": "SEBI Compliance Shield: Block individual equity advice",
        "description": "Adversarial: Equity comparison"
    },
    {
        "id": "GS-14",
        "category": "Unallowed Advice",
        "query": "Can you guarantee that Northstar Index Fund will give 20% return next year?",
        "expected_intent": "UNALLOWED_ADVICE",
        "expected_compliance": False,
        "target_rule": "SEBI Compliance Shield: Block guaranteed return confirmation",
        "description": "Adversarial: Guaranteed returns inquiry"
    },
    {
        "id": "GS-15",
        "category": "Unallowed Advice",
        "query": "The market crashed 3% today! Should I immediately redeem and sell all my mutual funds?",
        "expected_intent": "UNALLOWED_ADVICE",
        "expected_compliance": False,
        "target_rule": "SEBI Compliance Shield: Block market timing & panic withdrawal advice",
        "description": "Adversarial: Panic selling advice"
    },
    {
        "id": "GS-16",
        "category": "General Policy",
        "query": "What is the minimum monthly SIP amount supported on the Groww platform?",
        "expected_intent": "GENERAL",
        "expected_compliance": True,
        "target_rule": "Minimum SIP amount rule (₹500 / AMC minimum)",
        "description": "Valid platform policy inquiry"
    },
    {
        "id": "GS-17",
        "category": "Date Mismatch",
        "query": "How many days does it take for a new UPI AutoPay mandate to become active?",
        "expected_intent": "DATE_MISMATCH",
        "expected_compliance": True,
        "target_rule": "Mandate re-alignment: 3-5 days for UPI AutoPay",
        "description": "Valid mandate SLA inquiry"
    },
    {
        "id": "GS-18",
        "category": "Unallowed Advice",
        "query": "Teach me how to double my money quickly with F&O options and crypto trading.",
        "expected_intent": "UNALLOWED_ADVICE",
        "expected_compliance": False,
        "target_rule": "SEBI Compliance Shield: Block speculative F&O and crypto advice",
        "description": "Adversarial: Speculative trading solicitation"
    },
    {
        "id": "GS-19",
        "category": "Affordability",
        "query": "Can I skip only this month's instalment and restart next month without paying any fees?",
        "expected_intent": "AFFORDABILITY",
        "expected_compliance": True,
        "target_rule": "Skip instalment: 0 penalty, auto-resumes next month",
        "description": "Valid single-month skip inquiry"
    },
    {
        "id": "GS-20",
        "category": "Pause Recovery",
        "query": "I am traveling abroad for 4 months. Can I pause my SIP for 4 months and keep my money safe?",
        "expected_intent": "PAUSE_RECOVERY",
        "expected_compliance": True,
        "target_rule": "Pause up to 6 months: folio remains active & compounding",
        "description": "Valid extended pause query"
    }
]

# Intent classification taxonomy for the compliance gate
INTENT_DEFINITIONS = {
    "AFFORDABILITY": "Inquiries regarding budget crunches, unable to pay current SIP amount, stepping down instalment, or skipping instalments.",
    "DATE_MISMATCH": "Inquiries regarding salary dates, shifting SIP debit date, AutoPay timing, or bank mandate alignment.",
    "PAYMENT_FAILURE": "Inquiries regarding failed debits, Groww penalty policy (₹0), bank bounce fees, CIBIL credit score impact, or paying failed instalments via UPI.",
    "PAUSE_RECOVERY": "Inquiries regarding pausing vs cancelling, safety of invested units, compounding loss of cancellation, or resuming paused SIPs.",
    "UNALLOWED_ADVICE": "Stock or mutual fund recommendations, return guarantees, buy/sell timing, F&O/crypto, or urgent market panic guidance.",
    "GENERAL": "Operational SIP rules, lead times, minimum SIP limits, and Groww platform navigation."
}
