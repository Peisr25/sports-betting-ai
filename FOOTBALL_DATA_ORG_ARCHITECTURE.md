# 🏗️ Nova Arquitetura: football-data.org (API v4)

## 📋 Contexto da Mudança

### ❌ Problema com API-Football (free tier)
- Bloqueia temporadas atuais (2024/2025)
- Parâmetro `last` não funciona
- Partidas ao vivo limitadas
- Dados históricos apenas de temporadas antigas

### ✅ Solução: football-data.org
- **Temporadas ATUAIS disponíveis**
- Partidas SCHEDULED acessíveis
- Histórico completo
- 10 req/min (free tier)
- Dados suficientes para treinar modelos

---

## 📊 Dados Disponíveis (football-data.org)

### 1. Match Resource (Partida)

**Endpoint:** `GET /matches/{id}`

**Dados básicos:**
```json
{
  "id": 330299,
  "utcDate": "2022-02-27T16:05:00Z",
  "status": "FINISHED",  // SCHEDULED, TIMED, IN_PLAY, FINISHED
  "matchday": 26,
  "venue": "Stade de l'Aube",
  "attendance": 16871
}
```

**Score:**
```json
{
  "score": {
    "winner": "DRAW",  // HOME_TEAM, AWAY_TEAM, DRAW
    "fullTime": {"home": 1, "away": 1},
    "halfTime": {"home": 0, "away": 1}
  }
}
```

**Goals (detalhado):**
```json
{
  "goals": [
    {
      "minute": 28,
      "type": "PENALTY",  // REGULAR, PENALTY, OWN_GOAL
      "scorer": {"id": 8360, "name": "Dimitri Payet"},
      "assist": {"id": 123, "name": "Player Name"},
      "score": {"home": 0, "away": 1}
    }
  ]
}
```

**Lineup (Escalação):**
```json
{
  "homeTeam": {
    "formation": "3-4-1-2",
    "lineup": [
      {
        "id": 899,
        "name": "Gauthier Gallon",
        "position": "Goalkeeper",
        "shirtNumber": 30
      }
    ],
    "bench": [...]
  }
}
```

**Statistics (⭐ CRUCIAL):**
```json
{
  "homeTeam": {
    "statistics": {
      "corner_kicks": 4,
      "free_kicks": 10,
      "goal_kicks": 5,
      "offsides": 4,
      "fouls": 16,
      "ball_possession": 41,
      "saves": 1,
      "throw_ins": 12,
      "shots": 8,
      "shots_on_goal": 3,
      "shots_off_goal": 5,
      "yellow_cards": 5,
      "yellow_red_cards": 0,
      "red_cards": 0
    }
  }
}
```

**Bookings (Cartões):**
```json
{
  "bookings": [
    {
      "minute": 11,
      "player": {"id": 8695, "name": "Valentin Rongier"},
      "card": "YELLOW"  // YELLOW, YELLOW_RED, RED
    }
  ]
}
```

**Substitutions:**
```json
{
  "substitutions": [
    {
      "minute": 57,
      "playerOut": {"id": 8695, "name": "Valentin Rongier"},
      "playerIn": {"id": 166642, "name": "Pol Lirola"}
    }
  ]
}
```

**Odds (quando disponível):**
```json
{
  "odds": {
    "homeWin": 4.25,
    "draw": 3.72,
    "awayWin": 1.81
  }
}
```

---

### 2. Team Resource (Time)

**Endpoint:** `GET /teams/{id}`

**Dados:**
```json
{
  "id": 90,
  "name": "Real Betis Balompié",
  "founded": 1907,
  "venue": "Estadio Benito Villamarín",
  "squad": [...],  // Lista de jogadores
  "coach": {...},  // Treinador
  "runningCompetitions": [...]  // Competições atuais
}
```

**Matches do time:**
`GET /teams/{id}/matches?status=FINISHED&limit=10`

---

### 3. Competition Resource

**Endpoint:** `GET /competitions/{code}/matches`

**Códigos disponíveis (FREE TIER):**
- `PL` - Premier League
- `PD` - La Liga
- `BL1` - Bundesliga
- `SA` - Serie A
- `FL1` - Ligue 1
- `DED` - Eredivisie
- `PPL` - Primeira Liga
- `CL` - Champions League
- `ELC` - Championship
- `EC` - Euro Championship
- `WC` - World Cup

---

## 🎯 Features Que Podemos Extrair

### Features Básicas (21 features)

#### Por Time (10 features cada = 20 total)

**Ofensivas:**
1. `goals_scored_avg` - Média de gols marcados
2. `shots_avg` - Média de chutes
3. `shots_on_goal_avg` - Média de chutes no gol
4. `corners_avg` - Média de escanteios
5. `possession_avg` - Média de posse de bola

**Defensivas:**
6. `goals_conceded_avg` - Média de gols sofridos
7. `saves_avg` - Média de defesas do goleiro
8. `fouls_avg` - Média de faltas cometidas

**Forma:**
9. `win_rate` - Taxa de vitórias (últimas N partidas)
10. `points_avg` - Média de pontos (3-1-0)

