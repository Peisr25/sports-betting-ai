"""
Busca partidas agendadas disponíveis em TODAS as ligas/competições

Este script descobre quais ligas têm fixtures agendados acessíveis
no seu plano da API-Football (útil para planos free com restrições).

Uso:
    python find_available_fixtures.py
"""
from data.api_football_collector import APIFootballCollector
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import time
import json


def print_section(title):
    """Helper para printar seções"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def get_popular_leagues():
    """
    Retorna lista de ligas populares para testar

    Foca em ligas que normalmente têm jogos durante o ano todo
    """
    return [
        # Europa - Top 5
        {"id": 39, "name": "Premier League", "country": "England"},
        {"id": 140, "name": "La Liga", "country": "Spain"},
        {"id": 78, "name": "Bundesliga", "country": "Germany"},
        {"id": 135, "name": "Serie A", "country": "Italy"},
        {"id": 61, "name": "Ligue 1", "country": "France"},

        # Europa - Outras
        {"id": 94, "name": "Primeira Liga", "country": "Portugal"},
        {"id": 88, "name": "Eredivisie", "country": "Netherlands"},
        {"id": 144, "name": "Jupiler Pro League", "country": "Belgium"},
        {"id": 203, "name": "Super Lig", "country": "Turkey"},
        {"id": 235, "name": "Premier League", "country": "Russia"},

        # América do Sul
        {"id": 71, "name": "Brasileirão Série A", "country": "Brazil"},
        {"id": 72, "name": "Brasileirão Série B", "country": "Brazil"},
        {"id": 128, "name": "Liga Profesional", "country": "Argentina"},
        {"id": 239, "name": "Primera Division", "country": "Colombia"},
        {"id": 242, "name": "Primera Division", "country": "Chile"},

        # América do Norte
        {"id": 253, "name": "MLS", "country": "USA"},
        {"id": 262, "name": "Liga MX", "country": "Mexico"},

        # Ásia
        {"id": 307, "name": "Pro League", "country": "Saudi-Arabia"},
        {"id": 188, "name": "J1 League", "country": "Japan"},
        {"id": 292, "name": "K League 1", "country": "South-Korea"},

        # Competições Internacionais
        {"id": 2, "name": "UEFA Champions League", "country": "World"},
        {"id": 3, "name": "UEFA Europa League", "country": "World"},
        {"id": 848, "name": "UEFA Europa Conference League", "country": "World"},
        {"id": 9, "name": "Copa Libertadores", "country": "World"},
        {"id": 13, "name": "Copa Sudamericana", "country": "World"},

        # Copas Nacionais
        {"id": 48, "name": "FA Cup", "country": "England"},
        {"id": 143, "name": "Copa del Rey", "country": "Spain"},
        {"id": 137, "name": "Coppa Italia", "country": "Italy"},
        {"id": 66, "name": "Coupe de France", "country": "France"},
    ]


def find_available_fixtures(api_key: str, days_ahead: int = 14, max_leagues: int = None):
    """
    Busca fixtures agendados em múltiplas ligas

    Args:
        api_key: Chave da API-Football
        days_ahead: Quantos dias à frente buscar
        max_leagues: Limite de ligas para testar (None = todas)
    """
    print_section("BUSCANDO PARTIDAS AGENDADAS DISPONÍVEIS")

    collector = APIFootballCollector(api_key)

    # Datas de busca
    today = datetime.now()
    end_date = today + timedelta(days=days_ahead)

    print(f"\n📅 Período de busca:")
    print(f"   De: {today.strftime('%Y-%m-%d')}")
    print(f"   Até: {end_date.strftime('%Y-%m-%d')}")
    print(f"   Dias: {days_ahead}")

    # Ligas para testar
    leagues = get_popular_leagues()
    if max_leagues:
        leagues = leagues[:max_leagues]

    print(f"\n🔍 Testando {len(leagues)} ligas/competições...")

    # Resultados
    available_leagues = []
    restricted_leagues = []
    empty_leagues = []

    total_fixtures = 0

    for i, league in enumerate(leagues, 1):
        league_id = league["id"]
        league_name = league["name"]
        country = league["country"]

        print(f"\n[{i}/{len(leagues)}] 🏆 {league_name} ({country}) - ID: {league_id}")

        try:
            # Buscar fixtures agendados
            # Usa data range para evitar restrições
            params = {
                "league": league_id,
                "season": 2024,  # Temporada atual
                "from": today.strftime("%Y-%m-%d"),
                "to": end_date.strftime("%Y-%m-%d")
            }

            data = collector._make_request("fixtures", params)

            # Verificar erros
            errors = data.get("errors")
            if errors:
                if isinstance(errors, dict):
                    # Erro de restrição de plano
                    if "plan" in errors or "access" in str(errors).lower():
                        print(f"   ❌ Restrição de plano: {errors}")
                        restricted_leagues.append({
                            "league": league,
                            "error": errors
                        })
                        continue

            # Verificar fixtures
            fixtures = data.get("response", [])

            if not fixtures:
                print(f"   ℹ️  Sem jogos agendados neste período")
                empty_leagues.append(league)
            else:
                # Filtrar apenas jogos não iniciados
                scheduled = [f for f in fixtures if f.get("fixture", {}).get("status", {}).get("short") in ["NS", "TBD"]]

                if scheduled:
                    print(f"   ✅ {len(scheduled)} jogos agendados encontrados!")

                    # Mostra alguns exemplos
                    for j, fixture in enumerate(scheduled[:3], 1):
                        fix_data = fixture.get("fixture", {})
                        teams = fixture.get("teams", {})
                        home = teams.get("home", {}).get("name", "?")
                        away = teams.get("away", {}).get("name", "?")
                        date = fix_data.get("date", "")

                        # Parse date
                        try:
                            dt = datetime.fromisoformat(date.replace("Z", "+00:00"))
                            date_str = dt.strftime("%d/%m %H:%M")
                        except:
                            date_str = date[:16]

                        print(f"      {j}. {home} vs {away} - {date_str}")

                    if len(scheduled) > 3:
                        print(f"      ... e mais {len(scheduled) - 3} jogos")

                    available_leagues.append({
                        "league": league,
                        "fixtures": scheduled,
                        "count": len(scheduled)
                    })

                    total_fixtures += len(scheduled)
                else:
                    print(f"   ℹ️  {len(fixtures)} jogos, mas nenhum agendado (status NS/TBD)")
                    empty_leagues.append(league)

            # Rate limiting - aguarda para não estourar quota
            time.sleep(0.1)

        except Exception as e:
            print(f"   ❌ Erro: {e}")
            continue

    # Resumo
    print_section("RESUMO")

    print(f"\n📊 Estatísticas:")
    print(f"   Ligas testadas: {len(leagues)}")
    print(f"   ✅ Com jogos disponíveis: {len(available_leagues)}")
    print(f"   ❌ Com restrições: {len(restricted_leagues)}")
    print(f"   ℹ️  Sem jogos agendados: {len(empty_leagues)}")
    print(f"   📅 Total de fixtures encontrados: {total_fixtures}")

    # Ligas disponíveis
    if available_leagues:
        print(f"\n\n✅ LIGAS COM JOGOS DISPONÍVEIS ({len(available_leagues)}):")
        print("=" * 70)

        # Ordena por quantidade de jogos
        available_leagues.sort(key=lambda x: x["count"], reverse=True)

        for i, item in enumerate(available_leagues, 1):
            league = item["league"]
            count = item["count"]
            print(f"\n{i}. 🏆 {league['name']} ({league['country']})")
            print(f"   Liga ID: {league['id']}")
            print(f"   Jogos agendados: {count}")
            print(f"   Comando para coletar predições:")
            print(f"   python collect_predictions.py --league-id {league['id']} --days 14")

    # Ligas com restrição
    if restricted_leagues:
        print(f"\n\n❌ LIGAS COM RESTRIÇÕES ({len(restricted_leagues)}):")
        print("=" * 70)

        for i, item in enumerate(restricted_leagues, 1):
            league = item["league"]
            error = item["error"]
            print(f"\n{i}. {league['name']} ({league['country']}) - ID: {league['id']}")
            print(f"   Erro: {error}")

    # Salvar relatório
    report = {
        "timestamp": datetime.now().isoformat(),
        "period": {
            "from": today.strftime("%Y-%m-%d"),
            "to": end_date.strftime("%Y-%m-%d"),
            "days": days_ahead
        },
        "summary": {
            "leagues_tested": len(leagues),
            "available": len(available_leagues),
            "restricted": len(restricted_leagues),
            "empty": len(empty_leagues),
            "total_fixtures": total_fixtures
        },
        "available_leagues": [
            {
                "id": item["league"]["id"],
                "name": item["league"]["name"],
                "country": item["league"]["country"],
                "fixtures_count": item["count"]
            }
            for item in available_leagues
        ],
        "restricted_leagues": [
            {
                "id": item["league"]["id"],
                "name": item["league"]["name"],
                "country": item["league"]["country"],
                "error": str(item["error"])
            }
            for item in restricted_leagues
        ]
    }

    report_file = "available_fixtures_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n\n💾 Relatório salvo: {report_file}")

    # Sugestões
    if available_leagues:
        print_section("PRÓXIMOS PASSOS")

        print("\n🎯 Você pode coletar predições das ligas disponíveis:")
        print("\n1. Coletar de UMA liga específica:")
        top_league = available_leagues[0]["league"]
        print(f"   python collect_predictions.py --league-id {top_league['id']} --days 14")

        print("\n2. Coletar de TODAS as ligas disponíveis:")
        print("   Edite collect_predictions.py e adicione múltiplas ligas")

        print("\n3. Usar no treinamento:")
        print("   python train_xgboost_with_api.py")
        print("   (Automaticamente usará predições de todas as ligas)")

    else:
        print_section("⚠️  NENHUMA LIGA DISPONÍVEL")
        print("\nSeu plano free pode ter restrições de:")
        print("  - Datas (apenas X dias recentes/futuros)")
        print("  - Ligas específicas")
        print("  - Temporadas antigas")
        print("\nConsidere:")
        print("  1. Verificar documentação do seu plano")
        print("  2. Testar com datas diferentes")
        print("  3. Upgrade para plano pago se necessário")


def main():
    """Função principal"""
    print("\n" + "=" * 70)
    print(" " * 15 + "BUSCA DE FIXTURES DISPONÍVEIS")
    print("=" * 70)
    print("\nEste script testa múltiplas ligas para encontrar jogos agendados")
    print("acessíveis no seu plano da API-Football.")

    # Carrega API key
    load_dotenv()
    api_key = os.getenv("API_FOOTBALL_KEY")

    if not api_key:
        print("\n❌ API_FOOTBALL_KEY não encontrada!")
        print("\nConfigure no arquivo .env:")
        print("  API_FOOTBALL_KEY=your_key_here")
        return

    print(f"\n✓ API Key encontrada: {api_key[:10]}...")

    # Parâmetros
    print("\n⚙️  Configurações:")

    # Dias à frente
    days_str = input("\nQuantos dias à frente buscar? [14]: ").strip()
    days_ahead = int(days_str) if days_str else 14

    # Limite de ligas (para economizar quota)
    limit_str = input("Limitar número de ligas? (deixe vazio para todas) [Enter]: ").strip()
    max_leagues = int(limit_str) if limit_str else None

    print(f"\n📋 Resumo:")
    print(f"   Dias à frente: {days_ahead}")
    print(f"   Ligas a testar: {max_leagues if max_leagues else 'Todas (~30)'}")

    # Confirmação
    confirm = input("\nContinuar? [S/n]: ").strip().lower()
    if confirm == 'n':
        print("\n⚠️  Cancelado pelo usuário")
        return

    # Busca
    try:
        find_available_fixtures(api_key, days_ahead, max_leagues)

        print("\n" + "=" * 70)
        print(" " * 20 + "✅ BUSCA CONCLUÍDA!")
        print("=" * 70 + "\n")

    except KeyboardInterrupt:
        print("\n\n⚠️  Busca interrompida pelo usuário")
    except Exception as e:
        print(f"\n\n❌ Erro durante busca: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
