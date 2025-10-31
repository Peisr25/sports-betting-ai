# Guia do Sistema DUAL-API 🚀

## 📊 Visão Geral

O Sports Betting AI agora suporta **DUAS APIs** trabalhando em conjunto para maximizar a qualidade e quantidade de dados disponíveis:

### API 1: football-data.org (Existente)
- ✅ **Gratuita**: 10 req/min, ~100 req/dia
- ✅ **Boa cobertura**: Ligas europeias principais
- ✅ **Dados básicos**: Fixtures, resultados, classificações
- ⚠️ **Limitações**: Sem estatísticas detalhadas

### API 2: API-Football v3 (NOVA!)
- ✅ **Dados RICOS**: Escanteios, faltas, chutes, posse de bola
- ✅ **Estatísticas detalhadas**: 30+ métricas por partida
- ✅ **Eventos cronológicos**: Gols, cartões, substituições
- ✅ **Odds/Probabilidades**: Dados de casas de apostas
- ✅ **1100+ competições**: Cobertura mundial
- ⚠️ **Plano Free**: 100 requisições/dia

---

## 🎯 Estratégia Híbrida

O sistema combina o melhor de ambas as APIs:

```
┌─────────────────────────────────────────────────────┐
│          COLETA HÍBRIDA - FLUXO DE DADOS            │
├─────────────────────────────────────────────────────┤
│                                                     │
│  1️⃣ football-data.org                              │
│     └─> Busca fixtures básicos (RÁPIDO, GRÁTIS)   │
│         • Times, data, resultado                    │
│         • Status da partida                         │
│         • Competição                                │
│                                                     │
│  2️⃣ API-Football v3                                │
│     └─> Enriquece com dados detalhados             │
│         • ⚽ Escanteios (corners)                   │
│         • 🟨 Cartões amarelos/vermelhos            │
│         • 🎯 Chutes (total, no gol, fora, bloqueados)│
│         • 📊 Posse de bola (possession)             │
│         • ⚠️ Faltas (fouls)                         │
│         • ⛔ Impedimentos (offsides)                │
│         • 🧤 Defesas do goleiro                     │
│         • 🔄 Passes (total, precisão)               │
│         • 📈 Expected Goals (xG)                    │
│                                                     │
│  3️⃣ Database Expandido (SQLite)                    │
│     └─> Armazena TUDO em tabelas relacionadas      │
│         • matches (dados básicos + IDs de ambas APIs)│
│         • match_statistics (30+ métricas)           │
│         • match_events (eventos cronológicos)       │
│         • match_odds (probabilidades)               │
│         • teams (times consolidados)                │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Por Que Usar Ambas?

| Aspecto | football-data.org | API-Football v3 |
|---------|-------------------|-----------------|
| **Requisições grátis/dia** | ~100 | 100 |
| **Taxa de req/min** | 10 | 10 (Free) |
| **Fixtures básicos** | ✅ Excelente | ✅ Excelente |
| **Estatísticas detalhadas** | ❌ Não tem | ✅ Completo |
| **Escanteios/Faltas** | ❌ Não tem | ✅ Tem |
| **Eventos de jogo** | ❌ Não tem | ✅ Tem |
| **Expected Goals (xG)** | ❌ Não tem | ✅ Tem |
| **Odds/Probabilidades** | ❌ Não tem | ✅ Tem |

**Solução**: Usar football-data.org para fixtures (economiza quota) e API-Football v3 apenas para estatísticas detalhadas (maximiza dados)!

---

## 🔧 Configuração

### 1. Obter API Keys

#### API-Football v3

1. Acesse: https://www.api-football.com/
2. Clique em "Register" (ou use RapidAPI)
3. Confirme seu email
4. Copie sua API key do dashboard

**Planos disponíveis:**

| Plano | Preço | Req/Dia | Req/Min |
|-------|-------|---------|---------|
| Free | $0 | 100 | 10 |
| Pro | $19/mês | 7,500 | 300 |
| Ultra | $29/mês | 75,000 | 450 |
| Mega | $39/mês | 150,000 | 900 |

#### football-data.org (já configurada)

Veja `TROUBLESHOOTING.md` para instruções.

### 2. Configurar Variáveis de Ambiente

Edite `pro/.env`:

```bash
# API football-data.org (existente)
FOOTBALL_DATA_API_KEY=sua_key_football_data

