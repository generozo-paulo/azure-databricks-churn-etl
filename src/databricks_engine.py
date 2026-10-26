import pandas as pd
import numpy as np
from typing import Tuple
from src.schemas import BeneficiaryContractPayload, SilverBeneficiaryProfile, GoldPortfolioKPIs

class DatabricksChurnPipeline:
    """
    Motor distribuído de ETL e Analytics de Churn para Saúde Suplementar (Azure Databricks Spark).
    """

    @staticmethod
    def generate_adls_bronze(n_contracts: int = 2500, random_state: int = 42) -> pd.DataFrame:
        """Gera contratos corporativos e individuais de saúde no Azure Data Lake Storage (Bronze)."""
        np.random.seed(random_state)
        records = []
        tiers = ["INDIVIDUAL", "CORPORATIVO_PME", "CORPORATIVO_PREMIUM"]

        for i in range(n_contracts):
            tier = str(np.random.choice(tiers, p=[0.30, 0.45, 0.25]))
            if tier == "CORPORATIVO_PREMIUM":
                premium = float(np.random.normal(loc=1250, scale=180))
            elif tier == "CORPORATIVO_PME":
                premium = float(np.random.normal(loc=720, scale=90))
            else:
                premium = float(np.random.normal(loc=480, scale=60))
            premium = max(premium, 250.0)

            tenure = int(np.random.randint(2, 72))
            annual_prem = premium * 12

            # Sinistralidade esperada: normal em torno de 75%, com cauda longa de sinistros catastróficos
            mlr = float(np.random.beta(a=4, b=2) * 1.2)
            claims = round(annual_prem * mlr, 2)

            complaints = int(np.random.poisson(lam=1.2 if mlr > 0.85 else 0.4))

            # Churn simulado: alta sinistralidade + reclamações + tempo recente
            churn_prob = (
                (complaints * 0.15) +
                (0.25 if mlr > 0.90 else 0.05) +
                (0.15 if tenure < 12 else 0.0)
            )
            is_active = 0 if (np.random.rand() < min(churn_prob, 0.75)) else 1

            records.append({
                "contract_id": f"CTR-{i+1:06d}",
                "beneficiary_id": f"BEN-{np.random.randint(10000, 99999)}",
                "plan_tier": tier,
                "monthly_premium_brl": round(premium, 2),
                "tenure_months": tenure,
                "claims_cost_12m": claims,
                "n_complaints_csat": complaints,
                "active_contract": is_active
            })

        return pd.DataFrame(records)

    @staticmethod
    def process_silver_profile(bronze_df: pd.DataFrame) -> pd.DataFrame:
        """Transformação Spark Silver: cálculo de MLR, LTV e Score de Risco de Evasão."""
        df = bronze_df.copy()
        annual_revenue = df["monthly_premium_brl"] * 12
        df["mlr_ratio"] = (df["claims_cost_12m"] / annual_revenue).round(4)

        # LTV Projetado (Margem anual * permanência projetada em anos com desconto de 10% a.a.)
        annual_margin = annual_revenue - df["claims_cost_12m"]
        df["predicted_ltv_brl"] = (annual_margin * np.log1p(df["tenure_months"]) * 0.85).round(2)

        # Churn Risk Score (0.0 a 1.0)
        df["churn_risk_score"] = np.clip(
            (df["mlr_ratio"] * 0.40) +
            (df["n_complaints_csat"] * 0.12) +
            (1.0 / np.sqrt(df["tenure_months"]) * 0.25),
            0.05, 0.98
        ).round(4)

        def categorize_risk(score):
            if score >= 0.70:
                return "CRITICAL"
            elif score >= 0.50:
                return "HIGH"
            elif score >= 0.30:
                return "MEDIUM"
            return "LOW"

        df["churn_risk_category"] = df["churn_risk_score"].apply(categorize_risk)

        def recommend_action(row):
            if row["churn_risk_category"] == "CRITICAL":
                return "Negociação Comercial Imediata & Reestruturação de Coparticipação"
            elif row["churn_risk_category"] == "HIGH":
                return "Contato Ativo de Customer Success & Auditoria de Sinistralidade"
            elif row["churn_risk_category"] == "MEDIUM":
                return "Programa Preventivo de Gestão de Crônicos / Atenção Primária"
            return "Manutenção / Upsell de Coberturas"

        df["recommended_retention_action"] = df.apply(recommend_action, axis=1)
        return df

    @staticmethod
    def process_gold_executive_kpis(silver_df: pd.DataFrame) -> GoldPortfolioKPIs:
        """Agregação executiva de carteira (Gold KPI Report)."""
        active_df = silver_df[silver_df["active_contract"] == 1]
        total_active = len(active_df)
        avg_mlr = float(active_df["mlr_ratio"].mean()) if total_active > 0 else 0.0
        annual_premium = float((active_df["monthly_premium_brl"] * 12).sum())
        churn_rate = float(1.0 - (total_active / len(silver_df))) if len(silver_df) > 0 else 0.0

        # Receita em risco (contratos ativos com risco HIGH ou CRITICAL)
        at_risk_df = active_df[active_df["churn_risk_category"].isin(["HIGH", "CRITICAL"])]
        at_risk_rev = float((at_risk_df["monthly_premium_brl"] * 12).sum())

        return GoldPortfolioKPIs(
            total_active_contracts=total_active,
            avg_portfolio_mlr=round(avg_mlr, 4),
            total_annualized_premium=round(annual_premium, 2),
            churn_rate=round(churn_rate, 4),
            at_risk_revenue_brl=round(at_risk_rev, 2)
        )
