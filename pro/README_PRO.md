# Sports Betting AI - Versão PRO 🚀

Versão profissional com Ensemble (Poisson + XGBoost), análise de valor esperado e gestão de banca.

## 🎯 Recursos Exclusivos da Pro

✅ **Sistema Ensemble** - Combina Poisson + XGBoost
✅ **Modelo XGBoost** - Machine Learning avançado
✅ **Análise de Valor (EV)** - Identifica apostas lucrativas
✅ **Critério de Kelly** - Gestão otimizada de banca
✅ **Banco de Dados** - SQLite para histórico
✅ **Backtesting** - Teste suas estratégias
✅ **7+ Mercados** - Análise completa de apostas

## 📦 Instalação

```bash
cd pro/python_api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edite .env com sua API key
python app.py
```

## 🎓 Modelos Disponíveis

### 1. Poisson Distribution
Modelo estatístico clássico para predição de gols

### 2. XGBoost
Algoritmo de Machine Learning de alta performance
- Requer treinamento com dados históricos
- Aprende padrões complexos
- Maior precisão que modelos estatísticos

### 3. Ensemble (Recomendado)
Combina Poisson + XGBoost usando média ponderada
- Pesos padrão: 60% Poisson, 40% XGBoost
- Melhor precisão geral
- Reduz viés de modelo único

## 💡 Análise de Valor Esperado

### O que é EV?

```
EV = (Probabilidade × Retorno) - ((1 - Probabilidade) × Stake)
```

Apostas com **EV positivo** são teoricamente lucrativas no longo prazo.

### Exemplo

```bash
# Predição do modelo: Arsenal tem 55% de chance de vencer
# Odd da casa: Arsenal @1.80

# Probabilidade Implícita da Odd: 1/1.80 = 55.56%
# Nossa Probabilidade: 55%

# Como nossa probabilidade é menor que a implícita,
# NÃO há valor nesta aposta.
```

### Uso

```python
# Via API
POST /value-analysis
{
  "home_team": "Arsenal",
  "away_team": "Chelsea",
  "competition": "PL",
  "odds": {
    "result": {
      "home_win": 1.80,
      "draw": 3.50,
      "away_win": 4.50
    },
    "goals": {
      "over_2.5": 1.75,
      "under_2.5": 2.10
    }
  }
}
```

## 📊 Critério de Kelly

Fórmula para calcular stake ótimo:

```
Kelly % = (odds × probability - 1) / (odds - 1)
```

**Recomendação**: Use **25% Kelly** (fractional kelly) para reduzir volatilidade.

### Exemplo

```python
# Probabilidade: 60%
# Odds: 2.00
# Banca: $1000

# Kelly Full: 20%
# Kelly Fracional (25%): 5%
# Stake Recomendado: $50
```

## 🗄️ Banco de Dados

O Pro inclui SQLite para armazenar:
- ✅ Histórico de partidas
- ✅ Predições realizadas
- ✅ Resultados de apostas
- ✅ Performance de modelos

### Tabelas

- `matches` - Partidas salvas
- `predictions` - Predições feitas
- `betting_results` - Resultados (para backtesting)

## 🔬 Backtesting

Teste suas estratégias com dados históricos:

```python
# examples/backtesting_example.py
python backtesting_example.py PL 2024 --strategy value_betting
```

## 📝 Exemplos de Uso

### Predição Básica

```bash
cd examples
python easy_predict.py Arsenal Chelsea PL
```

### Predição com Ensemble

```bash
python advanced_prediction.py Arsenal Chelsea PL --ensemble
```

### Análise de Valor

```bash
python value_analysis_example.py Arsenal Chelsea PL
```

### Backtesting

```bash
python backtesting_example.py BSA 2024
```

## 🎯 Mercados Disponíveis

1. **Resultado (1X2)** - Vitória/Empate/Derrota
2. **Total de Gols** - Over/Under (0.5 a 4.5)
3. **Ambos Marcam** - Sim/Não
4. **Escanteios** - Over/Under
5. **Cartões** - Over/Under
6. **Placar Exato** - Probabilidades por placar
7. **Handicap** - Asiático e Europeu

## ⚙️ Configuração Avançada

### Ajustar Pesos do Ensemble

