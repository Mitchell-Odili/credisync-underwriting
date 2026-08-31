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