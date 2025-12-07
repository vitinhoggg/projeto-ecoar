from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente (se quiser usar .env)
load_dotenv()
MONGO_URI = os.getenv(
    "MONGO_URI",
    ""
)

NOME_DO_BANCO = "ecoar"

client = MongoClient(MONGO_URI)
db = client[NOME_DO_BANCO]

def calcular_pontuacao(desempenho):
    pontos = 0
    motivos = []

    if desempenho.get("frequencia", 100) < 70:
        pontos += 2
        motivos.append("baixa frequência")

    if desempenho.get("media_geral", 10) < 6.0:
        pontos += 1
        motivos.append("média baixa")

    if desempenho.get("faltas", 0) > 15:
        pontos += 2
        motivos.append("faltas excessivas")

    if desempenho.get("participacao_plataforma", 100) < 50:
        pontos += 1
        motivos.append("baixa participação online")

    return pontos, motivos

def classificar_risco(pontos):
    if pontos <= 1:
        return "Baixo"
    elif pontos <= 3:
        return "Médio"
    else:
        return "Alto"

def atualizar_riscos():
    todos = db.desempenho.find()
    for d in todos:
        matricula = d["matricula"]
        pontos, motivos = calcular_pontuacao(d)
        nivel = classificar_risco(pontos)

        registro = {
            "matricula": matricula,
            "risco_ml_evasao": nivel,          # nome alinhado com app.py
            "risco_pontuacao_ml": pontos,      # nome alinhado com app.py
            "motivos": motivos
        }

        db.risco.update_one({"matricula": matricula}, {"$set": registro}, upsert=True)
        print(f"[RULE] {matricula} -> {nivel} (pontos {pontos})")

if __name__ == "__main__":
    atualizar_riscos()
