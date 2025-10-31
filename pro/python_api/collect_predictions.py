"""
Script de Coleta de Predições da API-Football

Coleta predições para partidas agendadas e salva no banco de dados.
As predições incluem:
- Percentuais de vitória/empate/derrota
- Over/Under recomendado
- Comparações estatísticas
- Forma dos times
- Análise H2H

Uso:
    # Por código de liga
    python collect_predictions.py BSA --season 2024 --days 7

    # Por ID de liga (descubra IDs com find_available_fixtures.py)
    python collect_predictions.py --league-id 39 --season 2024 --days 7

    # Buscar fixtures disponíveis primeiro
    python find_available_fixtures.py
"""
import sys
import os
import argparse
from datetime import datetime, timedelta
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.api_football_collector import APIFootballCollector
from data.database_v2 import Database


def collect_predictions_for_league(
    api_key: str,
    league_code: str = None,
    league_id: int = None,
    season: int = 2024,
    days_ahead: int = 7
):
    """
    Coleta predições para partidas agendadas de uma liga

    Args:
        api_key: API key da API-Football
        league_code: Código da liga (BSA, PL, etc) - Opcional se league_id fornecido
        league_id: ID da liga na API-Football - Opcional se league_code fornecido
        season: Temporada
        days_ahead: Quantos dias à frente buscar

    Returns:
        Dict com estatísticas da coleta
    """
    collector = APIFootballCollector(api_key)
    db = Database("database/betting_v2.db")

    # Determinar league_id
    if league_id:
        # Usa ID direto
        actual_league_id = league_id
        display_name = f"League ID {league_id}"
    elif league_code:
        # Mapeamento de códigos para IDs
        league_mapping = {
            "BSA": 71,
            "PL": 39,
            "PD": 140,
            "BL1": 78,
            "SA": 135,
            "FL1": 61,
            "CL": 2,
            "PPL": 94,
            "DED": 88,
        }

        actual_league_id = league_mapping.get(league_code)
        if not actual_league_id:
            print(f"❌ Liga {league_code} não encontrada no mapeamento")
            print("\nUse --league-id para especificar ID diretamente")
            print("Ou execute: python find_available_fixtures.py")
            return {}

        display_name = league_code
    else:
        print("❌ Especifique league_code ou league_id")
        return {}

    print(f"\n{'='*70}")
    print(f"COLETA DE PREDIÇÕES - {display_name}")
    print(f"{'='*70}")
    print(f"Liga ID: {actual_league_id}")
    print(f"Temporada: {season}")
    print(f"Período: Próximos {days_ahead} dias")
    print(f"{'='*70}\n")

    stats = {
        "fixtures_found": 0,
        "predictions_saved": 0,
        "errors": 0
    }

    try:
        # Buscar fixtures agendados
        print("📋 Buscando fixtures agendados...")

        fixtures = collector.get_fixtures(
            league_id=actual_league_id,
            season=season,
            status="NS"  # Not Started
        )

        if not fixtures:
            print(f"⚠️  Nenhum fixture agendado encontrado para {display_name}")
            return stats

        # Filtrar por data (próximos X dias)
        today = datetime.now()
        cutoff_date = today + timedelta(days=days_ahead)

        filtered_fixtures = []
        for fixture in fixtures:
            match_date_str = fixture["fixture"]["date"]
            match_date = datetime.fromisoformat(match_date_str.replace('Z', '+00:00'))

            if match_date <= cutoff_date:
                filtered_fixtures.append(fixture)

        stats["fixtures_found"] = len(filtered_fixtures)
        print(f"✓ Encontrados {len(filtered_fixtures)} fixtures nos próximos {days_ahead} dias\n")

        if not filtered_fixtures:
            return stats

        # Para cada fixture, buscar predição
        for i, fixture in enumerate(filtered_fixtures, 1):
            try:
                fixture_id = fixture["fixture"]["id"]
                home_team = fixture["teams"]["home"]["name"]
                away_team = fixture["teams"]["away"]["name"]
                match_date = fixture["fixture"]["date"]

                print(f"[{i}/{len(filtered_fixtures)}] {home_team} vs {away_team}")
                print(f"  Data: {match_date}")

                # Buscar predição
                params = {"fixture": fixture_id}
                data = collector._make_request("predictions", params)

                # Verificar erros
                errors = data.get("errors")
                if errors:
                    print(f"  ❌ Erro: {errors}")
                    stats["errors"] += 1

                    # Verificar se é erro de plano
                    if isinstance(errors, dict) and ("plan" in str(errors).lower() or "subscription" in str(errors).lower()):
                        print(f"\n⚠️  PLANO NÃO TEM ACESSO AO ENDPOINT /predictions")
                        print(f"   Interrompendo coleta...")
                        break

                    continue

                response = data.get("response", [])
                if not response:
                    print(f"  ⚠️  Sem predições disponíveis")
                    continue

                # Salvar predição
                prediction_data = response[0]
                saved = _save_prediction_to_db(db, fixture, prediction_data, display_name)

                if saved:
                    print(f"  ✓ Predição salva")
                    stats["predictions_saved"] += 1
                else:
                    print(f"  ⚠️  Predição não salva")

                # Rate limiting
                if i < len(filtered_fixtures):
                    time.sleep(1)  # 1s entre predições

            except Exception as e:
                print(f"  ❌ Erro ao processar: {e}")
                stats["errors"] += 1
                continue

        # Resumo
        print(f"\n{'='*70}")
        print("COLETA FINALIZADA")
        print(f"{'='*70}")
        print(f"Fixtures encontrados: {stats['fixtures_found']}")
        print(f"Predições salvas: {stats['predictions_saved']}")
        print(f"Erros: {stats['errors']}")
        print(f"{'='*70}\n")

    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()

    return stats


