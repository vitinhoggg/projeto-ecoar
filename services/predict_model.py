# predict_model.py
import os
import joblib
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = "mongodb+srv://murilo:aluno123@ecoar.3znlu18.mongodb.net/?appName=Ecoar"

# Banco de Dados e Coleção:
NOME_DO_BANCO = "ecoar"
MODEL_PATH = "models/risco_model.joblib"

if not MONGO_URI:
    raise RuntimeError("Defina MONGO_URI no .env ou variável de ambiente")

client = MongoClient(MONGO_URI)
db = client[NOME_DO_BANCO]

mapping = {0: "baixo", 1: "médio", 2: "alto"}

def main():
    model_pkg = joblib.load(MODEL_PATH)
    model = model_pkg["model"]
    features = model_pkg["features"]

    docs = list(db.desempenho.find())
    df = pd.DataFrame(docs)
    if df.empty:
        print("Nenhum desempenho encontrado.")
        return

    X = df[features].fillna(0)
    preds = model.predict(X)

    for matricula, pred in zip(df["matricula"], preds):
        nivel = mapping[int(pred)]
        registro = {
            "matricula": matricula,
            "risco_evasao_ml": nivel,
            "risco_ml_pontuacao": int(pred)  # 0/1/2 — apenas exemplo
        }
        db.risco.update_one({"matricula": matricula}, {"$set": registro}, upsert=True)
        print(f"[ML] {matricula} -> {nivel}")

if __name__ == "__main__":
    main()
