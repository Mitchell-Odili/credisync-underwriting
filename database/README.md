# CrediSync Underwriting Database (Google Cloud Spanner)

This directory contains operational data schemas for CrediSync Underwriting.

## Configuration
Configure your environment variables in your local `.env` file rather than hardcoding them:

```bash
SPANNER_INSTANCE_ID="your-spanner-instance-id"
SPANNER_DATABASE_ID="your-database-id"
```

## Database Schema
The database is structured into two primary tables to separate core business entities from AI document extraction telemetry:

1. **LoanApplicationRecords**: Stores high-level application metadata submitted by the borrower (applicant name, requested amount, stated income, employment status, and uploaded document references).

2. **IngestionExtractionRecords**: Serves as an immutable audit trail for the ingestion agent's parser outputs, capturing normalization results, tax IDs, confidence scores, and payload summaries.

3. **ValuationRecords**: Tracks the quantitative risk metrics computed during the valuation phase, including credit scores, risk tiers, debt-service coverage ratios (DSCR), collateral market values, and loan-to-value (LTV) ratios.

4. **UnderwritingResults**: Persists the core underwriting evaluation outputs, capturing probabilities of default, recommended lending limits, policy rule validation flags, and institutional risk notes.

5. **ComplianceRecords**: Records statutory compliance, anti-money laundering (AML) clearances, sanctions checks, audit trail identifiers, and regulatory notes for every loan application.


## Setting up the Table
1. Open the Google Cloud Console and navigate to **Cloud Spanner**.
2. Select your instance and create a new database using **Google Standard SQL**.
3. Apply the DDL script found in [schema.sql](schema.sql) to initialize both tables.

## Schema Migrations

Cloud Spanner supports online DDL changes. To alter table structures later without downtime, execute `ALTER TABLE` statements directly in the Spanner console or via client migrations.