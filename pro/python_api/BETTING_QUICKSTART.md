# 🎯 Sistema de Apostas em Tempo Real - Quick Start

## 📦 Arquivos do Sistema

### Scripts Principais

1. **find_live_and_upcoming.py** - Encontra partidas disponíveis para apostas
2. **collect_team_history.py** - Coleta dados históricos dos times
3. **calculate_predictions.py** - Calcula previsões usando ML
4. **generate_betting_recommendations.py** - Gera recomendações com análise EV

### Scripts Auxiliares

5. **run_betting_pipeline.py** - Executa todo o pipeline automaticamente
6. **monitor_betting.py** - Monitor em tempo real com alertas

### Documentação

- **LIVE_BETTING_GUIDE.md** - Guia completo do sistema
- **API_DATA_REFERENCE.md** - Referência das APIs
- **TRAINING_GUIDE.md** - Guia de treinamento de modelos

---

## 🚀 Uso Rápido

### Opção 1: Pipeline Completo (Recomendado)

```bash
# Ativar ambiente
cd pro/python_api
.\venv\Scripts\activate

# Executar tudo de uma vez
python run_betting_pipeline.py
```

**Resultado:** 
- ✅ Encontra partidas ao vivo/agendadas
- ✅ Coleta dados históricos
- ✅ Calcula previsões
- ✅ Gera recomendações

**Tempo:** 5-15 minutos

---

### Opção 2: Monitor Contínuo

```bash
# Inicia monitor (executa a cada 30 min)
python monitor_betting.py

# Ou com intervalo personalizado (ex: 15 min)
python monitor_betting.py --interval 15
```

**Benefício:** Alertas automáticos de novas oportunidades

---

### Opção 3: Passo a Passo Manual

```bash
# 1. Encontrar partidas
python find_live_and_upcoming.py

# 2. Coletar dados
python collect_team_history.py --from-live-fixtures

# 3. Calcular previsões
python calculate_predictions.py --from-live-fixtures

# 4. Ver recomendações
python generate_betting_recommendations.py
```

---

## 📊 Interpretação dos Resultados

### Arquivo: betting_recommendations.json

```json
{
  "recommendations": [
    {
      "match": "Flamengo vs Palmeiras",
      "analysis": {
        "best_bet": {
          "market": "HOME",           // Apostar na vitória da casa
          "odds": 2.00,               // Odd da casa de apostas
          "probability": 0.623,       // 62.3% de chance
          "expected_value": 0.246,    // +24.6% de valor esperado
          "kelly_stake": 0.031        // 3.1% do bankroll
        }
      }
    }
  ]
}
```

### Como Ler

- **EV > +10%** ⭐⭐⭐ Excelente
- **EV +5% a +10%** ⭐⭐ Bom
- **EV 0% a +5%** ⭐ Marginal
- **EV < 0%** ❌ Evitar

- **Kelly > 5%** = Oportunidade forte
- **Kelly 2-5%** = Oportunidade moderada  
- **Kelly < 2%** = Oportunidade fraca

⚠️ **NUNCA aposte mais de 5% do bankroll em uma única aposta!**

---

## 🔧 Configuração Inicial

### 1. Variáveis de Ambiente (.env)

```bash
API_FOOTBALL_KEY=sua_chave_rapidapi
FOOTBALL_DATA_API_KEY=b00e83b0962741e4a703a7dbe7b2f17f
```

### 2. Ajustar Parâmetros (opcional)

Edite `generate_betting_recommendations.py`:

```python
self.min_confidence = 0.45      # 45% confiança mínima
self.min_ev = 0.05              # 5% EV mínimo
self.min_data_quality = 5       # 5 partidas mínimas/time
```

---

## 📁 Arquivos Gerados

| Arquivo | Descrição |
|---------|-----------|
| `live_and_upcoming_fixtures.json` | Partidas disponíveis |
| `betting_predictions.json` | Previsões calculadas |
| `betting_recommendations.json` | ⭐ RECOMENDAÇÕES FINAIS |
| `database/betting.db` | Histórico de partidas |

---

## 💡 Dicas de Gestão

### Bankroll Management

1. **Kelly Fracionado:** Use 25% do Kelly completo (já aplicado)
2. **Limite por Aposta:** Máximo 5% do bankroll
3. **Limite Total:** Máximo 20% investido simultaneamente
4. **Nunca:** Aposte mais do que pode perder

### Seleção de Apostas

- ✅ Priorize **EV > +10%**
- ✅ Prefira **qualidade HIGH** (10+ partidas)
- ✅ Diversifique entre ligas/mercados
- ❌ Evite times sem histórico recente

---

## 🐛 Troubleshooting

### Nenhuma aposta recomendada
→ Normal se odds não oferecem valor. Aguarde novas partidas.

### Dados insuficientes
→ Execute `collect_team_history.py` primeiro

### Erro de API key
→ Verifique arquivo `.env`

### Database corrompido
```bash
copy database\betting.db database\betting_backup.db
del database\betting.db
python collect_team_history.py --from-live-fixtures
```

---

## 📞 Documentação Completa

Para informações detalhadas, consulte:

- 📖 **LIVE_BETTING_GUIDE.md** - Guia completo
- 🤖 **TRAINING_GUIDE.md** - Treinamento de modelos
- 🔌 **API_DATA_REFERENCE.md** - Referência de APIs

---

## ⚠️ Disclaimer

- Sistema para fins educacionais
- Apostas envolvem risco financeiro
- Nenhuma previsão é garantida
- Aposte com responsabilidade
- Verifique legalidade local

---

## 🎯 Fluxo Recomendado

### Iniciante

```bash
# 1. Primeira vez: executar pipeline
python run_betting_pipeline.py

# 2. Analisar resultados
notepad betting_recommendations.json

# 3. Entender o sistema
notepad LIVE_BETTING_GUIDE.md
```

### Uso Regular

```bash
# Monitor contínuo (deixar rodando)
python monitor_betting.py --interval 30
```

### Avançado

```bash
# Customizar cada etapa
python find_live_and_upcoming.py
python collect_team_history.py --from-live-fixtures --limit 50
python calculate_predictions.py --from-live-fixtures
python generate_betting_recommendations.py
```

---

**Boa sorte! 🍀**

*Lembre-se: Jogo responsável sempre!*
