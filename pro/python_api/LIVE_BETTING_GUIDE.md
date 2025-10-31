# 🎯 Guia do Sistema de Apostas em Tempo Real

## 📋 Visão Geral

Este sistema identifica oportunidades de apostas usando partidas ao vivo e agendadas como ponto de partida. O fluxo completo é:

1. **Descobrir partidas** ao vivo/agendadas disponíveis no API-Football
2. **Coletar dados históricos** dos times dessas partidas
3. **Calcular previsões** usando estatísticas históricas
4. **Gerar recomendações** com análise de valor esperado (EV)

---

## 🚀 Início Rápido

### 1. Ativar Ambiente Virtual

```bash
cd pro/python_api
.\venv\Scripts\activate
```

### 2. Executar Pipeline Completo

```bash
# Passo 1: Encontrar partidas ao vivo/agendadas
python find_live_and_upcoming.py

# Passo 2: Coletar dados históricos dos times
python collect_team_history.py --from-live-fixtures

# Passo 3: Calcular previsões
python calculate_predictions.py --from-live-fixtures

# Passo 4: Gerar recomendações de apostas
python generate_betting_recommendations.py
```

---

## 📖 Detalhamento dos Scripts

### 1️⃣ find_live_and_upcoming.py

**Objetivo:** Encontra partidas disponíveis para apostas

**Saída:** `live_and_upcoming_fixtures.json`

**O que faz:**
- Busca partidas ao vivo no API-Football (`/fixtures?live=all`)
- Busca próximas partidas agendadas (próximos 7 dias)
- Salva todas as fixtures encontradas

**Exemplo de saída:**
```json
{
  "live_fixtures": [
    {
      "fixture_id": 1234567,
      "date": "2024-01-15T18:30:00+00:00",
      "league_name": "Serie A - Brazil",
      "home_team": "Flamengo",
      "away_team": "Palmeiras",
      "status": "LIVE",
      "score": "1 - 0"
    }
  ],
  "total_found": 12
}
```

**Uso avançado:**
```bash
# Ver apenas resumo
python find_live_and_upcoming.py --summary

# Filtrar por liga específica
python find_live_and_upcoming.py --league "Serie A"
```

---

### 2️⃣ collect_team_history.py

**Objetivo:** Coleta dados históricos dos times nas partidas encontradas

**Entrada:** `live_and_upcoming_fixtures.json`

**O que faz:**
- Lê as fixtures do arquivo JSON
- Para cada time, busca histórico no football-data.org
- Salva dados no banco `betting.db`

**Informações coletadas:**
- Partidas dos últimos 12 meses
- Resultados (vitórias, empates, derrotas)
- Gols marcados e sofridos
- Forma recente

**Exemplo de execução:**
```bash
python collect_team_history.py --from-live-fixtures

# Com limite de requisições (útil para free tier)
python collect_team_history.py --from-live-fixtures --limit 20
```

**Resposta esperada:**
```
🔍 COLETANDO DADOS HISTÓRICOS
======================================
Total de times únicos: 24

[1/24] Buscando: Flamengo
   ✅ Encontrado no football-data.org
   📥 Coletando últimas 20 partidas...
   ✅ 18 partidas salvas no banco

...

✅ Coleta concluída!
   Times processados: 24
   Partidas coletadas: 432
```

---

### 3️⃣ calculate_predictions.py

**Objetivo:** Calcula previsões usando dados históricos

**Entrada:** `live_and_upcoming_fixtures.json` + database

**Saída:** `betting_predictions.json`

**Método de previsão:**

1. **Estatísticas dos times** (últimas 10 partidas):
   - Taxa de vitórias
   - Média de gols marcados/sofridos
   - Diferença de gols

2. **Cálculo de probabilidades:**
   ```
   Score_Casa = (win_rate × 0.4) + (goal_diff × 0.3) + (1 - away_win_rate × 0.3) + vantagem_casa
   Score_Fora = (win_rate × 0.4) + (goal_diff × 0.3) + (1 - home_win_rate × 0.3)
   Score_Empate = (draw_rate_casa × 0.5) + (draw_rate_fora × 0.5)
   ```

3. **Previsão de gols** (Poisson simplificado):
   ```
   Gols_Casa = (média_gols_casa + média_sofridos_fora) / 2
   Gols_Fora = (média_gols_fora + média_sofridos_casa) / 2
   ```

