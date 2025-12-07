# dashboard.py
import os
import pandas as pd
import matplotlib.pyplot as plt
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = ""

# Banco de Dados e Coleção:
NOME_DO_BANCO = "ecoar"

client = MongoClient(MONGO_URI)
db = client[NOME_DO_BANCO]

def plot_risco_distribution():
    riscos = list(db.risco.find())
    df = pd.DataFrame(riscos)
    if df.empty:
        print("Coleção 'risco' vazia — rode calcular_risco.py ou predict_model.py primeiro.")
        return

    # Use 'risco_evasao' se existir, fallback para 'risco_evasao_ml' se não
    if "risco_evasao" in df:
        col = "risco_evasao"
    else:
        col = "risco_evasao_ml"

    counts = df[col].value_counts()
    counts.plot(kind="bar")
    plt.title("Distribuição de risco (rule-based / ML)")
    plt.xlabel("Nível de risco")
    plt.ylabel("Quantidade de alunos")
    plt.tight_layout()
    plt.show()

def plot_media_por_curso():
    # join simples entre alunos e desempenho
    alunos = pd.DataFrame(list(db.alunos.find()))
    desempenho = pd.DataFrame(list(db.desempenho.find()))
    df = desempenho.merge(alunos[["matricula","curso"]], on="matricula", how="left")
    if df.empty:
        print("Dados insuficientes para plotagem.")
        return
    grouped = df.groupby("curso")["media_geral"].mean().sort_values()
    grouped.plot(kind="barh")
    plt.title("Média geral por curso")
    plt.xlabel("Média geral")
    plt.tight_layout()
    plt.show()

def plot_frequencia_vs_media():
    desempenho = pd.DataFrame(list(db.desempenho.find()))
    if desempenho.empty:
        print("Nenhum desempenho encontrado.")
        return
    plt.scatter(desempenho["frequencia"], desempenho["media_geral"])
    plt.title("Frequência vs Média Geral")
    plt.xlabel("Frequência (%)")
    plt.ylabel("Média geral")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    plot_risco_distribution()
    plot_media_por_curso()
    plot_frequencia_vs_media()
