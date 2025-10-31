# 📋 Sistema de Apostas - Índice de Arquivos

## 🎯 Visão Geral

Sistema completo para identificar oportunidades de apostas esportivas em tempo real, usando partidas ao vivo e agendadas como ponto de partida para análise preditiva.

---

## 📂 Estrutura de Arquivos

### 🔧 Scripts Principais (Pipeline)

#### 1. find_live_and_upcoming.py
**Função:** Descobre partidas disponíveis para apostas  
**API:** API-Football (RapidAPI)  
**Saída:** `live_and_upcoming_fixtures.json`  
**Uso:**
```bash
python find_live_and_upcoming.py
```

#### 2. collect_team_history.py
**Função:** Coleta dados históricos dos times  
**API:** football-data.org  
**Entrada:** `live_and_upcoming_fixtures.json`  
**Saída:** Banco de dados `database/betting.db`  
**Uso:**
```bash
python collect_team_history.py --from-live-fixtures
```

#### 3. calculate_predictions.py
**Função:** Calcula previsões usando estatísticas históricas  
**Método:** Análise estatística + Poisson simplificado  
**Entrada:** `live_and_upcoming_fixtures.json` + database  
**Saída:** `betting_predictions.json`  
**Uso:**
```bash
python calculate_predictions.py --from-live-fixtures
```

#### 4. generate_betting_recommendations.py
**Função:** Gera recomendações com análise de valor esperado (EV)  
**Método:** Cálculo EV + Critério de Kelly  
**Entrada:** `betting_predictions.json`  
**Saída:** `betting_recommendations.json`  
**Uso:**
```bash
python generate_betting_recommendations.py
```

---

### 🤖 Scripts Auxiliares

#### 5. run_betting_pipeline.py
**Função:** Executa todo o pipeline automaticamente  
**Executa:** Scripts 1 → 2 → 3 → 4 em sequência  
**Uso:**
```bash
python run_betting_pipeline.py
```

#### 6. monitor_betting.py
**Função:** Monitor em tempo real com alertas automáticos  
**Features:**
- Execução periódica do pipeline
- Alertas de novas oportunidades
- Estatísticas em tempo real
**Uso:**
```bash
python monitor_betting.py --interval 30  # A cada 30 minutos
```

---

### 📚 Documentação

#### BETTING_QUICKSTART.md
**Conteúdo:** Guia de referência rápida  
- Comandos básicos
- Interpretação de resultados
- Troubleshooting comum

#### LIVE_BETTING_GUIDE.md
**Conteúdo:** Guia completo do sistema  
- Visão geral detalhada
- Explicação de cada script
- Workflow completo
- Dicas de gestão de bankroll
- Exemplos práticos

#### API_DATA_REFERENCE.md
**Conteúdo:** Referência das APIs usadas  
- Endpoints disponíveis
- Estrutura de dados
- Limitações do free tier

#### TRAINING_GUIDE.md
**Conteúdo:** Guia de treinamento de modelos ML  
- Como treinar modelos personalizados
- Preparação de dados
- Avaliação de performance

---

### 📊 Arquivos de Dados (Gerados)

#### live_and_upcoming_fixtures.json
**Criado por:** find_live_and_upcoming.py  
**Conteúdo:** Lista de partidas ao vivo e agendadas  
**Estrutura:**
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "live_fixtures": [...],
  "upcoming_fixtures": [...],
  "all_fixtures": [...],
  "total_found": 12
}
```

#### betting_predictions.json
**Criado por:** calculate_predictions.py  
**Conteúdo:** Previsões calculadas para cada partida  
**Estrutura:**
```json
{
  "timestamp": "2024-01-15T10:35:00",
  "total_fixtures": 12,
  "predictions": [
    {
      "home_team": "Flamengo",
      "away_team": "Palmeiras",
      "prediction": "HOME",
      "confidence": 0.623,
      "probabilities": {...},
      "expected_goals": {...}
    }
  ]
}
```

#### betting_recommendations.json ⭐
**Criado por:** generate_betting_recommendations.py  
**Conteúdo:** Recomendações finais de apostas  
**⚠️ ARQUIVO MAIS IMPORTANTE - Use este para tomar decisões**  
**Estrutura:**
```json
{
  "timestamp": "2024-01-15T10:40:00",
  "total_analyzed": 12,
  "recommended_bets": 4,
  "recommendations": [
    {
      "match": "Flamengo vs Palmeiras",
      "analysis": {
        "best_bet": {
          "market": "HOME",
          "odds": 2.00,
          "expected_value": 0.246,
          "kelly_stake": 0.031
        }
      }
    }
  ]
}
```

#### database/betting.db
**Criado por:** collect_team_history.py  
**Conteúdo:** Banco SQLite com histórico de partidas  
**Tabelas:**
- matches: Dados completos de partidas
- teams: Informações dos times

---

## 🔄 Fluxos de Trabalho

### Fluxo 1: Pipeline Completo Automatizado
```
run_betting_pipeline.py
    ↓
[1] find_live_and_upcoming.py → live_and_upcoming_fixtures.json
    ↓
