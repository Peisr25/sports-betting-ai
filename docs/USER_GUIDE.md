> [!NOTE]
> Lembre-se de substituir `sua-url-do-webhook-aqui` pela URL real do seu webhook de predição do n8n.

# Guia do Usuário - Fazendo suas Predições

Este guia mostra como interagir com o sistema para obter predições de apostas esportivas. Presume-se que você já tenha configurado o [backend Python e os workflows do n8n](./N8N_SETUP.md) conforme descrito nos guias de instalação.

## Como Solicitar uma Predição

A principal forma de interagir com o sistema é através do **webhook do n8n**. Você fará uma requisição `POST` para a URL do seu webhook de predição, enviando os nomes dos times para os quais deseja a análise.

### Ferramentas que Você Pode Usar

Você pode usar qualquer ferramenta que faça requisições HTTP. Algumas das mais comuns são:

-   **`curl`**: Uma ferramenta de linha de comando disponível na maioria dos sistemas operacionais.
-   **Postman**: Um aplicativo gráfico popular para testar APIs.
-   **Outro workflow n8n**: Você pode criar um novo workflow no n8n que simplesmente chama o webhook de predição.
-   **Qualquer linguagem de programação**: Python (com `requests`), JavaScript (com `fetch`), etc.

### Passo a Passo: Usando `curl`

Esta é a forma mais rápida e direta de testar o sistema.

1.  **Abra seu terminal** (ou Prompt de Comando no Windows).

2.  **Monte o comando `curl`**: Você precisará da URL do seu webhook e dos nomes dos times.

3.  **Execute o comando**:

**Exemplo 1: Predição para um jogo do Brasileirão**

```bash
curl -X POST sua-url-do-webhook-aqui \
-H "Content-Type: application/json" \
-d '{
  "home_team": "Flamengo",
  "away_team": "Corinthians"
}'
```

**Exemplo 2: Predição para um jogo da Premier League**

Para analisar um jogo de outra liga suportada, basta adicionar o campo `league` na sua requisição:

```bash
curl -X POST sua-url-do-webhook-aqui \
-H "Content-Type: application/json" \
-d '{
  "home_team": "Manchester United",
  "away_team": "Liverpool",
  "league": "Premier League"
}'
```

## Entendendo a Resposta

Se a requisição for bem-sucedida, o sistema retornará um objeto JSON rico em informações. A resposta é estruturada para ser clara e fácil de interpretar.

```json
{
  "success": true,
  "match": {
    "home_team": "Flamengo",
    "away_team": "Corinthians",
    "league": "Brasileirão Série A"
  },
  "probabilities": {
    "home_win": "48.5%",
    "draw": "27.1%",
    "away_win": "24.4%",
    "over_2_5_goals": "59.2%",
    "btts_yes": "55.8%"
  },
  "top_recommendations": [
    {
      "market": "Total de Cartões",
      "bet": "Over 4.5 Cartões",
      "probability": "68.2%",
      "confidence": "Alta",
      "reasoning": "Histórico de confrontos com média de 5.1 cartões"
    },
    {
      "market": "Resultado Final (1x2)",
      "bet": "Vitória do Time da Casa",
      "probability": "48.5%",
      "confidence": "Média",
      "reasoning": "Probabilidade de 48.5%"
    }
  ],
  "expected_goals": {
    "home": 1.7,
    "away": 1.1,
    "total": 2.8
  },
  "most_likely_score": {
    "home": 1,
    "away": 1,
    "probability": 0.12
  }
}
```

### Seções da Resposta

-   **`match`**: Confirma os detalhes da partida que você solicitou.
-   **`probabilities`**: Apresenta as probabilidades calculadas pelo modelo de IA para os principais mercados. Os valores são formatados como strings em porcentagem para facilitar a leitura.
-   **`top_recommendations`**: Esta é a parte mais importante. O sistema analisa todas as probabilidades e apresenta as apostas que ele considera terem o melhor valor, ordenadas por confiança. Cada recomendação inclui:
    -   `market`: O mercado da aposta (ex: "Total de Gols").
    -   `bet`: A aposta específica (ex: "Over 2.5 Gols").
    -   `probability`: A probabilidade calculada para aquele evento.
    -   `confidence`: Um nível de confiança qualitativo (Muito Alta, Alta, Média) para ajudar na sua decisão.
    -   `reasoning`: Uma breve explicação do porquê daquela recomendação.
-   **`expected_goals`**: A expectativa de gols para cada time, calculada pelo modelo de Poisson. É um ótimo indicador da tendência ofensiva da partida.
-   **`most_likely_score`**: O placar exato com a maior probabilidade de ocorrer, segundo o modelo de Poisson.

## Dicas de Uso

-   **Comece com o `UPDATE`**: Antes de fazer predições, sempre garanta que seu banco de dados está atualizado. Use o endpoint `/update` da API ou execute o workflow de atualização no n8n.
-   **Use Nomes Exatos**: O sistema depende dos nomes exatos dos times conforme eles estão na API-Football. Se uma predição falhar, o primeiro passo é verificar se os nomes dos times estão corretos.
-   **Não Confie Cegamente**: Lembre-se que este é um modelo estatístico. As predições são probabilidades, não garantias. Use as recomendações como um forte auxílio à sua própria análise, e não como uma verdade absoluta.
-   **Gerencie sua Cota de API**: Fique de olho no número de requisições que você faz à API-Football, especialmente se estiver no plano gratuito. O endpoint `/stats` da API Python pode ajudar a monitorar seu uso.

Com este guia, você está pronto para explorar todo o potencial do seu novo agente de apostas esportivas.as esportivas.ivas. Boas análises!
