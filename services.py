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
            "status": "Partida Encerrada",
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
            
            # Verificações de confrontos
            is_corinthians_palmeiras = (
                ("corinthians" in mandante.lower() and "palmeiras" in visitante.lower()) or
                ("palmeiras" in mandante.lower() and "corinthians" in visitante.lower())
            )
            
            is_cruzeiro_flamengo = (
                ("cruzeiro" in mandante.lower() and "flamengo" in visitante.lower()) or
                ("flamengo" in mandante.lower() and "cruzeiro" in visitante.lower())
            )

            is_mirassol_remo = (
                ("mirassol" in mandante.lower() and "remo" in visitante.lower()) or
                ("remo" in mandante.lower() and "mirassol" in visitante.lower())
            )

            is_athletico_vitoria = (
                ("athletico" in mandante.lower() and "vitória" in visitante.lower()) or
                ("vitória" in mandante.lower() and "athletico" in visitante.lower()) or
                ("athletico-pr" in mandante.lower() and "vitória" in visitante.lower()) or
                ("vitoria" in mandante.lower() and "athletico" in visitante.lower())
            )

            # Ajuste definitivo: Atlético-MG x Cruzeiro (Cruzeiro venceu por 1 a 0 fora de casa)
            is_cruzeiro_atleticomg = (
                ("cruzeiro" in mandante.lower() and ("atlético" in visitante.lower() or "atletico" in visitante.lower())) or
                (("atlético" in mandante.lower() or "atletico" in mandante.lower()) and "cruzeiro" in visitante.lower())
            )
            
            is_atletico_gremio = (
                ("atlético" in mandante.lower() and "grêmio" in visitante.lower()) or
                ("grêmio" in mandante.lower() and "atlético" in visitante.lower()) or
                ("atletico" in mandante.lower() and "gremio" in visitante.lower()) or
                ("gremio" in mandante.lower() and "atletico" in visitante.lower())
            )
            if is_cruzeiro_atleticomg:
                is_atletico_gremio = False

            is_vasco_flamengo = (
                ("vasco" in mandante.lower() and "flamengo" in visitante.lower()) or
                ("flamengo" in mandante.lower() and "vasco" in visitante.lower())
            )

            is_gremio_athletico = (
                ("grêmio" in mandante.lower() and "athletico" in visitante.lower()) or
                ("gremio" in mandante.lower() and "athletico" in visitante.lower()) or
                ("athletico" in mandante.lower() and "grêmio" in visitante.lower()) or
                ("athletico" in mandante.lower() and "gremio" in visitante.lower())
            )

            status_obj = evento.get("status", {})
            tipo_status = status_obj.get("type", {})
            status_descricao = tipo_status.get("description", "Encerrado")
            
            # Aplicação dos placares corretos e definitivos
            if is_corinthians_palmeiras:
                if "corinthians" in mandante.lower():
                    placar_mandante = "1"
                    placar_visitante = "4"
                else:
                    placar_mandante = "4"
                    placar_visitante = "1"
            elif is_cruzeiro_flamengo:
                if "cruzeiro" in mandante.lower():
                    placar_mandante = "2"
                    placar_visitante = "1"
                else:
                    placar_mandante = "1"
                    placar_visitante = "2"
            elif is_mirassol_remo:
                if "mirassol" in mandante.lower():
                    placar_mandante = "2"
                    placar_visitante = "1"
                else:
                    placar_mandante = "1"
                    placar_visitante = "2"
            elif is_athletico_vitoria:
                placar_mandante = "1"
                placar_visitante = "1"
            elif is_cruzeiro_atleticomg:
                # Atlético-MG mandante (Arena MRV) e Cruzeiro visitante: Cruzeiro 1 x 0 Atlético-MG
                if "cruzeiro" in mandante.lower():
                    placar_mandante = "1"
                    placar_visitante = "0"
                else:
                    placar_mandante = "0"
                    placar_visitante = "1"
            elif is_atletico_gremio:
                if "atlético" in mandante.lower() or "atletico" in mandante.lower():
                    placar_mandante = "3"
                    placar_visitante = "0"
                else:
                    placar_mandante = "0"
                    placar_visitante = "3"
            elif is_vasco_flamengo:
                if "vasco" in mandante.lower():
                    placar_mandante = "1"
                    placar_visitante = "4"  # Ajustado para 4 a 1 conforme solicitado
                else:
                    placar_mandante = "4"
                    placar_visitante = "1"
            elif is_gremio_athletico:
                status_descricao = "Agendado"

            placar = f"{placar_mandante} x {placar_visitante}"
            
            # Jogos que devem ser considerados encerrados obrigatoriamente pelas regras manuais
            jogo_encerrado_forcado = (
                is_corinthians_palmeiras or 
                is_cruzeiro_flamengo or 
                is_mirassol_remo or 
                is_athletico_vitoria or 
                is_atletico_gremio or
                is_cruzeiro_atleticomg or
                is_vasco_flamengo
            )
            
            # Definição da aba sugerida
            if is_gremio_athletico or "scheduled" in tipo_status.get("name", "").lower():
                aba = "agendados"
            elif "encerrado" in status_descricao.lower() or "post" in tipo_status.get("name", "").lower() or jogo_encerrado_forcado:
                aba = "encerrados"
            else:
                aba = "hoje"

            jogos_formatados.append({
                "mandante": mandante,
                "visitante": visitante,
                "estadio": estadio,
                "escudo_mandante": escudo_mandante,
                "escudo_visitante": escudo_visitante,
                "placar": placar,
                "status": "Partida Encerrada" if jogo_encerrado_forcado else status_descricao,
                "aba_sugerida": aba
            })
            
        return {
            "status": "sucesso",
            "fonte": "API Customizada com Ajustes",
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
                "status": "Partida Encerrada",
                "aba_sugerida": "encerrados"
            }
        ]
    }
