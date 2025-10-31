# Guia de Predições da API-Football 🔮

## 📊 Visão Geral

A API-Football oferece um endpoint `/predictions` que fornece análises e previsões para partidas agendadas. Este guia explica **como testar**, **como usar** e **se vale a pena** para seu sistema de apostas.

---

## 🧪 PASSO 1: Testar Acesso

Primeiro, verifique se seu plano tem acesso ao endpoint `/predictions`:

```bash
cd pro/python_api

# Testar acesso
python test_predictions_access.py --apif-key SUA_KEY

# Ou com .env configurado
python test_predictions_access.py
```

### Resultados Possíveis

#### ✅ Cenário 1: Acesso Confirmado

```
✅ ACESSO ÀS PREDIÇÕES CONFIRMADO!

📈 DADOS DA PREDIÇÃO:
----------------------------------------------------------------------
Vencedor previsto: Flamengo (Win or draw)

Percentuais:
  Casa: 65%
  Empate: 20%
  Fora: 15%

Over/Under: -2.5

Gols previstos:
  Casa: +1.5
  Fora: -1.5

Recomendação: Combo Double chance : Flamengo or draw and -2.5 goals
```

**Você pode usar predições!** 🎉

#### ❌ Cenário 2: Sem Acesso

```
❌ ERRO AO ACESSAR PREDIÇÕES:
   {'subscription': 'Your subscription plan does not allow access to this resource'}

💡 Tipo de erro: Restrição de plano
   Seu plano não tem acesso ao endpoint /predictions

   SOLUÇÕES:
   1. Upgrade para plano pago (a partir de $19/mês)
   2. Usar apenas nossas próprias predições (Poisson + XGBoost)
```

**Seu plano não inclui predições** 😕

---

## 📊 PASSO 2: Entender os Dados

As predições da API-Football incluem:

### Predição Principal

```json
{
  "winner": {
    "id": 123,
    "name": "Flamengo",
    "comment": "Win or draw"
  },
  "win_or_draw": true,
  "under_over": "-2.5",
  "goals": {
    "home": "+1.5",
    "away": "-1.5"
  },
  "advice": "Combo Double chance : Flamengo or draw and -2.5 goals",
  "percent": {
    "home": "65%",
    "draw": "20%",
    "away": "15%"
  }
}
```

### Comparações Estatísticas

```json
{
  "comparison": {
    "form": { "home": "70%", "away": "30%" },
    "att": { "home": "60%", "away": "40%" },
    "def": { "home": "55%", "away": "45%" },
    "poisson_distribution": { "home": "75%", "away": "25%" },
    "h2h": { "home": "40%", "away": "60%" },
    "total": { "home": "58.5%", "away": "41.5%" }
  }
}
```

### Estatísticas dos Times

```json
{
  "teams": {
    "home": {
      "name": "Flamengo",
      "last_5": {
        "form": "80%",  // 4W 1D de 5 jogos = 80%
        "att": "90%",
        "def": "70%"
      },
      "league": {
        "form": "WWDWL",  // Últimos 5: W=Win, D=Draw, L=Loss
        "fixtures": { ... },
        "goals": { ... }
      }
    }
  }
}
```

---

## 🚀 PASSO 3: Coletar Predições

Se você tem acesso, colete predições para partidas agendadas:

```bash
cd pro/python_api

# Coletar predições dos próximos 7 dias do Brasileirão
python collect_predictions.py BSA --season 2024 --days 7

# Coletar predições dos próximos 3 dias da Premier League
python collect_predictions.py PL --season 2024 --days 3

# Com API key manual
python collect_predictions.py BSA --season 2024 --days 7 --apif-key SUA_KEY
```

### Output Esperado

```
======================================================================
COLETA DE PREDIÇÕES - BSA
======================================================================
Liga: BSA
Temporada: 2024
Período: Próximos 7 dias
======================================================================

📋 Buscando fixtures agendados...
✓ Encontrados 10 fixtures nos próximos 7 dias

[1/10] Flamengo vs Palmeiras
  Data: 2024-11-05T20:00:00+00:00
  ✓ Predição salva

[2/10] Corinthians vs São Paulo
  Data: 2024-11-06T18:00:00+00:00
  ✓ Predição salva

...

======================================================================
COLETA FINALIZADA
======================================================================
Fixtures encontrados: 10
Predições salvas: 10
Erros: 0
======================================================================
```

