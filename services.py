from datetime import datetime, timezone
import requests

# URL da API pública da ESPN para o Brasileirão Série A
ESPN_API_URL = "https://site.api.espn.com/apis/site/v2/sports/soccer/brazil.1/scoreboard"

def buscar_jogos_serie_a():
    try:
        response = requests.get(ESPN_API_URL, timeout=10)
        if response.status_code != 200:
            return {"erro": "Falha ao conectar com a API da ESPN"}
        
        dados = response.json()
        eventos = dados.get("events", [])
        jogos_processados = []

        # Data e hora atual em UTC (garantindo compatibilidade com o fuso do servidor)
        agora_utc = datetime.now(timezone.utc)

        for evento in eventos:
            id_jogo = evento.get("id")
            nome_evento = evento.get("name")
            data_str = evento.get("date") # Ex: '2026-10-26T21:30:00Z'
            
            competicao = evento.get("competitions", [{}])[0]
            status_obj = competicao.get("status", {})
            tipo_status = status_obj.get("type", {})
            
            estado_original = tipo_status.get("name") # Ex: STATUS_SCHEDULED, STATUS_IN_PROGRESS, STATUS_FINAL
            descricao_status = tipo_status.get("description") # Ex: "Scheduled", "In Progress", "Full Time"
            
            # Times e Placar
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

            # Cálculo de tempo e contagem regressiva
            minutos_para_inicio = 999
            if data_str:
                try:
                    data_jogo_utc = datetime.fromisoformat(data_str.replace("Z", "+00:00"))
                    diferenca = data_jogo_utc - agora_utc
                    minutos_para_inicio = int(diferenca.total_seconds() / 60)
                except Exception:
                    pass

            # Lógica de Status, Cores e Abas
            aba_sugerida = "agendados"
            cor_status = "azul"
            status_traduzido = descricao_status

            # 1. Jogo Encerrado, Adiado ou Cancelado
            if estado_original in ["STATUS_FINAL", "FT"]:
                aba_sugerida = "encerrados"
                cor_status = "gelo" # Cinza/Gelo
                status_traduzido = "Encerrado"
            elif estado_original in ["STATUS_POSTPONED", "POSTPONED"]:
                aba_sugerida = "encerrados"
                cor_status = "gelo"
                status_traduzido = "Adiado"
            elif estado_original in ["STATUS_CANCELED", "CANCELED"]:
                aba_sugerida = "encerrados"
                cor_status = "gelo"
                status_traduzido = "Cancelado"

            # 2. Jogo em Andamento (Ao Vivo ou Intervalo)
            elif estado_original in ["STATUS_IN_PROGRESS", "HT", "STATUS_HALFTIME"]:
                aba_sugerida = "ao vivo"
                if estado_original in ["HT", "STATUS_HALFTIME"]:
                    cor_status = "amarelo"
                    status_traduzido = "Intervalo"
                else:
                    cor_status = "verde"
                    status_traduzido = "Em andamento"

            # 3. Jogo Agendado / Contagem Regressiva (10 minutos antes)
            elif estado_original in ["STATUS_SCHEDULED", "TIMED"]:
                if 0 <= minutos_para_inicio <= 10:
                    # Cai direto na aba ao vivo com contagem azul
                    aba_sugerida = "ao vivo"
                    cor_status = "azul"
                    status_traduzido = f"Começa em {minutos_para_inicio} min"
                elif minutos_para_inicio < 0:
                    # Caso a API demore para atualizar o estado para "in progress"
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
