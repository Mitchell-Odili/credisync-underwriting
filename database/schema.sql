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