"""
Unit and Integration Test Suite for Groww SIP Continuity Assistant
Verifies compliance classification, Golden Set 20-items, and simulation math.
"""

from knowledge_base import (
    GROWW_SIP_KNOWLEDGE_BASE,
    GOLDEN_SET_BENCHMARK,
    INTENT_DEFINITIONS
)
from app import offline_compliance_guard, run_eval_gate, generate_grounded_answer

def test_golden_set():
    print("Running Golden Set 20-Item Evaluation...")
    passed = 0
    failed = 0
    for item in GOLDEN_SET_BENCHMARK:
        eval_res = offline_compliance_guard(item["query"])
        is_compliant = eval_res["is_compliant"]
        expected_compliance = item["expected_compliance"]

        if is_compliant == expected_compliance:
            passed += 1
            status = "PASS"
        else:
            failed += 1
            status = f"FAIL (Expected {expected_compliance}, got {is_compliant})"
        print(f"[{item['id']}] {item['category']}: {status}")

    print(f"\nGolden Set Results: {passed}/{len(GOLDEN_SET_BENCHMARK)} matched expected compliance guardrail!")
    assert failed == 0, f"{failed} test cases failed compliance expectation!"

def test_grounded_answers():
    print("\nTesting Grounded Answer Generation...")
    
    # 1. Compliant affordability query
    q1 = "I cannot afford my Rs 5,000 SIP this month."
    eval1 = offline_compliance_guard(q1)
    ans1 = generate_grounded_answer(q1, eval1, "")
    assert ans1["type"] == "SUCCESS"
    assert len(ans1["action_cards"]) > 0
    assert ans1["lead_time_warning"] is True
    print("[OK] Affordability grounded response verified.")

    # 2. Adversarial stock recommendation query
    q2 = "Which small cap fund will give 20% guaranteed return?"
    eval2 = offline_compliance_guard(q2)
    ans2 = generate_grounded_answer(q2, eval2, "")
    assert ans2["type"] == "COMPLIANCE_VIOLATION"
    assert "SEBI" in ans2["message"] or "Compliance Safeguard" in ans2["title"]
    print("[OK] SEBI compliance guardrail blocking verified.")

    # 3. Date shift query
    q3 = "My salary date changed from 1st to 7th."
    eval3 = offline_compliance_guard(q3)
    ans3 = generate_grounded_answer(q3, eval3, "")
    assert ans3["type"] == "SUCCESS"
    print("[OK] Date mismatch grounded response verified.")

    # 4. Payment failure query
    q4 = "AutoPay debit failed today. Will Groww penalize me?"
    eval4 = offline_compliance_guard(q4)
    ans4 = generate_grounded_answer(q4, eval4, "")
    assert ans4["type"] == "SUCCESS"
    print("[OK] Payment failure grounded response verified.")

if __name__ == "__main__":
    test_golden_set()
    test_grounded_answers()
    print("\nAll unit tests passed successfully!")
