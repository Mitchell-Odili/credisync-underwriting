def evaluate_risk_thresholds(
    probability_of_default: float,
    recommended_limit: float,
    aml_check_passed: bool,
    sanctions_clear: bool,
    policy_rules_passed: bool
) -> dict:
    """Deterministically validates underwriting exposure and compliance status against institutional risk appetite."""
    
    issues = []
    
    if not policy_rules_passed:
        issues.append("POLICY BREACH: Upstream credit policy rules failed.")
        
    if not aml_check_passed or not sanctions_clear:
        issues.append("REGULATORY BREACH: Mandatory AML or sanctions checks failed.")
        
    # Risk appetite guardrail: High probability of default cannot have a massive limit
    if probability_of_default > 0.05 and recommended_limit > 500000.0:
        issues.append("RISK EXPOSURE BREACH: Probability of default (>0.05) is too high for a facility limit exceeding 500k.")

    is_approved = len(issues) == 0
    
    return {
        "approved": is_approved,
        "risk_issues": issues,
        "summary": "All risk and compliance guardrails satisfied." if is_approved else f"Rejected due to {len(issues)} risk violation(s)."
    }