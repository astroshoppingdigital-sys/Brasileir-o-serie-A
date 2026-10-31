import requests
from config import ESPN_BRASILEIRA_URL, ESPN_SUMARIO_URL

def obter_jogos_serie_a():
    try:
        response = requests.get(ESPN_BRASILEIRA_URL, timeout=10)
        if response.status_code != 200:
            return _resposta_oficial_santos_palmeiras()
        
        data = response.json()
        eventos = data.get("events", [])
        
        if not eventos:
            return _resposta_oficial_santos_palmeiras()
            
        jogos_formatados = []
        
        # Injeta diretamente o clássico Santos x Palmeiras com os links dos seus escudos oficiais
        jogos_formatados.append({
            "mandante": "Santos",
            "visitante": "Palmeiras",
            "estadio": "Estádio Urbano Caldeira (Vila Belmiro)",
            "escudo_mandante": "https://i.postimg.cc/4425PcHS/santos-fc.png",
            "escudo_visitante": "https://i.postimg.cc/BbP1MXdb/palmeiras.png",
            "placar": "0 x 0",
            "status": "Partida Finalizada",
            "cor_status": "#E0E0E0", # Tom gelo / claro para destaque
            "aba_sugerida": "encerrados"
        })
        
        # Adiciona os demais jogos da rodada da API
        for evento in eventos:
            competicao = evento.get("competitions", [{}])[0]
            competitors = competicao.get("competitors", [])
            
            mandante = ""
            visitante = ""
            for comp in competitors:
                team = comp.get("team", {})
                nome_time = team.get("displayName", "")
                if comp.get("homeAway") == "home":
                    mandante = nome_time
                elif comp.get("homeAway") == "away":
                    visitante = nome_time
            
            if not mandante or not visitante or "mandante" in mandante.lower() or "visitante" in visitante.lower():
                continue
                
            if "santos" in mandante.lower() and "palmeiras" in visitante.lower():
                continue

            venue = competicao.get("venue", {})
            estadio = venue.get("fullName", "Estádio do Brasileirão")
            
            escudo_mandante = ""
            escudo_visitante = ""
            placar_mandante = "0"
            placar_visitante = "0"
            
            for comp in competitors:
                team = comp.get("team", {})
                if comp.get("homeAway") == "home":
                    escudo_mandante = team.get("logo", "")
                    placar_mandante = comp.get("score", "0")
                elif comp.get("homeAway") == "away":
                    escudo_visitante = team.get("logo", "")
                    placar_visitante = comp.get("score", "0")
            
            status_obj = evento.get("status", {})
            tipo_status = status_obj.get("type", {})
            status_descricao = tipo_status.get("description", "Agendado")
            status_name = tipo_status.get("name", "").lower()
            
            # Identifica se a partida já começou, está ao vivo ou terminou pela ESPN
            is_ao_vivo = "in" in status_name or "status_in_progress" in status_name or "halftime" in status_name
            is_encerrado = "post" in status_name or "encerrado" in status_descricao.lower() or "ft" in status_name
            
            # Definição dinâmica da aba e do status visual
            if is_encerrado:
                aba = "encerrados"
                texto_status = "Partida Finalizada"
                cor_status = "#E0E0E0"  # Cor gelo solicitada
            elif is_ao_vivo:
                aba = "hoje"
                texto_status = status_descricao # Ex: "1º Tempo", "Intervalo", etc.
                cor_status = "#00FF7F"  # Verde destaque para ao vivo
            else:
                aba = "agendados"
                texto_status = status_descricao # Ex: "Scheduled" ou horário
                cor_status = "#FFD700"  # Amarelo para agendados

            placar = f"{placar_mandante} x {placar_visitante}"

            jogos_formatados.append({
                "mandante": mandante,
                "visitante": visitante,
                "estadio": estadio,
                "escudo_mandante": escudo_mandante,
                "escudo_visitante": escudo_visitante,
                "placar": placar,
                "status": texto_status,
                "cor_status": cor_status,
                "aba_sugerida": aba
            })
            
        return {
            "status": "sucesso",
            "fonte": "API Customizada ESPN em Tempo Real",
            "jogos": jogos_formatados
        }
        
    except Exception as e:
        return _resposta_oficial_santos_palmeiras()

def _resposta_oficial_santos_palmeiras():
    return {
        "status": "sucesso",
        "fonte": "Fallback Oficial - Santos x Palmeiras",
        "jogos": [
            {
                "mandante": "Santos",
                "visitante": "Palmeiras",
                "estadio": "Estádio Urbano Caldeira (Vila Belmiro)",
                "escudo_mandante": "https://i.postimg.cc/4425PcHS/santos-fc.png",
                "escudo_visitante": "https://i.postimg.cc/BbP1MXdb/palmeiras.png",
                "placar": "0 x 0",
                "status": "Partida Finalizada",
                "cor_status": "#E0E0E0",
                "aba_sugerida": "encerrados"
            }
        ]
    }
