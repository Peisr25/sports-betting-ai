# 🎯 Guia Completo: Pipeline de Análise de Apostas

## 📋 Visão Geral

O **Betting Pipeline** é um sistema completo que automatiza todo o processo de análise de apostas esportivas, desde a descoberta de partidas ao vivo até as recomendações finais de apostas.

### O que faz?

1. ✅ Busca partidas **AO VIVO** e **próximas**
2. ✅ Coleta **predições da API-Football** para cada partida
3. ✅ Busca **confrontos diretos** (H2H - últimos 5 jogos)
4. ✅ Busca **histórico dos times** (últimas 10 partidas de cada)
5. ✅ **Salva tudo no banco de dados** (evitando duplicatas)
6. ✅ **Processa com modelos** (Poisson + XGBoost + Ensemble)
7. ✅ **Gera recomendações** de apostas com análise de confiança

### Arquivo Principal

```
pro/python_api/betting_pipeline.py
```

---

## 🚀 Como Usar

### 1. Execução Básica

```bash
cd pro/python_api
python betting_pipeline.py
```

### 2. Pré-requisitos

- API_FOOTBALL_KEY configurada no `.env`
- Banco de dados inicializado (`database/betting_v2.db`)
- Python 3.8+
- Dependências instaladas

### 3. Primeira Execução

```bash
# 1. Configure a API key
echo "API_FOOTBALL_KEY=sua_key_aqui" >> pro/.env

# 2. Execute o pipeline
cd pro/python_api
python betting_pipeline.py

# 3. Verifique o output
ls -lh betting_analysis_*.json
```

---

## 🔄 Workflow Completo (7 Passos)

### STEP 1: Buscar Partidas ao Vivo

```python
def step1_get_live_fixtures(self) -> List[Dict]:
    """
    Busca partidas AO VIVO e próximas usando /fixtures?live=all

    Status aceitos:
    - NS: Não iniciadas (agendadas)
    - 1H: Primeiro tempo
    - HT: Intervalo
    - 2H: Segundo tempo
    """
```

**Endpoint:** `GET /fixtures?live=all`

**Output:** Lista de fixtures com:
- ID da partida
- Times (home/away)
- Liga
- Status
- Placar (se já iniciada)
- Horário

**Exemplo:**
```json
{
  "fixture": {"id": 12345, "date": "2024-11-01T15:00:00Z"},
  "teams": {
    "home": {"id": 33, "name": "Manchester United"},
    "away": {"id": 34, "name": "Chelsea"}
  },
  "league": {"id": 39, "name": "Premier League"},
  "goals": {"home": 1, "away": 1}
}
```

---

### STEP 2: Buscar Predições da API

```python
def step2_get_api_predictions(self, fixture: Dict) -> Optional[Dict]:
    """
    Busca predições da API-Football para a partida

    Informações coletadas:
    - Probabilidades 1X2
    - Over/Under
    - BTTS
    - Comparação de times (forma, ataque, defesa)
    - Estatísticas detalhadas
    """
```

**Endpoint:** `GET /predictions?fixture={fixture_id}`

**Output:**
```json
{
  "predictions": {
    "winner": {"id": 33, "name": "Manchester United"},
    "win_or_draw": true,
    "percent": {
      "home": "45%",
      "draw": "30%",
      "away": "25%"
    },
    "goals": {"home": "1.5", "away": "1.2"}
  },
  "comparison": {
    "form": {"home": "85%", "away": "70%"},
    "att": {"home": "78%", "away": "72%"},
    "def": {"home": "65%", "away": "75%"}
  }
}
```

---

### STEP 3: Buscar Confrontos Diretos (H2H)

```python
def step3_get_h2h(self, home_team_id: int, away_team_id: int, limit: int = 5) -> List[Dict]:
    """
    Busca últimos 5 confrontos diretos entre os times

    Importante para:
    - Histórico de confrontos
    - Padrões de resultados
    - Tendências específicas do confronto
    """
```

**Endpoint:** `GET /fixtures/headtohead?h2h={team1}-{team2}&last=5`

**Output:** Lista de 5 últimas partidas entre os times

**Exemplo:**
```json
[
  {
    "fixture": {"date": "2024-03-15"},
    "teams": {
      "home": {"name": "Man Utd"},
      "away": {"name": "Chelsea"}
    },
    "goals": {"home": 2, "away": 1}
  }
]
```

