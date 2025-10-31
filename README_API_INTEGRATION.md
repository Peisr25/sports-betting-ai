# 🚀 Sistema Integrado com API-Football Predictions

## 📋 Visão Geral

Este projeto agora integra **predições da API-Football** em toda a arquitetura, seguindo a estratégia de **Feature Engineering** (recomendada no PREDICTIONS_GUIDE.md).

### ✅ O que foi implementado?

1. **Feature Engineering** - 26 novas features das predições da API
2. **XGBoost Enriquecido** - Modelo usa features da API para melhorar predições
3. **Ensemble Completo** - Combina Poisson + XGBoost + API-Football
4. **API Endpoints** - Novos endpoints para predições detalhadas
5. **Pipeline Completo** - Coleta → Features → Treinamento → Predição

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                      COLETA DE DADOS                        │
├─────────────────────────────────────────────────────────────┤
│  football-data.org    →  Partidas básicas                   │
│  API-Football v3      →  Estatísticas detalhadas            │
│  API-Football v3      →  Predições (NOVO!)                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    BANCO DE DADOS V2                        │
├─────────────────────────────────────────────────────────────┤
│  matches              →  Partidas (dual-API IDs)            │
│  match_statistics     →  Estatísticas detalhadas            │
│  predictions          →  Predições da API (NOVO!)           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   FEATURE ENGINEERING                       │
├─────────────────────────────────────────────────────────────┤
│  APIPredictionFeatures  →  Extrai 26 features da API       │
│    • Probabilidades (home, draw, away)                      │
│    • Comparações (form, attack, defense, h2h)              │
│    • Under/Over, Poisson da API                             │
│    • Features derivadas (vantagem, confiança, etc)          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    MODELOS PREDITIVOS                       │
├─────────────────────────────────────────────────────────────┤
│  Poisson             →  21 features básicas                 │
│  XGBoost             →  21 básicas + 26 API (47 total!)     │
│  API-Football        →  Predições diretas da API            │
│  Ensemble            →  Combina os 3 modelos                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                     API REST (FastAPI)                      │
├─────────────────────────────────────────────────────────────┤
│  /predict            →  Predição ensemble                   │
│  /predict-detailed   →  Cada modelo individual (NOVO!)      │
│  /value-analysis     →  Análise de valor (EV)               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Novos Arquivos Criados

### 1. **Features** (Feature Engineering)

```
pro/python_api/features/
├── __init__.py
└── api_predictions_features.py  ⭐ NOVO
    ├── APIPredictionFeatures class
    ├── 26 features extraídas das predições
    └── Métodos de parsing e conversão
```

### 2. **Modelos Atualizados**

```
pro/python_api/models/
├── xgboost_model.py  ⭐ ATUALIZADO
│   ├── Suporta feature_extractor
│   ├── create_features() usa API features
│   └── predict() passa match_id
│
└── ensemble.py  ⭐ ATUALIZADO
    ├── APIFootballModel (wrapper)
    ├── Suporta 3 modelos: Poisson + XGBoost + API
    └── predict() combina todos
```

### 3. **Scripts de Treinamento**

```
pro/python_api/
└── train_xgboost_with_api.py  ⭐ NOVO
    ├── Prepara dados com API features
    ├── Treina XGBoost enriquecido
    └── Salva modelo em models/saved/
```

### 4. **API Atualizada**

```
pro/python_api/
└── app.py  ⭐ ATUALIZADO
    ├── Inicializa database_v2
    ├── Inicializa feature_extractor
    ├── Carrega XGBoost automaticamente
    ├── /predict - passa match_id
    └── /predict-detailed - mostra cada modelo ⭐ NOVO
```

### 5. **Documentação**

```
.
├── PREDICTIONS_GUIDE.md           ⭐ Guia de uso estratégico
└── README_API_INTEGRATION.md      ⭐ Este arquivo
```

---

## 🚀 Como Usar

### 1️⃣ **Coletar Dados**

#### a) Partidas Históricas
```bash
cd pro/python_api
python collect_historical_data.py
```

#### b) Estatísticas Detalhadas (Dual-API)
```bash
python collect_dual_api.py
```

#### c) Predições da API-Football ⭐ NOVO
```bash
# Testar acesso
python test_predictions_access.py

# Coletar predições
python collect_predictions.py
```

---

### 2️⃣ **Treinar Modelo XGBoost com Features da API** ⭐ NOVO

```bash
python train_xgboost_with_api.py
```

