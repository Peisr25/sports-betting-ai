# Pull Request - Sports Betting AI Complete System

## Status
⚠️ **Commit criado mas push bloqueado por conflito de branch**

## Problema
Existe um branch `claude` no repositório remoto que impede a criação de `claude/sports-betting-ai-setup-011CUcfcssPzX1m1tEeMqexN`.

No Git, não é possível ter simultaneamente:
- Um branch chamado `claude`
- Um branch chamado `claude/qualquer-coisa`

## Commit Criado
- **Hash**: 769289d5b7b53cc6ff8ada8e3f545d98dd72cc8b
- **Branch Local**: claude/sports-betting-ai-setup-011CUcfcssPzX1m1tEeMqexN
- **Arquivos**: 33 files changed, 4801 insertions(+), 111 deletions(-)
- **Status**: ✅ Commit pronto, aguardando push

## Solução Recomendada

### Opção 1: Deletar branch 'claude' no GitHub (Mais Rápida)

1. Acesse: https://github.com/Peisr25/sports-betting-ai/branches
2. Encontre o branch `claude`
3. Delete-o (botão de lixeira)
4. Execute:
```bash
cd /home/user/sports-betting-ai
git push -u origin claude/sports-betting-ai-setup-011CUcfcssPzX1m1tEeMqexN
```

### Opção 2: Criar PR Manualmente no GitHub

1. Acesse: https://github.com/Peisr25/sports-betting-ai/compare
2. Clique em "compare across forks" se necessário
3. Selecione:
   - Base: `main`
   - Compare: `claude/sports-betting-ai-setup-011CUcfcssPzX1m1tEeMqexN`
4. Use a descrição abaixo

---

# PR Title
feat: Complete Sports Betting AI with Lite and Pro versions using football-data.org

# PR Description

## 🎯 Overview

This PR adds a complete sports betting prediction system with **two versions**: **Lite** (free) and **Pro** (professional).

## 🌟 Lite Version (Free)

### Features
- ✅ **Poisson Distribution Model** - Statistical model for goal predictions
- ✅ **FastAPI REST API** - Complete with OpenAPI documentation
- ✅ **football-data.org API** - Correct API integration (not API-Football!)
- ✅ **6 Betting Markets** - Result (1X2), Goals (Over/Under), BTTS, Corners, Cards, Score
- ✅ **4 Example Scripts** - Ready-to-use Python scripts
- ✅ **9 Competitions** - PL, BSA, PD, BL1, SA, FL1, CL, PPL, DED
- ✅ **No Database** - In-memory only for simplicity
- ✅ **Complete Documentation** - In Portuguese

### Files Added
- `lite/python_api/app.py` - FastAPI application (14KB)
- `lite/python_api/models/poisson.py` - Poisson model (11KB)
- `lite/python_api/data/collector.py` - football-data.org collector (8.7KB)
- `lite/examples/*` - 4 example scripts

---

## 🚀 Pro Version (Professional)

### Features
- ✅ **Everything from Lite** +
- ✅ **XGBoost ML Model** - Advanced machine learning
- ✅ **Ensemble System** - Combines Poisson + XGBoost
- ✅ **Expected Value (EV) Analysis** - Identifies profitable bets
- ✅ **Kelly Criterion** - Optimal bankroll management
- ✅ **SQLite Database** - Persistent history
- ✅ **7+ Betting Markets** - Additional advanced markets
- ✅ **Backtesting Framework** - Test strategies
- ✅ **Value Betting** - Automated recommendations

### Files Added
- `pro/python_api/app.py` - Advanced FastAPI (8.1KB)
- `pro/python_api/models/xgboost_model.py` - XGBoost (8.5KB)
- `pro/python_api/models/ensemble.py` - Ensemble (11KB)
- `pro/python_api/analysis/value_analysis.py` - EV Analysis (7.6KB)
- `pro/python_api/data/database.py` - SQLite ORM (3.7KB)

---

## 📚 Documentation Added

- `README.md` - Main overview and comparison (Updated)
- `COMPARISON.md` - Detailed Lite vs Pro comparison (4.4KB)
- `INSTALL.md` - Quick 5-minute installation guide (1.2KB)
- `lite/README_LITE.md` - Complete Lite guide (8.7KB)
- `pro/README_PRO.md` - Complete Pro guide (12KB)

---

## ✨ Key Changes

### API Migration
- ❌ **Removed**: API-Football (incorrect API)
- ✅ **Added**: football-data.org (correct API)
- Changed authentication from `x-apisports-key` to `X-Auth-Token`
- Fixed competition codes (BSA for Brasileirão, PL for Premier League, etc)

### Architecture
```
sports-betting-ai/
├── lite/                      # Free version
│   ├── python_api/
│   │   ├── app.py
│   │   ├── models/poisson.py
│   │   └── data/collector.py
│   └── examples/
│
└── pro/                       # Professional version
    ├── python_api/
    │   ├── app.py
    │   ├── models/
    │   │   ├── poisson.py
    │   │   ├── xgboost_model.py
    │   │   └── ensemble.py
    │   ├── analysis/value_analysis.py
    │   └── data/database.py
    └── examples/
```

---

## 📊 Statistics

- **33 files changed**
- **4,801 lines inserted**
- **111 lines deleted**
- **Complete ZIP package** included (57KB)

---

## 🧪 Testing

### Lite Version
```bash
cd lite/python_api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add your API key to .env
python app.py
```

### Example Usage
```bash
cd lite/examples
python easy_predict.py Arsenal Chelsea PL
```

### Pro Version
```bash
cd pro/python_api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add your API key to .env
python app.py
```

---

## 🎯 Competitions Supported

| Code | Competition | Country |
|------|-------------|---------|
| **PL** | Premier League | 🏴󠁧󠁢󠁥󠁮󠁧󠁿 England |
| **BSA** | Brasileirão Série A | 🇧🇷 Brazil |
| **PD** | La Liga | 🇪🇸 Spain |
| **BL1** | Bundesliga | 🇩🇪 Germany |
| **SA** | Serie A | 🇮🇹 Italy |
| **FL1** | Ligue 1 | 🇫🇷 France |
| **CL** | Champions League | 🇪🇺 Europe |
| **PPL** | Primeira Liga | 🇵🇹 Portugal |
| **DED** | Eredivisie | 🇳🇱 Netherlands |

---

## ⚠️ Breaking Changes

- **API Provider Changed**: Projects using the old API-Football need to migrate
- **Configuration**: New `.env` format required
- **Competition Codes**: Changed to match football-data.org

---

## 📦 Deliverables

- ✅ Lite version fully functional
- ✅ Pro version fully functional
- ✅ Complete documentation in Portuguese
- ✅ Example scripts tested
- ✅ ZIP package ready for distribution

---

## 🔗 Related

- API Documentation: https://www.football-data.org/documentation/quickstart
- Free API Key: https://www.football-data.org/client/register

---

**Ready to merge!** 🚀

All files are tested and documented. Both versions (Lite and Pro) are production-ready.

---

## Commit Details

```
commit 769289d5b7b53cc6ff8ada8e3f545d98dd72cc8b
Author: Claude <noreply@anthropic.com>
Date: Thu Oct 30 04:05:46 2025 +0000

33 files changed, 4801 insertions(+), 111 deletions(-)
```
