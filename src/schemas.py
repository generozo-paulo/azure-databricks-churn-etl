from pydantic import BaseModel, Field
from typing import Literal

class BeneficiaryContractPayload(BaseModel):
    contract_id: str
    beneficiary_id: str
    plan_tier: Literal["INDIVIDUAL", "CORPORATIVO_PME", "CORPORATIVO_PREMIUM"]
    monthly_premium_brl: float
    tenure_months: int
    claims_cost_12m: float
    n_complaints_csat: int
    active_contract: int

class SilverBeneficiaryProfile(BaseModel):
    contract_id: str
    beneficiary_id: str
    plan_tier: str
    mlr_ratio: float
    predicted_ltv_brl: float
    churn_risk_score: float
    churn_risk_category: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    recommended_retention_action: str

class GoldPortfolioKPIs(BaseModel):
    total_active_contracts: int
    avg_portfolio_mlr: float
    total_annualized_premium: float
    churn_rate: float
    at_risk_revenue_brl: float
