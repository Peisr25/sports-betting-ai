# 📊 Estrutura de Dados das Partidas - API-Football

## 🎯 Dados Salvos no JSON (live_and_upcoming_fixtures.json)

### Estrutura do Arquivo Completo da API

Quando você chama `/fixtures?live=all`, a API retorna:

```json
{
  "fixture": {
    "id": 1342401,                    // ✅ ID único da partida
    "date": "2025-11-01T15:00:00+00:00",
    "timestamp": 1762009200,
    "status": {
      "long": "First Half",           // Status detalhado
      "short": "1H",                   // ✅ Status curto (NS, 1H, 2H, FT, etc)
      "elapsed": 5                     // Minuto do jogo
    },
    "venue": {
      "name": "Intility Arena",
      "city": "Oslo"
    }
  },
  "league": {
    "id": 103,                         // ✅ ID da liga
    "name": "Eliteserien",            // ✅ Nome da liga
    "country": "Norway",              // ✅ País
    "season": 2025,
    "round": "Regular Season - 27"
  },
  "teams": {
    "home": {
      "id": 326,                       // ✅ ID do time da casa
      "name": "Valerenga",            // ✅ Nome do time da casa
      "logo": "https://..."
    },
    "away": {
      "id": 327,                       // ✅ ID do time visitante
      "name": "Bodo/Glimt",           // ✅ Nome do time visitante
      "logo": "https://..."
    }
  },
  "goals": {
    "home": 0,                         // ✅ Gols da casa
    "away": 0                          // ✅ Gols visitante
  },
  "score": {
    "halftime": { "home": 0, "away": 0 },
    "fulltime": { "home": null, "away": null }
  },
  "events": []                         // Eventos do jogo (gols, cartões, etc)
}
```

---

## 📁 Estrutura do Seu Arquivo (find_live_and_upcoming.py)

O script `find_live_and_upcoming.py` salva assim:

```json
{
  "timestamp": "2025-11-01T...",
  "live_fixtures": 14,
  "upcoming_fixtures": 14,
  "total_fixtures": 28,
  "total_leagues": 26,
  "leagues": {
    "Eliteserien": {
      "league_id": 103,
      "country": "Norway",
      "count": 2,
      "fixtures": [...]
    }
  },
  "all_fixtures": [                    // ✅ ARRAY PRINCIPAL COM TODAS AS PARTIDAS
    {
      "fixture_id": 1342401,           // ✅ ID da partida
      "date": "01/11/2025 15:00",      // Data formatada
      "timestamp": 1762009200,
      "league_name": "Eliteserien",    // ✅ Nome da liga
      "league_id": 103,                // ✅ ID da liga
      "country": "Norway",             // ✅ País
      "home_team": "Valerenga",        // ✅ Time da casa
      "home_team_id": 326,             // ✅ ID do time da casa
      "away_team": "Bodo/Glimt",       // ✅ Time visitante
      "away_team_id": 327,             // ✅ ID do time visitante
      "status": "First Half (5')",     // Status formatado
      "status_short": "1H",            // ✅ Status curto
      "score": "0 x 0",                // ✅ Placar
      "venue": "Intility Arena",
      "raw_data": {...}                // ✅ DADOS COMPLETOS DA API
    }
  ]
}
```

---

## 🔍 Dados Importantes para o Fluxo

### Para Coletar Histórico (collect_team_history.py):

```python
# Ler do all_fixtures
for fixture in data["all_fixtures"]:
    home_team_id = fixture["home_team_id"]      # ✅
    away_team_id = fixture["away_team_id"]      # ✅
    home_team_name = fixture["home_team"]       # ✅
    away_team_name = fixture["away_team"]       # ✅
    league_id = fixture["league_id"]            # ✅
```

### Para Calcular Previsões (calculate_predictions.py):

```python
for fixture in data["all_fixtures"]:
    fixture_id = fixture["fixture_id"]          # ✅ ID único
    home_team = fixture["home_team"]            # ✅ Nome
    away_team = fixture["away_team"]            # ✅ Nome
    status = fixture["status_short"]            # ✅ NS, 1H, 2H, FT
    current_score = fixture["score"]            # ✅ "0 x 0"
    
    # Acessar dados completos da API se necessário
    raw_data = fixture["raw_data"]              # ✅ Objeto completo
```

### Para Análise de Apostas (generate_betting_recommendations.py):