**Análise extraída:**
- Vitórias home/away/empates
- Média de gols
- BTTS %
- Tendências

---

### STEP 4: Buscar Histórico dos Times

```python
def step4_get_team_last_matches(self, team_id: int, limit: int = 10) -> List[Dict]:
    """
    Busca últimas 10 partidas de cada time

    Importante para:
    - Forma recente
    - Média de gols
    - Defesa
    - Consistência
    """
```

**Endpoint:** `GET /fixtures?team={team_id}&last=10&status=FT`

**Output:** Lista de 10 últimas partidas finalizadas

**Estatísticas calculadas:**
```python
{
  "goals_scored_avg": 1.8,
  "goals_conceded_avg": 0.9,
  "wins": 7,
  "draws": 2,
  "losses": 1,
  "win_rate": 0.70,
  "clean_sheets": 5,
  "btts_rate": 0.40
}
```

---

### STEP 5: Salvar no Banco de Dados

```python
def step5_save_to_database(self, fixture: Dict, api_prediction: Optional[Dict] = None) -> Optional[int]:
    """
    Salva dados no banco com CHECAGEM DE DUPLICATAS

    Evita:
    - Desperdício de quota da API
    - Dados redundantes
    - Inconsistências

    Verifica:
    - Match já existe? (por match_id_apif)
    - Prediction já existe? (por match_id + model_name)
    """
```

**Tabelas afetadas:**
- `matches` - Dados da partida
- `predictions` - Predição da API-Football
- `teams` - Informações dos times (se novos)

**Verificação de duplicatas:**
```python
# Check match
existing = db.session.query(Match).filter_by(
    match_id_apif=fixture_data["id"]
).first()

if existing:
    print("ℹ️  Partida já existe no banco")
    return existing.id
else:
    # Save new match
    match_obj = db.save_match(match_data)
    stats["matches_saved"] += 1
    return match_obj.id
```

**Histórico salvo:**
```python
def step5_save_historical_matches(self, matches: List[Dict], team_name: str):
    """
    Salva partidas históricas (H2H + últimas partidas)

    Cada partida é verificada individualmente
    """
    for match in matches:
        self.step5_save_to_database(match)
        # ✅ Salva se novo
        # ℹ️  Skip se já existe
```

---

### STEP 6: Processar com Modelos

```python
def step6_process_with_models(self, match_stats: Dict, match_id: Optional[int] = None) -> Dict:
    """
    Processa com TODOS os modelos disponíveis

    Modelos usados:
    1. Poisson (sempre disponível)
    2. XGBoost (se treinado)
    3. Ensemble (combina todos)
    """
```

**Modelos executados:**

#### 1. Modelo Poisson
```python
pred_poisson = self.poisson.predict_match(
    home_attack=home_stats["goals_scored_avg"],
    away_attack=away_stats["goals_scored_avg"],
    home_defense=home_stats["goals_conceded_avg"],
    away_defense=away_stats["goals_conceded_avg"]
)
```

**Output:**
```json
{
  "model": "Poisson",
  "result": {
    "home_win": 0.42,
    "draw": 0.31,
    "away_win": 0.27
  },
  "goals": {
    "over_2.5": 0.48,
    "under_2.5": 0.52
  }
}
```

#### 2. Modelo XGBoost (se disponível)
```python
pred_xgboost = self.xgboost.predict(match_stats, match_id=match_id)
```

**Features usadas:** 47 features (21 básicas + 26 da API)

**Output:**
```json
{
  "model": "XGBoost + API Features",
  "result": {
    "home_win": 0.45,
    "draw": 0.28,
    "away_win": 0.27
  },
  "api_features_used": true
}
```

#### 3. Ensemble (Combina todos)
```python
pred_ensemble = self.ensemble.predict(match_stats, match_id=match_id)
```

**Pesos padrão:**
- Poisson: 50%
- XGBoost: 30%
- API-Football: 20%

**Output:**
```json
{
  "model": "Ensemble",
  "result": {
    "home_win": 0.43,
    "draw": 0.30,
    "away_win": 0.27
  },
  "models_used": ["poisson", "xgboost", "api-football"],
  "weights": {"poisson": 0.5, "xgboost": 0.3, "api-football": 0.2}
}
```

---

### STEP 7: Gerar Recomendações de Apostas

