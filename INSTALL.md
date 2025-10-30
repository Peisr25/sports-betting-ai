# Instalação Rápida - Sports Betting AI

## ⚡ Instalação em 5 Minutos

### 1️⃣ Requisitos

- Python 3.8+ (Lite) ou 3.10+ (Pro)
- Git (opcional)
- Conta em football-data.org

### 2️⃣ Obter API Key

1. Acesse: https://www.football-data.org/client/register
2. Registre-se (gratuito)
3. Copie sua API key do email

### 3️⃣ Escolher Versão

**Lite** (Gratuita, Poisson):
```bash
cd lite/python_api
```

**Pro** (Avançada, Ensemble):
```bash
cd pro/python_api
```

### 4️⃣ Instalar Dependências

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 5️⃣ Configurar

```bash
cp .env.example .env
```

Edite `.env`:
```
FOOTBALL_DATA_API_KEY=sua_chave_aqui
```

### 6️⃣ Iniciar

```bash
python app.py
```

Acesse: **http://localhost:5000/docs**

## ✅ Testar

```bash
cd ../examples
python easy_predict.py Arsenal Chelsea PL
```

## 🔧 Resolução de Problemas

### Erro de ImportError
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Erro de API Key
Verifique se copiou corretamente no `.env`

### Porta 5000 em uso
Edite `.env`:
```
APP_PORT=8000
```

---

**Pronto! 🎉**
