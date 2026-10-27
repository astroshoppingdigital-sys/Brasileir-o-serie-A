
from datetime import datetime, timezone
import requests

# URL limpa da API da ESPN para o Brasileirão Série A
ESPN_API_URL = "https://site.api.espn.com/apis/site/v2/sports/soccer/brazil.1/scoreboard"

def buscar_jogos_serie_a():
    try:
        # Usando um User-Agent padrão de navegador web comum
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json"
        }
        
        response = requests.get(ESPN_API_URL, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return {"erro": f"Falha ao conectar com a API da ESPN (Status: {response.status_code})"}
        
        dados = response.json()
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
            status_traduzido = descricao_status

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
                    status_traduzido = f"Agendado ({data_str[11:16]})"

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
        return {"erro": str(e)}
