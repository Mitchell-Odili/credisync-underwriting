from typing import List, Optional
from pydantic import BaseModel, Field

class LoanApplication(BaseModel):
    """Initial loan application payload submitted by the applicant."""
    application_id: str = Field(..., description="Unique UUID for the loan application")
    applicant_name: str = Field(..., description="Full legal name of the borrower")
    requested_amount: float = Field(..., description="Loan amount requested in USD/KES")
    stated_income: float = Field(..., description="Annual or monthly declared income")
    employment_status: str = Field(..., description="Employment type (e.g., Full-Time, Self-Employed)")
    documents: List[str] = Field(default_factory=list, description="List of uploaded document paths or identifiers")


class FinancialDocumentExtraction(BaseModel):
    """Extracted entities from unstructured financial documents like tax returns or bank statements."""
    application_id: str = Field(..., description="Unique UUID linking this extraction to the loan application")
    legal_entity_name: str = Field(..., description="The official registered business or individual name found in the doc.")
    tax_id: str = Field(..., description="Tax identification number or EIN.")
    stated_annual_revenue: float = Field(..., description="Total annual revenue stated in the documents.")
    total_liabilities: float = Field(..., description="Total liabilities or debt obligations found.")
    document_type: str = Field(..., description="Type of document ingested, e.g., 'tax_return' or 'bank_statement'.")
    confidence_score: float = Field(..., description="Confidence score of the extracted data between 0.0 and 1.0.")


class IngestionResult(BaseModel):
    """Output from the Ingestion Agent after parsing and sanitizing inputs."""
    application_id: str
    status: str = Field("SUCCESS", description="Ingestion processing status")
    normalized_income: float = Field(..., description="Normalized income figure verified after parsing statements")
    extracted_data: Optional[FinancialDocumentExtraction] = Field(None, description="Detailed document extraction breakdown")
    sanitized_payload_summary: str = Field(..., description="Model Armor verified summary of unstructured data")


class ValuationResult(BaseModel):
    application_id: str = Field(..., description="Unique loan application identifier")
    credit_score: int = Field(..., description="Retrieved bureau credit score")
    risk_tier: str = Field(..., description="Assigned risk tier (e.g., Low, Medium, High)")
    debt_service_coverage_ratio: float = Field(..., description="DSCR calculated from income and liabilities")
    collateral_market_value: Optional[float] = Field(None, description="Appraised market value of pledged assets")
    loan_to_value_ratio: Optional[float] = Field(None, description="LTV ratio if collateral is present")
    valuation_notes: List[str] = Field(default_factory=list, description="External verification notes or flags")


class UnderwritingResult(BaseModel):
    """Output from the Underwriting Agent detailing risk computation and credit rules."""
    application_id: str
    probability_of_default: float = Field(..., description="Calculated probability of default (0.0 to 1.0)")
    recommended_limit: float = Field(..., description="Maximum recommended credit limit")
    policy_rules_passed: bool = Field(..., description="Whether institutional credit rules were satisfied")
    notes: str = Field(..., description="Underwriting decision rationale")


class ComplianceResult(BaseModel):
    """Output from the Compliance Agent acting as the regulatory gatekeeper."""
    application_id: str
    aml_check_passed: bool = Field(..., description="Status of Anti-Money Laundering verification")
    sanctions_clear: bool = Field(..., description="Whether applicant passed sanctions screening")
    audit_trail_id: str = Field(..., description="Immutable compliance log hash or ID")
    regulatory_notes: str = Field(..., description="Statutory limit validation details")


class LendingPackage(BaseModel):
    """Final unified lending package assembled by the Dispatcher Agent."""
    application_id: str
    overall_status: str = Field(..., description="Final decision (e.g., APPROVED, REJECTED, REVISE)")
    summary_notes: str = Field(..., description="Synthesized executive summary of the underwriting and compliance review.")