```python
for fixture in data["all_fixtures"]:
    fixture_info = {
        "fixture_id": fixture["fixture_id"],
        "date": fixture["date"],
        "league": fixture["league_name"],
        "status": fixture["status"],
        "current_score": fixture["score"]
    }
    
    # Status para filtros
    is_live = fixture["status_short"] in ["1H", "2H", "HT"]
    is_upcoming = fixture["status_short"] in ["NS", "TBD"]
    is_finished = fixture["status_short"] == "FT"
```

---

## 🎯 Adaptação do Fluxo Atual

### OPÇÃO 1: Usar API-Football para Histórico (Recomendado)

```python
# collect_team_history.py - NOVA VERSÃO

def collect_from_api_football(fixture):
    """Coleta histórico direto do API-Football"""
    
    # Buscar últimas partidas do time da casa
    home_history = api.get_team_fixtures(
        team_id=fixture["home_team_id"],
        last=20  # Últimas 20 partidas
    )
    
    # Buscar últimas partidas do time visitante
    away_history = api.get_team_fixtures(
        team_id=fixture["away_team_id"],
        last=20
    )
    
    return home_history, away_history
```

**Endpoint:** `/fixtures?team={team_id}&last=20`

**Custo:** 2 requisições por partida (1 casa + 1 fora)
- 28 partidas × 2 = **56 requisições**
- Plano free: 100/dia ✅ **POSSÍVEL!**

---

### OPÇÃO 2: Usar Dados Existentes no Banco

```python
# calculate_predictions.py - USAR BANCO

def predict_with_existing_data(fixture):
    """Usa dados já coletados do Brasileirão"""
    
    # Busca no banco local (571 partidas)
    home_stats = db.get_team_stats(fixture["home_team"])
    away_stats = db.get_team_stats(fixture["away_team"])
    
    if not home_stats or not away_stats:
        return "INSUFFICIENT_DATA"
    
    # Calcular previsão
    prediction = calculate_prediction(home_stats, away_stats)
    return prediction
```

**Vantagem:** Sem custo de API  
**Limitação:** Só funciona para times do Brasileirão

---

### OPÇÃO 3: Híbrido (Melhor Estratégia!)

```python
def collect_team_history_hybrid(fixture):
    """Tenta banco primeiro, depois API-Football"""
    
    # 1. Tentar buscar no banco local
    home_data = db.get_team_history(fixture["home_team"])
    away_data = db.get_team_history(fixture["away_team"])
    
    # 2. Se não tem no banco, buscar na API-Football
    if not home_data:
        home_data = api_football.get_team_fixtures(
            team_id=fixture["home_team_id"],
            last=20
        )
        # Salvar no banco para próxima vez
        db.save_team_history(home_data)
    
    if not away_data:
        away_data = api_football.get_team_fixtures(
            team_id=fixture["away_team_id"],
            last=20
        )
        db.save_team_history(away_data)
    
    return home_data, away_data
```

---

## 🚀 Próxima Ação Recomendada

### 1. Criar `collect_team_history_v2.py`

Com suporte para API-Football usando os IDs dos times:

```python
# Endpoint para buscar histórico do time
GET /fixtures?team={team_id}&last=20

# Exemplo:
GET /fixtures?team=326&last=20  # Últimas 20 partidas do Valerenga
```

### 2. Modificar `calculate_predictions.py`

Para ler os dados no formato correto do `all_fixtures`:

```python
with open("live_and_upcoming_fixtures.json") as f:
    data = json.load(f)

for fixture in data["all_fixtures"]:
    home_team = fixture["home_team"]
    away_team = fixture["away_team"]
    # ... resto do código
```

### 3. Testar o Fluxo Completo

```bash
# 1. Encontrar partidas
python find_live_and_upcoming.py

# 2. Coletar histórico (versão 2 com API-Football)
python collect_team_history_v2.py --from-live-fixtures

# 3. Calcular previsões
python calculate_predictions.py --from-live-fixtures

# 4. Gerar recomendações
python generate_betting_recommendations.py
```

---

## ❓ Qual Opção Você Prefere?

1. **OPÇÃO 1:** Criar `collect_team_history_v2.py` com API-Football
   - ✅ Funciona com qualquer liga
   - ✅ Dados completos
   - ⚠️ Usa quota da API (56 req para 28 partidas)

2. **OPÇÃO 2:** Filtrar apenas times do Brasileirão
   - ✅ Usa dados existentes (571 partidas)
   - ✅ Sem custo de API
   - ❌ Limitado ao Brasileirão

3. **OPÇÃO 3:** Sistema híbrido (Recomendado!)
   - ✅ Usa banco quando possível
   - ✅ API-Football quando necessário
   - ✅ Melhor dos dois mundos

**Qual você quer que eu implemente?** 🎯
