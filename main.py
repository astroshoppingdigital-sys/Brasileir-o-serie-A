from fastapi import FastAPI, HTTPException
from services import buscar_detalhes_ao_vivo, buscar_proximos_jogos_espn

app = FastAPI(
    title="API Brasileirão Série A - Versão Final",
    description="API com controle de abas, contagem em azul, atrasos e gelo para encerrados.",
    version="3.1.0",
)


@app.get("/jogos/serie-a")
def get_jogos_serie_a():
  try:
    jogos = buscar_proximos_jogos_espn()
    return {"total": len(jogos), "jogos": jogos}
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


@app.get("/jogos/{event_id}/lances")
def get_lances_jogo(event_id: str):
  lances = buscar_detalhes_ao_vivo(event_id)
  if isinstance(lances, dict) and "erro" in lances:
    raise HTTPException(status_code=404, detail=lances["erro"])

  return {"event_id": event_id, "lances": lances}