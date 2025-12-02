'''# api.py
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from pymongo import MongoClient
import joblib
import pandas as pd

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "ecoar")
MODEL_PATH = "models/risco_model.joblib"

if not MONGO_URI:
    raise RuntimeError("Defina MONGO_URI no .env ou variável de ambiente")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

app = FastAPI(title="ECOAR API")

# Pydantic schemas
class AlunoIn(BaseModel):
    nome: str
    matricula: str
    curso: str
    periodo_atual: int
    status: str = "ativo"

class DesempenhoIn(BaseModel):
    matricula: str
    frequencia: int
    media_geral: float
    faltas: int
    participacao_plataforma: int

# helper rule (same as earlier)
def calcular_pontuacao_rule(desempenho):
    pontos = 0
    motivos = []
    if desempenho.get("frequencia", 100) < 70:
        pontos += 2; motivos.append("baixa frequência")
    if desempenho.get("media_geral", 10) < 6.0:
        pontos += 1; motivos.append("média baixa")
    if desempenho.get("faltas", 0) > 15:
        pontos += 2; motivos.append("faltas excessivas")
    if desempenho.get("participacao_plataforma", 100) < 50:
        pontos += 1; motivos.append("baixa participação online")
    if pontos <= 1: nivel = "baixo"
    elif pontos <= 3: nivel = "médio"
    else: nivel = "alto"
    return {"pontuacao": pontos, "motivos": motivos, "risco_evasao": nivel}

@app.get("/aluno/{matricula}")
def get_aluno(matricula: str):
    aluno = db.alunos.find_one({"matricula": matricula}, {"_id":0})
    desempenho = db.desempenho.find_one({"matricula": matricula}, {"_id":0})
    risco = db.risco.find_one({"matricula": matricula}, {"_id":0})
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    return {"aluno": aluno, "desempenho": desempenho, "risco": risco}

@app.get("/riscos")
def list_riscos(limit: int = 100):
    items = list(db.risco.find({}, {"_id":0}).limit(limit))
    return {"count": len(items), "items": items}

@app.post("/recalcular")
def recalcular():
    # Recalcula risco rule-based para todos
    docs = list(db.desempenho.find())
    for d in docs:
        calc = calcular_pontuacao_rule(d)
        registro = {
            "matricula": d["matricula"],
            "risco_evasao": calc["risco_evasao"],
            "pontuacao": calc["pontuacao"],
            "motivos": calc["motivos"]
        }
        db.risco.update_one({"matricula": d["matricula"]}, {"$set": registro}, upsert=True)
    return {"status":"ok", "processed": len(docs)}

@app.post("/predict")
def predict_all():
    # Carrega modelo
    pkg = joblib.load(MODEL_PATH)
    model = pkg["model"]
    features = pkg["features"]
    docs = list(db.desempenho.find())
    if not docs:
        raise HTTPException(status_code=400, detail="Nenhum desempenho para predizer")
    df = pd.DataFrame(docs)
    X = df[features].fillna(0)
    preds = model.predict(X)
    mapping = {0:"baixo",1:"médio",2:"alto"}
    for matricula, p in zip(df["matricula"], preds):
        db.risco.update_one({"matricula": matricula}, {"$set": {"matricula": matricula, "risco_evasao_ml": mapping[int(p)], "risco_ml_pontuacao": int(p)}}, upsert=True)
    return {"status":"ok", "processed": len(docs)}

@app.post("/inserir_aluno")
def inserir_aluno(payload: dict):
    # payload precisa conter aluno e desempenho
    aluno = payload.get("aluno")
    desempenho = payload.get("desempenho")
    if not aluno or not desempenho:
        raise HTTPException(status_code=400, detail="Envie 'aluno' e 'desempenho' no body")
    db.alunos.update_one({"matricula": aluno["matricula"]}, {"$set": aluno}, upsert=True)
    db.desempenho.update_one({"matricula": desempenho["matricula"]}, {"$set": desempenho}, upsert=True)
    # opcional: recalcular risco para esse aluno via regra
    calc = calcular_pontuacao_rule(desempenho)
    registro = {"matricula": desempenho["matricula"], "risco_evasao": calc["risco_evasao"], "pontuacao": calc["pontuacao"], "motivos": calc["motivos"]}
    db.risco.update_one({"matricula": desempenho["matricula"]}, {"$set": registro}, upsert=True)
    return {"status":"ok", "matricula": aluno["matricula"]}

# Run: uvicorn api:app --reload --port 8000
'''