**Exemplo de saída:**
```
🎯 CALCULANDO PREVISÕES
======================================

[1/12] Flamengo vs Palmeiras
   📊 Previsão: HOME (Confiança: 62.3%)
   📈 Probabilidades: Casa 62.3% | Empate 18.5% | Fora 19.2%
   ⚽ Gols esperados: 1.8 x 0.9

📊 RESUMO
======================================
✅ Previsões geradas: 10
⚠️ Sem dados suficientes: 2

🎯 TOP 5 APOSTAS (Maior Confiança):
1. Flamengo vs Palmeiras
   Previsão: HOME (Confiança: 62.3%)
   Gols: 1.8 x 0.9
```

---

### 4️⃣ generate_betting_recommendations.py

**Objetivo:** Gera recomendações com análise de valor esperado

**Entrada:** `betting_predictions.json`

**Saída:** `betting_recommendations.json`

**Análise realizada:**

1. **Valor Esperado (EV):**
   ```
   EV = (probabilidade × odd) - 1
   
   EV > 0: Aposta tem valor (RECOMENDADO)
   EV < 0: Aposta sem valor (REJEITAR)
   ```

2. **Critério de Kelly (stake ótimo):**
   ```
   Kelly = (prob × odd - 1) / (odd - 1)
   
   Kelly Fracionado = Kelly × 0.25  (reduz risco)
   ```

3. **Filtros de qualidade:**
   - Mínimo 5 partidas por time
   - Confiança mínima: 45%
   - EV mínimo: 5%

**Exemplo de saída:**
```
💰 GERANDO RECOMENDAÇÕES DE APOSTAS
======================================

📊 RESUMO DA ANÁLISE
======================================
✅ Partidas analisadas: 10
🎯 Apostas recomendadas: 4
❌ Apostas rejeitadas: 6

💎 MELHORES OPORTUNIDADES
======================================

🎯 APOSTA #1
--------------------------------------
Partida: Flamengo vs Palmeiras
Liga: Serie A - Brazil
Data: 2024-01-15T18:30:00+00:00
Status: LIVE

💰 RECOMENDAÇÃO: HOME
   Probabilidade: 62.3%
   Odd: 2.00
   Valor Esperado: +24.6%
   Kelly Stake: 3.1% do bankroll

📊 Qualidade dos Dados: HIGH
   Casa: 15 partidas
   Fora: 12 partidas

⚽ Gols Esperados: 1.8 x 0.9

📈 Análise de Todos os Mercados:
   ✅ HOME: EV=+24.6% | Prob=62.3% | Odd=2.00
   ❌ DRAW: EV=-47.1% | Prob=18.5% | Odd=3.50
   ❌ AWAY: EV=-27.0% | Prob=19.2% | Odd=3.80

🧮 CALCULADORA DE APOSTAS
======================================
Bankroll (R$): 1000

💵 Bankroll: R$ 1000.00

📋 Stakes Recomendadas (Kelly 25%):

1. Flamengo vs Palmeiras
   Mercado: HOME @ 2.00
   Stake: R$ 31.00 (3.1% do bankroll)
   Lucro potencial: R$ 31.00

💰 Total investido: R$ 31.00 (3.1% do bankroll)
💵 Restante: R$ 969.00
```

---

## 📊 Interpretando os Resultados

### Valor Esperado (EV)

- **EV > +10%**: Excelente valor ⭐⭐⭐
- **EV entre +5% e +10%**: Bom valor ⭐⭐
- **EV entre 0% e +5%**: Valor marginal ⭐
- **EV < 0%**: Sem valor ❌

### Confiança da Previsão

- **> 60%**: Alta confiança 🟢
- **50-60%**: Média confiança 🟡
- **< 50%**: Baixa confiança 🔴

### Qualidade dos Dados

- **HIGH**: 10+ partidas por time ✅
- **MEDIUM**: 5-9 partidas por time ⚠️
- **LOW**: < 5 partidas por time ❌

### Kelly Stake

Indica quanto apostar do seu bankroll:

- **> 5%**: Oportunidade forte
- **2-5%**: Oportunidade moderada
- **< 2%**: Oportunidade fraca

**⚠️ IMPORTANTE:** Nunca aposte mais de 10% do bankroll em uma única aposta!

---

## 🔄 Workflow Completo

### Cenário 1: Apostas em Partidas Ao Vivo

```bash
# 1. Descobrir partidas ao vivo
python find_live_and_upcoming.py

# 2. Coletar dados (rápido, só times necessários)
python collect_team_history.py --from-live-fixtures --limit 50

# 3. Calcular previsões
python calculate_predictions.py --from-live-fixtures

# 4. Ver recomendações
python generate_betting_recommendations.py
```

