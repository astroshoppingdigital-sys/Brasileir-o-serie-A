from datetime import datetime, timezone
import requests

# URL de uma API pública e aberta para resultados de futebol
API_URL = "https://www.thesportsdb.com/api/v1/json/3/eventsseason.php?id=4328&s=2026"

def buscar_jogos_serie_a():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json"
        }
        
        response = requests.get(API_URL, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return {"jogos": [], "aviso": f"Falha ao contactar a API de resultados (Status: {response.status_code})"}
        
        dados = response.json()
        eventos = dados.get("events", [])
        
        # Caso a temporada específica venha vazia, tentamos uma rota de placares gerais
        if not eventos:
            # Fallback para endpoint geral de eventos de futebol brasileiro
            url_alternativa = "https://www.thesportsdb.com/api/v1/json/3/eventsday.php?d=2026-06-01"
            resp_alt = requests.get(url_alternativa, headers=headers, timeout=10)
            if resp_alt.status_code == 200:
                eventos = resp_alt.json().get("events", [])

        jogos_processados = []
        agora_utc = datetime.now(timezone.utc)

        for evento in eventos:
            id_jogo = evento.get("idEvent")
            nome_evento = evento.get("strEvent")
            data_str = evento.get("dateEvent")
            hora_str = evento.get("strTime", "20:00:00")
            
            mandante = evento.get("strHomeTeam", "Mandante")
            visitante = evento.get("strAwayTeam", "Visitante")
            
            gols_mandante = evento.get("intHomeScore")
            gols_visitante = evento.get("intAwayScore")
            
            placar_m = str(gols_mandante) if gols_mandante is not None else "0"
            placar_v = str(gols_visitante) if gols_visitante is not None else "0"
            placar = f"{placar_m} x {placar_v}"

            status_evento = evento.get("strStatus", "Not Started")
            
            # Cálculo de minutos se houver data completa
            minutos_para_inicio = 999
            if data_str:
                try:
                    dt_completa = f"{data_str}T{hora_str}Z"
                    data_jogo_utc = datetime.fromisoformat(dt_completa.replace("Z", "+00:00"))
                    diferenca = data_jogo_utc - agora_utc
                    minutos_para_inicio = int(diferenca.total_seconds() / 60)
                except Exception:
                    pass

            aba_sugerida = "agendados"
            cor_status = "azul"
            status_traduzido = "Agendado"

            if status_evento in ["FT", "AET", "Pen"]:
                aba_sugerida = "encerrados"
                cor_status = "gelo"
                status_traduzido = "Encerrado"
            elif status_evento in ["Live", "HT"]:
                aba_sugerida = "ao vivo"
                cor_status = "verde" if status_evento == "Live" else "amarelo"
                status_traduzido = "Em andamento" if status_evento == "Live" else "Intervalo"
            else:
                if 0 <= minutos_para_inicio <= 10:
                    aba_sugerida = "ao vivo"
                    cor_status = "azul"
                    status_traduzido = f"Começa em {minutos_para_inicio} min"
                elif minutos_para_inicio < 0 and status_evento not in ["FT"]:
                    aba_sugerida = "ao vivo"
                    cor_status = "verde"
                    status_traduzido = "Em andamento"
                else:
                    aba_sugerida = "agendados"
                    cor_status = "azul"
                    status_traduzido = f"Agendado ({hora_str[:5]})"

            jogos_processados.append({
                "id": id_jogo,
                "nome_evento": nome_evento,
                "mandante": mandante,
                "visitante": visitante,
                "placar": placar,
                "status": status_traduzido,
                "cor_status": cor_status,
                "aba_sugerida": aba_sugerida,
                "minutos_para_inicio": minutos_para_inicio,
                "status_original": status_evento,
                "data_original": data_str
            })

        return {"jogos": jogos_processados}

    except Exception as e:
        return {"jogos": [], "erro": str(e)}
