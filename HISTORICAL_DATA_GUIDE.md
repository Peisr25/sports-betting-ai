# Guia de Coleta de Dados Históricos

## 📊 Situação Atual

### Quantas Partidas São Usadas nas Predições?

**Atualmente: 10 partidas** por time

```python
# Em lite/python_api/config.py e pro/python_api/config.py
DEFAULT_HISTORY_MATCHES = 10
```

Quando você faz uma predição de **Arsenal vs Chelsea**:
- Busca **10 últimas partidas do Arsenal**
- Busca **10 últimas partidas do Chelsea**
- **Total: 20 partidas** (2 requisições à API)

---

## ⚠️ Limitações da API (Tier Gratuito)

**football-data.org Tier Gratuito:**
- ✅ **10 requisições/minuto**
- ✅ **~100 requisições/dia**
- ⚠️ Algumas competições limitadas

**Cálculos de Requisições:**

### Cenário 1: Uma Predição
```
2 times × 1 requisição = 2 requisições
Tempo: ~13 segundos (com delay de 6.5s)
```

### Cenário 2: Brasileirão Completo (20 times)
```
20 times × 1 requisição = 20 requisições
Tempo: ~2 minutos (respeitando rate limit)
✅ CABE no rate limit diário!
```

### Cenário 3: Todas as Partidas do Brasileirão (~380)
```
380 partidas × 1 requisição = 380 requisições
Tempo: ~38 minutos
❌ ESTOURA limite diário (100 req/dia)
```

---

## ✅ Solução: Coleta Incremental com Database

### Versão PRO com Banco de Dados

A versão Pro inclui um sistema que:
1. **Coleta dados gradualmente** respeitando rate limit
2. **Salva no SQLite** para reutilização
3. **Evita duplicatas** (não recoleta o que já tem)
4. **Permite pausar/retomar** a coleta

---

## 🚀 Como Coletar Dados Históricos

### 1. Usar o Script de Coleta (Versão Pro)

```bash
cd pro/python_api

# Coletar Brasileirão 2024
python collect_historical_data.py BSA --season 2024

# Coletar Premier League 2024
python collect_historical_data.py PL --season 2024

# Simular sem salvar (dry-run)
python collect_historical_data.py BSA --dry-run
```

**O script irá:**
- ✅ Buscar todos os 20 times do Brasileirão
- ✅ Para cada time, buscar até 50 últimas partidas
- ✅ Salvar no banco SQLite (sem duplicatas)
- ✅ Respeitar rate limit de 10 req/min
- ✅ Mostrar progresso em tempo real

**Tempo estimado:**
```
20 times × 6.5s = 130 segundos = ~2.2 minutos
```

---

### 2. Exemplo de Uso Completo

```bash
# 1. Configure sua API key
cd pro/python_api
cp ../.env.example .env
# Edite .env e adicione sua API key

# 2. Instale dependências (se ainda não fez)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Colete dados do Brasileirão
python collect_historical_data.py BSA --season 2024

# Saída esperada:
# ======================================================================
# COLETA DE DADOS HISTÓRICOS
# ======================================================================
# Competição: BSA
# Temporada: 2024
# Rate Limit: 6.5s entre requisições
# ======================================================================
#
# 📋 Buscando times...
# ✓ Encontrados 20 times
#
# [1/20] Coletando dados de: Botafogo
#   ✓ Salvas 38 partidas no banco
#   ⏳ Aguardando 6.5s (rate limit)...
#
# [2/20] Coletando dados de: Palmeiras
#   ✓ Salvas 38 partidas no banco
#   ⏳ Aguardando 6.5s (rate limit)...
# ...
```

---

### 3. Verificar Dados Coletados

```python
from data.database import Database

db = Database()

# Ver total de partidas
matches = db.get_matches(competition="BSA", limit=1000)
print(f"Total de partidas do Brasileirão: {len(matches)}")

# Ver partidas de um time específico
flamengo_matches = [m for m in matches if "Flamengo" in m.home_team or "Flamengo" in m.away_team]
print(f"Partidas do Flamengo: {len(flamengo_matches)}")
```

---

## 📈 Como Aumentar o Número de Partidas Usadas

### Opção 1: Alterar Configuração Global

**Edite `config.py`:**

```python
# lite/python_api/config.py ou pro/python_api/config.py

class Config:
    # ... outras configs ...

    # Predições
    DEFAULT_HISTORY_MATCHES = 20  # Era 10, agora 20! 🎯
    MIN_CONFIDENCE_THRESHOLD = 0.55
```

**Impacto:**
- ✅ Todas as predições usarão mais dados
- ⚠️ Aumenta tempo de resposta da API
- ⚠️ Aumenta consumo de requisições

### Opção 2: Configurar por Predição

**Na versão Pro, você pode passar o parâmetro:**

```python
# Em pro/python_api/app.py
home_stats = calculate_team_stats(home_team["id"], last_n=30)  # 30 partidas!
away_stats = calculate_team_stats(away_team["id"], last_n=30)
```

### Opção 3: Usar Dados do Database (Versão Pro)

**Vantagem:** Não faz requisições à API!

```python
# Busca partidas do banco ao invés da API
def calculate_team_stats_from_db(team_id: int, last_n: int = 30):
    """Calcula stats usando dados salvos no banco"""
    matches = db.get_matches_by_team(team_id, limit=last_n)
    # Processa as partidas...
```

---

## 🎯 Recomendações

### Para Análise Mais Precisa

