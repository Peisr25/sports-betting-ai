"""
Busca partidas agendadas por DATA (não por liga)

Versão mais rápida que busca diretamente por datas
sem precisar iterar por ligas.

Uso:
    python find_fixtures_by_date.py
"""
from data.api_football_collector import APIFootballCollector
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import json


def find_fixtures_by_date(api_key: str, date_str: str = None):
    """
    Busca fixtures por data específica

    Args:
        api_key: Chave da API-Football
        date_str: Data no formato YYYY-MM-DD (None = hoje)
    """
    collector = APIFootballCollector(api_key)

    # Define data
    if date_str:
        search_date = datetime.strptime(date_str, "%Y-%m-%d")
    else:
        search_date = datetime.now()

    date_formatted = search_date.strftime("%Y-%m-%d")

    print(f"\n📅 Buscando fixtures para: {date_formatted}")

    try:
        # Busca fixtures da data
        params = {"date": date_formatted}
        data = collector._make_request("fixtures", params)

        # Verifica erros
        errors = data.get("errors")
        if errors:
            print(f"\n❌ Erro na API:")
            print(f"   {errors}")

            if isinstance(errors, dict) and "plan" in errors:
                print(f"\n⚠️  RESTRIÇÃO DE PLANO DETECTADA")
                print(f"   Seu plano não tem acesso a esta data")
                return None

        # Processa fixtures
        fixtures = data.get("response", [])

        if not fixtures:
            print(f"\n❌ Nenhum fixture encontrado para {date_formatted}")
            return None

        print(f"\n✅ {len(fixtures)} fixtures encontrados!")

        # Agrupa por liga
        by_league = {}
        for fixture in fixtures:
            league_data = fixture.get("league", {})
            league_id = league_data.get("id")
            league_name = league_data.get("name")
            country = league_data.get("country")

            key = f"{league_id}_{league_name}"
            if key not in by_league:
                by_league[key] = {
                    "id": league_id,
                    "name": league_name,
                    "country": country,
                    "fixtures": []
                }

            by_league[key]["fixtures"].append(fixture)

        # Mostra por liga
        print(f"\n🏆 Ligas encontradas: {len(by_league)}")
        print("=" * 70)

        for key, league_info in sorted(by_league.items(), key=lambda x: len(x[1]["fixtures"]), reverse=True):
            league_fixtures = league_info["fixtures"]

            print(f"\n🏆 {league_info['name']} ({league_info['country']})")
            print(f"   Liga ID: {league_info['id']}")
            print(f"   Jogos: {len(league_fixtures)}")

            # Mostra primeiros 5 jogos
            for i, fixture in enumerate(league_fixtures[:5], 1):
                fix_data = fixture.get("fixture", {})
                teams = fixture.get("teams", {})
                status = fix_data.get("status", {}).get("short", "?")

                home = teams.get("home", {}).get("name", "?")
                away = teams.get("away", {}).get("name", "?")
                time = fix_data.get("date", "")

                # Parse time
                try:
                    dt = datetime.fromisoformat(time.replace("Z", "+00:00"))
                    time_str = dt.strftime("%H:%M")
                except:
                    time_str = time[11:16]

                # Status icon
                status_icon = "🟢" if status == "NS" else "🔴" if status == "LIVE" else "⚪"

                print(f"      {i}. {status_icon} {home} vs {away} - {time_str} ({status})")

            if len(league_fixtures) > 5:
                print(f"      ... e mais {len(league_fixtures) - 5} jogos")

        return by_league

    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return None


