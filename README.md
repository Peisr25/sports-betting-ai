> [!IMPORTANT]
> Para o correto funcionamento deste projeto, é crucial que você possua uma chave de API válida para a [API-Football](https://www.api-football.com/). O plano gratuito oferece 100 requisições por dia, o que é suficiente para testes e uso moderado.

# Sports Betting AI - Agente de Apostas Esportivas

Este projeto é um sistema completo de análise e recomendação de apostas esportivas, projetado para ser flexível e poderoso. Ele utiliza uma arquitetura híbrida que combina a orquestração de workflows do **n8n** com o poder de processamento de um **script Python local** para cálculos de Machine Learning.

O sistema é capaz de coletar estatísticas detalhadas de times de futebol, processar esses dados, e utilizar um modelo de IA (ensemble de Poisson e XGBoost) para gerar probabilidades e recomendações de apostas para diversos mercados, como resultado final, total de gols, cartões e escanteios.

## Arquitetura do Sistema

A solução é dividida em dois componentes principais que trabalham em conjunto:

1.  **API Python (Backend de IA)**: O cérebro do sistema, responsável por todo o processamento pesado. Ele é construído com FastAPI e inclui:
    *   **Coleta de Dados**: Módulo que se conecta à API-Football para buscar estatísticas de ligas, times e partidas.
    *   **Processamento e Feature Engineering**: Transforma dados brutos em features relevantes para o modelo de IA.
    *   **Modelagem de IA**: Utiliza um modelo *ensemble* que combina a robustez estatística da **Distribuição de Poisson** para mercados de gols com a precisão de um modelo de **Machine Learning (XGBoost)** para mercados mais complexos (cartões, escanteios, etc.).
    *   **Banco de Dados**: Armazena dados em um banco de dados SQLite local para rápido acesso e para evitar chamadas repetidas à API.
    *   **API REST**: Expõe endpoints para que o n8n (ou qualquer outro cliente) possa solicitar predições e acionar atualizações de dados.

2.  **Workflows n8n (Frontend e Orquestração)**: Atua como a camada de interface e automação. O projeto inclui dois workflows pré-construídos:
    *   **Workflow de Predição**: Um webhook que recebe a partida desejada pelo usuário, chama a API Python para obter as análises e retorna um JSON formatado com as probabilidades e recomendações.
    *   **Workflow de Atualização**: Um workflow agendado (executa diariamente) que aciona a API Python para atualizar o banco de dados local com os últimos resultados e estatísticas, garantindo que as predições sejam sempre baseadas em dados recentes.

Para uma visão mais aprofundada da arquitetura, consulte o documento [ARCHITECTURE.md](./docs/ARCHITECTURE.md).

## Funcionalidades

-   **Análise Multi-Mercado**: Gera probabilidades para uma vasta gama de mercados:
    -   Resultado Final (Vitória/Empate/Derrota)
    -   Total de Gols (Over/Under)
    -   Ambos Marcam (Sim/Não)
    -   Total de Cartões (Over/Under)
    -   Total de Escanteios (Over/Under)
    -   Total de Faltas (Over/Under)
-   **Recomendações Claras**: Fornece recomendações de aposta com nível de confiança (Muito Alta, Alta, Média) e uma breve justificativa.
-   **Modelo Híbrido (Ensemble)**: Combina modelos estatísticos e de Machine Learning para predições mais precisas e robustas.
-   **Sistema Automatizado**: O n8n gerencia as requisições do usuário e a atualização periódica dos dados de forma automática.
-   **Flexível e Extensível**: A arquitetura modular permite adicionar novas ligas, novos mercados de aposta e até mesmo novos modelos de IA com facilidade.
-   **Gerenciamento de API**: O sistema controla o número de requisições à API-Football para se manter dentro dos limites do plano utilizado.

## Estrutura do Projeto

```
sports-betting-ai/
│
├── python_api/              # Contém todo o código do backend Python
│   ├── app.py                 # Servidor da API (FastAPI)
│   ├── models/                # Modelos de IA (Poisson, ML, Ensemble)
│   ├── data/                  # Módulos de coleta, processamento e DB
│   ├── prediction/            # Engine de predição
│   ├── config.py              # Configurações do sistema
│   ├── requirements.txt       # Dependências Python
│   └── .env.example           # Arquivo de exemplo para variáveis de ambiente
│
├── n8n_workflows/           # Contém os workflows para importação no n8n
│   ├── betting_prediction.json
│   └── data_update.json
│
├── database/                # Diretório onde o banco de dados será criado
│   └── sports_betting.db      # (Criado na primeira execução)
│
├── docs/                    # Documentação detalhada
│   ├── ARCHITECTURE.md
│   ├── API_DOCUMENTATION.md
│   ├── N8N_SETUP.md
│   └── USER_GUIDE.md
│
└── README.md                # Este arquivo
```

## Como Começar

Para colocar o sistema em funcionamento, siga os passos abaixo.

### Pré-requisitos

-   Python 3.10 ou superior
-   Acesso a uma instância do n8n (Cloud ou Self-hosted)
-   Uma chave de API da [API-Football](https://www.api-football.com/)

### 1. Configurar o Backend Python

Clone ou faça o download deste repositório para sua máquina local.

```bash
# Navegue até o diretório da API
cd sports-betting-ai/python_api

# Crie um ambiente virtual (recomendado)
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt

# Renomeie o arquivo .env.example para .env
cp .env.example .env
```

Abra o arquivo `.env` recém-criado e adicione sua chave da API-Football:

```dotenv
# .env
API_FOOTBALL_KEY=sua_chave_de_api_aqui
```

### 2. Iniciar a API Python

Com as dependências instaladas e a chave de API configurada, inicie o servidor:

```bash
# A partir do diretório python_api/
uvicorn app:app --host 0.0.0.0 --port 5000
```

O servidor estará rodando em `http://localhost:5000`. Você pode acessar a documentação interativa da API em `http://localhost:5000/docs`.

### 3. Configurar os Workflows no n8n

Agora, importe os workflows para sua instância do n8n.

1.  No seu painel do n8n, vá em **Workflows**.
2.  Clique em **Import from File**.
3.  Selecione os arquivos `betting_prediction.json` e `data_update.json` do diretório `n8n_workflows/` e importe-os um de cada vez.

Para instruções detalhadas sobre como configurar e ativar os workflows, consulte o guia [N8N_SETUP.md](./docs/N8N_SETUP.md).

### 4. Popular o Banco de Dados (Primeira Execução)

Para que o sistema possa fazer predições, ele precisa de dados históricos. Use o endpoint `/update` para popular o banco de dados pela primeira vez. Você pode fazer isso com uma ferramenta como o `curl` ou diretamente pelo n8n.

```bash
curl -X POST http://localhost:5000/update -H "Content-Type: application/json" -d '{
  "league": "Brasileirão Série A",
  "season": 2025
}'
```

Este processo pode levar alguns minutos, pois ele está buscando dados da API-Football e salvando-os localmente.

### 5. Fazer sua Primeira Predição

Com tudo configurado, você pode fazer uma predição! Use o webhook do n8n ou chame a API diretamente.

Para instruções detalhadas sobre como usar o sistema, consulte o [USER_GUIDE.md](./docs/USER_GUIDE.md).

## Limitações e Próximos Passos

-   **Treinamento de Modelo**: O modelo de Machine Learning (XGBoost) neste projeto é fornecido como uma estrutura. Para obter predições de alta qualidade, é necessário treinar o modelo com um grande volume de dados históricos. Um script de treinamento pode ser desenvolvido como um próximo passo.
-   **Odds de Apostas**: O sistema atualmente não compara as probabilidades calculadas com as odds oferecidas pelas casas de apostas. Integrar uma API de odds para calcular o **valor esperado (EV)** seria uma melhoria significativa.
-   **Cobertura de Ligas**: O sistema está pré-configurado para algumas das principais ligas, mas pode ser facilmente estendido para outras, bastando adicionar o ID da liga no arquivo de configuração.

## Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir uma *issue* ou enviar um *pull request*.


