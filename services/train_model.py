# train_model.py
import os
import numpy as np
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib

load_dotenv()
MONGO_URI = ""

# Banco de Dados e Coleção:
NOME_DO_BANCO = "ecoar"
MODEL_PATH = "models/risco_model.joblib"

if not MONGO_URI:
    raise RuntimeError("Defina MONGO_URI no .env ou variável de ambiente")

client = MongoClient(MONGO_URI)
db = client[NOME_DO_BANCO]

def regra_label(des):
    pontos = 0
    if des.get("frequencia", 100) < 70: pontos += 2
    if des.get("media_geral", 10) < 6.0: pontos += 1
    if des.get("faltas", 0) > 15: pontos += 2
    if des.get("participacao_plataforma", 100) < 50: pontos += 1
    if pontos <= 1: return 0  # baixo
    if pontos <= 3: return 1  # medio
    return 2  # alto

def main():
    docs = list(db.desempenho.find())
    if not docs:
        raise RuntimeError("Nenhum documento encontrado em 'desempenho'. Rode generate_data.py primeiro.")

    df = pd.DataFrame(docs)
    # Features
    X = df[["frequencia","media_geral","faltas","participacao_plataforma"]].fillna(0)
    y = df.apply(lambda r: regra_label(r), axis=1)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    clf = DecisionTreeClassifier(max_depth=5, random_state=42)
    clf.fit(X_train, y_train)

    preds = clf.predict(X_test)
    print("Accuracy:", accuracy_score(y_test, preds))
    print(classification_report(y_test, preds, target_names=["baixo","médio","alto"]))

    # Save model and optionally feature names
    os.makedirs("models", exist_ok=True)
    joblib.dump({"model": clf, "features": list(X.columns)}, MODEL_PATH)
    print(f"Modelo salvo em {MODEL_PATH}")

if __name__ == "__main__":
    main()
