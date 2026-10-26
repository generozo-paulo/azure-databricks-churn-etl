# CRISP-DM: Entendimento de Negócio (Business Understanding)

## 1. Problema de Sinistralidade e Churn em Planos de Saúde
Operadoras de saúde enfrentam o dilema duplo de alta sinistralidade (**Medical Loss Ratio > 85%**) e evasão (churn) de empresas contratantes insatisfeitas com reajustes anuais ou qualidade do atendimento.
A identificação tardia de contas em risco de cancelamento resulta em perda de receita recorrente anual (ARR).

## 2. Solução ETL Distribuída no Azure Databricks
- Unificação de sinistros ambulatoriais, hospitalares e chamados de suporte ao cliente.
- Cálculo distribuído de LTV e razão de sinistralidade.
- Segmentação automática para equipes de Customer Success e Retenção Comercial antes do período de renovação contratual.
