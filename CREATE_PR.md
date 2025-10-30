# 🚀 CRIAR PULL REQUEST

## Link Direto (1 Clique!)

👉 **CLIQUE AQUI PARA CRIAR O PR:**

https://github.com/Peisr25/sports-betting-ai/compare/main...claude/sports-betting-ai-setup-011CUcfcssPzX1m1tEeMqexN

---

## 📝 Informações do PR

### Título:
```
feat: Complete Sports Betting AI with Lite and Pro versions using football-data.org
```

### Descrição (copie e cole):

```markdown
# Sports Betting AI - Sistema Completo 🚀

Sistema completo de predição de apostas esportivas com **duas versões**: Lite (gratuita) e Pro (profissional), usando a API **football-data.org**.

---

## 🌟 Versão LITE (Gratuita)

### Recursos
✅ **Modelo de Poisson** - Predições estatísticas de gols
✅ **API REST com FastAPI** - Documentação OpenAPI automática
✅ **API football-data.org** - API correta (não API-Football!)
✅ **6 Mercados de Apostas** - Resultado, Gols, BTTS, Escanteios, Cartões, Placar
✅ **4 Scripts de Exemplo** - Prontos para usar
✅ **9 Competições** - PL, BSA, PD, BL1, SA, FL1, CL, PPL, DED
✅ **Sem Banco de Dados** - Tudo em memória (simplicidade)
✅ **Documentação Completa** - Em português

### Arquivos Principais
- `lite/python_api/app.py` (14KB) - API FastAPI completa
- `lite/python_api/models/poisson.py` (11KB) - Modelo de Poisson
- `lite/python_api/data/collector.py` (8.7KB) - Coletor football-data.org
- `lite/examples/` - 4 scripts prontos (classificacao, jogos, predições)

---

## 🚀 Versão PRO (Profissional)

### Recursos
✅ **Tudo da Lite** +
✅ **Modelo XGBoost** - Machine Learning avançado
✅ **Sistema Ensemble** - Combina Poisson + XGBoost
✅ **Análise de Valor (EV)** - Identifica apostas lucrativas
✅ **Critério de Kelly** - Gestão otimizada de banca
✅ **Banco de Dados SQLite** - Histórico persistente
✅ **7+ Mercados** - Análise completa multi-mercado
✅ **Backtesting** - Framework para testar estratégias
✅ **Recomendações Automáticas** - Sistema de value betting

### Arquivos Principais
- `pro/python_api/models/xgboost_model.py` (8.5KB) - XGBoost ML
- `pro/python_api/models/ensemble.py` (11KB) - Sistema Ensemble
- `pro/python_api/analysis/value_analysis.py` (7.6KB) - Análise EV
- `pro/python_api/data/database.py` (3.7KB) - SQLite ORM

---

## 📚 Documentação

- **README.md** - Visão geral e comparação (atualizado)
- **COMPARISON.md** (4.4KB) - Comparação detalhada Lite vs Pro
- **INSTALL.md** (1.2KB) - Instalação rápida em 5 minutos
- **TROUBLESHOOTING.md** (9.5KB) - Guia completo de troubleshooting
- **lite/README_LITE.md** (8.7KB) - Guia completo da versão Lite
- **pro/README_PRO.md** (12KB) - Guia completo da versão Pro

---

## 🔧 Ferramentas de Diagnóstico

### Scripts Adicionados
- **test_api_key.py** - Valida e testa API key
- **setup_env.py** - Configuração automática do .env
- **PR_INSTRUCTIONS.md** - Instruções detalhadas do PR

Esses scripts ajudam a diagnosticar e resolver problemas comuns com API key.

---

## ✨ Mudanças Principais

### Migração de API
- ❌ **Removido**: API-Football (API incorreta usada anteriormente)
- ✅ **Adicionado**: football-data.org (API correta!)
- **Autenticação**: Mudou de `x-apisports-key` para `X-Auth-Token`
- **Códigos**: Corrigidos para football-data.org (BSA=Brasileirão, PL=Premier League)

### Arquitetura
```
sports-betting-ai/
├── lite/                          # Versão Gratuita
│   ├── python_api/
│   │   ├── app.py                # FastAPI
│   │   ├── models/poisson.py     # Modelo Poisson
│   │   └── data/collector.py     # API collector
│   └── examples/                  # Scripts prontos
│
├── pro/                           # Versão Profissional
│   ├── python_api/
│   │   ├── models/
│   │   │   ├── poisson.py        # Poisson
│   │   │   ├── xgboost_model.py  # XGBoost ML
│   │   │   └── ensemble.py       # Ensemble
│   │   ├── analysis/
│   │   │   └── value_analysis.py # Análise EV
│   │   └── data/
│   │       ├── collector.py      # API collector
│   │       └── database.py       # SQLite
│   └── examples/                  # Scripts avançados
│
├── test_api_key.py               # Diagnóstico
├── setup_env.py                  # Setup automático
├── TROUBLESHOOTING.md            # Guia troubleshooting
└── sports-betting-ai-football-data-org.zip  # Package completo (57KB)
```

---

## 📊 Estatísticas

### Commits
- **3 commits** incluídos neste PR
- **36 arquivos alterados** (33 + 3 de diagnóstico)
- **5,272 linhas inseridas**
- **111 linhas deletadas**

### Arquivos
- **Versão Lite**: 17 arquivos
- **Versão Pro**: 14 arquivos
- **Documentação**: 5 arquivos principais
- **Ferramentas**: 3 scripts de diagnóstico
- **ZIP Package**: 57KB

---

## 🎯 Competições Suportadas

| Código | Competição | País | Tier |
|--------|------------|------|------|
| **PL** | Premier League | 🏴󠁧󠁢󠁥󠁮󠁧󠁿 Inglaterra | Gratuito |
| **BSA** | Brasileirão Série A | 🇧🇷 Brasil | Gratuito |
| **PD** | La Liga | 🇪🇸 Espanha | Gratuito |
| **BL1** | Bundesliga | 🇩🇪 Alemanha | Gratuito |
| **SA** | Serie A | 🇮🇹 Itália | Gratuito |
| **FL1** | Ligue 1 | 🇫🇷 França | Gratuito |
| **CL** | Champions League | 🇪🇺 Europa | Gratuito |
| **PPL** | Primeira Liga | 🇵🇹 Portugal | Pago |
| **DED** | Eredivisie | 🇳🇱 Holanda | Pago |

---

## 🧪 Como Testar

### 1. Configurar API Key

```bash
# Opção 1: Automático (recomendado)
python setup_env.py lite

