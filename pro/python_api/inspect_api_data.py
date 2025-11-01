"""
Script para inspecionar TODOS os dados que a API retorna para uma partida
Verifica se há informações de escanteios, cartões, faltas, chutes, etc.
"""
import os
import sys
import json
from pprint import pprint

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.collector import FootballDataCollector

# API key
api_key = "b00e83b0962741e4a703a7dbe7b2f17f"

print("\n" + "="*70)
print("🔍 INSPEÇÃO COMPLETA DOS DADOS DA API")
print("="*70)

# Criar coletor
collector = FootballDataCollector(api_key)

# Buscar uma partida finalizada recente do Brasileirão
print("\n📋 Buscando partida finalizada recente do Brasileirão...")

try:
    matches = collector.get_matches(
        competition_code="BSA",
        status="FINISHED",
    )
    
    if not matches:
        print("❌ Nenhuma partida encontrada!")
        exit(1)
    
    # Pegar a primeira partida
    match = matches[0]
    
    print(f"\n✅ Partida encontrada:")
    home = match.get('homeTeam', {}).get('name', '?')
    away = match.get('awayTeam', {}).get('name', '?')
    date = match.get('utcDate', '?')
    
    score = match.get('score', {})
    home_score = score.get('fullTime', {}).get('home', '-')
    away_score = score.get('fullTime', {}).get('away', '-')
    
    print(f"   {home} {home_score} x {away_score} {away}")
    print(f"   Data: {date}")
    
    # Mostrar TODOS os campos disponíveis
    print("\n" + "="*70)
    print("📊 ESTRUTURA COMPLETA DOS DADOS")
    print("="*70)
    
    print("\n🔑 CAMPOS DE PRIMEIRO NÍVEL:")
    print("-" * 70)
    for key in match.keys():
        value = match[key]
        value_type = type(value).__name__
        
        if isinstance(value, dict):
            print(f"  {key}: {value_type} (objeto)")
        elif isinstance(value, list):
            print(f"  {key}: {value_type} ({len(value)} itens)")
        else:
            print(f"  {key}: {value_type} = {value}")
    
    # Detalhar campos importantes
    print("\n" + "="*70)
    print("📝 DETALHAMENTO DOS CAMPOS")
    print("="*70)
    
    # 1. Score (placar)
    if 'score' in match:
        print("\n1️⃣ SCORE (Placar):")
        print("-" * 70)
        score = match['score']
        print(json.dumps(score, indent=2, ensure_ascii=False))
    
    # 2. Odds (se disponível)
    if 'odds' in match:
        print("\n2️⃣ ODDS (Cotações):")
        print("-" * 70)
        odds = match['odds']
        print(json.dumps(odds, indent=2, ensure_ascii=False))
    else:
        print("\n2️⃣ ODDS: ❌ Não disponível no tier gratuito")
    
    # 3. Referees (árbitros)
    if 'referees' in match:
        print("\n3️⃣ REFEREES (Árbitros):")
        print("-" * 70)
        referees = match['referees']
        if referees:
            for ref in referees:
                print(f"   - {ref.get('name', '?')} ({ref.get('type', '?')})")
        else:
            print("   ❌ Sem dados de árbitros")
    
    # 4. Head2Head (confronto direto) - se disponível
    if 'head2head' in match:
        print("\n4️⃣ HEAD2HEAD:")
        print("-" * 70)
        h2h = match['head2head']
        print(json.dumps(h2h, indent=2, ensure_ascii=False))
    
    # Verificar campos de estatísticas detalhadas
    print("\n" + "="*70)
    print("⚽ ESTATÍSTICAS DETALHADAS")
    print("="*70)
    
    stats_fields = [
        'corners', 'cornerKicks', 'escanteios',
        'fouls', 'faltas', 'faults',
        'yellowCards', 'cartõesAmarelos', 'cartoes',
        'redCards', 'cartõesVermelhos',
        'shots', 'chutes',
        'shotsOnTarget', 'chutesNoGol',
        'possession', 'posse', 'possessao',
        'passes', 'passes',
        'offsides', 'impedimentos',
        'saves', 'defesas'
    ]
    
    found_stats = []
    for field in stats_fields:
        if field in match:
            found_stats.append(field)
            print(f"   ✅ {field}: {match[field]}")
    
    if not found_stats:
        print("\n   ❌ NENHUMA estatística detalhada encontrada!")
        print("   ℹ️  A API gratuita retorna apenas:")
        print("      - Placar final")
        print("      - Placar do intervalo")
        print("      - Placar prorrogação (se houver)")
        print("      - Placar penaltis (se houver)")
    
    # Mostrar JSON completo
    print("\n" + "="*70)
    print("📄 JSON COMPLETO DA PARTIDA")
    print("="*70)
    print(json.dumps(match, indent=2, ensure_ascii=False))
    
    # Resumo
    print("\n" + "="*70)
    print("📋 RESUMO - O QUE A API FORNECE")
    print("="*70)
    
    print("\n✅ DADOS DISPONÍVEIS:")
    print("   • ID da partida")
    print("   • Data/hora (UTC)")
    print("   • Times (nome, ID, escudo)")
    print("   • Competição")
    print("   • Status (SCHEDULED, LIVE, FINISHED, etc)")
    print("   • Placar final")
    print("   • Placar do intervalo")
    print("   • Placar prorrogação (se houver)")
    print("   • Árbitros (às vezes)")
    print("   • Estádio (venue)")
    
    print("\n❌ DADOS NÃO DISPONÍVEIS (tier gratuito):")
    print("   • Escanteios (corners)")
    print("   • Faltas (fouls)")
    print("   • Cartões amarelos/vermelhos")
    print("   • Chutes (shots)")
    print("   • Chutes no gol (shots on target)")
    print("   • Posse de bola (possession)")
    print("   • Passes")
    print("   • Impedimentos (offsides)")
    print("   • Defesas do goleiro (saves)")
    print("   • Cotações/odds")
    
    print("\n💡 COMO OBTER ESTATÍSTICAS DETALHADAS:")
    print("   1. Upgrade para tier pago da football-data.org")
    print("   2. Usar API alternativa (ex: API-Football, SportMonks)")
    print("   3. Web scraping de sites de estatísticas")
    
    print("\n" + "="*70 + "\n")
    
except Exception as e:
    print(f"\n❌ Erro: {e}")
    import traceback
    traceback.print_exc()
