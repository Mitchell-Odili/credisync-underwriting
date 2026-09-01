---
name: valuation-extractor
description: Assesses borrower solvency, queries credit bureau risk profiles, computes debt-service coverage ratios (DSCR), and appraises collateral market value to generate structured financial valuation payloads. Use when you need credit risk validation, DSCR calculations, loan-to-value appraisals, or borrower financial solvency checks for a loan application.
---

Follow these steps sequentially to generate valuation extraction payloads.

## Core Objectives
Establish the external financial baseline and collateral worth of an applicant by querying credit risk profiles, calculating solvency metrics, and committing structured `ValuationResult` telemetry to database persistence layers.

## Workflow

1. **Read References:** You MUST read [Valuation Rules](valuation-rules.md) and review the `ValuationResult` model in `shared/schemas.py` before processing.
2. **Credit Risk Scoring:** Interact with bureau verification tools to retrieve credit histories, past default indicators, and composite risk tiers.
3. **Solvency & Cash-Flow Analysis:** Compute Debt-Service Coverage Ratios (DSCR) using verified income metrics and estimated debt obligations.
4. **Collateral & LTV Appraisal:** Assess asset market values and calculate Loan-to-Value (LTV) ratios for secured commercial or retail credit applications.
5. **State Persistence & Telemetry:** Automatically commit structured `ValuationResult` payloads to the Cloud Spanner `ValuationRecords` table and update `tool_context.state["valuation_result"]`.
6. **Execute Valuation:** Run the valuation extraction script to query bureaus, calculate DSCR, and appraise collateral:
  ```bash
  uv run python agents/valuation_agent/agent.py