def find_fixtures_next_days(api_key: str, days: int = 7):
    """
    Busca fixtures dos próximos N dias

    Args:
        api_key: Chave da API-Football
        days: Número de dias à frente
    """
    print("\n" + "=" * 70)
    print(f"  BUSCANDO FIXTURES DOS PRÓXIMOS {days} DIAS")
    print("=" * 70)

    all_leagues = {}
    total_fixtures = 0
    accessible_dates = []
    restricted_dates = []

    today = datetime.now()

    for day_offset in range(days):
        search_date = today + timedelta(days=day_offset)
        date_str = search_date.strftime("%Y-%m-%d")
        day_name = search_date.strftime("%A")

        print(f"\n{'='*70}")
        print(f"📅 {day_name}, {search_date.strftime('%d/%m/%Y')} ({date_str})")
        print(f"{'='*70}")

        by_league = find_fixtures_by_date(api_key, date_str)

        if by_league is None:
            restricted_dates.append(date_str)
            print(f"   ⚠️  Data não acessível (restrição de plano)")
            continue

        if not by_league:
            print(f"   ℹ️  Sem jogos agendados")
            continue

        accessible_dates.append(date_str)

        # Conta fixtures
        day_total = sum(len(league["fixtures"]) for league in by_league.values())
        total_fixtures += day_total

        # Merge ligas
        for key, league_info in by_league.items():
            if key not in all_leagues:
                all_leagues[key] = {
                    "id": league_info["id"],
                    "name": league_info["name"],
                    "country": league_info["country"],
                    "fixtures_count": 0
                }
            all_leagues[key]["fixtures_count"] += len(league_info["fixtures"])

    # Resumo final
    print("\n" + "=" * 70)
    print("  RESUMO FINAL")
    print("=" * 70)

    print(f"\n📊 Estatísticas:")
    print(f"   Dias testados: {days}")
    print(f"   ✅ Datas acessíveis: {len(accessible_dates)}")
    print(f"   ❌ Datas restritas: {len(restricted_dates)}")
    print(f"   🏆 Ligas diferentes: {len(all_leagues)}")
    print(f"   📅 Total de fixtures: {total_fixtures}")

    if restricted_dates:
        print(f"\n❌ Datas com restrição:")
        for date in restricted_dates:
            print(f"   - {date}")

    if all_leagues:
        print(f"\n\n✅ TOP 10 LIGAS COM MAIS JOGOS:")
        print("=" * 70)

        # Ordena por número de fixtures
        sorted_leagues = sorted(all_leagues.items(), key=lambda x: x[1]["fixtures_count"], reverse=True)

        for i, (key, league_info) in enumerate(sorted_leagues[:10], 1):
            print(f"\n{i}. 🏆 {league_info['name']} ({league_info['country']})")
            print(f"   Liga ID: {league_info['id']}")
            print(f"   Total de jogos: {league_info['fixtures_count']}")

    # Salvar relatório
    report = {
        "timestamp": datetime.now().isoformat(),
        "period": {
            "days": days,
            "from": today.strftime("%Y-%m-%d"),
            "to": (today + timedelta(days=days-1)).strftime("%Y-%m-%d")
        },
        "summary": {
            "accessible_dates": len(accessible_dates),
            "restricted_dates": len(restricted_dates),
            "total_leagues": len(all_leagues),
            "total_fixtures": total_fixtures
        },
        "accessible_dates": accessible_dates,
        "restricted_dates": restricted_dates,
        "leagues": [
            {
                "id": info["id"],
                "name": info["name"],
                "country": info["country"],
                "fixtures_count": info["fixtures_count"]
            }
            for key, info in sorted(all_leagues.items(), key=lambda x: x[1]["fixtures_count"], reverse=True)
        ]
    }

    report_file = "fixtures_by_date_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n\n💾 Relatório salvo: {report_file}")

    # Recomendações
    if all_leagues:
        print("\n" + "=" * 70)
        print("  PRÓXIMOS PASSOS")
        print("=" * 70)

        print("\n🎯 Ligas recomendadas para coletar predições:")

        for i, (key, league_info) in enumerate(sorted_leagues[:5], 1):
            print(f"\n{i}. {league_info['name']} ({league_info['fixtures_count']} jogos)")
            print(f"   python collect_predictions.py --league-id {league_info['id']} --days {days}")


def main():
    """Função principal"""
    print("\n" + "=" * 70)
    print(" " * 15 + "BUSCA DE FIXTURES POR DATA")
    print("=" * 70)
    print("\nEste script busca fixtures agendados por data,")
    print("descobrindo automaticamente quais ligas têm jogos disponíveis.")

    # Carrega API key
    load_dotenv()
    api_key = os.getenv("API_FOOTBALL_KEY")

    if not api_key:
        print("\n❌ API_FOOTBALL_KEY não encontrada!")
        print("\nConfigure no arquivo .env:")
        print("  API_FOOTBALL_KEY=your_key_here")
        return

    print(f"\n✓ API Key encontrada: {api_key[:10]}...")

    # Opções
    print("\n⚙️  Opções:")
    print("  1. Buscar fixtures de UMA data específica")
    print("  2. Buscar fixtures dos PRÓXIMOS N dias")

    choice = input("\nEscolha [1/2]: ").strip()

    try:
        if choice == "1":
            # Data específica
            date_input = input("\nData (YYYY-MM-DD) ou Enter para hoje: ").strip()
            date_str = date_input if date_input else None

            find_fixtures_by_date(api_key, date_str)

        elif choice == "2":
            # Próximos dias
            days_str = input("\nQuantos dias à frente? [7]: ").strip()
            days = int(days_str) if days_str else 7

            find_fixtures_next_days(api_key, days)

        else:
            print("\n❌ Opção inválida")
            return

        print("\n" + "=" * 70)
        print(" " * 20 + "✅ BUSCA CONCLUÍDA!")
        print("=" * 70 + "\n")

    except KeyboardInterrupt:
        print("\n\n⚠️  Busca interrompida pelo usuário")
    except Exception as e:
        print(f"\n\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
