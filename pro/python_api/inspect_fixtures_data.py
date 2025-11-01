"""
Script para mostrar estrutura dos dados salvos
"""
import json

with open('live_and_upcoming_fixtures.json', encoding='utf-8') as f:
    data = json.load(f)

print('\n' + '='*70)
print('📊 ESTRUTURA DO ARQUIVO: live_and_upcoming_fixtures.json')
print('='*70)

print(f'\n├─ timestamp: {data["timestamp"]}')
print(f'├─ live_fixtures: {data["live_fixtures"]}')
print(f'├─ upcoming_fixtures: {data["upcoming_fixtures"]}')
print(f'├─ total_fixtures: {data["total_fixtures"]}')
print(f'├─ total_leagues: {data["total_leagues"]}')
print(f'├─ leagues: {len(data["leagues"])} ligas')
print(f'└─ all_fixtures: [{len(data["all_fixtures"])} partidas] ⭐ ARRAY PRINCIPAL\n')

print('='*70)
print('📋 EXEMPLO DE 1 PARTIDA (all_fixtures[0]):')
print('='*70)

fixture = data['all_fixtures'][0]

print(f'\n✅ DADOS ESSENCIAIS PARA O FLUXO:')
print(f'  fixture_id:     {fixture["fixture_id"]}')
print(f'  home_team:      {fixture["home_team"]}')
print(f'  home_team_id:   {fixture["home_team_id"]} ⭐ USAR PARA BUSCAR HISTÓRICO')
print(f'  away_team:      {fixture["away_team"]}')
print(f'  away_team_id:   {fixture["away_team_id"]} ⭐ USAR PARA BUSCAR HISTÓRICO')
print(f'  league_name:    {fixture["league_name"]}')
print(f'  league_id:      {fixture["league_id"]}')
print(f'  country:        {fixture["country"]}')
print(f'  status_short:   {fixture["status_short"]}')
print(f'  score:          {fixture["score"]}')
print(f'  date:           {fixture["date"]}')

print('\n' + '='*70)
print('🎯 ENDPOINT PARA BUSCAR HISTÓRICO DOS TIMES:')
print('='*70)

print(f'\nTime da Casa (historico):')
print(f'  GET /fixtures?team={fixture["home_team_id"]}&last=20')
print(f'  Retorna: Últimas 20 partidas do {fixture["home_team"]}')

print(f'\nTime Visitante (histórico):')
print(f'  GET /fixtures?team={fixture["away_team_id"]}&last=20')
print(f'  Retorna: Últimas 20 partidas do {fixture["away_team"]}')

print('\n' + '='*70)
print('📊 TODAS AS PARTIDAS:')
print('='*70)

print(f'\nTotal: {len(data["all_fixtures"])} partidas\n')

for i, fix in enumerate(data['all_fixtures'][:5], 1):
    status_icon = '🔴' if fix['status_short'] not in ['NS', 'TBD', 'PST'] else '🟢'
    print(f'{i}. {status_icon} {fix["home_team"]} vs {fix["away_team"]}')
    print(f'   IDs: {fix["home_team_id"]} vs {fix["away_team_id"]}')
    print(f'   Liga: {fix["league_name"]} ({fix["league_id"]})')
    print(f'   Status: {fix["status_short"]} | Score: {fix["score"]}')
    print()

if len(data['all_fixtures']) > 5:
    print(f'... e mais {len(data["all_fixtures"]) - 5} partidas')

print('\n' + '='*70)
print('💡 PRÓXIMA AÇÃO:')
print('='*70)

print('\nCriar collect_team_history_v2.py que:')
print('  1. Lê all_fixtures[]')
print('  2. Para cada partida, busca:')
print('     - GET /fixtures?team={home_team_id}&last=20')
print('     - GET /fixtures?team={away_team_id}&last=20')
print('  3. Salva histórico no banco de dados')

print('\nCusto: 2 requisições × ' + str(len(data['all_fixtures'])) + ' partidas = ' + str(len(data['all_fixtures']) * 2) + ' requisições')
print('Plano free: 100/dia ✅ VIÁVEL!' if len(data['all_fixtures']) * 2 <= 100 else 'Plano free: 100/dia ⚠️ EXCEDE!')

print('\n' + '='*70 + '\n')
