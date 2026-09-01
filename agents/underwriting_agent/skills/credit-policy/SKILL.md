---
name: credit-policy
description: Evaluates borrower valuation metrics against institutional lending guidelines, calculating default probabilities, approved loan limits, and policy compliance. Use when you need to run credit risk rules on DSCR and LTV telemetry.
---

## Core Objectives
Assess financial valuation metrics (DSCR, LTV, stated income) against institutional risk parameters, determine eligibility, and compute maximum recommended credit limits before persisting the decision.

## Evaluation Workflow
1. **Telemetry Review:** Extract the Debt-Service Coverage Ratio (DSCR), Loan-to-Value (LTV), and stated income from upstream valuation state (`val_result`).
2. **Policy Compliance Check:** 
   - Execute your `assess_credit` function from `policy_logic` using the extracted parameters to evaluate whether institutional thresholds are met ($\ge 1.25$ DSCR, $\le 0.80$ LTV).
   ```bash
   python3 scripts/policy_logic.py
   ```
   - Review the calculated probability of default and approved limit returned by the function.
3. **Persistence Trigger:** Pass the evaluated results into `persist_underwriting_record` to commit the data to Google Cloud Spanner and update the session state.
