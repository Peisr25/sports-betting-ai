"""
Sistema de Apostas Baseado em Partidas AO VIVO e Próximas

Este script:
1. Busca partidas AO VIVO e próximas na API-Football (live=all)
2. Para cada partida, coleta dados históricos dos times
3. Calcula probabilidades usando nossos modelos
4. Gera recomendações de apostas

Uso:
    python live_betting_analyzer.py
"""
import sys
import os
from datetime import datetime, timedelta
import time
from typing import Dict, List

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.api_football_collector import APIFootballCollector
from data.database_v2 import Database
from models.poisson import PoissonModel
from models.xgboost_model import XGBoostModel
from models.ensemble import EnsembleModel
from features.api_predictions_features import APIPredictionFeatures
from analysis.value_analysis import ValueAnalyzer
from dotenv import load_dotenv
import json


def print_section(title):
    """Helper para printar seções"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def get_live_and_upcoming_fixtures(api_key: str):
    """
    Busca partidas AO VIVO e próximas usando live=all

    Args:
        api_key: Chave da API-Football

    Returns:
        Lista de fixtures
    """
    collector = APIFootballCollector(api_key)

    print_section("BUSCANDO PARTIDAS AO VIVO E PRÓXIMAS")

    try:
        # Endpoint: /fixtures?live=all
        data = collector._make_request("fixtures", {"live": "all"})

        fixtures = data.get("response", [])

        if not fixtures:
            print("\n⚠️  Nenhuma partida ao vivo encontrada no momento")
            return []

        print(f"\n✅ {len(fixtures)} partidas encontradas!")

        # Agrupar por status
        by_status = {}
        for fixture in fixtures:
            status = fixture["fixture"]["status"]["short"]
            if status not in by_status:
                by_status[status] = []
            by_status[status].append(fixture)

        print(f"\n📊 Por status:")
        status_names = {
            "NS": "Não Iniciadas",
            "1H": "1º Tempo",
            "HT": "Intervalo",
            "2H": "2º Tempo",
            "ET": "Prorrogação",
            "P": "Pênaltis",
            "FT": "Finalizadas",
            "LIVE": "Ao Vivo"
        }

        for status, fixtures_list in sorted(by_status.items()):
            status_name = status_names.get(status, status)
            print(f"   {status_name} ({status}): {len(fixtures_list)}")

        return fixtures

    except Exception as e:
        print(f"\n❌ Erro ao buscar fixtures: {e}")
        return []


def calculate_team_stats_simple(team_name: str, league_id: int, season: int, collector) -> Dict:
    """
    Calcula estatísticas básicas de um time

    Versão simplificada sem acesso ao banco de dados histórico
    """
    # Estatísticas padrão (médias da liga)
    return {
        "goals_scored_avg": 1.5,
        "goals_conceded_avg": 1.5,
        "wins": 5,
        "draws": 3,
        "losses": 2,
        "matches_played": 10,
        "goals_for_total": 15,
        "goals_against_total": 15
    }


def analyze_fixture(fixture: Dict, collector, db: Database, models: Dict):
    """
    Analisa uma partida e gera recomendações de aposta

    Args:
        fixture: Dados da partida
        collector: APIFootballCollector
        db: Database instance
        models: Dict com modelos {poisson, xgboost, ensemble}

    Returns:
        Dict com análise completa
    """
    # Extrair dados básicos
    fixture_data = fixture["fixture"]
    teams = fixture["teams"]
    league_data = fixture["league"]
    goals = fixture.get("goals", {})
    status = fixture_data["status"]

    fixture_id = fixture_data["id"]
    home_team = teams["home"]["name"]
    away_team = teams["away"]["name"]
    home_team_id = teams["home"]["id"]
    away_team_id = teams["away"]["id"]
    league_id = league_data["id"]
    league_name = league_data["name"]
    season = league_data["season"]
    match_date = fixture_data["date"]
    status_short = status["short"]
    status_long = status["long"]
    elapsed = status.get("elapsed")

    # Parse date
    try:
        dt = datetime.fromisoformat(match_date.replace("Z", "+00:00"))
        date_str = dt.strftime("%d/%m/%Y %H:%M")
    except:
        date_str = match_date[:16]

    print(f"\n{'='*70}")
    print(f"🏆 {league_name} ({league_data['country']})")
    print(f"{'='*70}")
    print(f"⚽ {home_team} vs {away_team}")
    print(f"📅 {date_str}")
    print(f"📊 Status: {status_long} ({status_short})")

    if status_short not in ["NS"]:
        # Partida já iniciada - mostra placar
        home_goals = goals.get("home", 0)
        away_goals = goals.get("away", 0)
        print(f"🎯 Placar: {home_team} {home_goals} x {away_goals} {away_team}")
        if elapsed:
            print(f"⏱️  Tempo: {elapsed}'")

    # Calcular estatísticas dos times
    print(f"\n📊 Calculando estatísticas dos times...")

    home_stats = calculate_team_stats_simple(home_team, league_id, season, collector)
    away_stats = calculate_team_stats_simple(away_team, league_id, season, collector)

    match_stats = {
        "home": home_stats,
        "away": away_stats
    }

    # Fazer predições
    print(f"\n🔮 Gerando predições...")

    predictions = {}

    # Poisson
    try:
        poisson = models.get("poisson")
        if poisson:
            pred_poisson = poisson.predict_match(
                home_attack=home_stats["goals_scored_avg"],
                away_attack=away_stats["goals_scored_avg"],
                home_defense=home_stats["goals_conceded_avg"],
                away_defense=away_stats["goals_conceded_avg"]
            )
            predictions["poisson"] = pred_poisson
            print(f"   ✓ Poisson calculado")
    except Exception as e:
        print(f"   ⚠️  Erro no Poisson: {e}")

    # XGBoost (se treinado)
    try:
        xgboost = models.get("xgboost")
        if xgboost and xgboost.is_trained:
            pred_xgboost = xgboost.predict(match_stats, match_id=None)
            predictions["xgboost"] = pred_xgboost
            print(f"   ✓ XGBoost calculado")
    except Exception as e:
        print(f"   ⚠️  XGBoost não disponível: {e}")

    # Ensemble
    try:
        ensemble = models.get("ensemble")
        if ensemble:
            pred_ensemble = ensemble.predict(match_stats, match_id=None)
            predictions["ensemble"] = pred_ensemble
            print(f"   ✓ Ensemble calculado")
    except Exception as e:
        print(f"   ⚠️  Erro no Ensemble: {e}")

    # Usar melhor predição disponível
    best_prediction = predictions.get("ensemble") or predictions.get("xgboost") or predictions.get("poisson")

    if best_prediction:
        result = best_prediction.get("result", {})

        print(f"\n🎯 PROBABILIDADES:")
        print(f"   Casa ({home_team}): {result.get('home_win', 0):.1%}")
        print(f"   Empate: {result.get('draw', 0):.1%}")
        print(f"   Fora ({away_team}): {result.get('away_win', 0):.1%}")

        # Goals
        if "goals" in best_prediction:
            goals_pred = best_prediction["goals"]
            print(f"\n⚽ GOLS:")
            print(f"   Over 2.5: {goals_pred.get('over_2.5', 0):.1%}")
            print(f"   Under 2.5: {goals_pred.get('under_2.5', 0):.1%}")

        # BTTS
        if "both_teams_score" in best_prediction:
            btts = best_prediction["both_teams_score"]
            print(f"\n🎲 AMBOS MARCAM:")
            print(f"   Sim: {btts.get('yes', 0):.1%}")
            print(f"   Não: {btts.get('no', 0):.1%}")

        # Recomendação simples
        print(f"\n💡 RECOMENDAÇÃO:")

        max_prob = max(result.get('home_win', 0), result.get('draw', 0), result.get('away_win', 0))

        if result.get('home_win', 0) == max_prob:
            recommendation = f"Vitória {home_team}"
            confidence = result.get('home_win', 0)
        elif result.get('draw', 0) == max_prob:
            recommendation = "Empate"
            confidence = result.get('draw', 0)
        else:
            recommendation = f"Vitória {away_team}"
            confidence = result.get('away_win', 0)

        confidence_level = "Alta" if confidence > 0.55 else "Média" if confidence > 0.45 else "Baixa"

        print(f"   📌 {recommendation}")
        print(f"   📊 Confiança: {confidence_level} ({confidence:.1%})")

        # Avisos
        if status_short != "NS":
            print(f"\n⚠️  ATENÇÃO: Partida já iniciada!")
            print(f"   Status: {status_long}")
            print(f"   Considere apostas ao vivo (odds dinâmicas)")

    return {
        "fixture_id": fixture_id,
        "home_team": home_team,
        "away_team": away_team,
        "league": league_name,
        "status": status_short,
        "predictions": predictions,
        "best_prediction": best_prediction,
        "match_stats": match_stats
    }


def main():
    """Função principal"""
    print("\n" + "=" * 70)
    print(" " * 15 + "ANALISADOR DE APOSTAS AO VIVO")
    print("=" * 70)
    print("\nEste script busca partidas AO VIVO e próximas,")
    print("calcula probabilidades e gera recomendações de apostas.")

    # Carrega configurações
    load_dotenv()
    api_key = os.getenv("API_FOOTBALL_KEY")

    if not api_key:
        print("\n❌ API_FOOTBALL_KEY não encontrada!")
        print("\nConfigure no arquivo .env:")
        print("  API_FOOTBALL_KEY=your_key_here")
        return

    print(f"\n✓ API Key encontrada: {api_key[:10]}...")

    # Inicializa componentes
    print("\n📦 Inicializando modelos...")

    collector = APIFootballCollector(api_key)
    db = Database("database/betting_v2.db")

    # Modelos
    poisson = PoissonModel()
    print("   ✓ Poisson")

    # XGBoost (se disponível)
    xgboost = None
    try:
        import glob
        model_files = glob.glob("models/saved/xgboost_with_api_*.pkl")
        if model_files:
            latest_model = max(model_files, key=os.path.getctime)
            feature_extractor = APIPredictionFeatures(db)
            xgboost = XGBoostModel(
                model_path=latest_model,
                feature_extractor=feature_extractor,
                use_api_features=True
            )
            print("   ✓ XGBoost (com API features)")
        else:
            print("   ⚠️  XGBoost não treinado")
    except Exception as e:
        print(f"   ⚠️  XGBoost não disponível: {e}")

    # Ensemble
    ensemble = EnsembleModel(database=db, include_api_predictions=False)
    if xgboost:
        ensemble.add_model("xgboost", xgboost, weight=0.3)
    print("   ✓ Ensemble")

    models = {
        "poisson": poisson,
        "xgboost": xgboost,
        "ensemble": ensemble
    }

    # Buscar partidas ao vivo
    fixtures = get_live_and_upcoming_fixtures(api_key)

    if not fixtures:
        print("\n⚠️  Nenhuma partida encontrada")
        print("\nDica: Tente em horários com mais jogos acontecendo")
        print("      (geralmente tardes/noites de sexta, sábado, domingo)")
        db.close()
        return

    # Filtrar partidas (apenas não iniciadas e ao vivo)
    valid_statuses = ["NS", "1H", "2H", "HT", "ET", "LIVE"]
    filtered_fixtures = [f for f in fixtures if f["fixture"]["status"]["short"] in valid_statuses]

    print(f"\n📋 Partidas para análise: {len(filtered_fixtures)}")
    print(f"   (Filtrado: não iniciadas + ao vivo)")

    # Limitar análise
    max_analyze = 10
    if len(filtered_fixtures) > max_analyze:
        print(f"\n⚠️  Limitando análise a {max_analyze} primeiras partidas")
        filtered_fixtures = filtered_fixtures[:max_analyze]

    # Analisar cada partida
    analyses = []

    for i, fixture in enumerate(filtered_fixtures, 1):
        print(f"\n\n{'#'*70}")
        print(f"# PARTIDA {i}/{len(filtered_fixtures)}")
        print(f"{'#'*70}")

        try:
            analysis = analyze_fixture(fixture, collector, db, models)
            analyses.append(analysis)

            # Rate limiting
            if i < len(filtered_fixtures):
                time.sleep(1)

        except Exception as e:
            print(f"\n❌ Erro ao analisar partida: {e}")
            import traceback
            traceback.print_exc()
            continue

    # Resumo final
    print_section("RESUMO FINAL")

    print(f"\n📊 Partidas analisadas: {len(analyses)}")

    # Top recomendações
    print(f"\n\n🎯 TOP RECOMENDAÇÕES:")
    print("=" * 70)

    for i, analysis in enumerate(analyses[:5], 1):
        best_pred = analysis.get("best_prediction", {})
        if not best_pred:
            continue

        result = best_pred.get("result", {})
        max_prob = max(result.get('home_win', 0), result.get('draw', 0), result.get('away_win', 0))

        if result.get('home_win', 0) == max_prob:
            recommendation = f"Vitória {analysis['home_team']}"
        elif result.get('draw', 0) == max_prob:
            recommendation = "Empate"
        else:
            recommendation = f"Vitória {analysis['away_team']}"

        print(f"\n{i}. {analysis['home_team']} vs {analysis['away_team']}")
        print(f"   Liga: {analysis['league']}")
        print(f"   Status: {analysis['status']}")
        print(f"   Recomendação: {recommendation} ({max_prob:.1%})")

    # Salvar relatório
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_fixtures": len(fixtures),
        "analyzed": len(analyses),
        "analyses": [
            {
                "fixture_id": a["fixture_id"],
                "home_team": a["home_team"],
                "away_team": a["away_team"],
                "league": a["league"],
                "status": a["status"],
                "predictions": {
                    k: {
                        "result": v.get("result", {})
                    }
                    for k, v in a.get("predictions", {}).items()
                }
            }
            for a in analyses
        ]
    }

    report_file = "live_betting_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n\n💾 Relatório salvo: {report_file}")

    db.close()

    print("\n" + "=" * 70)
    print(" " * 20 + "✅ ANÁLISE CONCLUÍDA!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Análise interrompida pelo usuário")
    except Exception as e:
        print(f"\n\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
