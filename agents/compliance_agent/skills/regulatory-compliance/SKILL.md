---
name: regulatory-compliance
description: Evaluates approved underwriting decisions against regulatory compliance frameworks, AML checks, and sanctions screening, then persists audit records to Spanner. Use when you need to run statutory validations and log audit trails.
---

## Core Objectives
Validate underwriting results against institutional risk and statutory requirements, execute AML and sanctions screening, issue an immutable audit trail ID, and commit the final compliance record to Google Cloud Spanner.

## Evaluation Workflow
1. **Telemetry Review:** Extract the `application_id`, `policy_rules_passed`, and `recommended_limit` from the upstream underwriting state (`underwriting_result`).
2. **Regulatory & AML Verification:** 
   - Execute your `evaluate_regulatory_compliance` skill function using the extracted parameters to generate validation flags (`aml_check_passed`, `sanctions_clear`), `regulatory_notes`, and a unique cryptographic `audit_trail_id`.
    ```bash
   python3 scripts/compliance_logic.py
   ```
3. **Cloud Spanner Persistence:** 
   - Invoke the `persist_compliance_record` tool to commit the finalized compliance payload and audit trail directly to the `ComplianceRecords` table.
4. **Audit Summary:** Output your final regulatory clearance memo summarizing the compliance status and transaction audit reference.