[2] collect_team_history.py → database/betting.db
    ↓
[3] calculate_predictions.py → betting_predictions.json
    ↓
[4] generate_betting_recommendations.py → betting_recommendations.json
```

### Fluxo 2: Monitor Contínuo
```
monitor_betting.py
    ↓
[Loop a cada X minutos]
    ↓
Executa run_betting_pipeline.py
    ↓
Detecta novas fixtures
    ↓
Detecta novas recomendações
    ↓
🚨 ALERTA de oportunidades
    ↓
Aguarda próximo ciclo
```

### Fluxo 3: Manual (Passo a Passo)
```
Usuário → find_live_and_upcoming.py
    ↓
Usuário → collect_team_history.py --from-live-fixtures
    ↓
Usuário → calculate_predictions.py --from-live-fixtures
    ↓
Usuário → generate_betting_recommendations.py
    ↓
Usuário analisa betting_recommendations.json
```

---

## 📖 Como Usar (Por Situação)

### Situação 1: Primeira Vez
```bash
# 1. Ler documentação
notepad BETTING_QUICKSTART.md

# 2. Executar pipeline
python run_betting_pipeline.py

# 3. Analisar resultados
notepad betting_recommendations.json
```

### Situação 2: Uso Diário
```bash
# Monitor contínuo (deixar rodando)
python monitor_betting.py --interval 30
```

### Situação 3: Análise Pontual
```bash
# Execução única
python run_betting_pipeline.py

# Ver recomendações
notepad betting_recommendations.json
```

### Situação 4: Debugging/Customização
```bash
# Passo a passo manual
python find_live_and_upcoming.py
python collect_team_history.py --from-live-fixtures
python calculate_predictions.py --from-live-fixtures
python generate_betting_recommendations.py
```

---

## 🎯 Arquivos Por Prioridade

### Prioridade 1: Essenciais para Operar
1. ⭐ **BETTING_QUICKSTART.md** - Leia primeiro!
2. ⭐ **run_betting_pipeline.py** - Use para começar
3. ⭐ **betting_recommendations.json** - Resultados finais

### Prioridade 2: Para Entender o Sistema
4. **LIVE_BETTING_GUIDE.md** - Documentação completa
5. **find_live_and_upcoming.py** - Primeiro passo do pipeline
6. **calculate_predictions.py** - Lógica de previsão

### Prioridade 3: Uso Avançado
7. **monitor_betting.py** - Automação contínua
8. **collect_team_history.py** - Coleta de dados
9. **generate_betting_recommendations.py** - Análise EV

### Prioridade 4: Referência
10. **API_DATA_REFERENCE.md** - Detalhes das APIs
11. **TRAINING_GUIDE.md** - Para treinar modelos próprios

---

## 🔑 Pontos-Chave

### Inputs Necessários
- ✅ API-Football key (RapidAPI) - partidas ao vivo
- ✅ football-data.org key - dados históricos
- ✅ Arquivo `.env` configurado

### Outputs Gerados
- 📄 `live_and_upcoming_fixtures.json` - Partidas disponíveis
- 📄 `betting_predictions.json` - Previsões
- 📄 `betting_recommendations.json` - **RECOMENDAÇÕES FINAIS** ⭐
- 💾 `database/betting.db` - Histórico

### Limites de API (Free Tier)
- API-Football: 100 req/dia (~2 req por execução)
- football-data.org: 10 req/min (1 req por time)

---

## 🎓 Conceitos Importantes

### Valor Esperado (EV)
```
EV = (probabilidade × odd) - 1
```
- EV > 0: Aposta tem valor ✅
- EV < 0: Aposta sem valor ❌

### Critério de Kelly (Stake Ótimo)
```
Kelly = (prob × odd - 1) / (odd - 1)
Kelly Fracionado = Kelly × 0.25
```
Indica % do bankroll para apostar

### Qualidade dos Dados
- HIGH: 10+ partidas/time
- MEDIUM: 5-9 partidas/time  
- LOW: < 5 partidas/time

---

## 📞 Troubleshooting Rápido

| Problema | Solução |
|----------|---------|
| Nenhuma fixture encontrada | API-Football sem partidas no momento |
| Dados insuficientes | Executar `collect_team_history.py` |
| Nenhuma aposta recomendada | Odds não oferecem valor (normal) |
| Erro de API key | Verificar arquivo `.env` |
| Database corrompido | Backup e reconstruir |

---

## ⚠️ Disclaimer

Este sistema é para **fins educacionais e de pesquisa**.

- Apostas envolvem risco financeiro
- Nenhuma previsão é garantida
- Aposte apenas o que pode perder
- Verifique legalidade local
- **Jogo responsável sempre**

---

## 🚀 Próximos Passos

1. ✅ Ler `BETTING_QUICKSTART.md`
2. ✅ Executar `python run_betting_pipeline.py`
3. ✅ Analisar `betting_recommendations.json`
4. ✅ Iniciar `python monitor_betting.py` para uso contínuo

---

**Última atualização:** 2024-01-15  
**Versão do sistema:** 1.0  
**Status:** Pronto para uso ✅