```python
def step7_generate_betting_recommendations(self, predictions: Dict, fixture: Dict) -> Dict:
    """
    Gera recomendações para TODOS os mercados:
    - 1X2 (Vitória Casa/Empate/Vitória Fora)
    - Over/Under 2.5
    - BTTS (Ambos Marcam)

    Com análise de confiança
    """
```

**Mercados de apostas:**

#### 1. Mercado 1X2
```json
{
  "1x2": {
    "recommendation": "home_win",
    "recommendation_name": "Vitória Manchester United",
    "probability": 0.45,
    "confidence": "Média",
    "probabilities": {
      "home_win": 0.45,
      "draw": 0.28,
      "away_win": 0.27
    }
  }
}
```

**Níveis de confiança:**
- **Alta:** Probabilidade > 55%
- **Média:** Probabilidade 45-55%
- **Baixa:** Probabilidade < 45%

#### 2. Over/Under 2.5 Gols
```json
{
  "over_under_2.5": {
    "recommendation": "over_2.5",
    "probability": 0.52,
    "confidence": "Média",
    "probabilities": {
      "over_2.5": 0.52,
      "under_2.5": 0.48
    }
  }
}
```

#### 3. BTTS (Both Teams To Score)
```json
{
  "btts": {
    "recommendation": "yes",
    "probability": 0.58,
    "confidence": "Alta",
    "probabilities": {
      "yes": 0.58,
      "no": 0.42
    }
  }
}
```

---

## 📊 Output JSON Completo

### Estrutura

```json
{
  "timestamp": "2024-11-01T14:30:00",
  "statistics": {
    "fixtures_found": 12,
    "fixtures_processed": 10,
    "predictions_fetched": 10,
    "h2h_fetched": 10,
    "team_history_fetched": 20,
    "matches_saved": 45,
    "predictions_saved": 10,
    "errors": 0
  },
  "fixtures_analyzed": [
    {
      "fixture_id": 12345,
      "home_team": "Manchester United",
      "away_team": "Chelsea",
      "league": "Premier League",
      "status": "NS",
      "kickoff": "2024-11-01T15:00:00Z",

      "api_prediction": {
        "predictions": {...},
        "comparison": {...}
      },

      "h2h": [
        {"fixture": {...}, "goals": {...}},
        ...
      ],

      "home_last_matches": [
        {"fixture": {...}, "goals": {...}},
        ...
      ],

      "away_last_matches": [
        {"fixture": {...}, "goals": {...}},
        ...
      ],

      "statistics": {
        "home": {
          "goals_scored_avg": 1.8,
          "goals_conceded_avg": 0.9,
          "wins": 7,
          "draws": 2,
          "losses": 1,
          "win_rate": 0.70
        },
        "away": {
          "goals_scored_avg": 1.5,
          "goals_conceded_avg": 1.2,
          "wins": 5,
          "draws": 3,
          "losses": 2,
          "win_rate": 0.50
        }
      },

      "model_predictions": {
        "poisson": {...},
        "xgboost": {...},
        "ensemble": {...}
      },

      "betting_recommendations": {
        "1x2": {
          "recommendation": "home_win",
          "recommendation_name": "Vitória Manchester United",
          "probability": 0.45,
          "confidence": "Média"
        },
        "over_under_2.5": {
          "recommendation": "over_2.5",
          "probability": 0.52,
          "confidence": "Média"
        },
        "btts": {
          "recommendation": "yes",
          "probability": 0.58,
          "confidence": "Alta"
        }
      }
    }
  ],

  "top_recommendations": [
    {
      "fixture": "Manchester United vs Chelsea",
      "league": "Premier League",
      "market": "btts",
      "recommendation": "yes",
      "probability": 0.58,
      "confidence": "Alta"
    },
    ...
  ]
}
```

### Arquivo salvo

```
betting_analysis_20241101_143000.json
```

---

## 🎮 Exemplo de Uso Completo

### Código

```python
from betting_pipeline import BettingPipeline
from dotenv import load_dotenv
import os

# Carrega configurações
load_dotenv()
api_key = os.getenv("API_FOOTBALL_KEY")

# Inicializa pipeline
pipeline = BettingPipeline(
    api_key=api_key,
    db_path="database/betting_v2.db"
)

# Executa análise completa
pipeline.run(max_fixtures=10)

# Output:
# ✅ betting_analysis_20241101_143000.json
# ✅ Dados salvos no banco
# ✅ Top 5 recomendações impressas
```

### Saída no Console

