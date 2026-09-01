---
name: financial-document-extraction-parser
description: Extracts, normalizes, and audits unstructured financial documents such as tax returns, P&L statements, and bank statements. Use when you need to parse accounting line items, normalize currencies, or audit financial records for a loan application. 
---

## Core Objectives
Extract standard accounting line items from unstructured text or OCR output, normalize currencies to KES/USD, and calculate baseline debt-to-income indicators before populating the `FinancialDocumentExtraction` schema.

## Extraction Workflow
1. **Document Classification:** Identify whether the uploaded file is a corporate tax return, audited P&L, or personal bank statement.
2. **Entity Recognition:** Locate the legal business name, Tax ID / PIN, and reporting period.
3. **Financial Normalization:** 
   - Parse revenue and liability figures using `parser_utils.clean_currency()`.
   - Flag discrepancies where stated income diverges significantly from transaction flows.
4. **Confidence Scoring:** Assign a confidence score (0.0 to 1.0) based on document legibility and completeness.