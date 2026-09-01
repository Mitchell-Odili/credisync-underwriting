def assess_credit(
    application_id: str,
    stated_income: float | str,
    debt_service_coverage_ratio: float | str,
    loan_to_value_ratio: float | str
) -> dict:
    """Evaluates institutional credit thresholds, computes default risk, and determines borrowing limits."""
    
    # Defensive casting
    if isinstance(stated_income, str):
        stated_income = float(stated_income.replace("$", "").replace(",", "").strip())
    if isinstance(debt_service_coverage_ratio, str):
        debt_service_coverage_ratio = float(debt_service_coverage_ratio.strip())
    if isinstance(loan_to_value_ratio, str):
        loan_to_value_ratio = float(loan_to_value_ratio.replace("%", "").strip()) / (100.0 if "%" in loan_to_value_ratio else 1.0)

    # Core Policy Logic
    policy_passed = debt_service_coverage_ratio >= 1.25 and loan_to_value_ratio <= 0.80
    
    if debt_service_coverage_ratio > 1.40 and loan_to_value_ratio < 0.70:
        prob_default = 0.03
    elif policy_passed:
        prob_default = 0.08
    else:
        prob_default = 0.25

    recommended_limit = stated_income * 0.35 if policy_passed else 0.0
    
    notes = (
        "Successfully met institutional credit policy rules (DSCR >= 1.25, LTV <= 0.80)."
        if policy_passed
        else "Declined/Referred: Failed minimum DSCR or maximum LTV institutional thresholds."
    )

    return {
        "application_id": application_id,
        "probability_of_default": prob_default,
        "recommended_limit": recommended_limit,
        "policy_rules_passed": policy_passed,
        "notes": notes
    }

