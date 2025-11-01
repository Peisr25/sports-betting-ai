# ⚡ Guia: Sistema de Apostas em Tempo Real

## 🎯 Visão Geral

Dois scripts poderosos para análise de apostas em **tempo real**:

1. **`live_betting_analyzer.py`** ⭐ - Analisa partidas AO VIVO e gera recomendações
2. **`find_available_fixtures_fd.py`** - Busca fixtures na football-data.org (plano free)

---

## 🔥 Script Principal: Live Betting Analyzer

### O que faz?

1. **Busca partidas AO VIVO** usando `/fixtures?live=all` da API-Football
2. **Coleta dados** de cada partida (times, liga, status, placar)
3. **Calcula probabilidades** usando Poisson + XGBoost + Ensemble
4. **Gera recomendações** de apostas com níveis de confiança
5. **Salva relatório** JSON com todas as análises

### Como usar?

```bash
cd pro/python_api
python live_betting_analyzer.py
```

### Saída Esperada:

```
=======================================================================
  ANALISADOR DE APOSTAS AO VIVO
=======================================================================

✓ API Key encontrada: b7f3a8d2e1...

📦 Inicializando modelos...
   ✓ Poisson
   ✓ XGBoost (com API features)
   ✓ Ensemble

=======================================================================
  BUSCANDO PARTIDAS AO VIVO E PRÓXIMAS
=======================================================================

✅ 12 partidas encontradas!

📊 Por status:
   1º Tempo (1H): 5
   2º Tempo (2H): 3
   Intervalo (HT): 2
   Não Iniciadas (NS): 2

📋 Partidas para análise: 12
   (Filtrado: não iniciadas + ao vivo)

######################################################################
# PARTIDA 1/12
######################################################################
=======================================================================
🏆 Liga Profesional Argentina (Argentina)
=======================================================================
⚽ San Lorenzo vs Deportivo Riestra
📅 31/10/2024 22:00
📊 Status: Second Half (2H)
🎯 Placar: San Lorenzo 0 x 0 Deportivo Riestra
⏱️  Tempo: 47'

📊 Calculando estatísticas dos times...

🔮 Gerando predições...
   ✓ Poisson calculado
   ✓ XGBoost calculado
   ✓ Ensemble calculado

🎯 PROBABILIDADES:
   Casa (San Lorenzo): 45.2%
   Empate: 28.5%
   Fora (Deportivo Riestra): 26.3%

⚽ GOLS:
   Over 2.5: 42.8%
   Under 2.5: 57.2%

🎲 AMBOS MARCAM:
   Sim: 48.5%
   Não: 51.5%

💡 RECOMENDAÇÃO:
   📌 Vitória San Lorenzo
   📊 Confiança: Baixa (45.2%)

⚠️  ATENÇÃO: Partida já iniciada!
   Status: Second Half
   Considere apostas ao vivo (odds dinâmicas)

######################################################################
# PARTIDA 2/12
######################################################################
=======================================================================
🏆 Serie B (Brazil)
=======================================================================
⚽ Coritiba vs CRB
📅 31/10/2024 22:00
📊 Status: Halftime (HT)
🎯 Placar: Coritiba 0 x 0 CRB
⏱️  Tempo: 45'

[... análise ...]

=======================================================================
  RESUMO FINAL
=======================================================================

📊 Partidas analisadas: 12

🎯 TOP RECOMENDAÇÕES:
=======================================================================

1. Coritiba vs CRB
   Liga: Serie B
   Status: HT
   Recomendação: Vitória Coritiba (58.7%)

2. Atletico Goianiense vs Paysandu
   Liga: Serie B
   Status: HT
   Recomendação: Vitória Paysandu (52.3%)

3. San Lorenzo vs Deportivo Riestra
   Liga: Liga Profesional Argentina
   Status: 2H
   Recomendação: Vitória San Lorenzo (45.2%)

4. Wanderers vs Boston River
   Liga: Primera División - Clausura
   Status: 1H
   Recomendação: Empate (48.1%)

5. Bolívar vs San Antonio Bulo Bulo
   Liga: Copa de la División Profesional
   Status: 1H
   Recomendação: Vitória Bolívar (67.8%)


💾 Relatório salvo: live_betting_report.json

=======================================================================
                     ✅ ANÁLISE CONCLUÍDA!
=======================================================================
```

---

## 📊 Entendendo os Resultados

### Status das Partidas

| Status | Significado | Apostas? |
|--------|------------|----------|
| **NS** | Não Iniciada | ✅ Odds normais |
| **1H** | 1º Tempo | ⚡ Apostas ao vivo |
| **HT** | Intervalo | ⚡ Apostas ao vivo |
| **2H** | 2º Tempo | ⚡ Apostas ao vivo |
| **ET** | Prorrogação | ⚡ Apostas ao vivo |
| **FT** | Finalizada | ❌ Não aceita apostas |

