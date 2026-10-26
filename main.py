from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from services import buscar_jogos_serie_a

app = FastAPI(
    title="API Brasileirão Série A",
    description="API customizada para controle de jogos, status, cores e abas do Brasileirão Série A",
    version="1.0.0"
)

# Libera o acesso para o seu site/front-end (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite requisições de qualquer origem
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "mensagem": "API do Brasileirão Série A rodando perfeitamente!",
        "documentacao": "/docs",
        "endpoint_jogos": "/jogos/serie-a"
    }

@app.get("/jogos/serie-a")
def obter_jogos():
    resultado = buscar_jogos_serie_a()
    if "erro" in resultado:
        raise HTTPException(status_code=500, detail=resultado["erro"])
    return resultado
