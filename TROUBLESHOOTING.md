# Resolução de Problemas - API Token Inválido

## 🔍 Diagnóstico

Você está recebendo o erro:
```
{"detail":"Erro HTTP 400: {\"message\":\"Your API token is invalid.\",\"errorCode\":400}"}
```

Este erro ocorre quando:
1. O arquivo `.env` não existe
2. A API key está incorreta
3. A API key tem formatação errada (espaços, aspas extras)
4. A conta não foi ativada em football-data.org

---

## ✅ Solução Passo a Passo

### 1. Obter API Key (se ainda não tem)

1. Acesse: https://www.football-data.org/client/register
2. Preencha o formulário de registro
3. Confirme seu email
4. Copie a API key que receber por email

**Formato esperado:** String alfanumérica longa (ex: `abc123def456...`)

---

### 2. Configurar o Arquivo .env

#### Opção A: Usando o Script Automático (Recomendado)

```bash
# Para versão Lite
python setup_env.py lite

# Para versão Pro
python setup_env.py pro
```

O script irá:
- Criar o arquivo `.env` no local correto
- Solicitar sua API key
- Configurar automaticamente

#### Opção B: Manualmente

**Para Versão LITE:**

```bash
# 1. Vá para o diretório da versão Lite
cd lite/python_api

# 2. Copie o template
cp ../.env.example .env

# 3. Edite o arquivo .env
# No Windows: notepad .env
# No Linux/Mac: nano .env
```

**Edite o arquivo `.env` e substitua:**
```env
FOOTBALL_DATA_API_KEY=YOUR_API_KEY_HERE
```

**Por:**
```env
FOOTBALL_DATA_API_KEY=sua_api_key_aqui_sem_aspas
```

⚠️ **IMPORTANTE:**
- ❌ NÃO adicione aspas: `"sua_key"`
- ❌ NÃO adicione espaços: ` sua_key `
- ✅ APENAS a key: `sua_key`

---

### 3. Testar a API Key

Use o script de diagnóstico:

```bash
# Teste manual (digite a key quando solicitado)
python test_api_key.py

# Ou simplesmente pressione Enter para testar o .env atual
```

O script irá:
- ✅ Validar formato da key
- ✅ Testar conexão com football-data.org
- ✅ Mostrar detalhes do erro (se houver)

---

### 4. Verificar Tier da API

A API football-data.org tem limitações:

**Tier Gratuito:**
- ✅ 10 requisições/minuto
- ✅ 100 requisições/dia (pode variar)
- ⚠️ Algumas competições podem não estar disponíveis
- ⚠️ Dados podem ter delay

**Tier Pago (a partir de €19/mês):**
- ✅ 3000+ requisições/dia
- ✅ Todas as competições
- ✅ Dados em tempo real

---

## 🧪 Testando a Configuração

Depois de configurar o `.env`, teste:

### 1. Iniciar o Servidor

```bash
cd lite/python_api
python app.py
```

### 2. Testar Endpoints

```bash
# Competições (não usa API externa)
curl http://localhost:5000/competitions

# Times da Premier League (usa API)
curl http://localhost:5000/teams/PL

# Partidas do Brasileirão (usa API)
curl "http://localhost:5000/matches/BSA?status=SCHEDULED"

# Classificação da Premier League (usa API)
curl http://localhost:5000/standings/PL
```

### 3. Usar Scripts de Exemplo

```bash
cd lite/examples

# Classificação
python classificacao.py BSA

# Próximos jogos
python proximos_jogos.py PL

# Predição
python easy_predict.py Arsenal Chelsea PL
```

---

## 🐛 Erros Comuns

### Erro: "Your API token is invalid"

**Causa:** API key incorreta ou mal formatada

**Solução:**
1. Verifique se copiou a key completa
2. Remova espaços e aspas do `.env`
3. Confirme que a conta foi ativada no email

### Erro: "Rate limit exceeded" (429)

**Causa:** Muitas requisições em pouco tempo

