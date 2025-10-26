# Documentação da API Python (Backend de IA)

Esta documentação descreve os endpoints disponíveis na API Python, que serve como o motor de análise e predição do sistema. A API é construída com **FastAPI** e pode ser acessada em `http://localhost:5000` quando executada localmente.

A documentação interativa (Swagger UI) está disponível em `http://localhost:5000/docs`.

## Endpoints Principais

### 1. `POST /predict`

Este é o endpoint principal para obter predições para uma partida específica. Ele orquestra a coleta de dados em tempo real, o processamento e a execução dos modelos de IA para gerar um relatório completo de probabilidades e recomendações.

-   **Método**: `POST`
-   **URL**: `/predict`
-   **Corpo da Requisição** (JSON):

| Campo     | Tipo     | Obrigatório | Descrição                                                                 |
| :-------- | :------- | :---------- | :------------------------------------------------------------------------ |
| `home_team` | `string` | Sim         | Nome exato do time da casa.                                               |
| `away_team` | `string` | Sim         | Nome exato do time visitante.                                             |
| `league`    | `string` | Não         | Nome da liga. Padrão: `"Brasileirão Série A"`.                             |
| `season`    | `integer`| Não         | Ano da temporada. Padrão: `2025`.                                         |

-   **Exemplo de Requisição**:

```bash
curl -X POST http://localhost:5000/predict -H "Content-Type: application/json" -d 
    "{
      \"home_team\": \"Flamengo\",
      \"away_team\": \"Palmeiras\",
      \"league\": \"Brasileirão Série A\"
    }"
```

-   **Resposta de Sucesso (200 OK)**:

Retorna um objeto JSON detalhado contendo estatísticas, probabilidades e recomendações. Veja um exemplo simplificado abaixo:

```json
{
  "match": {
    "home_team": "Flamengo",
    "away_team": "Palmeiras",
    "league": "Brasileirão Série A"
  },
  "predictions": {
    "result": {
      "home_win": 0.45,
      "draw": 0.28,
      "away_win": 0.27
    },
    "over_2_5": 0.62,
    // ... outras predições
  },
  "recommendations": [
    {
      "market": "Over 2.5 Gols",
      "bet": "Sim",
      "probability": 0.62,
      "confidence": "Alta",
      "reasoning": "Ambos times têm média de 1.8 gols/jogo"
    },
    // ... outras recomendações
  ]
}
```

-   **Resposta de Erro**:
    -   `400 Bad Request`: Se os times não forem encontrados ou se os dados forem insuficientes.
    -   `500 Internal Server Error`: Se ocorrer um erro inesperado durante o processamento.

### 2. `POST /update`

Este endpoint é usado para popular e atualizar o banco de dados local com os dados mais recentes de uma liga específica. Ele busca times, partidas e estatísticas da API-Football.

> **Atenção**: Este processo pode consumir um número significativo de requisições da sua cota na API-Football e pode levar vários minutos para ser concluído.

-   **Método**: `POST`
-   **URL**: `/update`
-   **Corpo da Requisição** (JSON):

| Campo    | Tipo     | Obrigatório | Descrição                                      |
| :------- | :------- | :---------- | :--------------------------------------------- |
| `league`   | `string` | Não         | Nome da liga. Padrão: `"Brasileirão Série A"`. |
| `season`   | `integer`| Não         | Ano da temporada. Padrão: `2025`.              |

-   **Exemplo de Requisição**:

```bash
curl -X POST http://localhost:5000/update -H "Content-Type: application/json" -d 
    "{
      \"league\": \"Premier League\",
      \"season\": 2025
    }"
```

-   **Resposta de Sucesso (200 OK)**:

```json
{
  "status": "success",
  "message": "Dados da Premier League atualizados",
  "api_requests_used": 53
}
```

## Endpoints de Apoio

### `GET /`

Retorna informações básicas sobre a API e os endpoints disponíveis.

-   **Método**: `GET`
-   **URL**: `/`

### `GET /health`

Verifica o estado da API, incluindo a configuração da chave da API-Football e a conexão com o banco de dados.

-   **Método**: `GET`
-   **URL**: `/health`

### `GET /leagues`

Retorna uma lista de ligas pré-configuradas e suportadas pelo sistema.

-   **Método**: `GET`
-   **URL**: `/leagues`

### `GET /stats`

Fornece estatísticas sobre o uso da API-Football, mostrando o número de requisições feitas na sessão atual e o limite diário.

-   **Método**: `GET`
-   **URL**: `/stats`

## Modelo de Dados Interno

A API utiliza um banco de dados SQLite para armazenar dados e acelerar as consultas. As principais tabelas são:

-   `leagues`: Armazena informações sobre as ligas.
-   `teams`: Armazena informações sobre os times.
-   `matches`: Contém dados detalhados de cada partida, incluindo resultados e estatísticas.
-   `predictions`: Guarda um histórico das predições feitas pelo sistema.

Para mais detalhes sobre o esquema do banco de dados, consulte o arquivo `python_api/data/database.py`.