```
======================================================================
  BETTING PIPELINE - ANÁLISE COMPLETA DE APOSTAS
======================================================================

======================================================================
  STEP 1: BUSCANDO PARTIDAS AO VIVO
======================================================================

✅ 12 partidas encontradas!

📊 Por status:
   Não Iniciadas (NS): 8
   1º Tempo (1H): 3
   2º Tempo (2H): 1

📋 Partidas para análise: 10 (limitado)

======================================================================
  PROCESSANDO PARTIDAS
======================================================================

######################################################################
# PARTIDA 1/10
######################################################################

🏆 Premier League (England)
⚽ Manchester United vs Chelsea
📅 01/11/2024 15:00
📊 Status: Not Started (NS)

📡 STEP 2: Buscando predições da API-Football...
   ✅ Predições coletadas

💾 STEP 5a: Salvando partida no banco...
   ℹ️  Partida já existe no banco (ID: 123)

🔍 STEP 3: Buscando H2H (últimos 5 confrontos)...
   ✅ 5 confrontos encontrados
   💾 Salvando histórico...
      ✅ 2 novas partidas salvas
      ℹ️  3 já existiam

📊 STEP 4: Buscando últimas 10 partidas de cada time...

   🏠 Manchester United:
      ✅ 10 partidas encontradas
      💾 5 novas partidas salvas

   ✈️  Chelsea:
      ✅ 10 partidas encontradas
      💾 4 novas partidas salvas

📈 Calculando estatísticas...

   Manchester United:
      Média de gols: 1.8
      Média sofridos: 0.9
      Vitórias: 7/10 (70%)

   Chelsea:
      Média de gols: 1.5
      Média sofridos: 1.2
      Vitórias: 5/10 (50%)

🔮 STEP 6: Processando com modelos...
   ✓ Poisson calculado
   ✓ XGBoost calculado (com API features)
   ✓ Ensemble calculado

🎯 PROBABILIDADES (Ensemble):
   Casa (Manchester United): 45.0%
   Empate: 28.0%
   Fora (Chelsea): 27.0%

⚽ GOLS:
   Over 2.5: 52.0%
   Under 2.5: 48.0%

🎲 AMBOS MARCAM:
   Sim: 58.0%
   Não: 42.0%

💡 RECOMENDAÇÕES:

   📌 1X2: Vitória Manchester United
      Confiança: Média (45.0%)

   📌 Over/Under: Over 2.5 gols
      Confiança: Média (52.0%)

   📌 BTTS: Sim (Ambos Marcam)
      Confiança: Alta (58.0%)

...

======================================================================
  ANÁLISE CONCLUÍDA
======================================================================

📊 ESTATÍSTICAS FINAIS:

   Partidas encontradas: 12
   Partidas processadas: 10
   Predições da API coletadas: 10
   H2H coletados: 10
   Histórico de times: 20

   💾 BANCO DE DADOS:
      Novas partidas salvas: 45
      Novas predições salvas: 10
      Duplicatas evitadas: ~80

   ❌ Erros: 0

🎯 TOP 5 RECOMENDAÇÕES:

1. Manchester United vs Chelsea (Premier League)
   BTTS: Sim - 58% (Alta confiança) ⭐

2. Barcelona vs Real Madrid (La Liga)
   1X2: Vitória Casa - 62% (Alta confiança) ⭐

3. Bayern vs Dortmund (Bundesliga)
   Over 2.5: Sim - 67% (Alta confiança) ⭐⭐

...

💾 Relatório completo salvo: betting_analysis_20241101_143000.json

✅ ANÁLISE CONCLUÍDA!
```

---

## ⚙️ Configurações

### Parâmetros do Pipeline

```python
pipeline = BettingPipeline(
    api_key=api_key,              # API key da API-Football
    db_path="database/betting_v2.db"  # Caminho do banco
)

pipeline.run(
    max_fixtures=10  # Limita número de partidas analisadas
)
```

### Rate Limiting

O pipeline inclui rate limiting automático:

```python
# Entre fixtures
time.sleep(2)  # 2 segundos
```

**Estimativa de requisições:**

Para cada partida:
- 1 req: predictions
- 1 req: H2H
- 2 req: team history (1 por time)

**Total por partida:** ~4 requisições

**Para 10 partidas:** ~40 requisições (OK para free plan de 100/dia)

---

## 🔧 Troubleshooting

### Erro: "API quota exceeded"

**Causa:** Excedeu limite de 100 req/dia