# API-Football v3 (NOVA)
API_FOOTBALL_KEY=sua_key_api_football

# Configurações
HISTORY_MATCHES=15
```

**Ou crie arquivo separado** `pro/.env.apifootball`:

```bash
API_FOOTBALL_KEY=sua_key_aqui
```

### 3. Testar Conexões

```bash
cd pro/python_api

# Testar API-Football v3
python -c "from data.api_football_collector import APIFootballCollector; \
           import os; \
           collector = APIFootballCollector(os.getenv('API_FOOTBALL_KEY')); \
           print('✅ API-Football conectada!' if collector.api_key != 'YOUR_API_KEY_HERE' else '❌ Configure API_FOOTBALL_KEY')"
```

---

## 🚀 Uso do Sistema Dual-API

### Coleta Básica (Apenas Fixtures)

```bash
cd pro/python_api

# Coletar fixtures do Brasileirão 2024 (usa apenas football-data.org)
python collect_dual_api.py BSA --season 2024
```

**Resultado**: Partidas com dados básicos (times, placar, data)

### Coleta COMPLETA (Fixtures + Estatísticas)

```bash
# Coletar fixtures + estatísticas detalhadas
python collect_dual_api.py BSA --season 2024 --with-stats

# Coletar fixtures + estatísticas + eventos
python collect_dual_api.py BSA --season 2024 --with-stats --with-events
```

**Resultado**: Partidas com:
- ✅ Dados básicos
- ✅ Escanteios, faltas, chutes
- ✅ Posse de bola, passes
- ✅ Eventos (gols, cartões, substituições)

### Opções Avançadas

```bash
# Especificar API keys manualmente
python collect_dual_api.py PL --season 2024 \
    --fd-key SUA_KEY_FOOTBALL_DATA \
    --apif-key SUA_KEY_API_FOOTBALL \
    --with-stats \
    --with-events

# Limitar número de partidas (para testar)
python collect_dual_api.py BSA --season 2024 --with-stats --limit 5

# Modo dry-run (simulação sem salvar)
python collect_dual_api.py BSA --season 2024 --with-stats --dry-run
```

---

## 📊 Dados Disponíveis

### Tabela: `matches`

Dados básicos da partida (de ambas APIs):

```python
match.match_id_fd        # ID da football-data.org
match.match_id_apif      # ID da API-Football v3
match.competition        # Código (BSA, PL, etc)
match.season            # Temporada
match.home_team         # Time da casa
match.away_team         # Time visitante
match.home_score        # Placar casa
match.away_score        # Placar visitante
match.match_date        # Data/hora
match.status            # FINISHED, SCHEDULED, etc
match.data_source       # 'football-data', 'api-football', 'both'
```

### Tabela: `match_statistics`

Estatísticas DETALHADAS (apenas de API-Football v3):

```python
stats.home_possession          # Posse de bola (%)
stats.away_possession

stats.home_shots_total         # Chutes totais
stats.away_shots_total
stats.home_shots_on_goal       # Chutes no gol
stats.away_shots_on_goal
stats.home_shots_off_goal      # Chutes fora
stats.away_shots_off_goal
stats.home_shots_blocked       # Chutes bloqueados
stats.away_shots_blocked

stats.home_corners             # Escanteios 🎯
stats.away_corners

stats.home_fouls               # Faltas ⚠️
stats.away_fouls

stats.home_yellow_cards        # Cartões amarelos 🟨
stats.away_yellow_cards
stats.home_red_cards           # Cartões vermelhos 🟥
stats.away_red_cards

stats.home_offsides            # Impedimentos
stats.away_offsides

stats.home_goalkeeper_saves    # Defesas do goleiro 🧤
stats.away_goalkeeper_saves

stats.home_passes_total        # Passes totais
stats.away_passes_total
stats.home_passes_accurate     # Passes certos
stats.away_passes_accurate
stats.home_passes_percentage   # Precisão de passe (%)
stats.away_passes_percentage