#### Contexto da Partida (1 feature)
21. `home_advantage` - 1 se casa, 0 se fora

---

### Features Avançadas (Opcionais - 15+ features)

**Disciplina:**
- `yellow_cards_avg`
- `red_cards_avg`

**Eficiência:**
- `shot_accuracy` = shots_on_goal / shots
- `conversion_rate` = goals / shots_on_goal
- `clean_sheet_rate` - % de jogos sem sofrer gol

**Forma Recente:**
- `last_5_wins` - Vitórias nas últimas 5
- `last_5_goals_scored` - Gols marcados últimas 5
- `last_5_goals_conceded` - Gols sofridos últimas 5

**Confronto Direto (H2H):**
- `h2h_wins` - Vitórias em confrontos diretos
- `h2h_goals_avg` - Média de gols em H2H
- `h2h_home_advantage` - Vantagem em casa nos H2H

**Escalação:**
- `squad_value` - Valor de mercado da escalação
- `starter_changes` - Mudanças na escalação titular
- `formation_stability` - Consistência de formação

**Competição:**
- `league_position` - Posição na tabela
- `points_difference` - Diferença de pontos entre times

---

## 🏗️ Nova Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                   FOOTBALL-DATA.ORG API                      │
│                    (10 req/min free tier)                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              FootballDataCollector (EXISTENTE)               │
│  - get_matches() - Buscar partidas                           │
│  - get_team_matches_history() - Histórico do time            │
│  - get_head_to_head() - Confrontos diretos                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              FootballDataFeatureExtractor (NOVO)             │
│  - extract_match_features() - Extrai 21+ features            │
│  - calculate_team_stats() - Estatísticas do time             │
│  - calculate_h2h_features() - Features H2H                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Database v2 (SQLite)                        │
│  - Matches (partidas completas com stats)                   │
│  - Teams (times)                                             │
│  - Predictions (predições salvas)                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Modelos Preditivos                        │
│  1. Poisson (goals_scored_avg, goals_conceded_avg)          │
│  2. XGBoost (21+ features)                                   │
│  3. Ensemble (combinação)                                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Betting Analyzer                          │
│  - Busca partidas SCHEDULED                                  │
│  - Extrai features                                           │
│  - Faz predições                                             │
│  - Calcula value bets                                        │
│  - Gera recomendações                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Estrutura de Arquivos

```
pro/python_api/
├── data/
│   ├── collector.py              # ✅ JÁ EXISTE (FootballDataCollector)
│   ├── database_v2.py            # ✅ JÁ EXISTE
│   └── fd_feature_extractor.py  # 🆕 CRIAR
│
├── models/
│   ├── poisson.py                # ✅ JÁ EXISTE (adaptar)
│   ├── xgboost_model.py          # ✅ JÁ EXISTE (adaptar)
│   └── ensemble.py               # ✅ JÁ EXISTE (adaptar)
│
├── collection/
│   ├── collect_historical_fd.py  # 🆕 CRIAR - Coleta histórico
│   └── collect_scheduled_fd.py   # 🆕 CRIAR - Coleta agendadas
│
├── analysis/
│   ├── betting_analyzer_fd.py    # 🆕 CRIAR - Análise completa
│   └── value_analysis.py         # ✅ JÁ EXISTE
│
├── train_model_fd.py             # 🆕 CRIAR - Treina com dados FD
└── app_fd.py                     # 🆕 CRIAR - API REST
```

---

## 🔄 Workflow Completo

### 1. Coleta de Dados Históricos

```python
# collect_historical_fd.py

1. Buscar todas as competições disponíveis (PL, PD, BL1, SA, FL1)
2. Para cada competição:
   - Buscar partidas FINISHED (dateFrom/dateTo)
   - Salvar partida completa (score, stats, lineup, bookings)
3. Salvar no banco de dados
4. Evitar duplicatas
```

**Estimativa:** ~500-1000 partidas por competição/temporada

---

### 2. Feature Engineering

```python
# fd_feature_extractor.py

def extract_team_features(team_id, last_n_matches=10):
    """
    Extrai features de um time baseado em últimas N partidas

    Returns:
        {
            'goals_scored_avg': 1.8,
            'goals_conceded_avg': 0.9,
            'shots_avg': 12.5,
            'shots_on_goal_avg': 5.2,
            'possession_avg': 55.0,
            'corners_avg': 6.3,
            'win_rate': 0.70,
            'clean_sheet_rate': 0.40,
            'yellow_cards_avg': 2.1,
            'shot_accuracy': 0.416
        }
    """

def extract_h2h_features(team1_id, team2_id):
    """
    Extrai features de confronto direto
    """

def extract_match_features(home_team_id, away_team_id):
    """
    Combina features dos 2 times + H2H

    Returns array com 21+ features
    """
```

---

### 3. Treinamento de Modelos

```python
# train_model_fd.py

1. Buscar todas as partidas FINISHED no banco
2. Para cada partida:
   - Extrair 21+ features
   - Label = resultado (home_win, draw, away_win)
3. Treinar XGBoost com 21+ features
4. Validação cruzada
5. Salvar modelo
```