**Solução:**
```python
# Reduza o número de fixtures
pipeline.run(max_fixtures=5)  # Ao invés de 10
```

### Erro: "XGBoost model not found"

**Causa:** Modelo XGBoost não foi treinado

**Solução:**
```bash
# Treine o modelo primeiro
python train_xgboost_with_api.py
```

**Resultado:** Pipeline continua com Poisson + Ensemble

### Erro: "Database locked"

**Causa:** Múltiplas instâncias do pipeline rodando

**Solução:**
- Execute apenas uma instância por vez
- Ou use banco de dados separado

### Aviso: "Partida já existe no banco"

**Não é erro!** Sistema está funcionando corretamente:
- ✅ Duplicatas são detectadas
- ✅ Quota da API é economizada
- ✅ Dados consistentes

### Muitos erros de API

**Possíveis causas:**
1. API key inválida
2. Fixture ID inexistente
3. Dados não disponíveis para a partida

**Solução:**
- Verificar API key
- Pipeline continua com próxima partida

---

## 📈 Performance

### Tempo de Execução

**Para 10 partidas:**
- Busca live fixtures: ~1s
- Por partida: ~8s (4 req × 2s)
- **Total:** ~80-90 segundos

### Uso de Memória

- Pipeline: ~50-100 MB
- Banco de dados: Cresce gradualmente
- JSON output: ~500 KB por análise

### Quota da API

**Free plan:** 100 req/dia

**Recomendado:**
- Executar 1-2 vezes por dia
- Limitar a 10-15 partidas por execução
- Monitore `statistics.errors`

---

## 🎯 Melhores Práticas

### 1. Execute em Horários Estratégicos

```bash
# Manhã: Partidas europeias da tarde
10:00 - 12:00

# Tarde: Partidas europeias da noite
14:00 - 16:00

# Noite: Partidas ao vivo
19:00 - 22:00
```

### 2. Monitore Estatísticas

```python
# Sempre verifique o output
print(f"Partidas salvas: {stats['matches_saved']}")
print(f"Duplicatas evitadas: {total - saved}")
```

### 3. Combine com Odds Reais

O pipeline não busca odds automáticamente. Para análise de value:

```python
from analysis.value_analysis import ValueAnalyzer

analyzer = ValueAnalyzer()

# Para cada recomendação
ev = analyzer.calculate_expected_value(
    probability=0.58,
    odds=1.85,
    stake=10
)

if ev > 0:
    print(f"✅ Value bet! EV: €{ev:.2f}")
```

### 4. Treine o Modelo Regularmente

```bash
# A cada 100 novas partidas no banco
python train_xgboost_with_api.py

# Pipeline auto-carrega o modelo mais recente
```

### 5. Backup do Banco

```bash
# Antes de executar
cp database/betting_v2.db database/betting_v2_backup.db

# Ou configure backup automático
```

---

## 🔗 Arquivos Relacionados

### Scripts
- `betting_pipeline.py` - Pipeline principal
- `live_betting_analyzer.py` - Análise simples de partidas ao vivo
- `find_available_fixtures.py` - Descobrir ligas disponíveis
- `train_xgboost_with_api.py` - Treinar modelo com API features

### Documentação
- `LIVE_BETTING_GUIDE.md` - Guia de apostas ao vivo
- `README_API_INTEGRATION.md` - Integração da API-Football
- `PREDICTIONS_GUIDE.md` - Uso estratégico de predições
- `FIND_FIXTURES_GUIDE.md` - Descoberta de fixtures

### Módulos
- `data/api_football_collector.py` - Coleta de dados
- `data/database_v2.py` - Gerenciamento do banco
- `features/api_predictions_features.py` - Feature engineering
- `models/ensemble.py` - Ensemble de modelos
- `analysis/value_analysis.py` - Análise de value bets

---

## 🎉 Resultado Final

Com o **Betting Pipeline** você tem:

✅ **Automação completa** do processo de análise
✅ **Todas as informações** relevantes coletadas
✅ **Múltiplos modelos** trabalhando em conjunto
✅ **Banco de dados** sempre atualizado
✅ **Economia de quota** com duplicate checking
✅ **JSON estruturado** com todas as apostas possíveis
✅ **Top recomendações** com análise de confiança

**Pronto para apostas inteligentes!** 🚀

---

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique os logs do console
2. Revise o JSON de output
3. Consulte os guias relacionados
4. Verifique o banco de dados

**Happy betting!** 🎰
