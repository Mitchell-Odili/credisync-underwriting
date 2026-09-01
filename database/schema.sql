CREATE TABLE LoanApplicationRecords (
    application_id STRING(MAX) NOT NULL,
    applicant_name STRING(MAX) NOT NULL,
    requested_amount FLOAT64 NOT NULL,
    stated_income FLOAT64 NOT NULL,
    employment_status STRING(MAX) NOT NULL,
    documents ARRAY<STRING(MAX)>,
    created_at TIMESTAMP OPTIONS (allow_commit_timestamp = true),
    last_updated TIMESTAMP OPTIONS (allow_commit_timestamp = true)
) PRIMARY KEY (application_id);

CREATE TABLE IngestionExtractionRecords (
    application_id STRING(MAX) NOT NULL,
    extraction_timestamp TIMESTAMP OPTIONS (allow_commit_timestamp = true),
    status STRING(MAX),
    normalized_income FLOAT64,
    sanitized_payload_summary STRING(MAX),
    -- Fields from the nested FinancialDocumentExtraction model:
    legal_entity_name STRING(MAX),
    tax_id STRING(MAX),
    stated_annual_revenue FLOAT64,
    total_liabilities FLOAT64,
    document_type STRING(MAX),
    confidence_score FLOAT64,
) PRIMARY KEY (application_id);

CREATE TABLE ValuationRecords (
    application_id STRING(MAX) NOT NULL,
    valuation_timestamp TIMESTAMP OPTIONS (allow_commit_timestamp = true),
    credit_score INT64,
    risk_tier STRING(MAX),
    debt_service_coverage_ratio FLOAT64,
    collateral_market_value FLOAT64,
    loan_to_value_ratio FLOAT64,
    valuation_notes ARRAY<STRING(MAX)>,
) PRIMARY KEY (application_id);

CREATE TABLE UnderwritingResults (
    application_id STRING(MAX) NOT NULL,
    probability_of_default FLOAT64 NOT NULL,
    recommended_limit FLOAT64 NOT NULL,
    policy_rules_passed BOOL NOT NULL,
    notes STRING(MAX),
    last_updated TIMESTAMP OPTIONS (allow_commit_timestamp = true)
) PRIMARY KEY (application_id);