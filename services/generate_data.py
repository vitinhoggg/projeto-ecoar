from pymongo import MongoClient
from faker import Faker
import random

fake = Faker("pt_BR")  # nomes brasileiros

# ===== CONEXÃO =====
client = MongoClient("mongodb+srv://murilo:aluno123@ac-bmkbk7g.3znlu18.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client.ecoar

# ===== CONFIGURAR QUANTOS NOVOS ALUNOS GERAR =====
NOVOS_ALUNOS = 10  # <-- altere aqui quando quiser gerar mais

# ===== GERAR MATRÍCULA AUTOMÁTICA =====
def proxima_matricula():
    ultimo = db.alunos.find_one(
        sort=[("matricula", -1)]
    )
    
    if not ultimo:
        return 2023001  # primeira matrícula

    return int(ultimo["matricula"]) + 1

# ===== GERAR DADOS DO ALUNO =====
def gerar_aluno(matricula):
    return {
        "matricula": str(matricula),
        "nome": fake.name(),  # <-- NOME ALEATÓRIO
        "curso": random.choice([
            "ADS", "Direito", "Administração", "Enfermagem", "Fisioterapia",
            "Medicina", "Psicologia", "Nutrição", "Odontologia", "Farmácia",
            "Veterinária", "Biomedicina", "Educação Física", "Serviço Social",
            "Pedagogia", "Letras", "História", "Geografia", "Matemática",
            "Física", "Química", "Biologia", "Engenharia Civil",
            "Engenharia Mecânica", "Engenharia Elétrica", "Engenharia de Produção",
            "Arquitetura e Urbanismo"
        ]),
        "periodo": random.randint(1, 8)
    }

# ===== GERAR DESEMPENHO DO ALUNO =====
def gerar_desempenho(matricula):
    return {
        "matricula": str(matricula),
        "frequencia": random.randint(40, 100),
        "media_geral": round(random.uniform(4, 9), 1),
        "faltas": random.randint(0, 30),
        "participacao_plataforma": random.randint(0, 100)
    }

# ===== INSERIR NOVOS ALUNOS =====
def gerar_novos_alunos():
    matricula_atual = proxima_matricula()

    for _ in range(NOVOS_ALUNOS):
        aluno = gerar_aluno(matricula_atual)
        desempenho = gerar_desempenho(matricula_atual)

        db.alunos.insert_one(aluno)
        db.desempenho.insert_one(desempenho)

        print(f"Aluno gerado → matrícula {matricula_atual}")

        matricula_atual += 1

    print("\n✔ Finalizado: novos alunos adicionados sem sobrescrever os antigos!\n")


# ===== EXECUTAR =====
if __name__ == "__main__":
    gerar_novos_alunos()