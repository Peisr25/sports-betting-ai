# Guia Rápido de Início (Quick Start)

Este guia permite que você comece a usar o sistema de apostas esportivas em apenas alguns minutos.

## Pré-requisitos Rápidos

-   Python 3.10+
-   Uma chave de API da [API-Football](https://www.api-football.com/)
-   n8n (Cloud ou Self-hosted)

## 5 Passos para Começar

### 1. Instalar Dependências Python

```bash
cd sports-betting-ai/python_api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configurar API Key

```bash
# Renomear .env.example para .env
cp .env.example .env

# Editar .env e adicionar sua API key
# API_FOOTBALL_KEY=sua_chave_aqui
```

### 3. Iniciar o Servidor Python

```bash
uvicorn app:app --host 0.0.0.0 --port 5000
```

O servidor estará rodando em `http://localhost:5000`

### 4. Importar Workflows no n8n

1. Abra seu n8n
2. Vá em **Workflows** → **Import from File**
3. Importe `n8n_workflows/betting_prediction.json`
4. Importe `n8n_workflows/data_update.json`
5. Ative ambos os workflows

### 5. Popular o Banco de Dados

Antes da primeira predição, atualize o banco de dados:

```bash
curl -X POST http://localhost:5000/update \
-H "Content-Type: application/json" \
-d '{"league": "Brasileirão Série A", "season": 2025}'
```

## Fazer sua Primeira Predição

Agora você pode fazer predições! Use a URL do webhook do n8n:

```bash
curl -X POST sua-url-do-webhook-n8n \
-H "Content-Type: application/json" \
-d '{
  "home_team": "Flamengo",
  "away_team": "Palmeiras"
}'
```

## Próximos Passos

-   Leia o [README.md](./README.md) para entender a arquitetura completa
-   Consulte [USER_GUIDE.md](./docs/USER_GUIDE.md) para uso avançado
-   Veja [API_DOCUMENTATION.md](./docs/API_DOCUMENTATION.md) para todos os endpoints

## Solução Rápida de Problemas

-   **Erro de conexão no n8n**: Verifique se a API Python está rodando
-   **Times não encontrados**: Use os nomes exatos dos times da API-Football
-   **Limite de API atingido**: O plano gratuito tem 100 requisições/dia

Pronto! Você agora tem um agente de apostas esportivas funcionando! 🎉