### Níveis de Confiança

- **Alta** (> 55%): Recomendação forte
- **Média** (45-55%): Recomendação moderada
- **Baixa** (< 45%): Considere apenas como informação

### Tipos de Apostas Analisadas

1. **Resultado Final** (1X2)
   - Vitória Casa
   - Empate
   - Vitória Fora

2. **Total de Gols**
   - Over 2.5
   - Under 2.5

3. **Ambos Marcam** (BTTS)
   - Sim
   - Não

---

## 🔍 Script Alternativo: Football-Data.org

### Quando usar?

Use `find_available_fixtures_fd.py` quando:
- API-Football bloquear ligas atuais (ex: Brasileirão)
- Quiser acesso a ligas europeias top
- Plano free da API-Football estourou quota

### Como usar?

```bash
cd pro/python_api
python find_available_fixtures_fd.py
```

### Competições Disponíveis (Free):

- ✅ Premier League (Inglaterra)
- ✅ La Liga (Espanha)
- ✅ Bundesliga (Alemanha)
- ✅ Serie A (Itália)
- ✅ Ligue 1 (França)
- ✅ Eredivisie (Holanda)
- ✅ Primeira Liga (Portugal)
- ✅ UEFA Champions League
- ✅ Championship (Inglaterra)
- ✅ European Championship (quando disponível)
- ✅ World Cup (quando disponível)

### Saída Esperada:

```
=======================================================================
  BUSCANDO PARTIDAS NA FOOTBALL-DATA.ORG
=======================================================================

📅 Período de busca:
   De: 2024-10-31
   Até: 2024-11-14
   Dias: 14

🔍 Testando 11 competições...

[1/11] 🏆 Premier League (England) - Code: PL
   ✅ 18 jogos agendados encontrados!
      1. Arsenal vs Liverpool - 03/11 17:30
      2. Man City vs Brighton - 03/11 15:00
      3. Chelsea vs Man Utd - 03/11 14:00
      ... e mais 15 jogos

[2/11] 🏆 La Liga (Spain) - Code: PD
   ✅ 15 jogos agendados encontrados!
      ...

=======================================================================
  RESUMO
=======================================================================

📊 Estatísticas:
   Competições testadas: 11
   ✅ Com jogos disponíveis: 7
   ❌ Com restrições: 0
   ℹ️  Sem jogos agendados: 4
   📅 Total de fixtures encontrados: 89

✅ COMPETIÇÕES COM JOGOS DISPONÍVEIS (7):

1. 🏆 Premier League (England)
   Código: PL
   Jogos agendados: 18
   Comando para coletar dados:
   python collect_historical_data.py PL --season 2024

2. 🏆 La Liga (Spain)
   Código: PD
   Jogos agendados: 15
   ...
```

---

## 💡 Estratégias de Uso

### 1. Apostas Pré-Jogo (NS)

```bash
# 1. Buscar partidas não iniciadas
python live_betting_analyzer.py

# 2. Focar em partidas com status NS
# 3. Verificar confiança Alta (> 55%)
# 4. Apostar antes do jogo começar
```

**Vantagens:**
- Odds mais estáveis
- Mais tempo para análise
- Menos risco

### 2. Apostas Ao Vivo (1H, 2H, HT)

```bash
# 1. Executar durante jogos
python live_betting_analyzer.py

# 2. Ver status da partida (placar, tempo)
# 3. Comparar predição vs realidade
# 4. Aproveitar odds dinâmicas
```

**Vantagens:**
- Odds podem estar desbalanceadas
- Informação do jogo em andamento
- Oportunidades de value bets

**Riscos:**
- Odds mudam rapidamente
- Menos tempo para decidir
- Maior volatilidade

### 3. Modo Contínuo (Monitoramento)

```bash
# Criar loop para atualização
while true; do
    python live_betting_analyzer.py
    sleep 300  # 5 minutos
done
```

**Uso:**
- Monitora partidas continuamente
- Detecta mudanças de odds
- Identifica oportunidades ao vivo

---

## 📈 Exemplos Práticos

### Exemplo 1: Jogo no Intervalo

```
🏆 Serie B (Brazil)
⚽ Coritiba vs CRB
📊 Status: Halftime (HT)
🎯 Placar: Coritiba 0 x 0 CRB

🎯 PROBABILIDADES:
   Casa (Coritiba): 58.7%
   Empate: 25.3%
   Fora (CRB): 16.0%

💡 RECOMENDAÇÃO:
   📌 Vitória Coritiba
   📊 Confiança: Média (58.7%)
```

