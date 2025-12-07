from pymongo import MongoClient

# Substitua com sua connection string
client = MongoClient()

db = client.ecoar

# Buscar alunos com risco alto
def buscar_alto_risco():
    alunos_risco = db.risco.find({"risco_evasao": "alto"})
    for r in alunos_risco:
        aluno = db.alunos.find_one({"matricula": r["matricula"]})
        print(f"Aluno: {aluno['nome']} | Curso: {aluno['curso']} | Risco: {r['risco_evasao']}")

buscar_alto_risco()