---

## 💡 PASSO 4: Como Usar Estrategicamente

### ❓ As Predições da API São Úteis?

**✅ SIM!** Mas use com inteligência. Aqui estão 5 estratégias:

---

### 1️⃣  ENSEMBLE COM NOSSOS MODELOS

Combine predições da API com as nossas (Poisson + XGBoost):

```python
# Exemplo de ensemble
nossa_pred_home = 0.70  # 70% vitória casa
api_pred_home = 0.65     # 65% vitória casa

# Média ponderada (dar mais peso ao nosso modelo)
ensemble_pred = (0.7 * nossa_pred_home) + (0.3 * api_pred_home)
# Resultado: 0.685 = 68.5%

# OU média simples
ensemble_pred = (nossa_pred_home + api_pred_home) / 2
# Resultado: 0.675 = 67.5%
```

**Quando usar:**
- ✅ Quando ambas concordam (±10%): Alta confiança
- ⚠️ Quando discordam (>20%): Investigar ou passar

---

### 2️⃣  FEATURE ENGINEERING (RECOMENDADO!) ⭐

**Esta é a melhor forma de usar as predições!**

Adicione as predições da API como **features EXTRAS** no seu modelo XGBoost:

```python
# Criar features do XGBoost
features = {
    # Nossas features existentes
    'avg_goals_scored_home': 1.8,
    'avg_goals_conceded_home': 0.9,
    'shots_avg_home': 12.5,
    'corners_avg_home': 6.2,

    # NOVAS FEATURES DA API-FOOTBALL! ⭐
    'api_home_win_prob': 0.65,
    'api_draw_prob': 0.20,
    'api_away_win_prob': 0.15,
    'api_form_comparison_home': 0.70,  # 70% vs 30% away
    'api_att_comparison_home': 0.60,   # 60% vs 40% away
    'api_def_comparison_home': 0.55,   # 55% vs 45% away
    'api_poisson_home': 0.75,
    'api_h2h_home': 0.40,
    'api_total_home': 0.585,
}

# XGBoost irá aprender QUANDO confiar na API
# e QUANTO peso dar a cada feature!
prediction = xgb_model.predict([list(features.values())])
```

**Por que isso é poderoso?**
- ✅ XGBoost aprende automaticamente quando confiar na API
- ✅ Combina TODAS as informações disponíveis
- ✅ Você não precisa decidir manualmente os pesos
- ✅ Modelo fica muito mais rico e preciso

---

### 3️⃣  IDENTIFICAR VALUE BETS

Use divergências entre sua predição e a API para encontrar oportunidades:

```python
# Exemplo 1: Concordância (APOSTA CONFIÁVEL)
nossa_pred = 0.70      # 70% vitória casa
api_pred = 0.65        # 65% vitória casa
diferenca = abs(0.70 - 0.65)  # 5%

if diferenca <= 0.10:
    print("✅ Alta confiança! Ambos modelos concordam")
    print("   Apostar: Vitória Casa")

# Exemplo 2: Divergência (VALUE BET ou PASSAR)
nossa_pred = 0.75      # 75% vitória casa
api_pred = 0.50        # 50% vitória casa (MUITO DIFERENTE!)
diferenca = abs(0.75 - 0.50)  # 25%

if diferenca > 0.20:
    print("⚠️ Grande divergência!")
    print("   Opção 1: VALUE BET - Se confiamos mais no nosso modelo")
    print("   Opção 2: PASSAR - Se há incerteza demais")
```

**Regra de ouro:**
- **Concordância (±10%)**: ✅ Alta confiança → APOSTAR
- **Divergência moderada (10-20%)**: ⚠️ Cuidado → Investigar
- **Divergência grande (>20%)**: ❌ Muito risco → PASSAR (ou value bet se muito confiante)

---

### 4️⃣  VALIDAÇÃO CRUZADA

Compare performance dos modelos:

