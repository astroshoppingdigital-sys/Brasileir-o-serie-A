from datetime import datetime, timezone
import requests

# Rota alternativa da ESPN (geralmente usada pelo app web deles, sem bloqueio de 400)
ESPN_API_URL = "https://site.core.api.espn.com/apis/v2/scoreboard/header?sport=soccer&league=bra.1"

def buscar_jogos_serie_a():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "application/json"
        }
        
        response = requests.get(ESPN_API_URL, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return {"jogos": [], "aviso": f"Falha na API alternativa (Status: {response.status_code})"}
        
        dados = response.json()
        
        # O formato dessa rota core costuma vir aninhado em sports -> leagues -> events
        eventos = []
        try:
            sports = dados.get("sports", [])
            for sport in sports:
                leagues = sport.get("leagues", [])
                for league in leagues:
                    eventos = league.get("events", [])
        except Exception:
            eventos = dados.get("events", [])

        jogos_processados = []
        agora_utc = datetime.now(timezone.utc)

        for evento in eventos:
            id_jogo = evento.get("id")
            nome_evento = evento.get("name")
            data_str = evento.get("date")
            
            competicao = evento.get("competitions", [{}])[0]
            status_obj = competicao.get("status", {})
            tipo_status = status_obj.get("type", {})
            
            estado_original = tipo_status.get("name")
            descricao_status = tipo_status.get("description")
            
            competidores = competicao.get("competitors", [])
            mandante = "Mandante"
            visitante = "Visitante"
            placar_mandante = "0"
            placar_visitante = "0"

            for comp in competidores:
                lugar = comp.get("homeAway")
                nome_time = comp.get("team", {}).get("displayName", "")
                gols = comp.get("score", "0")
                if lugar == "home":
                    mandante = nome_time
                    placar_mandante = gols
                else:
                    visitante = nome_time
                    placar_visitante = gols

            placar = f"{placar_mandante} x {placar_visitante}"

            minutos_para_inicio = 999
            if data_str:
                try:
                    data_jogo_utc = datetime.fromisoformat(data_str.replace("Z", "+00:00"))
                    diferenca = data_jogo_utc - agora_utc
                    minutos_para_inicio = int(diferenca.total_seconds() / 60)
                except Exception:
                    pass

            aba_sugerida = "agendados"
            cor_status = "azul"
            status_traduzido = descricao_status or "Agendado"

            if estado_original in ["STATUS_FINAL", "FT"]:
                aba_sugerida = "encerrados"
                cor_status = "gelo"
                status_traduzido = "Encerrado"
            elif estado_original in ["STATUS_POSTPONED", "POSTPONED"]:
                aba_sugerida = "encerrados"
                cor_status = "gelo"
                status_traduzido = "Adiado"
            elif estado_original in ["STATUS_CANCELED", "CANCELED"]:
                aba_sugerida = "encerrados"
                cor_status = "gelo"
                status_traduzido = "Cancelado"
            elif estado_original in ["STATUS_IN_PROGRESS", "HT", "STATUS_HALFTIME"]:
                aba_sugerida = "ao vivo"
                if estado_original in ["HT", "STATUS_HALFTIME"]:
                    cor_status = "amarelo"
                    status_traduzido = "Intervalo"
                else:
                    cor_status = "verde"
                    status_traduzido = "Em andamento"
            elif estado_original in ["STATUS_SCHEDULED", "TIMED"]:
                if 0 <= minutos_para_inicio <= 10:
                    aba_sugerida = "ao vivo"
                    cor_status = "azul"
                    status_traduzido = f"Começa em {minutos_para_inicio} min"
                elif minutos_para_inicio < 0:
                    aba_sugerida = "ao vivo"
                    cor_status = "verde"
                    status_traduzido = "Vai começar"
                else:
                    aba_sugerida = "agendados"
                    cor_status = "azul"
                    status_traduzido = f"Agendado ({data_str[11:16] if data_str and len(data_str) >= 16 else ''})"

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
                "status_original": estado_original,
                "data_original": data_str
            })

        return {"jogos": jogos_processados}

    except Exception as e:
        return {"jogos": [], "erro": str(e)}
