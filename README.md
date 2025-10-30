# Sports Betting AI - Complete Package

Sistema completo de análise e predição de apostas esportivas com **2 versões**: Lite (gratuita) e Pro (profissional).

## 📦 O que está incluído?

### 🌟 Versão LITE (Gratuita)
- ✅ Modelo de Poisson para predições
- ✅ API REST com FastAPI
- ✅ API football-data.org (tier gratuito)
- ✅ 3 mercados de apostas principais
- ✅ Scripts prontos para usar
- ✅ SEM banco de dados (tudo em memória)

### 🚀 Versão PRO (Profissional)
- ✅ Tudo da versão Lite +
- ✅ Modelo XGBoost (Machine Learning)
- ✅ Sistema Ensemble (combina Poisson + XGBoost)
- ✅ Análise de Valor Esperado (EV)
- ✅ Critério de Kelly para gestão de banca
- ✅ Banco de dados SQLite
- ✅ 7+ mercados de apostas
- ✅ Backtesting de estratégias

## 🏆 Competições Suportadas

| Código | Competição | País |
|--------|------------|------|
| **PL** | Premier League | 🏴󐁧󐁢󐁥󐁮󐁧󐁿 Inglaterra |
| **BSA** | Brasileirão Série A | 🇧🇷 Brasil |
| **PD** | La Liga | 🇪🇸 Espanha |
| **BL1** | Bundesliga | 🇩🇪 Alemanha |
| **SA** | Serie A | 🇮🇹 Itália |
| **FL1** | Ligue 1 | 🇫🇷 França |
| **CL** | Champions League | 🇪🇺 Europa |

## 🚀 Início Rápido

### 1. Escolha sua versão

**Lite** - Para testes e aprendizado:
```bash
cd lite/
```

**Pro** - Para uso profissional:
```bash
cd pro/
```

### 2. Instale as dependências

```bash
cd python_api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure a API Key

1. Registre-se em: https://www.football-data.org/client/register
2. Copie o `.env.example`:
   ```bash
   cp .env.example .env
   ```
3. Adicione sua chave no `.env`:
   ```
   FOOTBALL_DATA_API_KEY=sua_chave_aqui
   ```

### 4. Inicie o servidor

```bash
python app.py
```

Acesse: **http://localhost:5000/docs**

## 📊 Comparação Lite vs Pro

| Recurso | Lite | Pro |
|---------|------|-----|
| Modelo de Poisson | ✅ | ✅ |
| Modelo XGBoost | ❌ | ✅ |
| Sistema Ensemble | ❌ | ✅ |
| Análise de Valor (EV) | ❌ | ✅ |
| Critério de Kelly | ❌ | ✅ |
| Banco de Dados | ❌ | ✅ SQLite |
| Mercados Básicos | 3 | 7+ |
| Backtesting | ❌ | ✅ |
| Recomendações Auto | Básicas | Avançadas |

## 📖 Documentação

Cada versão inclui documentação completa:

- `README_LITE.md` / `README_PRO.md` - Guia completo
- `docs/API_DOCUMENTATION.md` - Referência da API
- `docs/USER_GUIDE.md` - Guia do usuário
- `docs/N8N_SETUP.md` - Integração com n8n

## 🎯 Exemplos de Uso

### Predição Simples (Lite ou Pro)

```bash
cd examples/
python easy_predict.py Arsenal Chelsea PL
```

### Análise de Valor (Pro)

```bash
python value_analysis_example.py Arsenal Chelsea PL
```

### Predições em Lote

```bash
python jogos_e_predicoes.py BSA 5
```

## 🔬 Modelos Disponíveis

### Modelo de Poisson (Lite e Pro)
- Distribuição estatística clássica
- Ideal para predição de gols
- Rápido e eficiente
- Não requer treinamento

### Modelo XGBoost (Pro)
- Machine Learning de alto desempenho
- Aprende com dados históricos
- Considera múltiplas features
- Precisa ser treinado

### Sistema Ensemble (Pro)
- Combina Poisson + XGBoost
- Média ponderada de predições
- Maior precisão
- Reduz viés de modelo único

## 💡 Recursos Avançados (Pro)

### Análise de Valor Esperado
```python
EV = (Probabilidade × Retorno) - (Probabilidade de Perda × Stake)
```
- Identifica apostas com valor positivo
- Lucrativo no longo prazo
- Considera odds das casas

### Critério de Kelly
```python
Kelly % = (odds × probability - 1) / (odds - 1)
```
- Gestão de banca otimizada
- Maximiza crescimento logarítmico
- Minimiza risco de ruína

## ⚙️ Requisitos

### Versão Lite
- Python 3.8+
- 2GB RAM
- 1GB espaço em disco
- API Key gratuita (100 req/dia)

### Versão Pro
- Python 3.10+
- 4GB RAM
- 2GB espaço em disco
- API Key (plano pago recomendado)

## 🐛 Problemas Comuns

### "API key inválida"
- Verifique o arquivo `.env`
- Confirme que a key está ativa

### "Limite de requisições atingido"
- Tier gratuito: 10 req/min, 100/dia
- Aguarde ou faça upgrade

### "Time não encontrado"
- Use nomes parciais: "Arsenal", "Flamengo"
- Verifique a competição correta

## ⚠️ Aviso Legal

1. **Uso Educacional**: Sistema para fins educacionais e de pesquisa
2. **Sem Garantias**: Predições não garantem lucros
3. **Responsabilidade**: Aposte apenas o que pode perder
4. **Legalidade**: Verifique se apostas são legais em sua região

## 📞 Suporte

- Documentação: `/docs` em cada versão
- API Docs: http://localhost:5000/docs
- GitHub Issues: Para reportar problemas

## 🆙 Migração Lite → Pro

1. Copie seu `.env` da versão Lite
2. Instale dependências da Pro
3. Treine o modelo XGBoost (opcional)
4. Ajuste pesos do Ensemble
5. Configure banco de dados

## 📄 Estrutura do Projeto

```
sports-betting-ai-complete/
├── README.md                    ← Você está aqui
├── COMPARISON.md                ← Comparação detalhada
├── INSTALL.md                   ← Instalação rápida
│
├── lite/                        ← Versão Gratuita
│   ├── README_LITE.md
│   ├── python_api/
│   ├── examples/
│   └── docs/
│
└── pro/                         ← Versão Profissional
    ├── README_PRO.md
    ├── python_api/
    ├── examples/
    └── docs/
```

## 🙏 Créditos

- **API de Dados**: [football-data.org](https://www.football-data.org)
- **Frameworks**: FastAPI, XGBoost, SQLAlchemy
- **Inspiração**: Comunidade de análise esportiva

---

**Desenvolvido com ❤️ para a comunidade**

*Última atualização: Outubro 2025*