stats.home_expected_goals      # Expected Goals (xG) 📈
stats.away_expected_goals
```

### Tabela: `match_events`

Eventos cronológicos da partida:

```python
event.time_elapsed        # Minuto do evento
event.event_type          # 'Goal', 'Card', 'subst', 'Var'
event.event_detail        # 'Normal Goal', 'Yellow Card', etc
event.team               # 'home' ou 'away'
event.player_name        # Nome do jogador
event.assist_player_name # Nome do assistente (em gols)
```

---

## 💡 Exemplos de Consultas

### Python: Buscar Partida com Estatísticas

```python
from data.database_v2 import Database

db = Database("database/betting_v2.db")

# Buscar partidas do Brasileirão 2024
matches = db.get_matches(competition="BSA", season=2024, limit=10)

for match in matches:
    print(f"\n{match.home_team} {match.home_score} x {match.away_score} {match.away_team}")

    # Se tem estatísticas detalhadas
    if match.statistics:
        stats = match.statistics
        print(f"  Escanteios: {stats.home_corners} x {stats.away_corners}")
        print(f"  Chutes: {stats.home_shots_total} x {stats.away_shots_total}")
        print(f"  Chutes no gol: {stats.home_shots_on_goal} x {stats.away_shots_on_goal}")
        print(f"  Posse: {stats.home_possession}% x {stats.away_possession}%")
        print(f"  Faltas: {stats.home_fouls} x {stats.away_fouls}")
        print(f"  Cartões: 🟨 {stats.home_yellow_cards} + 🟥 {stats.home_red_cards} x 🟨 {stats.away_yellow_cards} + 🟥 {stats.away_red_cards}")

    # Se tem eventos
    if match.events:
        print(f"  Eventos: {len(match.events)}")
        for event in match.events[:5]:  # Primeiros 5
            print(f"    {event.time_elapsed}' - {event.event_type}: {event.player_name}")
```

### SQL: Análise de Escanteios

```sql
-- Média de escanteios por partida
SELECT
    AVG(home_corners + away_corners) as avg_corners,
    AVG(home_corners) as avg_home_corners,
    AVG(away_corners) as avg_away_corners
FROM match_statistics
JOIN matches ON match_statistics.match_id = matches.id
WHERE matches.competition = 'BSA' AND matches.season = 2024;

-- Times com mais escanteios a favor (casa)
SELECT
    matches.home_team,
    AVG(match_statistics.home_corners) as avg_corners,
    COUNT(*) as games
FROM matches
JOIN match_statistics ON matches.id = match_statistics.match_id
WHERE matches.competition = 'BSA' AND matches.season = 2024
GROUP BY matches.home_team
ORDER BY avg_corners DESC
LIMIT 10;
```

---

## 📈 Melhorando Predições com Dados Extras

### Antes (Apenas football-data.org)

```python
# Modelo baseado apenas em gols
home_goals = [2, 1, 0, 3, 1]  # Últimas 5 partidas
away_goals = [1, 1, 2, 0, 2]

avg_home = sum(home_goals) / len(home_goals)  # 1.4
```

### Agora (Com API-Football v3)

```python
# Modelo baseado em MÚLTIPLAS métricas
features = {
    'avg_goals': 1.4,
    'avg_shots': 12.5,           # NOVO
    'avg_shots_on_target': 4.2,  # NOVO
    'avg_corners': 6.1,           # NOVO
    'avg_possession': 52.3,       # NOVO
    'avg_fouls': 11.2,            # NOVO
    'avg_yellow_cards': 2.1,      # NOVO
    'avg_xG': 1.6                 # NOVO (Expected Goals)
}

# XGBoost pode usar TODAS essas features!
prediction = model.predict([list(features.values())])
```

**Resultado**: Predições muito mais precisas! 🎯

---

## ⚠️ Gestão de Quotas

### Plano Free: Estratégia Recomendada

**Quotas diárias**:
- football-data.org: ~100 req/dia
- API-Football v3: 100 req/dia

**Estratégia de economia**:

1. **Use football-data.org para fixtures** (não gasta quota da API-Football)
2. **Use API-Football apenas para estatísticas** (vale a pena!)
3. **Priorize partidas importantes** (use `--limit` para testes)

**Exemplo de uso eficiente:**

```bash
# DIA 1: Coletar fixtures básicos (usa apenas football-data.org)
python collect_dual_api.py BSA --season 2024
# Gasto: ~20 req football-data, 0 req API-Football