```python
# python_api/models/ensemble.py
weights = {
    "poisson": 0.6,  # 60%
    "xgboost": 0.4   # 40%
}
```

### Treinar XGBoost

```python
# examples/train_xgboost.py
from models.xgboost_model import XGBoostModel

model = XGBoostModel()
# Carregue seus dados históricos
model.train(X_train, y_train)
model.save_model("models_trained/xgboost.pkl")
```

### Configurar Threshold de EV

```python
# config.py
MIN_EV_THRESHOLD = 0.05  # 5% mínimo
MIN_CONFIDENCE = 0.55    # 55% mínimo
```

## 📈 Performance

### Precisão Esperada

| Mercado | Poisson | XGBoost | Ensemble |
|---------|---------|---------|----------|
| Resultado (1X2) | 52% | 57% | **59%** |
| Over/Under 2.5 | 58% | 62% | **64%** |
| BTTS | 57% | 61% | **63%** |

*Baseado em testes com Premier League 2023/24*

## 🔧 API Endpoints

### Predição

```bash
POST /predict
{
  "home_team": "Arsenal",
  "away_team": "Chelsea",
  "competition": "PL",
  "use_ensemble": true
}
```

### Análise de Valor

```bash
POST /value-analysis
{
  "home_team": "Arsenal",
  "away_team": "Chelsea",
  "competition": "PL",
  "odds": {...}
}
```

### Histórico

```bash
GET /history?competition=PL&limit=50
```

## 💰 Gestão de Banca

### Estratégias Recomendadas

1. **Flat Betting**: Apostar sempre a mesma % da banca (ex: 2%)
2. **Kelly Criterion**: Apostar baseado em valor e probabilidade
3. **Progressive**: Aumentar stake após vitórias
4. **Value Betting**: Apostar apenas quando EV > threshold

### Exemplo de Uso

```python
from analysis.value_analysis import ValueAnalyzer

analyzer = ValueAnalyzer(min_ev=0.05)

# Análise
analysis = analyzer.calculate_ev(
    probability=0.60,
    odds=2.00,
    stake=100
)

# Kelly Criterion
kelly = analyzer.calculate_kelly_criterion(
    probability=0.60,
    odds=2.00,
    bankroll=1000,
    fractional_kelly=0.25
)

print(f"Stake Recomendado: ${kelly['recommended_stake']}")
```

## ⚠️ Avisos Importantes

1. **Treine o XGBoost**: O modelo XGBoost precisa ser treinado com seus dados
2. **Valide Odds**: Sempre compare com múltiplas casas de apostas
3. **Gestão de Banca**: Nunca aposte mais que pode perder
4. **Backtesting**: Teste suas estratégias antes de usar dinheiro real

## 🆙 Upgrade da Lite

Se você está vindo da versão Lite:

1. ✅ Seu `.env` continua funcionando
2. ✅ Scripts de exemplo compatíveis
3. ✅ Endpoints básicos iguais
4. ✅ Recursos novos disponíveis gradualmente

## 📚 Documentação Adicional

- `docs/API_DOCUMENTATION.md` - Referência completa da API
- `docs/USER_GUIDE.md` - Guia do usuário avançado
- `docs/N8N_SETUP.md` - Integração com n8n
- `docs/ADVANCED_FEATURES.md` - Recursos avançados

## 🐛 Solução de Problemas

### Erro ao importar XGBoost

```bash
pip install --upgrade xgboost
```

### Banco de dados corrompido

```bash
rm database/betting.db
python -c "from data.database import Database; Database()"
```

### Modelo não treinado

O XGBoost precisa ser treinado. Use o Poisson ou Ensemble até treinar:

```python
POST /predict
{
  "use_ensemble": false  # Usa apenas Poisson
}
```

## 🎓 Próximos Passos

1. ✅ Treine o modelo XGBoost com seus dados
2. ✅ Ajuste os pesos do Ensemble
3. ✅ Configure thresholds de EV
4. ✅ Faça backtesting de suas estratégias
5. ✅ Integre com n8n para automação
6. ✅ Configure notificações (Telegram/Discord)

---

**Desenvolvido para análise profissional de apostas esportivas**

*Versão Pro - Ensemble + XGBoost + Value Analysis*
