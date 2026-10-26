import streamlit as st
import pandas as pd
import plotly.express as px
from src.databricks_engine import DatabricksChurnPipeline

st.set_page_config(
    page_title="Azure Databricks Healthcare Churn & LTV ETL",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Azure Databricks Churn & Lifetime Value (LTV) ETL Pipeline")
st.markdown("""
Pipeline analítico distribuído para saúde suplementar. Processamento Delta Lake no **Azure Databricks** integrando sinistros, reclamações e previsão de evasão (churn) de carteiras corporativas.
""")

@st.cache_data
def load_databricks_data():
    bronze = DatabricksChurnPipeline.generate_adls_bronze(n_contracts=2000)
    silver = DatabricksChurnPipeline.process_silver_profile(bronze)
    gold = DatabricksChurnPipeline.process_gold_executive_kpis(silver)
    return bronze, silver, gold

bronze_df, silver_df, gold_kpis = load_databricks_data()

tab1, tab2, tab3 = st.tabs(["📊 Visão Executiva Gold", "🎯 Segmentação de Risco Silver", "🏗️ Delta Lake Medallion Pipeline"])

with tab1:
    st.subheader("Painel Executivo de Sinistralidade (MLR) e Receita em Risco")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Contratos Ativos", f"{gold_kpis.total_active_contracts:,}")
    c2.metric("Sinistralidade Média (MLR)", f"{gold_kpis.avg_portfolio_mlr:.1%}")
    c3.metric("Taxa de Evasão (Churn Histórico)", f"{gold_kpis.churn_rate:.1%}")
    c4.metric("Receita em Risco (Anual)", f"R$ {gold_kpis.at_risk_revenue_brl:,.2f}")

    col1, col2 = st.columns(2)
    with col1:
        fig1 = px.histogram(
            silver_df,
            x="mlr_ratio",
            color="churn_risk_category",
            title="Distribuição de Sinistralidade (MLR) por Categoria de Risco",
            labels={"mlr_ratio": "Sinistralidade (Claims / Prêmio)", "churn_risk_category": "Risco de Churn"},
            color_discrete_map={"LOW": "#2ca02c", "MEDIUM": "#ff7f0e", "HIGH": "#d62728", "CRITICAL": "#7f1717"}
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = px.box(
            silver_df,
            x="plan_tier",
            y="predicted_ltv_brl",
            color="plan_tier",
            title="Lifetime Value (LTV) Projetado por Segmento de Plano",
            labels={"predicted_ltv_brl": "LTV Projetado (R$)", "plan_tier": "Categoria do Plano"}
        )
        st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.subheader("Fila de Ação de Retenção Comercial & Prevenção (Silver Delta View)")
    st.markdown("Contratos ordenados prioritariamente por probabilidade de cancelamento:")
    retention_queue = silver_df[silver_df["active_contract"] == 1].sort_values("churn_risk_score", ascending=False)
    st.dataframe(
        retention_queue[[
            "contract_id", "plan_tier", "monthly_premium_brl", "mlr_ratio", 
            "churn_risk_score", "churn_risk_category", "recommended_retention_action"
        ]].head(50),
        use_container_width=True
    )

with tab3:
    st.subheader("Topologia da Solução na Nuvem (Azure Databricks + ADLS Gen2)")
    st.markdown("""
    - **Bronze Ingestion**: Azure Data Lake Storage (ADLS Gen2) conectado via Delta Autoloader.
    - **Silver Transformations**: PySpark Jobs com particionamento por `plan_tier` e `tenure_group`.
    - **Gold Layer**: Power BI DirectQuery / Databricks SQL Warehouses para comitês executivos de sinistralidade.
    """)
