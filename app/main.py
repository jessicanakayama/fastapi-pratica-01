from fastapi import FastAPI
from app.endpoints import curso_router
from app.endpoints import disciplina_router
from app.endpoints import auth_router # Linha Adicionada

# Criando uma instância do FastAPI
app = FastAPI(
    title="Sistema Acadêmico - Modular",
    description="API para gerenciamento de cursos e disciplinas",
    version="1.0.0"
)

# Incluindo as rotas de Autenticação
app.include_router(auth_router)

# Incluindo as rotas do recurso de Cursos
app.include_router(curso_router)

# Incluindo as rotas do recurso de Disciplinas
app.include_router(disciplina_router)

# Definindo a rota principal "/"
@app.get("/")
def raiz():
    return {"mensagem": "Bem-vindo à API do Sistema Acadêmico!"}