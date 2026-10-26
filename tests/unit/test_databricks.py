import pytest
from src.databricks_engine import DatabricksChurnPipeline

def test_adls_bronze_generation():
    bronze = DatabricksChurnPipeline.generate_adls_bronze(n_contracts=100)
    assert len(bronze) == 100
    assert "monthly_premium_brl" in bronze.columns
    assert "claims_cost_12m" in bronze.columns

def test_silver_profile_transform():
    bronze = DatabricksChurnPipeline.generate_adls_bronze(n_contracts=200)
    silver = DatabricksChurnPipeline.process_silver_profile(bronze)
    assert len(silver) == 200
    assert "mlr_ratio" in silver.columns
    assert "churn_risk_score" in silver.columns
    assert "churn_risk_category" in silver.columns
    assert (silver["churn_risk_score"] >= 0.0).all()
    assert (silver["churn_risk_score"] <= 1.0).all()

def test_gold_kpis_calculation():
    bronze = DatabricksChurnPipeline.generate_adls_bronze(n_contracts=300)
    silver = DatabricksChurnPipeline.process_silver_profile(bronze)
    gold = DatabricksChurnPipeline.process_gold_executive_kpis(silver)
    assert gold.total_active_contracts > 0
    assert gold.avg_portfolio_mlr > 0.0
    assert gold.total_annualized_premium > 0.0
    assert 0.0 <= gold.churn_rate <= 1.0
