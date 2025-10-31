# 📊 Dados Disponíveis na API - football-data.org

## ✅ O Que a API Gratuita Fornece

### Informações Básicas da Partida:
- ✅ **ID da partida** - Identificador único
- ✅ **Data/hora** (UTC) - Quando o jogo acontece/aconteceu
- ✅ **Times** - Nome, ID, escudo (crest)
- ✅ **Competição** - Nome, código, emblema
- ✅ **Status** - SCHEDULED, LIVE, FINISHED, POSTPONED, etc
- ✅ **Rodada** (matchday) - Número da rodada
- ✅ **Estágio** - REGULAR_SEASON, PLAYOFFS, etc

### Placar:
- ✅ **Placar final** - Gols de cada time
- ✅ **Placar do intervalo** - Gols no 1º tempo
- ✅ **Placar prorrogação** - Se houver tempo extra
- ✅ **Placar penaltis** - Se decidido nos penaltis
- ✅ **Vencedor** - HOME, AWAY, DRAW

### Outros Dados:
- ✅ **Árbitros** - Nome e tipo (às vezes vazio)
- ✅ **Venue** - Estádio (quando disponível)
- ✅ **Temporada** - Ano/período da competição

---

## ❌ O Que NÃO Está Disponível (Tier Gratuito)

### Estatísticas de Jogo:
- ❌ **Escanteios** (corners)
- ❌ **Faltas** (fouls)
- ❌ **Cartões amarelos**
- ❌ **Cartões vermelhos**
- ❌ **Chutes** (shots)
- ❌ **Chutes no gol** (shots on target)
- ❌ **Posse de bola** (possession %)
- ❌ **Passes** (total, precisão)
- ❌ **Impedimentos** (offsides)
- ❌ **Defesas do goleiro** (saves)
- ❌ **Cruzamentos** (crosses)
- ❌ **Desarmes** (tackles)
- ❌ **Dribles** (dribbles)

### Dados Comerciais:
- ❌ **Cotações/Odds** (apostas)
- ❌ **Lineups** (escalações) - Requer tier pago
- ❌ **Eventos ao vivo** (gols, cartões em tempo real)

---

## 💰 Planos Pagos da football-data.org

### Tier Pago (€10-60/mês):
- ✅ Estatísticas detalhadas (escanteios, cartões, etc)
- ✅ Lineups (escalações)
- ✅ Eventos da partida (timeline)
- ✅ Mais requisições por minuto
- ✅ Head-to-head detalhado
- ✅ Dados de jogadores individuais

**Mais info:** https://www.football-data.org/pricing

---

## 🔧 Alternativas para Obter Estatísticas Detalhadas

### 1️⃣ API-Football (RapidAPI)
**URL:** https://www.api-football.com/

**Prós:**
- ✅ Estatísticas completas (escanteios, cartões, chutes, etc)
- ✅ Lineups e formações
- ✅ Eventos em tempo real
- ✅ Odds de várias casas de apostas
- ✅ Tier gratuito: 100 req/dia

**Contras:**
- ❌ Limite mais baixo no tier gratuito
- ❌ Interface via RapidAPI

**Exemplo de uso:**
```python
import requests

url = "https://v3.football.api-sports.io/fixtures"
headers = {
    'x-rapidapi-host': "v3.football.api-sports.io",
    'x-rapidapi-key': "YOUR_API_KEY"
}
params = {"id": "215662"}  # ID da partida

response = requests.get(url, headers=headers, params=params)
data = response.json()

# Estatísticas disponíveis:
stats = data['response'][0]['statistics']
# corners, fouls, yellow_cards, red_cards, etc
```

---

### 2️⃣ SportMonks
**URL:** https://www.sportmonks.com/football-api/

**Prós:**
- ✅ Dados extremamente detalhados
- ✅ Estatísticas de jogadores
- ✅ Previsões e análises
- ✅ Cobertura global

**Contras:**
- ❌ Mais caro (a partir de $25/mês)
- ❌ Sem tier gratuito robusto

---

### 3️⃣ Web Scraping

#### Opção A: FlashScore
**URL:** https://www.flashscore.com.br/

**Dados disponíveis:**
- Escanteios, cartões, chutes
- Timeline da partida
- Estatísticas detalhadas
- Formações

**Exemplo com BeautifulSoup:**
```python
from bs4 import BeautifulSoup
import requests

url = f"https://www.flashscore.com.br/jogo/{match_id}/#/resumo-de-jogo"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Extrair escanteios, etc
corners = soup.find('div', class_='stat__row--corners')
```

⚠️ **Atenção:** Web scraping pode violar termos de serviço!

---

#### Opção B: SofaScore
**URL:** https://www.sofascore.com/