```python
# Para cada partida no histórico
matches = get_past_matches_with_predictions()

nossa_accuracy = 0
api_accuracy = 0
ensemble_accuracy = 0

for match in matches:
    # Verificar acerto
    if nossa_pred == resultado_real:
        nossa_accuracy += 1

    if api_pred == resultado_real:
        api_accuracy += 1

    if ensemble_pred == resultado_real:
        ensemble_accuracy += 1

# Comparar
print(f"Nosso modelo: {nossa_accuracy / len(matches):.1%}")
print(f"API-Football: {api_accuracy / len(matches):.1%}")
print(f"Ensemble: {ensemble_accuracy / len(matches):.1%}")

# Resultado típico:
# Nosso modelo: 62.5%
# API-Football: 60.0%
# Ensemble: 65.0%  ← MELHOR! ✅
```

---

### 5️⃣  BACKTESTING COMPARATIVO

Teste com dinheiro "virtual":

```python
bankroll_nosso = 1000
bankroll_api = 1000
bankroll_ensemble = 1000

for match in historical_matches:
    # Apostar $10 em cada modelo
    stake = 10

    # Nosso modelo
    if nossa_pred > 0.60:
        if resultado == vitoria_casa:
            bankroll_nosso += stake * odds
        else:
            bankroll_nosso -= stake

    # API model
    if api_pred > 0.60:
        if resultado == vitoria_casa:
            bankroll_api += stake * odds
        else:
            bankroll_api -= stake

    # Ensemble (concordância)
    ensemble = (nossa_pred + api_pred) / 2
    if ensemble > 0.60 and abs(nossa_pred - api_pred) < 0.10:
        if resultado == vitoria_casa:
            bankroll_ensemble += stake * odds
        else:
            bankroll_ensemble -= stake

# Ver ROI
print(f"ROI Nosso: {(bankroll_nosso - 1000) / 1000:.1%}")
print(f"ROI API: {(bankroll_api - 1000) / 1000:.1%}")
print(f"ROI Ensemble: {(bankroll_ensemble - 1000) / 1000:.1%}")
```

---

## ⚠️ O QUE NÃO FAZER

### ❌ 1. Usar APENAS as Predições da API

```python
# ERRADO ❌
if api_pred_home > 0.60:
    apostar_casa()  # Ignorando completamente nossos modelos!
```

**Por quê é ruim?**
- Perde seu **edge competitivo**
- A API usa dados públicos que TODO MUNDO tem acesso
- Você não ganha vantagem sobre outros apostadores

### ❌ 2. Confiar Cegamente

```python
# ERRADO ❌
if api_advice == "Bet on home team":
    apostar_100_reais_casa()  # Sem questionar!
```

**Por quê é ruim?**
- A API não conhece **nuances locais** (ex: técnico novo, jogador suspenso)
- Não tem informações **recentes** (atualiza a cada hora)
- Pode errar como qualquer modelo

### ❌ 3. Dar Peso Igual Sempre

```python
# ERRADO ❌
# Sempre 50/50
ensemble = (nossa_pred + api_pred) / 2
```

**Por quê é ruim?**
- Às vezes nosso modelo é melhor
- Às vezes a API é melhor
- Depende do contexto (liga, times, situação)