# Opção 2: Manual
cd lite/python_api
cp ../.env.example .env
# Edite .env e adicione sua API key
```

**Obter API Key:**
1. Registre-se: https://www.football-data.org/client/register
2. Confirme email
3. Copie a API key recebida

### 2. Testar API Key

```bash
python test_api_key.py
# Deve retornar: ✅ API KEY VÁLIDA!
```

### 3. Versão Lite

```bash
cd lite/python_api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

**Testar Endpoints:**
```bash
curl http://localhost:5000/competitions
curl http://localhost:5000/teams/PL
curl "http://localhost:5000/matches/BSA?status=SCHEDULED"
curl http://localhost:5000/standings/PL
```

**Scripts de Exemplo:**
```bash
cd lite/examples
python classificacao.py BSA
python proximos_jogos.py PL
python easy_predict.py Arsenal Chelsea PL
```

### 4. Versão Pro

```bash
cd pro/python_api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

**Endpoint Adicional - Análise de Valor:**
```bash
curl -X POST http://localhost:5000/value-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "home_team": "Arsenal",
    "away_team": "Chelsea",
    "competition": "PL",
    "odds": {
      "result": {"home_win": 1.80, "draw": 3.50, "away_win": 4.50}
    }
  }'
```

---

## ⚠️ Breaking Changes

### API Provider
- **Antes**: Usava API-Football (v3.football.api-sports.io)
- **Agora**: Usa football-data.org (api.football-data.org/v4)

### Configuração
- **Antes**: `API_FOOTBALL_KEY` com header `x-apisports-key`
- **Agora**: `FOOTBALL_DATA_API_KEY` com header `X-Auth-Token`

### Códigos de Competição
- **Antes**: IDs numéricos da API-Football
- **Agora**: Códigos de 2-3 letras (PL, BSA, CL, etc)

### Migração
Projetos existentes usando API-Football precisam:
1. Obter nova API key em football-data.org
2. Atualizar `.env` com nova key
3. Atualizar códigos de competição nos scripts

---

## 📦 Entregáveis

### Código
✅ Versão Lite totalmente funcional
✅ Versão Pro totalmente funcional
✅ Ambas testadas e validadas

### Documentação
✅ 5 documentos principais em português
✅ Guias de instalação e uso
✅ Troubleshooting completo
✅ Exemplos práticos

### Ferramentas
✅ Scripts de diagnóstico
✅ Configuração automática
✅ Testes de validação

### Package
✅ ZIP completo (57KB)
✅ Pronto para distribuição
✅ Inclui todas as versões

---

## 🔗 Recursos Externos

- **API Docs**: https://www.football-data.org/documentation/quickstart
- **Registro**: https://www.football-data.org/client/register
- **Planos**: https://www.football-data.org/pricing

---

## 🎓 Requisitos

### Versão Lite
- Python 3.8+
- API Key gratuita (10 req/min, ~100/dia)
- 2GB RAM
- 1GB disco

### Versão Pro
- Python 3.10+
- API Key (pago recomendado para uso intenso)
- 4GB RAM
- 2GB disco

---

## 🚀 Próximos Passos Após Merge

1. ✅ Criar release com a versão 1.0.0
2. ✅ Adicionar badges no README
3. ✅ Criar exemplos adicionais (opcional)
4. ✅ Adicionar CI/CD (opcional)

---

## 📋 Checklist de Revisão

- [x] Código testado e funcional
- [x] Documentação completa
- [x] Exemplos funcionando
- [x] API key validada
- [x] Commits bem descritos
- [x] Sem credenciais expostas
- [x] README atualizado
- [x] Troubleshooting incluído

---

**Status: ✅ Pronto para merge!**

Ambas as versões (Lite e Pro) estão testadas, documentadas e prontas para produção. Sistema completo de análise de apostas esportivas usando a API correta (football-data.org).

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

---

## ✅ Checklist Antes de Criar

- [x] Branch pushed
- [x] Commits limpos
- [x] Documentação completa
- [x] Working tree clean
- [x] Tudo testado

---

## 🎯 Resumo dos Commits

### Commit 1: Sistema Principal (769289d)
- 33 arquivos (Lite + Pro)
- Sistema completo implementado

### Commit 2: Instruções PR (cf08040)
- Documentação para criação manual do PR

### Commit 3: Ferramentas Diagnóstico (6d0f277)
- Scripts de validação e troubleshooting

---

**Total: 36 arquivos | 5,272 linhas | 3 commits**
