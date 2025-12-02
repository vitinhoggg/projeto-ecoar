# backend.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import math

app = Flask(__name__)
CORS(app)

# ==========================================
# CONEXÃO COM O MONGODB
# ==========================================
client = MongoClient(
    "mongodb+srv://murilo:aluno123@ac-bmkbk7g.3znlu18.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
)
db = client["ecoar"]
alunos_col = db["alunos"]
desempenho_col = db["desempenho"]

# ==========================================
# UTILITÁRIOS
# ==========================================
def calcular_risco(media):
    try:
        v = float(media)
    except:
        v = 0.0
    risco_ml_evasao = 1.0 if v < 6 else (0.5 if v < 7.5 else 0.0)
    categoria = "Alto" if risco_ml_evasao >= 0.7 else ("Médio" if risco_ml_evasao >= 0.4 else "Baixo")
    return risco_ml_evasao, categoria

def normalizar_periodo(valor):
    s = str(valor).strip().lower()
    mapa = {str(i): f"{i}º semestre" for i in range(1, 9)}
    # Também aceita variações comuns
    for i in range(1, 9):
        if s in {str(i), f"{i}º", f"{i} semestre", f"{i}º semestre"}:
            return f"{i}º semestre"
    return s.title() if s else "Não informado"

# ==========================================
# ENDPOINT: OPÇÕES PARA FILTROS
# ==========================================
@app.get("/api/options")
def get_options():
    cursos = sorted({(doc.get("curso") or "Não informado") for doc in alunos_col.find({}, {"curso": 1})})
    periodos_raw = {(doc.get("periodo_atual") or "Não informado") for doc in alunos_col.find({}, {"periodo_atual": 1})}
    periodos = sorted({normalizar_periodo(p) for p in periodos_raw})
    riscos = ["Baixo", "Médio", "Alto"]
    return jsonify({"curso": ["Todos"] + cursos, "periodo_atual": ["Todos"] + periodos, "risco": ["Todos"] + riscos})

# ==========================================
# ENDPOINT: LISTA PAGINADA DE ALUNOS + KPIs
# ==========================================
@app.get("/api/alunos")
def get_alunos():
    # Query params
    curso = request.args.get("curso")
    periodo = request.args.get("periodo")
    risco = request.args.get("risco")
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 50))
    page_size = max(10, min(page_size, 200))  # segurança

    # Filtro base
    filtro = {}
    if curso and curso != "Todos":
        filtro["curso"] = curso
    if periodo and periodo != "Todos":
        # normaliza na consulta também
        filtro["periodo_atual"] = periodo

    # Merge simples via aplicação: pega alunos e junta desempenho por matricula
    # Para performance real com milhões, o ideal é pré-juntar em uma coleção única ou usar $lookup no Mongo.
    total_docs = alunos_col.count_documents(filtro)

    # Paginação
    skip = (page - 1) * page_size
    alunos_cursor = alunos_col.find(filtro).skip(skip).limit(page_size)

    itens = []
    soma_media = 0.0
    alto = medio = baixo = 0

    matriculas = [a.get("matricula") for a in alunos_cursor]
    # Recarregue o cursor (foi consumido): melhor guardar dados
    alunos_cursor = alunos_col.find(filtro).skip(skip).limit(page_size)
    desempenho_map = {d.get("matricula"): d for d in desempenho_col.find({"matricula": {"$in": matriculas}})}

    for a in alunos_cursor:
        mat = a.get("matricula")
        d = desempenho_map.get(mat, {})
        media = d.get("media_geral", a.get("media_geral", 0))
        try:
            media = float(media)
        except:
            media = 0.0

        risco_ml_evasao, categoria = calcular_risco(media)

        item = {
            "matricula": mat,
            "nome": a.get("nome", "Não informado"),
            "curso": a.get("curso", "Não informado"),
            "periodo_atual": normalizar_periodo(a.get("periodo_atual", "Não informado")),
            "status": a.get("status", "Ativo"),
            "media_geral": round(media, 2),
            "risco_ml_evasao": risco_ml_evasao,
            "categoria_risco": categoria
        }
        itens.append(item)

        soma_media += media
        if categoria == "Alto":
            alto += 1
        elif categoria == "Médio":
            medio += 1
        else:
            baixo += 1

    # KPIs
    total = max(1, total_docs)
    media_geral = round(soma_media / len(itens), 2) if itens else 0.0
    perc_alto = round((alto / len(itens)) * 100, 1) if itens else 0.0
    perc_medio = round((medio / len(itens)) * 100, 1) if itens else 0.0

    return jsonify({
        "items": itens,
        "page": page,
        "page_size": page_size,
        "total": total_docs,
        "pages": math.ceil(total_docs / page_size),
        "kpi": {
            "total_alunos": total_docs,
            "media_geral": media_geral,
            "perc_alto": perc_alto,
            "perc_medio": perc_medio
        },
        "counts": {"Baixo": baixo, "Médio": medio, "Alto": alto}
    })

# ==========================================
# ENDPOINT: ALTO RISCO (lista rápida)
# ==========================================
@app.get("/api/alto_risco")
def get_alto_risco():
    # Limita retorno para evitar carga excessiva
    limite = int(request.args.get("limit", 100))
    # Busca alunos; calcula risco na aplicação
    alunos_cursor = alunos_col.find({}, {"matricula": 1, "nome": 1, "curso": 1, "periodo_atual": 1, "status": 1}).limit(5000)
    desempenho_map = {d.get("matricula"): d for d in desempenho_col.find({}, {"matricula": 1, "media_geral": 1})}

    result = []
    for a in alunos_cursor:
        mat = a.get("matricula")
        media = desempenho_map.get(mat, {}).get("media_geral", a.get("media_geral", 0))
        try:
            media = float(media)
        except:
            media = 0.0
        risco_ml_evasao, categoria = calcular_risco(media)
        if categoria == "Alto":
            result.append({
                "matricula": mat,
                "nome": a.get("nome", "Não informado"),
                "curso": a.get("curso", "Não informado"),
                "periodo_atual": normalizar_periodo(a.get("periodo_atual", "Não informado")),
                "media_geral": round(media, 2),
                "risco_ml_evasao": risco_ml_evasao
            })
            if len(result) >= limite:
                break

    return jsonify({"items": result})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)