**Análise:**
- Jogo empatado no intervalo
- Modelo favorece Coritiba em casa (58.7%)
- Se odds do Coritiba estiverem > 1.70 → Value bet!

### Exemplo 2: Jogo em Andamento

```
🏆 Liga Profesional Argentina
⚽ San Lorenzo vs Deportivo Riestra
📊 Status: Second Half (2H)
🎯 Placar: San Lorenzo 0 x 0 Deportivo Riestra
⏱️  Tempo: 47'

🎯 PROBABILIDADES:
   Empate: 48.1%
   Casa: 30.2%
   Fora: 21.7%

💡 RECOMENDAÇÃO:
   📌 Empate
   📊 Confiança: Baixa (48.1%)
```

**Análise:**
- 2º tempo recém começou
- Ainda 0x0 aos 47'
- Alta probabilidade de empate (48.1%)
- Considere aposta no empate se odds > 2.10

### Exemplo 3: Jogo Não Iniciado

```
🏆 Primera División - Clausura (Uruguay)
⚽ Wanderers vs Boston River
📊 Status: Not Started (NS)
📅 01/11/2024 20:00

🎯 PROBABILIDADES:
   Casa (Wanderers): 67.8%
   Empate: 21.5%
   Fora (Boston River): 10.7%

💡 RECOMENDAÇÃO:
   📌 Vitória Wanderers
   📊 Confiança: Alta (67.8%)
```

**Análise:**
- Jogo não começou
- Forte favorito: Wanderers (67.8%)
- Confiança ALTA
- **Recomendação**: Apostar em Wanderers se odds > 1.50

---

## 🔄 Workflow Completo

### Passo 1: Executar Análise

```bash
cd pro/python_api
python live_betting_analyzer.py
```

### Passo 2: Revisar Relatório

```bash
cat live_betting_report.json | jq '.analyses[] | {home: .home_team, away: .away_team, status: .status}'
```

### Passo 3: Filtrar Oportunidades

```python
# Script Python para filtrar
import json

with open("live_betting_report.json") as f:
    data = json.load(f)

# Filtrar alta confiança
for analysis in data["analyses"]:
    predictions = analysis.get("predictions", {})
    ensemble = predictions.get("ensemble", {})
    result = ensemble.get("result", {})

    max_prob = max(result.values()) if result else 0

    if max_prob > 0.55:  # Alta confiança
        print(f"{analysis['home_team']} vs {analysis['away_team']}")
        print(f"Confiança: {max_prob:.1%}")
        print()
```

### Passo 4: Fazer Apostas

- Verificar odds nas casas de apostas
- Comparar com probabilidades do modelo
- Calcular value bets (EV > 0)
- Aplicar gestão de banca (Kelly Criterion)

---

## ⚠️ Avisos Importantes

### 1. Apostas Responsáveis

- ❌ Nunca aposte mais do que pode perder
- ❌ Não persiga perdas
- ✅ Use gestão de banca
- ✅ Defina limites diários/mensais

### 2. Limitações do Sistema

- Modelo usa estatísticas históricas
- Não considera lesões, suspensões
- Não considera motivação/contexto
- Odds mudam em tempo real

### 3. Validação

- Sempre compare com múltiplas fontes
- Verifique histórico do modelo
- Faça backtesting antes de apostar real
- Use stake pequeno inicialmente

---

## 📚 Recursos Adicionais

### Relatórios JSON

```bash
# Visualizar top recomendações
cat live_betting_report.json | jq '.analyses[] |
    select(.predictions.ensemble.result.home_win > 0.55) |
    {match: (.home_team + " vs " + .away_team), prob: .predictions.ensemble.result.home_win}'
```

### Logs Históricos

Salve relatórios com timestamp:

```bash
python live_betting_analyzer.py
mv live_betting_report.json "reports/live_$(date +%Y%m%d_%H%M%S).json"
```

### Integração com Value Analyzer

```python
from analysis.value_analysis import ValueAnalyzer

analyzer = ValueAnalyzer()

# Odds da casa de apostas
odds = {"result": {"home_win": 2.10, "draw": 3.20, "away_win": 3.50}}

# Nossas probabilidades
predictions = {...}  # Do relatório

# Análise de valor
analyses = analyzer.analyze_match(predictions, odds, stake=100)
best_bets = analyzer.get_best_bets(analyses)
```

---

## 🎉 Conclusão

Com esses dois scripts, você tem:

✅ **Análise em tempo real** de partidas ao vivo
✅ **Recomendações automáticas** de apostas
✅ **Alternativa** quando API-Football bloqueia (football-data.org)
✅ **Relatórios JSON** para análise posterior
✅ **Integração** com todos os modelos do sistema

**Execute agora:**

```bash
python live_betting_analyzer.py
```

**Boas apostas!** 🍀
