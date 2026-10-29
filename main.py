from fastapi import FastAPI
from services import obter_jogos_serie_a

app = FastAPI(
    title="Live Gol Série A - API Oficial",
    description="API em tempo real para rastrear partidas do Campeonato Brasileiro Série A",
    version="1.0.0"
)

@app.get("/")
def home():
    return {
        "status": "online",
        "mensagem": "API do Brasileirão Série A rodando perfeitamente!",
        "documentacao": "/docs",
        "endpoint_jogos": "/jogos/serie-a"
    }

@app.get("/jogos/serie-a")
def listar_jogos_serie_a():
    return obter_jogos_serie_a()
