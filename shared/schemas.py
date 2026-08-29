from datetime import datetime
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

class IngestionResult(BaseModel):
    """Output from the Ingestion Agent after parsing and sanitizing inputs."""
    application_id: str
    status: str = Field("SUCCESS", description="Ingestion processing status")
    normalized_income: float = Field(..., description="Normalized income figure verified after parsing statements")
    sanitized_payload_summary: str = Field(..., description="Model Armor verified summary of unstructured data")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ValuationResult(BaseModel):
    """Output from the Valuation Agent covering credit scores and asset pricing."""
    application_id: str
    credit_bureau_score: int = Field(..., description="Credit score retrieved from external bureaus")
    collateral_value: float = Field(..., description="Appraised asset or collateral valuation")
    risk_tier: str = Field(..., description="Assigned risk tier (e.g., Low, Medium, High)")

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
    ingestion: IngestionResult
    valuation: ValuationResult
    underwriting: UnderwritingResult
    compliance: ComplianceResult
    generated_at: datetime = Field(default_factory=datetime.utcnow)