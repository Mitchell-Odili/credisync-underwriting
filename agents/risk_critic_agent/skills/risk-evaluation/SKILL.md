---
name: risk-evaluation
description: Programmatically evaluates underwriting telemetry and compliance records against institutional risk appetite rules. Use to run deterministic credit risk checks.
---

## Core Objectives
Execute programmatic checks against underwriting metrics and compliance statuses to catch risk appetite breaches, policy mismatches, or regulatory holds.

## Evaluation Workflow
1. **Telemetry Extraction:** Extract `probability_of_default`, `recommended_limit`, and `policy_rules_passed` from the underwriting state, along with `aml_check_passed` and `sanctions_clear` from the compliance state.
2. **Deterministic Risk Assessment:**
   - Execute your `evaluate_risk_thresholds` skill function using the extracted values:
   ```bash
   python3 scripts/risk_evaluation_logic.py