| Tipo de Análise | Partidas Recomendadas | Motivo |
|------------------|----------------------|---------|
| **Rápida/Teste** | 5-10 partidas | Forma recente |
| **Padrão** | 10-15 partidas | Equilíbrio |
| **Detalhada** | 20-30 partidas | Tendências |
| **Estatística Completa** | 38+ partidas | Temporada inteira |

### Considerações

**10 partidas (atual):**
- ✅ Rápido (~13s por predição)
- ✅ Boa para forma recente
- ⚠️ Pode não capturar tendências longas

**20-30 partidas:**
- ✅ Estatística mais robusta
- ✅ Capta tendências
- ⚠️ Mais lento (~25-40s por predição)
- ⚠️ Mais requisições à API

**38+ partidas (temporada completa):**
- ✅ Máxima precisão estatística
- ✅ Ideal para análise de longo prazo
- ⚠️ Requer dados no banco (não fazer via API a cada vez!)
- ✅ **Use versão Pro com database**

---

## 💾 Estratégia Recomendada

### 1. Coleta Inicial (Uma Vez)

```bash
# Coletar dados históricos de todas as competições que você usa
python collect_historical_data.py BSA --season 2024
python collect_historical_data.py PL --season 2024
python collect_historical_data.py PD --season 2024
# ... outras competições
```

**Tempo total:** ~10-15 minutos para 5 competições

### 2. Atualização Semanal

```bash
# Toda segunda-feira, coletar partidas novas
python collect_historical_data.py BSA --season 2024
```

**Tempo:** ~2 minutos (só coleta novas partidas)

### 3. Usar Dados Salvos nas Predições

Com dados no banco, você pode:
- ✅ Usar 30+ partidas sem custo de API
- ✅ Fazer predições instantâneas
- ✅ Economizar quota diária

---

## 📊 Comparação de Métodos

| Método | Partidas | Requisições API | Tempo | Precisão |
|--------|----------|-----------------|-------|----------|
| **Atual (Lite)** | 10 | 2/predição | 13s | Boa |
| **Aumentado (Lite)** | 30 | 2/predição | 13s | Melhor |
| **Com Database (Pro)** | 50+ | 0/predição* | <1s | Ótima |

*Após coleta inicial

---

## 🔧 Modificar o Código

### Para Usar Mais Partidas Agora (Simples)

**1. Edite `lite/python_api/config.py`:**

```python
DEFAULT_HISTORY_MATCHES = 20  # Aumente de 10 para 20
```

**2. Reinicie o servidor:**

```bash
python app.py
```

**3. Teste:**

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"home_team": "Flamengo", "away_team": "Palmeiras", "competition": "BSA"}'
```

Agora usará 20 partidas ao invés de 10!

---

### Para Usar Database (Avançado - Pro)

**1. Cole dados históricos:**

```bash
cd pro/python_api
python collect_historical_data.py BSA --season 2024
```

**2. Modifique `calculate_team_stats` para usar database:**

```python
def calculate_team_stats(team_id: int, last_n: int = 30):
    # Tenta buscar do banco primeiro
    matches_from_db = db.get_team_matches(team_id, limit=last_n)

    if len(matches_from_db) >= last_n:
        # Tem dados suficientes no banco
        return process_matches(matches_from_db)
    else:
        # Busca da API como fallback
        matches = collector.get_team_matches_history(team_id, last_n=last_n)
        return process_matches(matches)
```

---

## 📈 Melhorando a Predição

### Fatores que Afetam Precisão

1. **Número de Partidas**
   - Mais partidas = mais dados = potencialmente mais preciso
   - Mas partidas antigas podem não refletir forma atual

2. **Qualidade dos Dados**
   - Partidas da mesma competição são mais relevantes
   - Jogos em casa vs fora têm dinâmicas diferentes

3. **Contexto**
   - Lesões, suspensões não são capturados
   - Motivação (final de campeonato, rebaixamento)

### Recomendações Práticas

**Para Times em Boa Forma:**
- Use 10-15 partidas (forma recente importa mais)

**Para Times Inconstantes:**
- Use 20-30 partidas (captura variabilidade)

**Para Análise de Longo Prazo:**
- Use 38+ partidas (temporada completa)
- **Requer database** (versão Pro)

---

## 🆙 Upgrade para Tier Pago

Se você precisa fazer muitas predições por dia:

**football-data.org Tier Pago:**
- A partir de **€19/mês**
- **3000+ requisições/dia**
- Sem rate limit severo
- Mais competições disponíveis

**Vale a pena se:**
- Faz 100+ predições/dia
- Precisa atualizar dados frequentemente
- Usa comercialmente

---

## 📞 Resumo

### Agora (10 partidas)
```
✅ Funciona bem para análise rápida
✅ Não estoura rate limit
⚠️ Pode ser limitado para análise profunda
```

### Aumentar para 20-30 (Recomendado)
```
✅ Melhor precisão estatística
✅ Ainda cabe no rate limit
⚠️ Um pouco mais lento
```

### Usar Database (Pro - Ideal)
```
✅ Usa 50+ partidas sem custo
✅ Predições instantâneas
✅ Análise profunda
✅ Reutiliza dados
```

---

## 🚀 Próximos Passos

1. **Testar com 20 partidas:**
   - Edite `config.py`
   - Mude `DEFAULT_HISTORY_MATCHES = 20`
   - Teste as predições

2. **Coletar dados (Pro):**
   - Execute `collect_historical_data.py`
   - Espere ~2 minutos
   - Tenha 500+ partidas salvas

3. **Comparar resultados:**
   - Compare predições com 10 vs 20 vs 30 partidas
   - Veja qual funciona melhor para seu caso

---

**Dica:** Comece com 15-20 partidas. É um bom equilíbrio entre precisão e performance!
