import os
from google.cloud import spanner
from shared.schemas import LoanApplication

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

# Singleton instance for tool imports
db_client = SpannerClientWrapper()