def _save_prediction_to_db(db: Database, fixture: dict, prediction_data: dict, league_code: str) -> bool:
    """
    Salva predição no banco de dados

    Args:
        db: Database object
        fixture: Dados do fixture
        prediction_data: Dados da predição
        league_code: Código da liga

    Returns:
        True se salvou com sucesso
    """
    try:
        # Verificar/criar match no banco
        match_data = {
            "match_id_apif": fixture["fixture"]["id"],
            "competition": league_code,
            "season": fixture["league"]["season"],
            "home_team": fixture["teams"]["home"]["name"],
            "away_team": fixture["teams"]["away"]["name"],
            "home_team_id_apif": fixture["teams"]["home"]["id"],
            "away_team_id_apif": fixture["teams"]["away"]["id"],
            "match_date": datetime.fromisoformat(fixture["fixture"]["date"].replace('Z', '+00:00')),
            "status": fixture["fixture"]["status"]["short"],
            "data_source": "api-football"
        }

        match_obj = db.save_match(match_data)

        # Extrair dados da predição
        predictions = prediction_data.get("predictions", {})
        percent = predictions.get("percent", {})
        comparison = prediction_data.get("comparison", {})

        # Preparar dados de predição
        pred_data = {
            "match_id": match_obj.id,
            "model_name": "api-football",
            "home_win_prob": float(percent.get("home", "0").replace("%", "")) / 100 if percent.get("home") else 0,
            "draw_prob": float(percent.get("draw", "0").replace("%", "")) / 100 if percent.get("draw") else 0,
            "away_win_prob": float(percent.get("away", "0").replace("%", "")) / 100 if percent.get("away") else 0,
            "confidence": predictions.get("advice", ""),
            "extra_predictions": {
                "under_over": predictions.get("under_over"),
                "goals_home": predictions.get("goals", {}).get("home"),
                "goals_away": predictions.get("goals", {}).get("away"),
                "winner": predictions.get("winner", {}).get("name"),
                "win_or_draw": predictions.get("win_or_draw"),
                "comparison": {
                    "form": comparison.get("form", {}),
                    "att": comparison.get("att", {}),
                    "def": comparison.get("def", {}),
                    "poisson": comparison.get("poisson_distribution", {}),
                    "h2h": comparison.get("h2h", {}),
                    "total": comparison.get("total", {})
                },
                "teams_data": prediction_data.get("teams", {})
            }
        }

        db.save_prediction(pred_data)
        return True

    except Exception as e:
        print(f"      Erro ao salvar: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Coleta predições da API-Football para partidas agendadas"
    )

    parser.add_argument(
        "league",
        nargs="?",
        help="Código da liga (BSA, PL, PD, BL1, SA, FL1, CL, PPL, DED) - Opcional se usar --league-id"
    )

    parser.add_argument(
        "--league-id",
        type=int,
        help="ID da liga na API-Football (ex: 39 para Premier League). Use find_available_fixtures.py para descobrir IDs"
    )

    parser.add_argument(
        "--season",
        type=int,
        default=2024,
        help="Temporada (ano)"
    )

    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Quantos dias à frente coletar (padrão: 7)"
    )

    parser.add_argument(
        "--apif-key",
        help="API key da API-Football v3"
    )

    args = parser.parse_args()

    # Validar parâmetros
    if not args.league and not args.league_id:
        parser.error("Especifique 'league' ou --league-id")

    # Obter API key
    api_key = args.apif_key or os.getenv("API_FOOTBALL_KEY")

    if not api_key:
        print("❌ API key da API-Football não configurada!")
        print("\nOpções:")
        print("1. Passe --apif-key SUA_KEY")
        print("2. Configure API_FOOTBALL_KEY no .env")
        sys.exit(1)

    # Executar coleta
    stats = collect_predictions_for_league(
        api_key=api_key,
        league_code=args.league,
        league_id=args.league_id,
        season=args.season,
        days_ahead=args.days
    )

    # Mensagem final
    if stats and stats["predictions_saved"] > 0:
        print("✅ Predições coletadas com sucesso!")
        print("\n💡 PRÓXIMO PASSO: Usar em ensemble com nossos modelos")
        print("   Ver: DUAL_API_GUIDE.md seção 'Usando Predições'")


if __name__ == "__main__":
    main()