**Tempo estimado:** 5-10 minutos

---

### Cenário 2: Preparação para o Dia

```bash
# Manhã: Coletar fixtures do dia
python find_live_and_upcoming.py

# Coletar dados históricos
python collect_team_history.py --from-live-fixtures

# Gerar previsões
python calculate_predictions.py --from-live-fixtures

# Ver melhores apostas
python generate_betting_recommendations.py
```

**Tempo estimado:** 15-30 minutos

---

### Cenário 3: Monitoramento Contínuo

Crie um script de automação:

```bash
# monitor.bat (Windows)
@echo off
:loop
echo === Atualizacao %date% %time% ===
python find_live_and_upcoming.py
python collect_team_history.py --from-live-fixtures --limit 30
python calculate_predictions.py --from-live-fixtures
python generate_betting_recommendations.py

timeout /t 1800
goto loop
```

Executa a cada 30 minutos.

---

## 📁 Arquivos Gerados

| Arquivo | Descrição | Quando é criado |
|---------|-----------|-----------------|
| `live_and_upcoming_fixtures.json` | Lista de partidas disponíveis | find_live_and_upcoming.py |
| `betting_predictions.json` | Previsões calculadas | calculate_predictions.py |
| `betting_recommendations.json` | Recomendações de apostas | generate_betting_recommendations.py |
| `betting.db` | Banco de dados com histórico | collect_team_history.py |

---

## ⚙️ Configurações

### Limites de API

Edite os scripts conforme sua conta:

```python
# API-Football (find_live_and_upcoming.py)
- Free tier: 100 requisições/dia
- Custo: Cerca de 2 req por execução

# football-data.org (collect_team_history.py)
- Free tier: 10 requisições/minuto
- Custo: 1 req por time
```

### Parâmetros de Recomendação

Edite `generate_betting_recommendations.py`:

```python
class BettingRecommender:
    def __init__(self):
        # Ajuste esses valores
        self.min_confidence = 0.45      # 45% confiança mínima
        self.min_ev = 0.05              # 5% EV mínimo
        self.min_data_quality = 5       # 5 partidas mínimas
```

---

## 🎓 Dicas de Uso

### 1. Gestão de Bankroll

- Use **Kelly fracionado** (25% do Kelly completo)
- Nunca aposte mais de **5% do bankroll** em uma aposta
- Máximo de **20% do bankroll** investido simultaneamente

### 2. Seleção de Apostas

- Priorize apostas com **EV > +10%**
- Prefira **alta qualidade de dados** (10+ partidas)
- Evite apostas em times sem histórico recente

### 3. Timing

- **Partidas ao vivo:** Aproveite mudanças de odds
- **Pré-jogo:** Analise com antecedência para melhores odds
- **Evite:** Final de campeonatos (motivação irregular)

### 4. Diversificação

- Não aposte tudo em uma liga
- Distribua entre diferentes mercados
- Misture diferentes níveis de confiança

---

## 🐛 Solução de Problemas

### Erro: API key inválida

```bash
# Verifique .env
API_FOOTBALL_KEY=sua_chave_aqui
FOOTBALL_DATA_API_KEY=b00e83b0962741e4a703a7dbe7b2f17f
```

### Erro: Sem dados suficientes

- Execute `collect_team_history.py` primeiro
- Aguarde coletar pelo menos 5 partidas por time

### Erro: Nenhuma aposta recomendada

- Normal se odds não oferecem valor
- Aguarde novas partidas ou melhores odds

### Banco de dados corrompido

```bash
# Backup e reconstrução
copy database\betting.db database\betting_backup.db
del database\betting.db
python collect_historical_data.py
```

---

## 📞 Suporte

- **Documentação API:** Veja `API_DATA_REFERENCE.md`
- **Guia de Treinamento:** Veja `TRAINING_GUIDE.md`
- **Logs:** Verifique saída do console

---

## ⚠️ Aviso Legal

Este sistema é para fins educacionais e de pesquisa. 

- Apostas envolvem risco financeiro
- Nenhuma previsão é 100% garantida
- Aposte apenas o que pode perder
- Verifique legalidade em sua jurisdição
- Jogo responsável sempre

---

## 🚀 Próximos Passos

1. Execute o pipeline completo uma vez
2. Analise os resultados
3. Ajuste parâmetros conforme necessário
4. Monitore performance ao longo do tempo
5. Refine o modelo com mais dados

**Boa sorte! 🍀**
