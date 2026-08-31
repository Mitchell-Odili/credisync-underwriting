# CrediSync Underwriting Database (Google Cloud Spanner)

This directory contains operational data schemas for CrediSync Underwriting.

## Configuration
Configure your environment variables in your local `.env` file rather than hardcoding them:

```bash
SPANNER_INSTANCE_ID="your-spanner-instance-id"
SPANNER_DATABASE_ID="your-database-id"
```

## Setting up the Table
1. Open the Google Cloud Console and navigate to **Cloud Spanner**.
2. Select your instance and create a new database using **Google Standard SQL**.
3. Apply the DDL script found in [schema.sql](schema.sql) to initialize the `LoanApplicationRecords` table.

## Schema Migrations

Cloud Spanner supports online DDL changes. To alter the table structure later without downtime, execute `ALTER TABLE` statements directly in the Spanner console or via client migrations.