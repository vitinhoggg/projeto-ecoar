import streamlit as st
from pymongo import MongoClient
import pandas as pd

# ==========================================
# CONEXÃO COM O MONGODB
# ==========================================
client = MongoClient(
    
)
db = client.ecoar

alunos_col = db.alunos
desempenho_col = db.desempenho

# ==========================================
# CARREGAR DADOS
# ==========================================
df_alunos = pd.DataFrame(list(alunos_col.find()))
df_desempenho = pd.DataFrame(list(desempenho_col.find()))

# Remover _id
for _df in (df_alunos, df_desempenho):
    if "_id" in _df.columns:
        _df.drop("_id", axis=1, inplace=True)

# Verifica coluna matricula
if "matricula" not in df_alunos.columns:
    st.error("Erro: a coleção 'alunos' precisa ter a coluna 'matricula'.")
    st.stop()

# ==========================================
# MERGE DAS COLEÇÕES
# ==========================================
df = df_alunos.merge(df_desempenho, on="matricula", how="left")
linhas = len(df)

# ==========================================
# FUNÇÕES AUXILIARES
# ==========================================
def safe_series(col, default=None):
    if col in df.columns:
        return df[[col]].squeeze()
    else:
        return pd.Series([default] * linhas)

def safe_unique_sorted_strings(series):
    vals = series.fillna("Não informado").astype(str).unique().tolist()
    try:
        return sorted(vals)
    except:
        return sorted(vals, key=lambda x: str(x))

# ==========================================
# TRATAR COLUNAS TEXTUAIS
# ==========================================
df["periodo_atual"] = safe_series("periodo_atual", "Não informado").fillna("Não informado").astype(str)
df["status"] = safe_series("status", "Ativo").fillna("Ativo").astype(str)
df["curso"] = safe_series("curso", "Não informado").fillna("Não informado").astype(str)

# ==========================================
# TRATAR COLUNAS NUMÉRICAS
# ==========================================
df["media_geral"] = pd.to_numeric(safe_series("media_geral", None), errors="coerce").fillna(0)

# Criar risco com base na média geral
df["risco_ml_evasao"] = df["media_geral"].apply(lambda x: 1 if x < 6 else (0.5 if x < 7.5 else 0))
df["risco_pontuacao_ml"] = df["risco_ml_evasao"] * 10

# ==========================================
# CATEGORIZAR RISCO
# ==========================================
def categorize_risk(value):
    try:
        v = float(value)
    except:
        v = 0.0
    if v >= 0.7:
        return "Alto"
    elif v >= 0.4:
        return "Médio"
    else:
        return "Baixo"

df["categoria_risco"] = df["risco_ml_evasao"].apply(categorize_risk)

# ==========================================
# LAYOUT / TÍTULO
# ==========================================
st.set_page_config(layout="wide")
st.title("📊 Dashboard ECOAR – Análise Acadêmica & Risco de Evasão")
st.write("Painel completo com indicadores e filtros.")

# ==========================================
# OPÇÕES DOS FILTROS
# ==========================================
curso_options = ["Todos"] + safe_unique_sorted_strings(df["curso"])
periodo_options = ["Todos"] + safe_unique_sorted_strings(df["periodo_atual"])
risco_options = ["Todos", "Baixo", "Médio", "Alto"]

# ==========================================
# FILTROS – SIDEBAR
# ==========================================
st.sidebar.header("🔍 Filtros")
curso_filtro = st.sidebar.selectbox("Filtrar por Curso", curso_options)
periodo_filtro = st.sidebar.selectbox("Filtrar por Período", periodo_options)
risco_filtro = st.sidebar.selectbox("Filtrar por Risco", risco_options)

df_filtrado = df.copy()

if curso_filtro != "Todos":
    df_filtrado = df_filtrado[df_filtrado["curso"].astype(str) == str(curso_filtro)]

if periodo_filtro != "Todos":
    df_filtrado = df_filtrado[df_filtrado["periodo_atual"].astype(str) == str(periodo_filtro)]

if risco_filtro != "Todos":
    df_filtrado = df_filtrado[df_filtrado["categoria_risco"] == risco_filtro]

# ==========================================
# TABELA FILTRADA
# ==========================================
st.write("### 📄 Dados Filtrados")
st.dataframe(df_filtrado)

# ==========================================
# KPIs
# ==========================================
total = len(df) if len(df) > 0 else 1
media_geral = df["media_geral"].mean() if len(df) > 0 else 0

num_alto = df["categoria_risco"].value_counts().get("Alto", 0)
num_medio = df["categoria_risco"].value_counts().get("Médio", 0)

perc_alto = (num_alto / total) * 100
perc_medio = (num_medio / total) * 100

col1, col2, col3, col4 = st.columns(4)
col1.metric("👨‍🎓 Total de Alunos", len(df))
col2.metric("📘 Média Geral da Turma", f"{media_geral:.2f}")
col3.metric("🚨 % Alto Risco", f"{perc_alto:.1f}%")
col4.metric("🟡 % Risco Médio", f"{perc_medio:.1f}%")

# ==========================================
# GRÁFICOS
# ==========================================
st.write("## 📊 Visualizações")

if not df_filtrado["media_geral"].empty:
    st.write("### Distribuição da Média Geral")
    st.bar_chart(df_filtrado["media_geral"])

if not df_filtrado["risco_ml_evasao"].empty:
    st.write("### Distribuição do Risco de Evasão (ML)")
    st.bar_chart(df_filtrado["risco_ml_evasao"])

st.write("### Categoria de Risco")
cat_counts = df_filtrado["categoria_risco"].value_counts().reindex(["Baixo", "Médio", "Alto"], fill_value=0)
st.bar_chart(cat_counts)

# ==========================================
# TABELA ALTO RISCO
# ==========================================
st.write("## 🚨 Alunos em Alto Risco de Evasão")
st.dataframe(df[df["categoria_risco"] == "Alto"])
