# 🔍 Guia: Descobrir Fixtures Disponíveis

## 📋 Problema

Planos **free** da API-Football têm **restrições de acesso** a datas e ligas específicas. O Brasileirão Série A (BSA) pode estar restrito, mas **outras ligas podem estar disponíveis**!

## 🎯 Solução

Use os scripts de descoberta para encontrar **automaticamente** quais ligas têm fixtures agendados acessíveis no seu plano.

---

## 🚀 Opção 1: Busca por Liga (Recomendado)

### Script: `find_available_fixtures.py`

Testa **30+ ligas populares** para descobrir quais têm jogos agendados disponíveis.

### Uso:

```bash
cd pro/python_api
python find_available_fixtures.py
```

### Passo a Passo:

```
Quantos dias à frente buscar? [14]: 7 ← Enter
Limitar número de ligas? [Enter]: ← Enter (testa todas)
Continuar? [S/n]: S ← Enter
```

### Saída Esperada:

```
=======================================================================
  BUSCANDO PARTIDAS AGENDADAS DISPONÍVEIS
=======================================================================

📅 Período de busca:
   De: 2024-10-31
   Até: 2024-11-07
   Dias: 7

🔍 Testando 30 ligas/competições...

[1/30] 🏆 Premier League (England) - ID: 39
   ✅ 12 jogos agendados encontrados!
      1. Arsenal vs Chelsea - 01/11 15:00
      2. Man City vs Liverpool - 02/11 17:30
      3. Man Utd vs Tottenham - 03/11 14:00
      ... e mais 9 jogos

[2/30] 🏆 La Liga (Spain) - ID: 140
   ✅ 10 jogos agendados encontrados!
      ...

[3/30] 🏆 Brasileirão Série A (Brazil) - ID: 71
   ❌ Restrição de plano: Free plans do not have access...

...

=======================================================================
  RESUMO
=======================================================================

📊 Estatísticas:
   Ligas testadas: 30
   ✅ Com jogos disponíveis: 8
   ❌ Com restrições: 5
   ℹ️  Sem jogos agendados: 17
   📅 Total de fixtures encontrados: 67

✅ LIGAS COM JOGOS DISPONÍVEIS (8):

1. 🏆 Premier League (England)
   Liga ID: 39
   Jogos agendados: 12
   Comando para coletar predições:
   python collect_predictions.py --league-id 39 --days 7

2. 🏆 La Liga (Spain)
   Liga ID: 140
   Jogos agendados: 10
   Comando para coletar predições:
   python collect_predictions.py --league-id 140 --days 7

...

💾 Relatório salvo: available_fixtures_report.json
```

### Próximos Passos:

Copie o comando sugerido e execute:

```bash
python collect_predictions.py --league-id 39 --days 7
```

---

## 📅 Opção 2: Busca por Data (Mais Rápida)

### Script: `find_fixtures_by_date.py`

Busca fixtures **diretamente por data**, sem iterar por ligas.

### Uso:

```bash
cd pro/python_api
python find_fixtures_by_date.py
```

### Opções:

```
⚙️  Opções:
  1. Buscar fixtures de UMA data específica
  2. Buscar fixtures dos PRÓXIMOS N dias

Escolha [1/2]: 2 ← Enter

Quantos dias à frente? [7]: 7 ← Enter
```

### Saída Esperada:

```
=======================================================================
  BUSCANDO FIXTURES DOS PRÓXIMOS 7 DIAS
=======================================================================

=======================================================================
📅 Thursday, 31/10/2024 (2024-10-31)
=======================================================================

📅 Buscando fixtures para: 2024-10-31

✅ 45 fixtures encontrados!

🏆 Ligas encontradas: 12
=======================================================================

🏆 Premier League (England)
   Liga ID: 39
   Jogos: 4
      1. 🟢 Arsenal vs Chelsea - 20:00 (NS)
      2. 🟢 Man City vs Liverpool - 17:30 (NS)
      ...

🏆 La Liga (Spain)
   Liga ID: 140
   Jogos: 3
      ...

...

=======================================================================
  RESUMO FINAL
=======================================================================

📊 Estatísticas:
   Dias testados: 7
   ✅ Datas acessíveis: 7
   ❌ Datas restritas: 0
   🏆 Ligas diferentes: 15
   📅 Total de fixtures: 89

✅ TOP 10 LIGAS COM MAIS JOGOS:

1. 🏆 Premier League (England)
   Liga ID: 39
   Total de jogos: 12

2. 🏆 La Liga (Spain)
   Liga ID: 140
   Total de jogos: 10

...

💾 Relatório salvo: fixtures_by_date_report.json
```