# DIA 2: Enriquecer com estatísticas (usa ambas APIs)
python collect_dual_api.py BSA --season 2024 --with-stats --limit 50
# Gasto: ~20 req football-data, ~50 req API-Football
```

### Monitoramento de Uso

O script mostra uso após cada execução:

```
📈 Uso das APIs:
  football-data.org: 23 requisições
  API-Football v3: 47 requisições

⚠️  ATENÇÃO: 47 requisições usadas da API-Football
   Você tem 53 requisições restantes hoje!
```

---

## 🆕 Novos Mercados de Apostas

Com os dados extras, você pode prever:

### 1. Escanteios (Corners)

```python
# Total de escanteios Over/Under 9.5
avg_corners_home = 6.2
avg_corners_away = 5.8
total_expected = avg_corners_home + avg_corners_away  # 12.0

if total_expected > 9.5:
    print("✅ Apostar em OVER 9.5 escanteios")
```

### 2. Cartões (Cards)

```python
# Total de cartões Over/Under 3.5
avg_yellows_home = 2.1
avg_yellows_away = 1.9
avg_reds_home = 0.1
avg_reds_away = 0.1

total_cards = avg_yellows_home + avg_yellows_away + avg_reds_home + avg_reds_away
# 4.2 cartões esperados

if total_cards > 3.5:
    print("✅ Apostar em OVER 3.5 cartões")
```

### 3. Chutes no Gol (Shots on Target)

```python
# Total de chutes no gol Over/Under 8.5
avg_shots_on_target = (home_shots_on_goal + away_shots_on_goal)

if avg_shots_on_target > 8.5:
    print("✅ Apostar em OVER 8.5 chutes no gol")
```

---

## 🔄 Migração do Sistema Antigo

Se você já tem dados coletados com o sistema antigo:

### Opção 1: Database Separado (Recomendado)

Mantenha ambos os databases:

```
database/
├── betting.db       # Sistema antigo (football-data.org apenas)
└── betting_v2.db    # Sistema novo (dual-API)
```

### Opção 2: Migração Completa

```python
# Script de migração (exemplo)
from data.database import Database as OldDB
from data.database_v2 import Database as NewDB

old_db = OldDB("database/betting.db")
new_db = NewDB("database/betting_v2.db")

# Migrar partidas
old_matches = old_db.get_matches(limit=1000)

for old_match in old_matches:
    new_match_data = {
        "match_id_fd": old_match.match_id,
        "competition": old_match.competition,
        "home_team": old_match.home_team,
        "away_team": old_match.away_team,
        "home_score": old_match.home_score,
        "away_score": old_match.away_score,
        "match_date": old_match.match_date,
        "status": old_match.status,
        "data_source": "football-data"
    }
    new_db.save_match(new_match_data)

print("✅ Migração concluída!")
```

---

## 🎯 Próximos Passos

1. **Configure ambas as API keys** no `.env`
2. **Colete dados históricos** com `--with-stats`
3. **Explore os novos dados** (escanteios, faltas, xG)
4. **Atualize seus modelos** para usar as novas features
5. **Teste novos mercados** (corners, cards)

---

## 📞 Suporte

- **Documentação API-Football v3**: https://www.api-football.com/documentation-v3
- **Dashboard API-Football**: https://dashboard.api-football.com/
- **Planos e Preços**: https://www.api-football.com/pricing

---

## ✅ Checklist de Configuração

- [ ] Criar conta na API-Football v3
- [ ] Obter API key
- [ ] Adicionar `API_FOOTBALL_KEY` no `.env`
- [ ] Testar conexão
- [ ] Executar coleta de teste (`--limit 5`)
- [ ] Executar coleta completa com `--with-stats`
- [ ] Verificar dados no database (`betting_v2.db`)
- [ ] Atualizar modelos de predição

**Boas predições com dados COMPLETOS!** ⚽📊🎯
