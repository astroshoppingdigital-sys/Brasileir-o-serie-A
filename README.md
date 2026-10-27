# <img src="https://i.postimg.cc/J7s81cJG/Gemini-Generated-Image-68mx5c68mx5c68mx.jpg" alt="Live Gol Logo" width="45" height="45" style="vertical-align: middle;"> Live Gol Série A - API Oficial

API REST em tempo real desenvolvida com **FastAPI** e hospedada no **Render**, criada para rastrear e fornecer dados atualizados das partidas do **Campeonato Brasileiro Série A**. O sistema organiza os jogos de forma dinâmica em abas (*Ao Vivo*, *Agendados* e *Encerrados*), trazendo os escudos oficiais dos clubes e status atualizados em tempo real.

---

## 🚀 Tecnologias Utilizadas

* **Python 3.10+**
* **FastAPI** (Framework web de alta performance)
* **Uvicorn** (Servidor ASGI)
* **Requests** (Consumo de dados da API esportiva oficial)
* **Render** (Plataforma de hospedagem em nuvem)

---

## 📡 Endpoints Disponíveis

### 1. Status da API (Raiz)
* **URL:** `GET /`
* **Retorno:** Confirma se o servidor está online e exibe o link para a documentação.

### 2. Listagem de Jogos da Série A
* **URL:** `GET /jogos/serie-a`
* **Retorno:** Retorna um JSON estruturado contendo todos os jogos da temporada, separados automaticamente por abas, com placares, status, horários e os **escudos oficiais** dos clubes.

---

## 📋 Exemplo de Resposta JSON (`/jogos/serie-a`)

```json
{
  "status": "sucesso",
  "fonte": "Live Gol Série A - Oficial",
  "jogos": [
    {
      "id": "123456",
      "nome_evento": "Flamengo x Palmeiras",
      "mandante": "Flamengo",
      "escudo_mandante": "[https://a.espncdn.com/i/teamlogos/soccer/500/819.png](https://a.espncdn.com/i/teamlogos/soccer/500/819.png)",
      "visitante": "Palmeiras",
      "escudo_visitante": "[https://a.espncdn.com/i/teamlogos/soccer/500/874.png](https://a.espncdn.com/i/teamlogos/soccer/500/874.png)",
      "placar": "1 x 0",
      "status": "Em andamento",
      "cor_status": "verde",
      "aba_sugerida": "ao vivo",
      "minutos_para_inicio": 0,
      "data_original": "2026-10-27T19:00:00Z"
    }
  ]
}