---

## 📊 Comparação

| Característica | find_available_fixtures.py | find_fixtures_by_date.py |
|---|---|---|
| **Método** | Itera por ligas | Busca por data |
| **Velocidade** | Mais lento (~30 requisições) | Mais rápido (~7 requisições) |
| **Detalhes** | Mostra fixtures de cada liga | Agrupa por liga automaticamente |
| **Melhor para** | Descobrir ligas específicas | Visão geral rápida |
| **Relatório** | available_fixtures_report.json | fixtures_by_date_report.json |

---

## 🎯 Workflow Completo

### 1. Descobrir Fixtures Disponíveis

```bash
# Opção A: Por liga (mais detalhado)
python find_available_fixtures.py

# Opção B: Por data (mais rápido)
python find_fixtures_by_date.py
```

### 2. Revisar Relatório

```bash
# Ver ligas disponíveis
cat available_fixtures_report.json | jq '.available_leagues'

# Ou
cat fixtures_by_date_report.json | jq '.leagues'
```

### 3. Coletar Predições

```bash
# Use o ID da liga descoberta
python collect_predictions.py --league-id 39 --days 7
```

### 4. Treinar Modelo com Novas Predições

```bash
python train_xgboost_with_api.py
```

### 5. Usar na API

```bash
python app.py
```

---

## 💡 Dicas

### 1. **Economize Quota**

Planos free têm **100 req/dia**. Limite a busca:

```bash
# Limitar a 10 ligas
python find_available_fixtures.py
> Limitar número de ligas? 10
```

### 2. **Teste Diferentes Períodos**

```bash
# Próximos 3 dias (economiza quota)
python find_fixtures_by_date.py
> Escolha [1/2]: 2
> Quantos dias à frente? 3

# Próximas 2 semanas
> Quantos dias à frente? 14
```

### 3. **Combine Múltiplas Ligas**

Se encontrar várias ligas disponíveis, colete de todas:

```bash
# Premier League
python collect_predictions.py --league-id 39 --days 7

# La Liga
python collect_predictions.py --league-id 140 --days 7

# Bundesliga
python collect_predictions.py --league-id 78 --days 7
```

### 4. **Automatize**

Crie um script bash para coletar de todas as ligas disponíveis:

```bash
#!/bin/bash
# collect_all.sh

DAYS=7

# IDs descobertos pelos scripts de busca
LEAGUES=(39 140 78 135 61)

for LEAGUE_ID in "${LEAGUES[@]}"; do
    echo "Coletando liga $LEAGUE_ID..."
    python collect_predictions.py --league-id $LEAGUE_ID --days $DAYS
    sleep 5  # Rate limiting
done

echo "✅ Coleta completa!"
```

---

## 🔧 Troubleshooting

### Erro: "Free plans do not have access"

**Causa**: Seu plano não tem acesso a essa data/liga

**Solução**:
- Teste outras ligas com `find_available_fixtures.py`
- Teste datas diferentes
- Considere upgrade de plano

### Erro: "Nenhum fixture encontrado"

**Causa**: Não há jogos agendados no período

**Solução**:
- Aumente o período: `--days 14`
- Teste outras ligas
- Verifique calendário das ligas

### Erro: "API key não configurada"

**Solução**:
```bash
# Configure no .env
echo "API_FOOTBALL_KEY=sua_key_aqui" >> pro/.env

# Ou passe diretamente
python find_available_fixtures.py --apif-key SUA_KEY
```

---

## 📚 Referências

- **Ligas Testadas**: Ver código de `find_available_fixtures.py`
- **IDs de Ligas**: https://www.api-football.com/documentation-v3#tag/Leagues
- **Planos da API**: https://www.api-football.com/pricing

---

## 🎉 Resultado

Agora você pode descobrir **automaticamente** quais ligas estão acessíveis no seu plano free e coletar predições de **qualquer liga**, não apenas BSA!

**Exemplo real:**

Se BSA está restrito mas Premier League está disponível:
1. ✅ Descubra com `find_available_fixtures.py`
2. ✅ Colete 50+ predições da PL com `--league-id 39`
3. ✅ Treine modelo enriquecido
4. ✅ Use para fazer apostas!

**Happy collecting!** 🚀
