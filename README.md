📘 README – Projeto ECOAR
Sistema de Acompanhamento de Alunos em Risco de Evasão

📌 Descrição do Projeto


O Projeto ECOAR tem como objetivo monitorar, acompanhar e intervir precocemente em casos de alunos com risco de evasão no ambiente acadêmico.
O sistema foi desenvolvido para auxiliar instituições de ensino superior a detectar sinais de alerta, registrar informações importantes e facilitar o contato entre aluno e equipe de suporte.

O projeto utiliza:

MongoDB como banco de dados NoSQL

Python/Flask (presumido pelo histórico do chat — posso ajustar caso seja outra tecnologia)

Visual Studio Code como ambiente principal de desenvolvimento

Arquitetura simples, modular e fácil de escalar

🎯 Objetivos do Sistema


Identificar alunos com risco de evasão através de dados acadêmicos e comportamentais.

Registrar atendimentos, alertas e justificativas.

Facilitar o acompanhamento por parte de coordenadores e equipes pedagógicas.

Manter um histórico centralizado e acessível.

Apoiar decisões institucionais com informações confiáveis.

🧩 Principais Funcionalidades


📋 Cadastro de Alunos

⚠️ Identificação de risco de evasão

📝 Registro de intervenções e atendimentos

📊 Consulta e geração de relatórios (se aplicável)

🔍 Filtros por curso, período, status e nível de risco

👨‍🏫 Área para equipe pedagógica (ajustável conforme o projeto)

📦 Integração com MongoDB para armazenamento

🏗️ Tecnologias Utilizadas


Back-end

Python

Flask (se for outra tecnologia, me diga)

MongoDB (banco principal)

pymongo ou outro driver de conexão

Front-end

HTML, CSS, JS (ou especifique se usa framework ex: React/Vue)

Ambiente de Desenvolvimento

Visual Studio Code

Extensões recomendadas:

MongoDB for VS Code

Python

Live Server (se houver front-end estático)

📂 Estrutura do Projeto (exemplo)



/Project-ECOAR
│── /inicio

│   ├── run.py

│   ├── /static

│   ├── /templates

│   ├── /routes

│   ├── /services

│   └── /models
│
│── README.md

│── requirements.txt

🔧 Instalação e Configuração
1. Clonar o repositório
git clone https://github.com/vitinhoggg/project-ecoar.git
cd projeto-ecoar

3. Criar ambiente virtual
python -m venv venv
venv\Scripts\activate

4. Instalar dependências
pip install -r requirements.txt

5. Configurar variáveis de ambiente

Crie um arquivo .env:

MONGO_URI=mongodb://localhost:27017
DATABASE_NAME=ecoar_db

5. Iniciar o servidor
python run.py


Servidor rodará em:
👉http://localhost:8080/index.html

🗄️ Configuração do Banco (MongoDB)



O banco contém coleções típicas como:

alunos

riscos

atendimentos

usuarios (se houver sistema de login)

Exemplo de documento no MongoDB:

{
  "nome": "João Silva",
  
  "curso": "Engenharia",
  
  "periodo": 3,
  
  "risco_evasao": "alto",
  
  "justificativa": "Faltas recorrentes",
  
  "ultima_acao": "Contato realizado"
}




