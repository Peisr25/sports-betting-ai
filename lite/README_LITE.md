# Sports Betting AI - Versão LITE 🌟

Versão gratuita com modelo de Poisson para predições de apostas esportivas.

## 📋 Características

✅ **API REST completa** com FastAPI
✅ **Modelo de Poisson** para predições estatísticas
✅ **API football-data.org** (tier gratuito)
✅ **SEM banco de dados** (tudo em memória)
✅ **Scripts prontos** para usar
✅ **9+ competições suportadas**

## 🎯 Mercados de Apostas

- ✅ Resultado (1X2) - Vitória/Empate/Derrota
- ✅ Total de Gols - Over/Under (0.5, 1.5, 2.5, 3.5, 4.5)
- ✅ Ambos Marcam (BTTS)
- ✅ Placar Mais Provável
- ✅ Escanteios (estimativa)
- ✅ Cartões (estimativa)

## 🏆 Competições Suportadas

| Código | Competição | País |
|--------|------------|------|
| **PL** | Premier League | Inglaterra |
| **BSA** | Brasileirão Série A | Brasil |
| **PD** | La Liga | Espanha |
| **BL1** | Bundesliga | Alemanha |
| **SA** | Serie A | Itália |
| **FL1** | Ligue 1 | França |
| **CL** | Champions League | Europa |
| **PPL** | Primeira Liga | Portugal |
| **DED** | Eredivisie | Holanda |

## 🚀 Instalação Rápida

### 1. Requisitos

- Python 3.8+
- Chave API da football-data.org (gratuita)

### 2. Instalar Dependências

```bash
cd lite/python_api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configurar API Key

1. Obtenha sua chave em: https://www.football-data.org/client/register
2. Copie o arquivo de configuração:

```bash
cp .env.example .env
```

3. Edite `.env` e adicione sua chave:

```
FOOTBALL_DATA_API_KEY=sua_chave_aqui
```

### 4. Iniciar Servidor

```bash
python app.py
```

Acesse: http://localhost:5000/docs

## 📖 Uso

### API REST

#### 1. Listar Competições

```bash
curl http://localhost:5000/competitions
```

#### 2. Listar Times

```bash
curl http://localhost:5000/teams/PL
```

#### 3. Próximas Partidas

```bash
curl "http://localhost:5000/matches/BSA?status=SCHEDULED"
```

#### 4. Classificação

```bash
curl http://localhost:5000/standings/PL
```

#### 5. Fazer Predição

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "home_team": "Arsenal",
    "away_team": "Chelsea",
    "competition": "PL"
  }'
```

### Scripts Python

#### Classificação

```bash
cd examples
python classificacao.py BSA
```

#### Próximos Jogos

```bash
python proximos_jogos.py PL
```

#### Predição Fácil

```bash
python easy_predict.py Arsenal Chelsea PL
python easy_predict.py Flamengo Palmeiras BSA
```

#### Jogos + Predições Automáticas

```bash
python jogos_e_predicoes.py BSA 5
```

## 📊 Exemplo de Resposta

```json
{
  "match": {
    "home_team": "Arsenal FC",
    "away_team": "Chelsea FC",
    "competition": "PL"
  },
  "statistics": {
    "home": {
      "goals_avg": 2.1,
      "conceded_avg": 1.0,
      "matches": 10,
      "form": "7W-2D-1L"
    },
    "away": {
      "goals_avg": 1.8,
      "conceded_avg": 1.2,
      "matches": 10,
      "form": "5W-3D-2L"
    }
  },
  "predictions": {
    "model": "Poisson Distribution",
    "result": {
      "home_win": 0.524,
      "draw": 0.267,
      "away_win": 0.209
    },
    "goals": {
      "over_2.5": 0.618,
      "under_2.5": 0.382
    },
    "both_teams_score": {
      "yes": 0.672,
      "no": 0.328
    },
    "most_likely_score": {
      "score": "2-1",
      "probability": 0.156
    }
  },
  "recommendations": [
    {
      "market": "Resultado (1X2)",
      "bet": "Vitória Arsenal FC",
      "confidence": "Média",
      "probability": 0.524
    },
    {
      "market": "Total de Gols",
      "bet": "Over 2.5",
      "confidence": "Alta",
      "probability": 0.618
    },
    {
      "market": "Ambos Marcam",
      "bet": "Sim",
      "confidence": "Alta",
      "probability": 0.672
    }
  ],
  "confidence": "Alta"
}
```