---

### 4. Pipeline de Predição

```python
# betting_analyzer_fd.py

1. Buscar partidas SCHEDULED (próximas 7 dias)
2. Para cada partida:
   - Extrair features dos times
   - Calcular H2H
   - Fazer predição (Poisson + XGBoost + Ensemble)
   - Calcular value bets
3. Gerar relatório JSON com recomendações
```

---

## 📊 Exemplo de Output

```json
{
  "timestamp": "2025-11-01T15:00:00Z",
  "api": "football-data.org",
  "scheduled_matches": [
    {
      "match_id": 444558,
      "competition": "Premier League",
      "home_team": {
        "id": 65,
        "name": "Manchester City",
        "recent_form": "WWDWW",
        "goals_avg": 2.3,
        "win_rate": 0.80
      },
      "away_team": {
        "id": 57,
        "name": "Arsenal",
        "recent_form": "WWWDW",
        "goals_avg": 2.1,
        "win_rate": 0.75
      },
      "kickoff": "2025-11-03T15:00:00Z",
      "predictions": {
        "poisson": {
          "home_win": 0.45,
          "draw": 0.28,
          "away_win": 0.27
        },
        "xgboost": {
          "home_win": 0.48,
          "draw": 0.25,
          "away_win": 0.27
        },
        "ensemble": {
          "home_win": 0.46,
          "draw": 0.27,
          "away_win": 0.27,
          "confidence": "Medium"
        }
      },
      "betting_recommendations": {
        "1x2": {
          "recommendation": "Home Win",
          "probability": 0.46,
          "confidence": "Medium"
        },
        "over_under_2.5": {
          "recommendation": "Over 2.5",
          "probability": 0.62,
          "confidence": "High"
        },
        "btts": {
          "recommendation": "Yes",
          "probability": 0.58,
          "confidence": "Medium"
        }
      },
      "features_used": 21,
      "historical_data": {
        "h2h_matches": 8,
        "home_last_matches": 10,
        "away_last_matches": 10
      }
    }
  ],
  "summary": {
    "total_scheduled": 35,
    "analyzed": 35,
    "high_confidence": 8,
    "medium_confidence": 18,
    "low_confidence": 9
  }
}
```

---

## ⚡ Rate Limiting

**Free tier:** 10 requisições/minuto

**Estratégia:**
```python
import time

class RateLimiter:
    def __init__(self, max_requests=10, time_window=60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []

    def wait_if_needed(self):
        now = time.time()
        # Remove requisições antigas
        self.requests = [r for r in self.requests if now - r < self.time_window]

        if len(self.requests) >= self.max_requests:
            sleep_time = self.time_window - (now - self.requests[0])
            print(f"⏳ Rate limit: aguardando {sleep_time:.1f}s")
            time.sleep(sleep_time)

        self.requests.append(now)
```

---

## 🎯 Vantagens da Nova Arquitetura

### ✅ Dados Atuais
- Temporada 2024/2025 disponível
- Partidas SCHEDULED acessíveis
- Treinamento com dados recentes

### ✅ Features Suficientes
- 21+ features básicas
- Gols, chutes, posse, escanteios
- Escalação disponível
- Cartões disponíveis

### ✅ Simplicidade
- Uma única API
- Sem mixing de APIs
- Código mais limpo
- Manutenção mais fácil

### ✅ Validação
- Testar com free tier
- Se funcionar → assinar API paga
- Se não → mínimo investimento

---

## 📅 Roadmap de Implementação

### Fase 1: Base (1-2 dias)
- [x] FootballDataCollector (já existe)
- [ ] FootballDataFeatureExtractor
- [ ] Adaptar database_v2 para FD data

### Fase 2: Coleta (1 dia)
- [ ] collect_historical_fd.py
- [ ] Coletar ~2000 partidas (4-5 ligas)
- [ ] Popular banco de dados

### Fase 3: Modelos (1 dia)
- [ ] Adaptar Poisson para FD features
- [ ] Adaptar XGBoost para 21 features
- [ ] Treinar e validar

### Fase 4: Predição (1 dia)
- [ ] betting_analyzer_fd.py
- [ ] Buscar SCHEDULED
- [ ] Fazer predições
- [ ] Gerar relatórios

### Fase 5: Validação (ongoing)
- [ ] Comparar predições vs resultados reais
- [ ] Calcular ROI
- [ ] Ajustar modelos

---

## 🎉 Próximos Passos Imediatos

1. **Criar `fd_feature_extractor.py`**
   - Extrair 21+ features de partidas
   - Calcular stats de times
   - Calcular H2H

2. **Criar `collect_historical_fd.py`**
   - Buscar partidas FINISHED
   - Salvar no banco
   - Popular base de treino

3. **Adaptar modelos**
   - Poisson com FD features
   - XGBoost com 21 features
   - Ensemble

4. **Criar `betting_analyzer_fd.py`**
   - Pipeline completo
   - SCHEDULED → Features → Predição → Recomendações

---

**Pronto para começar! 🚀**