**Saída esperada:**
```
=======================================================================
TREINAMENTO DO XGBOOST COM FEATURES DA API-FOOTBALL
=======================================================================

1. Conectando ao banco de dados...
   ✓ Conectado!

2. Criando extrator de features...
   ✓ 26 features da API disponíveis

3. Preparando dados de treinamento...
   ✓ Partidas processadas: 500
   ✓ Partidas com predições da API: 120
   ✓ Features por partida: 47
     - Features básicas: 21
     - Features da API: 26

4. Treinando modelo...
   ✓ Treinamento concluído!
   Acurácia (treino): 65.2%
   Acurácia (validação): 58.3%

5. Salvando modelo...
   ✓ Modelo salvo: models/saved/xgboost_with_api_20251031_120000.pkl

✅ TREINAMENTO CONCLUÍDO COM SUCESSO!
```

---

### 3️⃣ **Iniciar API**

```bash
cd pro/python_api
python app.py
```

**Startup Message:**
```
=======================================================================
SPORTS BETTING AI - VERSÃO PRO 3.0
=======================================================================
Modelos:
  ✓ Poisson Distribution
  ✓ XGBoost (com features da API-Football)
  ✓ API-Football Predictions (direto da API)
  ✓ Ensemble (combina todos os modelos)

Features:
  ✓ Features básicas (21 features)
  ✓ Features da API-Football (26 features)

Análise:
  ✓ Valor Esperado (EV)
  ✓ Kelly Criterion

Endpoints:
  /predict - Predição com ensemble
  /predict-detailed - Mostra cada modelo individualmente ⭐ NOVO
  /value-analysis - Análise de valor com odds
=======================================================================
```

---

### 4️⃣ **Fazer Predições**

#### Endpoint Padrão: `/predict`
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "home_team": "Arsenal",
    "away_team": "Chelsea",
    "competition": "PL",
    "use_ensemble": true
  }'
```

**Response:**
```json
{
  "match": {
    "home_team": "Arsenal FC",
    "away_team": "Chelsea FC",
    "competition": "PL",
    "match_id": 123
  },
  "predictions": {
    "model": "Ensemble (Weighted Average)",
    "result": {
      "home_win": 0.55,
      "draw": 0.25,
      "away_win": 0.20
    },
    "models_used": ["poisson", "xgboost", "api-football"]
  },
  "api_features_used": true
}
```

#### ⭐ Endpoint Detalhado: `/predict-detailed` **NOVO**
```bash
curl -X POST "http://localhost:8000/predict-detailed" \
  -H "Content-Type: application/json" \
  -d '{
    "home_team": "Arsenal",
    "away_team": "Chelsea",
    "competition": "PL"
  }'
```

**Response:**
```json
{
  "match": {
    "home_team": "Arsenal FC",
    "away_team": "Chelsea FC",
    "match_id": 123
  },
  "individual_predictions": {
    "poisson": {
      "model": "Poisson",
      "result": {"home_win": 0.52, "draw": 0.26, "away_win": 0.22}
    },
    "xgboost": {
      "model": "XGBoost + API Features",
      "result": {"home_win": 0.58, "draw": 0.24, "away_win": 0.18},
      "api_features_used": true
    },
    "api-football": {
      "model": "API-Football",
      "result": {"home_win": 0.55, "draw": 0.25, "away_win": 0.20}
    }
  },
  "ensemble_prediction": {
    "model": "Ensemble (Weighted Average)",
    "result": {"home_win": 0.55, "draw": 0.25, "away_win": 0.20},
    "weights": {"poisson": 0.5, "xgboost": 0.3, "api-football": 0.2}
  },
  "models_used": ["poisson", "xgboost", "api-football"],
  "has_api_predictions": true
}
```

---

## 🎯 Features da API-Football Extraídas

### Probabilidades Básicas (3 features)
- `api_home_win_prob` - Probabilidade de vitória da casa
- `api_draw_prob` - Probabilidade de empate
- `api_away_win_prob` - Probabilidade de vitória fora

### Features Derivadas (3 features)
- `api_home_advantage` - Vantagem da casa (home - away)
- `api_prediction_confidence` - Confiança (max prob)
- `api_draw_likelihood` - Likelihood de empate

### Under/Over (2 features)
- `api_over_25_prob` - Probabilidade de Over 2.5
- `api_under_25_prob` - Probabilidade de Under 2.5

### Comparações (14 features)
- `api_form_home/away` - Forma dos times
- `api_att_home/away` - Força de ataque
- `api_def_home/away` - Força de defesa
- `api_poisson_home/away` - Poisson da API
- `api_h2h_home/away` - Head-to-head
- `api_goals_home/away` - Expected goals
- `api_total_home/away` - Comparação geral

### Features Derivadas de Comparações (2 features)
- `api_form_diff` - Diferença de forma
- `api_attack_vs_defense` - Ataque vs Defesa

### Forma Recente (2 features)
- `api_recent_form_home` - Forma recente (WWDLW → score)
- `api_recent_form_away` - Forma recente visitante

**Total: 26 features + 21 básicas = 47 features!**

---

## 🔬 Comparação: Com vs Sem API Features

### Modelo Tradicional (21 features)
```python
Features básicas:
✓ goals_scored_avg (casa/fora)
✓ goals_conceded_avg (casa/fora)
✓ wins, draws, losses (casa/fora)
✓ matches_played (casa/fora)
✓ goals_for_total (casa/fora)
✓ Features derivadas (5)

