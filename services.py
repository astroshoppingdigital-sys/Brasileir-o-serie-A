from datetime import datetime, timezone
import requests
from config import ESPN_BRASILEIRAO_URL, ESPN_SUMARIO_URL


def processar_status_e_tempo(status_type: str, data_jogo_str: str):
  """Calcula o status amigável, a cor e a contagem regressiva com base no horário real."""
  agora = datetime.now(timezone.utc)

  try:
    data_jogo = datetime.fromisoformat(data_jogo_str.replace("Z", "+00:00"))
  except Exception:
    data_jogo = None

  # 1. Adiados ou cancelados (voltam para agendados)
  if status_type in ["STATUS_POSTPONED", "STATUS_CANCELED"]:
    return {
        "aba": "agendados",
        "texto": "Jogo adiado / Remarcado",
        "cor": "laranja",
        "mensagem_especial": (
            "Partida adiada. Consulte a nova data agendada."
        ),
    }

  # 2. Encerrados (Cor Gelo)
  if status_type in ["STATUS_FULL_TIME", "STATUS_FINAL"]:
    return {
        "aba": "encerrados",
        "texto": "Partida encerrada",
        "cor": "gelo",  # Cor solicitada para jogos encerrados
        "mensagem_especial": None,
    }

  # 3. Intervalo
  if status_type in ["STATUS_HALFTIME"]:
    return {
        "aba": "ao_vivo",
        "texto": "Intervalo em descanso",
        "cor": "amarelo",
        "mensagem_especial": None,
    }

  # 4. Jogo em andamento
  if status_type in [
      "STATUS_IN_PROGRESS",
      "STATUS_FIRST_HALF",
      "STATUS_SECOND_HALF",
  ]:
    return {
        "aba": "ao_vivo",
        "texto": "Jogo em andamento",
        "cor": "verde",
        "mensagem_especial": None,
    }

  # 5. Pré-jogo, contagem regressiva e atrasos
  if data_jogo:
    diferenca_segundos = (data_jogo - agora).total_seconds()
    minutos_para_inicio = diferenca_segundos / 60

    if -15 <= minutos_para_inicio <= 10:
      if minutos_para_inicio < -2:
        return {
            "aba": "ao_vivo",
            "texto": "Jogo em atraso",
            "cor": "laranja",
            "mensagem_especial": (
                "A partida está sofrendo atraso na inicialização."
            ),
        }

      if 0 <= minutos_para_inicio <= 10:
        mins_restantes = int(minutos_para_inicio)
        return {
            "aba": "ao_vivo",
            "texto": f"Pré-jogo: Inicia em {mins_restantes} min",
            "cor": "azul",
            "mensagem_especial": "Contagem regressiva para o início.",
        }

  # Padrão para jogos futuros
  return {
      "aba": "agendados",
      "texto": "Não iniciado",
      "cor": "cinza",
      "mensagem_especial": None,
  }


def buscar_proximos_jogos_espn():
  try:
    response = requests.get(ESPN_BRASILEIRAO_URL, timeout=10)
    response.raise_for_status()
    data = response.json()

    jogos_processados = []
    events = data.get("events", [])

    for event in events:
      competitions = event.get("competitions", [{}])[0]
      status_raw = competitions.get("status", {}).get("type", {}).get("name", "")
      data_jogo_str = event.get("date", "")

      info_status = processar_status_e_tempo(status_raw, data_jogo_str)

      times = competitions.get("competitors", [])
      mandante = "Desconhecido"
      visitante = "Desconhecido"
      gols_mandante = "0"
      gols_visitante = "0"

      for t in times:
        if t.get("homeAway") == "home":
          mandante = t.get("team", {}).get("displayName", "Desconhecido")
          gols_mandante = t.get("score", "0")
        elif t.get("homeAway") == "away":
          visitante = t.get("team", {}).get("displayName", "Desconhecido")
          gols_visitante = t.get("score", "0")

      jogos_processados.append({
          "id": event.get("id"),
          "data_original": data_jogo_str,
          "nome_evento": event.get("name"),
          "mandante": mandante,
          "visitante": visitante,
          "placar": f"{gols_mandante} x {gols_visitante}",
          "aba_sugerida": info_status["aba"],
          "status": info_status["texto"],
          "cor_status": info_status["cor"],  # Vai retornar "gelo" para encerrados
          "mensagem_especial": info_status["mensagem_especial"],
          "status_original": status_raw,
      })

    return jogos_processados

  except Exception as e:
    raise Exception(f"Erro ao conectar com a API da ESPN: {str(e)}")


def buscar_detalhes_ao_vivo(event_id: str):
  try:
    url = f"{ESPN_SUMARIO_URL}?event={event_id}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()

    lances = []
    plays = data.get("plays", [])

    for play in plays:
      texto_lance = play.get("text", "")
      tipo_lance = play.get("type", {}).get("text", "Outros")
      minuto = play.get("clock", {}).get("displayValue", "")

      lances.append({
          "minuto": minuto,
          "tipo": tipo_lance,
          "descricao": texto_lance,
      })

    return lances

  except Exception as e:
    return {"erro": f"Não foi possível carregar os lances: {str(e)}"}