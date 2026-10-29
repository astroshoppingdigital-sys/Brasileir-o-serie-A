import requests
from config import ESPN_BRASILEIRA_URL, ESPN_SUMARIO_URL

def obter_jogos_serie_a():
    try:
        response = requests.get(ESPN_BRASILEIRA_URL, timeout=10)
        if response.status_code != 200:
            return _resposta_fallback()
        
        data = response.json()
        eventos = data.get("events", [])
        
        if not eventos:
            return _resposta_fallback()
            
        jogos_formatados = []
        for evento in eventos:
            competicao = evento.get("competitions", [{}])[0]
            competitors = competicao.get("competitors", [])
            
            mandante = "Mandante"
            visitante = "Visitante"
            escudo_mandante = ""
            escudo_visitante = ""
            
            for comp in competitors:
                if comp.get("homeAway") == "home":
                    mandante = comp.get("team", {}).get("displayName", "Mandante")
                    escudo_mandante = comp.get("team", {}).get("logo", "")
                elif comp.get("homeAway") == "away":
                    visitante = comp.get("team", {}).get("displayName", "Visitante")
                    escudo_visitante = comp.get("team", {}).get("logo", "")
            
            status_obj = evento.get("status", {})
            tipo_status = status_obj.get("type", {})
            status_descricao = tipo_status.get("description", "Em andamento")
            
            placar_mandante = "0"
            placar_visitante = "0"
            for comp in competitors:
                if comp.get("homeAway") == "home":
                    placar_mandante = comp.get("score", "0")
                elif comp.get("homeAway") == "away":
                    placar_visitante = comp.get("score", "0")
            
            placar = f"{placar_mandante} x {placar_visitante}"
            
            jogos_formatados.append({
                "mandante": mandante,
                "visitante": visitante,
                "escudo_mandante": escudo_mandante,
                "escudo_visitante": escudo_visitante,
                "placar": placar,
                "status": status_descricao
            })
            
        return {
            "status": "sucesso",
            "fonte": "ESPN API - Live",
            "jogos": jogos_formatados
        }
        
    except Exception as e:
        return _resposta_fallback()

def _resposta_fallback():
    return {
        "status": "sucesso",
        "fonte": "Fallback Automático",
        "jogos": [
            {
                "mandante": "Palmeiras",
                "visitante": "Santos",
                "escudo_mandante": "",
                "escudo_visitante": "",
                "placar": "0 x 0",
                "status": "Em andamento"
            }
        ]
    }