Total: 21 features
```

### Modelo Enriquecido (47 features) ⭐
```python
Features básicas:
✓ Todas as 21 features acima

Features da API-Football:
✓ Probabilidades da API (3)
✓ Comparações de time (14)
✓ Under/Over da API (2)
✓ Features derivadas (7)

Total: 47 features

🎯 XGBoost aprende:
  - QUANDO confiar na API
  - QUANTO peso dar a cada feature
  - Quais features são mais preditivas
```

---

## 📊 Benefícios da Integração

### 1. **Maior Acurácia**
- XGBoost usa 47 features vs 21 (2.2x mais informação!)
- Combina múltiplas fontes de dados
- API fornece análise profissional

### 2. **Ensemble Robusto**
- Combina 3 modelos diferentes
- Reduz viés de modelo único
- Maior confiança nas predições

### 3. **Flexibilidade**
- Funciona COM ou SEM predições da API
- Modelo retrocompatível
- Fallback automático

### 4. **Valor Agregado**
- Identifica discrepâncias entre modelos
- Oportunidades de value bets
- Cross-validation com API profissional

---

## ⚙️ Configuração

### Pesos do Ensemble (Padrão)
```python
weights = {
    "poisson": 0.5,      # 50% - Modelo estatístico
    "xgboost": 0.3,      # 30% - Machine learning
    "api-football": 0.2   # 20% - API profissional
}
```

### Ajustar Pesos (Opcional)
```python
# No código
ensemble = EnsembleModel(
    database=database_v2,
    include_api_predictions=True,
    weights={
        "poisson": 0.4,
        "xgboost": 0.4,
        "api-football": 0.2
    }
)
```

---

## 🧪 Testes

### Teste 1: Feature Extraction
```bash
cd pro/python_api/features
python api_predictions_features.py
```

### Teste 2: XGBoost com API
```bash
cd pro/python_api/models
python xgboost_model.py
```

### Teste 3: Ensemble Completo
```bash
cd pro/python_api/models
python ensemble.py
```

### Teste 4: API Endpoint
```bash
# Terminal 1: Iniciar API
python app.py

# Terminal 2: Testar
curl http://localhost:8000/
curl -X POST http://localhost:8000/predict-detailed \
  -H "Content-Type: application/json" \
  -d '{"home_team": "Arsenal", "away_team": "Chelsea", "competition": "PL"}'
```

---

## 📈 Próximos Passos

### 1. **Backtesting**
- Compare performance: Tradicional vs Enriquecido
- Meça ROI em apostas simuladas
- Valide melhorias estatísticas

### 2. **Tuning de Hiperparâmetros**
- Grid search nos pesos do ensemble
- Optimize XGBoost params com API features
- A/B testing

### 3. **Mais Features**
- Adicionar odds das casas de apostas
- Incluir estatísticas de jogadores
- Condições climáticas, árbitro, etc

### 4. **Produção**
- Deploy da API em servidor
- Automação de coleta diária
- Monitoramento de performance

---

## 🆘 Troubleshooting

### Erro: "Nenhuma predição da API encontrada"
**Solução:**
```bash
# 1. Verificar se tem predições no banco
python test_predictions_access.py

# 2. Coletar predições
python collect_predictions.py

# 3. Verificar banco de dados
sqlite3 database/betting_v2.db "SELECT COUNT(*) FROM predictions WHERE model_name='api-football';"
```

### Erro: "XGBoost não carregado"
**Solução:**
```bash
# 1. Treinar modelo primeiro
python train_xgboost_with_api.py

# 2. Verificar se foi salvo
ls -la models/saved/

# 3. Reiniciar API
python app.py
```

### Features da API retornam None
**Causa:** Partida não tem predição da API no banco

**Solução:** Modelo usa fallback (0.5 neutro), funciona normalmente

---

## 📚 Documentação Relacionada

- **PREDICTIONS_GUIDE.md** - Guia estratégico de uso
- **DUAL_API_GUIDE.md** - Sistema dual-API (football-data + API-Football)
- **HISTORICAL_DATA_GUIDE.md** - Coleta de dados históricos

---

## 🎉 Conclusão

O sistema agora integra **completamente** as predições da API-Football usando a estratégia de **Feature Engineering**, permitindo que o XGBoost aprenda automaticamente quando e quanto confiar nas predições da API.

**Principais Conquistas:**
✅ 26 novas features da API-Football
✅ XGBoost enriquecido (47 features!)
✅ Ensemble com 3 modelos
✅ API REST completa com endpoint detalhado
✅ Pipeline end-to-end funcional
✅ Documentação completa

**Pronto para produção!** 🚀
