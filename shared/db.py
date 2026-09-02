import os
from google.cloud import spanner
from shared.schemas import LoanApplication, IngestionResult, ValuationResult, UnderwritingResult, ComplianceResult, LendingPackage


class SpannerClientWrapper:
    def __init__(self):
        self.client = spanner.Client()
        self.instance_id = os.getenv("SPANNER_INSTANCE_ID", "floodpulse-nairobi-lab")
        self.database_id = os.getenv("SPANNER_DATABASE_ID", "credisync-underwriting-db")
        
        self.instance = self.client.instance(self.instance_id)
        self.database = self.instance.database(self.database_id)

    def save_loan_application(self, loan_app: LoanApplication) -> None:
        """Upserts a LoanApplication payload into Cloud Spanner using native arrays."""
        
        def insert_or_update_transaction(transaction):
            row_data = {
                "application_id": loan_app.application_id,
                "applicant_name": loan_app.applicant_name,
                "requested_amount": loan_app.requested_amount,
                "stated_income": loan_app.stated_income,
                "employment_status": loan_app.employment_status,
                "documents": loan_app.documents,  # Maps cleanly to Spanner ARRAY<STRING(MAX)>
                "last_updated": spanner.COMMIT_TIMESTAMP,
            }
            
            transaction.insert_or_update(
                table="LoanApplicationRecords",
                columns=list(row_data.keys()),
                values=[list(row_data.values())]
            )

        self.database.run_in_transaction(insert_or_update_transaction)

    def save_ingestion_result(self, ingestion_result: IngestionResult) -> None:
        """Upserts an IngestionResult payload into the IngestionExtractionRecords table."""
        
        def insert_or_update_transaction(transaction):
            # Extract nested data safely if present
            ext = ingestion_result.extracted_data
            
            row_data = {
                "application_id": ingestion_result.application_id,
                "extraction_timestamp": spanner.COMMIT_TIMESTAMP,
                "status": ingestion_result.status,
                "normalized_income": ingestion_result.normalized_income,
                "sanitized_payload_summary": ingestion_result.sanitized_payload_summary,
                "legal_entity_name": ext.legal_entity_name if ext else None,
                "tax_id": ext.tax_id if ext else None,
                "stated_annual_revenue": ext.stated_annual_revenue if ext else None,
                "total_liabilities": ext.total_liabilities if ext else None,
                "document_type": ext.document_type if ext else None,
                "confidence_score": ext.confidence_score if ext else None,
            }
            
            transaction.insert_or_update(
                table="IngestionExtractionRecords",
                columns=list(row_data.keys()),
                values=[list(row_data.values())]
            )

        self.database.run_in_transaction(insert_or_update_transaction)
    
    def save_valuation_result(self, val_result: ValuationResult) -> None:
        """Upserts a ValuationResult payload into the ValuationRecords table."""
        
        def insert_or_update_transaction(transaction):
            row_data = {
                "application_id": val_result.application_id,
                "valuation_timestamp": spanner.COMMIT_TIMESTAMP,
                "credit_score": val_result.credit_score,
                "risk_tier": val_result.risk_tier,
                "debt_service_coverage_ratio": val_result.debt_service_coverage_ratio,
                "collateral_market_value": val_result.collateral_market_value,
                "loan_to_value_ratio": val_result.loan_to_value_ratio,
                "valuation_notes": val_result.valuation_notes,
            }
            
            transaction.insert_or_update(
                table="ValuationRecords",
                columns=list(row_data.keys()),
                values=[list(row_data.values())]
            )

        self.database.run_in_transaction(insert_or_update_transaction)

    def save_underwriting_result(self, result: UnderwritingResult) -> None:
        """Upserts an UnderwritingResult payload into the UnderwritingResults table."""
        
        def insert_or_update_transaction(transaction):
            row_data = {
                "application_id": result.application_id,
                "probability_of_default": result.probability_of_default,
                "recommended_limit": result.recommended_limit,
                "policy_rules_passed": result.policy_rules_passed,
                "notes": result.notes,
                "last_updated": spanner.COMMIT_TIMESTAMP,
            }
            
            transaction.insert_or_update(
                table="UnderwritingResults",
                columns=list(row_data.keys()),
                values=[list(row_data.values())]
            )

        self.database.run_in_transaction(insert_or_update_transaction)

    def save_compliance_result(self, result: ComplianceResult) -> None:
        """Upserts a ComplianceResult payload into the ComplianceRecords table."""
        
        def insert_or_update_transaction(transaction):
            row_data = {
                "application_id": result.application_id,
                "compliance_timestamp": spanner.COMMIT_TIMESTAMP,
                "aml_check_passed": result.aml_check_passed,
                "sanctions_clear": result.sanctions_clear,
                "audit_trail_id": result.audit_trail_id,
                "regulatory_notes": result.regulatory_notes,
            }
            
            transaction.insert_or_update(
                table="ComplianceRecords",
                columns=list(row_data.keys()),
                values=[list(row_data.values())]
            )

        self.database.run_in_transaction(insert_or_update_transaction)

    def save_lending_package(self, package: LendingPackage) -> None:
        """Upserts a LendingPackage payload into the LendingPackages table."""
        
        def insert_or_update_transaction(transaction):
            row_data = {
                "application_id": package.application_id,
                "overall_status": package.overall_status,
                "summary_notes": package.summary_notes,
                "generated_at": spanner.COMMIT_TIMESTAMP,
            }
            
            transaction.insert_or_update(
                table="LendingPackages",
                columns=list(row_data.keys()),
                values=[list(row_data.values())]
            )

        self.database.run_in_transaction(insert_or_update_transaction)

# Singleton instance for tool imports
db_client = SpannerClientWrapper()