- API não oficial
- Dados muito completos
- Requer engenharia reversa

---

### 4️⃣ Calculado/Estimado

Você pode **calcular ou estimar** algumas estatísticas baseado nos dados que tem:

#### Cartões Estimados:
```python
# Baseado em histórico
media_cartoes_amarelos_por_jogo = 3.5
media_cartoes_vermelhos_por_jogo = 0.2

# Ajustar por time/árbitro
if arbitro_rigoroso:
    media_cartoes *= 1.3
```

#### Escanteios Estimados:
```python
# Média da liga
media_escanteios = 10.5  # Brasileirão ~10-11 por jogo

# Ajustar por histórico do time
if time_atacante:
    escanteios_favor *= 1.2
```

#### Chutes Estimados:
```python
# Baseado em gols + média de conversão
taxa_conversao = 0.12  # ~12% dos chutes viram gol
chutes_estimados = gols / taxa_conversao
```

---

## 🎯 Recomendação para Seu Projeto

### Para Previsões Básicas (Atual):
✅ **Use football-data.org gratuito**
- Suficiente para prever resultado (HOME/DRAW/AWAY)
- Dados de placar e histórico são suficientes
- Sem custo adicional

### Para Previsões Avançadas:
💰 **Considere API-Football**
- Se quiser prever escanteios, cartões, etc
- Tier gratuito: 100 req/dia (suficiente para começar)
- Upgrade para €20/mês se precisar de mais

### Para Análise Profissional:
💎 **SportMonks ou Football-Data.org Pago**
- Dados de jogadores individuais
- Estatísticas avançadas
- Timeline de eventos
- Lineups e formações

---

## 📝 Exemplo: Como Seu Sistema Pode Evoluir

### Fase 1 (Atual): ✅ Implementado
```python
# Dados básicos: resultado, placar
features = [
    'home_wins_last_10',
    'away_wins_last_10',
    'goals_avg',
    'head_to_head'
]
prediction = model.predict(['HOME', 'DRAW', 'AWAY'])
```

### Fase 2: Com Estatísticas Básicas
```python
# Adicionar: escanteios, cartões
features += [
    'corners_avg',
    'yellow_cards_avg',
    'fouls_avg'
]
```

### Fase 3: Com Estatísticas Avançadas
```python
# Adicionar: posse, chutes, passes
features += [
    'possession_avg',
    'shots_on_target_avg',
    'pass_accuracy'
]
```

### Fase 4: Com Lineups e Jogadores
```python
# Adicionar: jogadores escalados
features += [
    'best_scorer_playing',
    'key_player_injured',
    'coach_tactics'
]
```

---

## 🚀 Implementação Prática

### Se Você Quiser Adicionar Estatísticas Agora:

#### 1. Instalar API-Football:
```bash
pip install requests
```

#### 2. Criar collector alternativo:
```python
# data/api_football_collector.py
class APIFootballCollector:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://v3.football.api-sports.io"
    
    def get_match_statistics(self, fixture_id):
        """Busca estatísticas detalhadas"""
        url = f"{self.base_url}/fixtures/statistics"
        headers = {'x-rapidapi-key': self.api_key}
        params = {'fixture': fixture_id}
        
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        
        return {
            'corners': data['statistics']['Corner Kicks'],
            'yellow_cards': data['statistics']['Yellow Cards'],
            'red_cards': data['statistics']['Red Cards'],
            'shots_on_goal': data['statistics']['Shots on Goal'],
            'possession': data['statistics']['Ball Possession']
        }
```

#### 3. Integrar no treinamento:
```python
# Adicionar features extras
def prepare_advanced_features(match_id):
    basic_stats = get_from_football_data(match_id)
    advanced_stats = get_from_api_football(match_id)
    
    return {**basic_stats, **advanced_stats}
```

---

## 📊 Conclusão

| Dados | football-data.org (gratuito) | API-Football | Web Scraping |
|-------|------------------------------|--------------|--------------|
| **Resultado** | ✅ | ✅ | ✅ |
| **Placar** | ✅ | ✅ | ✅ |
| **Escanteios** | ❌ | ✅ | ✅ |
| **Cartões** | ❌ | ✅ | ✅ |
| **Chutes** | ❌ | ✅ | ✅ |
| **Posse** | ❌ | ✅ | ✅ |
| **Lineups** | ❌ | ✅ | ✅ |
| **Custo** | 🆓 | 🆓-💰 | 🆓 |
| **Legalidade** | ✅ | ✅ | ⚠️ |

**Recomendação:** Comece com football-data.org, adicione API-Football se precisar de mais dados.

---

**Criado em:** 30/10/2025  
**API Testada:** football-data.org v4 (tier gratuito)
