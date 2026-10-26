# Especificação Contratual (SDD) - Azure Databricks Churn & Lifetime Value (LTV) ETL

## 1. Escopo & Objetivos
Pipeline corporativo de ETL distribuído simulando um ambiente **Azure Databricks** para operadoras de saúde e planos de saúde corporativos.
Processa:
1. Ingestão de logs de sinistralidade, coparticipação e cancelamentos contratuais (ADLS Gen2).
2. Transformação distribuída com cálculo de Lifetime Value (LTV), razão de sinistralidade (Medical Loss Ratio - MLR) e score de risco de churn.
3. Carga otimizada para Delta Lake e visualização analítica para comitês executivos.

## 2. Contratos de Entrada (Pydantic)

### 2.1 Contrato de Beneficiário (`BeneficiaryContractPayload`)
- `contract_id`: str
- `beneficiary_id`: str
- `plan_tier`: Literal["INDIVIDUAL", "CORPORATIVO_PME", "CORPORATIVO_PREMIUM"]
- `monthly_premium_brl`: float
- `tenure_months`: int
- `claims_cost_12m`: float
- `n_complaints_csat`: int
- `active_contract`: int # 1 = ativo, 0 = cancelado (churn)

## 3. Contratos de Saída (Pydantic)

### 3.1 Perfil Analítico Delta Silver (`SilverBeneficiaryProfile`)
- `contract_id`: str
- `beneficiary_id`: str
- `plan_tier`: str
- `mlr_ratio`: float # claims_cost_12m / (monthly_premium * 12)
- `predicted_ltv_brl`: float
- `churn_risk_score`: float
- `churn_risk_category`: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
- `recommended_retention_action`: str

### 3.2 Relatório Executivo de Carteira Gold (`GoldPortfolioKPIs`)
- `total_active_contracts`: int
- `avg_portfolio_mlr`: float
- `total_annualized_premium`: float
- `churn_rate`: float
- `at_risk_revenue_brl`: float