**Solução:**
1. Aguarde 1 minuto
2. Considere fazer upgrade do plano
3. Reduza frequência de requisições

### Erro: "Permission denied" (403)

**Causa:** Tier gratuito sem acesso a certa competição

**Solução:**
1. Tente outra competição (PL, PD, CL geralmente funcionam)
2. Faça upgrade para tier pago
3. Verifique se a competição está na lista suportada

### Erro: "No module named 'dotenv'"

**Causa:** Biblioteca python-dotenv não instalada

**Solução:**
```bash
pip install python-dotenv
```

---

## 📂 Estrutura Correta de Arquivos

A estrutura deve estar assim:

```
sports-betting-ai/
├── lite/
│   ├── .env.example          ✅ Template
│   └── python_api/
│       ├── .env              ✅ SEU ARQUIVO (criar este!)
│       ├── app.py
│       ├── config.py         ✅ Lê o .env
│       └── requirements.txt
│
└── pro/
    ├── .env.example
    └── python_api/
        ├── .env              ✅ SEU ARQUIVO (criar este!)
        ├── app.py
        └── ...
```

---

## 🆘 Ainda com Problemas?

### 1. Verifique os Logs

```bash
cd lite/python_api
python app.py
# Veja as mensagens de inicialização
```

Procure por:
- ✅ "API Key: ✓ Configurada"
- ❌ "API Key: ✗ Não configurada"

### 2. Teste Diretamente a API

```bash
# Substitua YOUR_KEY pela sua API key
curl -H "X-Auth-Token: YOUR_KEY" https://api.football-data.org/v4/competitions
```

Se funcionar aqui mas não no app, o problema é no arquivo `.env`.

### 3. Verifique Variáveis de Ambiente

```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv('lite/python_api/.env'); print(os.getenv('FOOTBALL_DATA_API_KEY'))"
```

Deve mostrar sua API key completa.

---

## 🐍 Erro Python 3.13 - ModuleNotFoundError: No module named 'distutils'

### Problema

Se você está usando **Python 3.13+** e recebe o erro ao instalar dependências da versão **Pro**:

```
ERROR: Exception:
[...]
ModuleNotFoundError: No module named 'distutils'
```

**Causa:** Python 3.13 removeu o módulo `distutils` que era usado por versões antigas de bibliotecas como numpy 1.24.3.

### ✅ Solução

O arquivo `requirements.txt` foi atualizado para Python 3.13. Basta instalar normalmente:

```bash
cd pro/python_api
pip install -r requirements.txt
```

As novas versões são:
- `numpy>=1.26.0` (primeira versão compatível com Python 3.13)
- `pandas>=2.1.0`
- `scikit-learn>=1.4.0`
- `xgboost>=2.0.3`

### 🔄 Alternativa: Usar Python 3.12 ou 3.11

Se você prefere usar as versões exatas testadas originalmente:

```bash
cd pro/python_api

# Instalar com as versões originais (Python 3.10-3.12)
pip install -r requirements-py312.txt
```

### 📝 Notas

- **Versão Lite** não tem este problema (não usa numpy/ML)
- **Python 3.11 ou 3.12** é recomendado para máxima compatibilidade
- **Python 3.13** é suportado com as versões atualizadas

---

## 📞 Suporte

- Documentação football-data.org: https://www.football-data.org/documentation/quickstart
- Registro de API key: https://www.football-data.org/client/register
- FAQ: https://www.football-data.org/documentation/api

---

## ✅ Checklist Final

Antes de usar o sistema, confirme:

- [ ] Registrei em football-data.org
- [ ] Recebi a API key por email
- [ ] Criei o arquivo `.env` em `lite/python_api/.env`
- [ ] Copiei a API key SEM aspas ou espaços
- [ ] Testei com `python test_api_key.py`
- [ ] O teste passou ✅
- [ ] Iniciei o servidor com `python app.py`
- [ ] Testei os endpoints com curl
- [ ] Tudo funciona! 🎉

---

**Boas predições!** ⚽🎯