## 🔬 Como Funciona o Modelo de Poisson

O modelo usa a **distribuição de Poisson** para calcular probabilidades de gols:

```
P(X = k) = (λ^k * e^(-λ)) / k!
```

Onde:
- **λ (lambda)** = média de gols esperados
- **k** = número de gols
- **e** = constante de Euler (2.71828...)

### Cálculo de Lambda

```python
lambda_casa = (ataque_casa + defesa_fora) / 2 + 0.15  # Fator casa
lambda_fora = (ataque_fora + defesa_casa) / 2 - 0.15
```

### Vantagens

✅ Modelo estatístico sólido e comprovado
✅ Rápido e eficiente
✅ Não requer treinamento
✅ Bom para times com histórico consistente

### Limitações

⚠️ Não considera forma recente detalhada
⚠️ Não analisa confrontos diretos
⚠️ Não considera lesões/suspensões
⚠️ Estimativas simples para escanteios/cartões

## ⚙️ Configurações

Edite `config.py` para ajustar:

```python
DEFAULT_HISTORY_MATCHES = 10  # Partidas para análise
MIN_CONFIDENCE_THRESHOLD = 0.55  # Confiança mínima (55%)
CACHE_TTL_SECONDS = 300  # Cache de 5 minutos
```

## 📝 Limites da API Gratuita

- **10 requisições por minuto**
- **100 requisições por dia** (dependendo do plano)
- Algumas competições podem não estar disponíveis no tier gratuito

## 🆙 Upgrade para PRO

Quer mais recursos? Veja a **versão PRO**:

- ✅ Modelo XGBoost (Machine Learning)
- ✅ Sistema Ensemble (múltiplos modelos)
- ✅ Análise de Valor Esperado (EV)
- ✅ Backtesting de estratégias
- ✅ Banco de dados SQLite
- ✅ 7+ mercados adicionais
- ✅ Recomendações automáticas avançadas
- ✅ Workflows n8n completos

Veja: `../pro/README_PRO.md`

## 📚 Documentação Adicional

- `docs/API_DOCUMENTATION.md` - Documentação completa da API
- `docs/USER_GUIDE.md` - Guia do usuário
- `docs/N8N_SETUP.md` - Como configurar n8n

## ⚠️ Avisos

1. **Uso Educacional**: Este sistema é para fins educacionais e de pesquisa.
2. **Não Garantimos Lucros**: Predições estatísticas não garantem resultados.
3. **Aposte com Responsabilidade**: Apenas o que você pode perder.
4. **Verifique Legalidade**: Apostas podem ser ilegais em sua região.

## 🐛 Problemas Comuns

### API Key Inválida

```
Erro: API key inválida ou sem acesso a esta competição
```

**Solução**: Verifique sua API key no `.env` e se ela está ativa em football-data.org

### Limite de Requisições

```
Erro: Limite de requisições atingido (10/min no tier gratuito)
```

**Solução**: Aguarde 1 minuto ou faça upgrade do plano

### Time Não Encontrado

```
Erro: Time da casa 'xxx' não encontrado
```

**Solução**: Use nomes exatos ou parciais (ex: "Arsenal", "Flamengo")

## 📞 Suporte

- Documentação: `/docs`
- Issues: GitHub Issues
- API Docs: http://localhost:5000/docs

---

**Feito com ❤️ para a comunidade de análise esportiva**

*Versão Lite - Modelo de Poisson - football-data.org*