**MELHOR:** Deixar XGBoost aprender os pesos automaticamente (estratégia #2)

---

## 💰 ESTRATÉGIA RECOMENDADA FINAL

### Fluxo de Trabalho Completo

1. **Coletar Predições da API** (1x por dia)
   ```bash
   python collect_predictions.py BSA --days 7
   ```

2. **Gerar Nossas Predições** (Poisson + XGBoost)
   - Use features enriquecidas com dados da API

3. **Calcular Ensemble**
   - Média ponderada: 70% nosso, 30% API
   - OU deixar XGBoost decidir pesos

4. **Filtrar por Concordância**
   ```python
   if abs(nossa_pred - api_pred) < 0.10 and ensemble > 0.65:
       # ✅ Alta confiança!
       considerar_aposta()
   ```

5. **Analisar Value**
   ```python
   prob_implicita = 1 / odds
   if ensemble > prob_implicita * 1.10:  # 10% de margem
       # ✅ Value bet!
       apostar()
   ```

---

## 📊 Exemplo Prático Completo

### Cenário: Flamengo vs Palmeiras

```python
# PASSO 1: Coletar dados
flamengo_stats = get_team_stats("Flamengo", last_n=10)
palmeiras_stats = get_team_stats("Palmeiras", last_n=10)

# PASSO 2: Nossa predição
nossa_pred = {
    "home": 0.55,   # 55%
    "draw": 0.25,   # 25%
    "away": 0.20    # 20%
}

# PASSO 3: Predição da API
api_pred = get_api_prediction(fixture_id=12345)
# api_pred = {"home": 0.60, "draw": 0.25, "away": 0.15}

# PASSO 4: Comparar
diff_home = abs(0.55 - 0.60)  # 5% de diferença
print(f"Diferença: {diff_home:.1%}")  # 5.0%

# PASSO 5: Decidir
if diff_home <= 0.10:
    print("✅ Concordância! Alta confiança")

    # Ensemble
    ensemble_home = (0.55 + 0.60) / 2  # 57.5%

    # Verificar value
    odds_casa = 1.75
    prob_implicita = 1 / 1.75  # 57.1%

    if ensemble_home > prob_implicita * 1.05:  # 5% de margem
        print("✅ VALUE BET ENCONTRADO!")
        print(f"Nossa predição: {ensemble_home:.1%}")
        print(f"Odds implícitas: {prob_implicita:.1%}")
        print(f"EV: +{(ensemble_home - prob_implicita):.1%}")
        print("RECOMENDAÇÃO: APOSTAR VITÓRIA FLAMENGO")
    else:
        print("⚠️ Sem value suficiente")
else:
    print("⚠️ Divergência grande! PASSAR")
```

### Output

```
Diferença: 5.0%
✅ Concordância! Alta confiança
✅ VALUE BET ENCONTRADO!
Nossa predição: 57.5%
Odds implícitas: 57.1%
EV: +0.4%
RECOMENDAÇÃO: APOSTAR VITÓRIA FLAMENGO
```

---

## 🎓 Quando Vale a Pena Pagar?

### Plano Free vs Pago

| Aspecto | Free | Pago ($19+/mês) |
|---------|------|-----------------|
| Fixtures | ✅ Sim | ✅ Sim |
| Estatísticas | ✅ Sim | ✅ Sim |
| **Predições** | ❌ Não | ✅ Sim |
| Dados históricos | ⚠️ Limitado | ✅ Completo |
| Rate limit | 100 req/dia | 7,500+ req/dia |

### Vale a Pena Pagar?

**SIM, se:**
- ✅ Você aposta regularmente (>5x por semana)
- ✅ Quer ter **vantagem sobre outros** apostadores
- ✅ Pretende usar **ensemble** ou **feature engineering**
- ✅ Seu ROI pode cobrir os $19/mês

**NÃO, se:**
- ❌ Você aposta esporadicamente
- ❌ Já tem bom ROI com seus modelos atuais
- ❌ Não tem como usar as predições estrategicamente

### Cálculo Simples

```
Custo: $19/mês
Break-even: Precisa ganhar $19 extras por mês

Se você aposta $50 por jogo, 4x por semana:
- Total apostado/mês: $50 × 4 × 4 = $800
- Break-even ROI: $19 / $800 = 2.4%

Se as predições melhorarem seu ROI em >2.4%, VALE A PENA!
```

---

## 📞 Resumo Final

### ✅ Faça

1. Teste se tem acesso: `python test_predictions_access.py`
2. Se tiver acesso: Colete predições para partidas agendadas
3. Use como **features no XGBoost** (melhor estratégia!)
4. OU faça **ensemble** com seus modelos
5. Filtre por **concordância** (±10%)
6. Identifique **value bets** quando houver divergência justificada

### ❌ Não Faça

1. Usar APENAS predições da API (perde seu edge)
2. Confiar cegamente sem validar
3. Ignorar completamente se não tiver acesso (seus modelos são bons!)

### 💡 Insight Final

**As predições da API são um COMPLEMENTO, não um substituto.**

Use-as para **enriquecer** seus modelos, não para **substituí-los**.

**Seus próprios modelos + dados únicos = Seu edge competitivo** 🎯

---

**Boa sorte e boas apostas!** ⚽💰🎲
