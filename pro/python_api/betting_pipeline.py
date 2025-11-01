"""
PIPELINE COMPLETO DE ANÁLISE DE APOSTAS
========================================

Este script implementa o fluxo completo:

1. Busca partidas AO VIVO e próximas
2. Para cada partida:
   - Busca predições da API-Football
   - Busca H2H (todos os confrontos dos últimos 2 anos)
   - Busca últimas 10 partidas de cada time (do último ano)
   - Salva TUDO no banco (evitando duplicatas)
3. Processa com modelos (Poisson + XGBoost + Ensemble)
4. Gera output final JSON com todas apostas possíveis

IMPORTANTE - FREE TIER:
- Não suporta parâmetro 'last' nos endpoints
- Solução: Usa 'from/to' com ranges de data
- H2H: Últimos 2 anos (completo)
- Team history: Último ano (limitado manualmente a 10)

Uso:
    python betting_pipeline.py
"""
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.api_football_collector import APIFootballCollector
from data.database_v2 import Database, Match, Prediction
from features.api_predictions_features import APIPredictionFeatures
from models.poisson import PoissonModel
from models.xgboost_model import XGBoostModel
from models.ensemble import EnsembleModel
from analysis.value_analysis import ValueAnalyzer
from dotenv import load_dotenv


class BettingPipeline:
    """Pipeline completo de análise de apostas"""

    def __init__(self, api_key: str, db_path: str = "database/betting_v2.db"):
        """
        Inicializa o pipeline

        Args:
            api_key: Chave da API-Football
            db_path: Caminho do banco de dados
        """
        self.api_key = api_key
        self.collector = APIFootballCollector(api_key)
        self.db = Database(db_path)
        self.feature_extractor = APIPredictionFeatures(self.db)

        # Inicializa modelos
        self.poisson = PoissonModel()

        # XGBoost (se disponível)
        self.xgboost = None
        try:
            import glob
            model_files = glob.glob("models/saved/xgboost_with_api_*.pkl")
            if model_files:
                latest_model = max(model_files, key=os.path.getctime)
                self.xgboost = XGBoostModel(
                    model_path=latest_model,
                    feature_extractor=self.feature_extractor,
                    use_api_features=True
                )
        except:
            pass

        # Ensemble
        self.ensemble = EnsembleModel(
            database=self.db,
            include_api_predictions=True
        )
        if self.xgboost and self.xgboost.is_trained:
            self.ensemble.add_model("xgboost", self.xgboost, weight=0.3)

        # Value analyzer
        self.value_analyzer = ValueAnalyzer()

        # Stats
        self.stats = {
            "fixtures_found": 0,
            "fixtures_processed": 0,
            "predictions_fetched": 0,
            "h2h_fetched": 0,
            "team_history_fetched": 0,
            "matches_saved": 0,
            "predictions_saved": 0,
            "errors": 0
        }

    def print_section(self, title: str):
        """Imprime seção formatada"""
        print("\n" + "=" * 70)
        print(f"  {title}")
        print("=" * 70)

    def step1_get_live_fixtures(self) -> List[Dict]:
        """
        STEP 1: Busca partidas AO VIVO e próximas

        Returns:
            Lista de fixtures
        """
        self.print_section("STEP 1: BUSCANDO PARTIDAS AO VIVO E PRÓXIMAS")

        try:
            # Endpoint: /fixtures?live=all
            data = self.collector._make_request("fixtures", {"live": "all"})
            fixtures = data.get("response", [])

            self.stats["fixtures_found"] = len(fixtures)

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
                "FT": "Finalizadas"
            }

            for status, fixtures_list in sorted(by_status.items()):
                status_name = status_names.get(status, status)
                print(f"   {status_name} ({status}): {len(fixtures_list)}")

            # Filtrar apenas partidas relevantes (NS, 1H, HT, 2H)
            valid_statuses = ["NS", "1H", "HT", "2H"]
            filtered = [f for f in fixtures if f["fixture"]["status"]["short"] in valid_statuses]

            print(f"\n✓ {len(filtered)} partidas selecionadas para análise")

            return filtered

        except Exception as e:
            print(f"\n❌ Erro ao buscar fixtures: {e}")
            self.stats["errors"] += 1
            return []

    def step2_get_api_predictions(self, fixture: Dict) -> Optional[Dict]:
        """
        STEP 2: Busca predições da API-Football para uma partida

        Args:
            fixture: Dados da partida

        Returns:
            Predições da API ou None
        """
        fixture_id = fixture["fixture"]["id"]

        try:
            params = {"fixture": fixture_id}
            data = self.collector._make_request("predictions", params)

            # Verificar erros
            errors = data.get("errors")
            if errors:
                if isinstance(errors, dict) and "plan" in str(errors).lower():
                    print(f"      ⚠️  Predições não disponíveis (plano free)")
                    return None

            response = data.get("response", [])
            if response:
                self.stats["predictions_fetched"] += 1
                print(f"      ✓ Predições da API obtidas")
                return response[0]

        except Exception as e:
            print(f"      ⚠️  Erro ao buscar predições: {e}")

        return None

    def step3_get_h2h(self, home_team_id: int, away_team_id: int) -> List[Dict]:
        """
        STEP 3: Busca H2H (últimos confrontos diretos)

        IMPORTANTE: Free tier não suporta parâmetro 'last'
        Solução: Usar 'from/to' com range de 2 anos

        Args:
            home_team_id: ID do time da casa
            away_team_id: ID do time visitante

        Returns:
            Lista de confrontos H2H (últimos 2 anos)
        """
        try:
            # Últimos 2 anos de confrontos (free tier compatible)
            today = datetime.now()
            from_date = (today - timedelta(days=730)).strftime("%Y-%m-%d")
            to_date = today.strftime("%Y-%m-%d")

            params = {
                "h2h": f"{home_team_id}-{away_team_id}",
                "from": from_date,  # ✅ Free tier compatible
                "to": to_date       # ✅ Free tier compatible
            }
            data = self.collector._make_request("fixtures/headtohead", params)

            h2h = data.get("response", [])

            if h2h:
                self.stats["h2h_fetched"] += 1
                print(f"      ✓ {len(h2h)} confrontos H2H obtidos (últimos 2 anos)")

            return h2h

        except Exception as e:
            print(f"      ⚠️  Erro ao buscar H2H: {e}")
            self.stats["errors"] += 1
            return []

    def step4_get_team_last_matches(self, team_id: int, limit: int = 10) -> List[Dict]:
        """
        STEP 4: Busca últimas partidas de um time

        IMPORTANTE: Free tier não suporta parâmetro 'last'
        Solução: Usar 'from/to' com range de 1 ano e limitar manualmente

        Args:
            team_id: ID do time
            limit: Número de partidas a retornar (limitação manual)

        Returns:
            Lista de partidas (últimas N do último ano)
        """
        try:
            # Último ano de partidas (free tier compatible)
            today = datetime.now()
            from_date = (today - timedelta(days=365)).strftime("%Y-%m-%d")
            to_date = today.strftime("%Y-%m-%d")

            params = {
                "team": team_id,
                "from": from_date,  # ✅ Free tier compatible
                "to": to_date,      # ✅ Free tier compatible
                "status": "FT"      # Finalizadas
            }
            data = self.collector._make_request("fixtures", params)

            matches = data.get("response", [])

            if matches:
                # Limitar manualmente às últimas N partidas
                matches = matches[-limit:] if len(matches) > limit else matches

                self.stats["team_history_fetched"] += 1
                print(f"      ✓ {len(matches)} partidas históricas obtidas (último ano)")

            return matches

        except Exception as e:
            print(f"      ⚠️  Erro ao buscar histórico: {e}")
            self.stats["errors"] += 1
            return []

    def step5_save_to_database(self, fixture: Dict, api_prediction: Optional[Dict] = None) -> Optional[int]:
        """
        STEP 5: Salva dados no banco (evitando duplicatas)

        Args:
            fixture: Dados da partida
            api_prediction: Predições da API (opcional)

        Returns:
            ID da partida no banco ou None
        """
        try:
            fixture_data = fixture["fixture"]
            teams = fixture["teams"]
            league = fixture["league"]

            # Verificar se partida já existe
            existing = self.db.session.query(Match).filter_by(
                match_id_apif=fixture_data["id"]
            ).first()

            if existing:
                print(f"      ℹ️  Partida já existe no banco (ID: {existing.id})")
                match_id = existing.id
            else:
                # Salvar nova partida
                match_data = {
                    "match_id_apif": fixture_data["id"],
                    "competition": league["name"],
                    "season": league["season"],
                    "home_team": teams["home"]["name"],
                    "away_team": teams["away"]["name"],
                    "home_team_id_apif": teams["home"]["id"],
                    "away_team_id_apif": teams["away"]["id"],
                    "match_date": datetime.fromisoformat(fixture_data["date"].replace('Z', '+00:00')),
                    "status": fixture_data["status"]["short"],
                    "venue": fixture_data.get("venue", {}).get("name"),
                    "referee": fixture_data.get("referee"),
                    "data_source": "api-football"
                }

                # Se partida já tem resultado
                score = fixture.get("score", {}).get("fulltime", {})
                if score.get("home") is not None:
                    match_data["home_score"] = score["home"]
                    match_data["away_score"] = score["away"]

                match_obj = self.db.save_match(match_data)
                match_id = match_obj.id
                self.stats["matches_saved"] += 1
                print(f"      ✓ Partida salva no banco (ID: {match_id})")

            # Salvar predição da API (se disponível)
            if api_prediction and match_id:
                # Verificar se já existe
                existing_pred = self.db.session.query(Prediction).filter_by(
                    match_id=match_id,
                    model_name="api-football"
                ).first()

                if not existing_pred:
                    predictions = api_prediction.get("predictions", {})
                    percent = predictions.get("percent", {})
                    comparison = api_prediction.get("comparison", {})
                    teams_data = api_prediction.get("teams", {})

                    pred_data = {
                        "match_id": match_id,
                        "model_name": "api-football",
                        "home_win_prob": float(percent.get("home", "0").replace("%", "")) / 100 if percent.get("home") else 0.33,
                        "draw_prob": float(percent.get("draw", "0").replace("%", "")) / 100 if percent.get("draw") else 0.33,
                        "away_win_prob": float(percent.get("away", "0").replace("%", "")) / 100 if percent.get("away") else 0.33,
                        "confidence": predictions.get("advice", ""),
                        "extra_predictions": {
                            "under_over": predictions.get("under_over"),
                            "comparison": comparison,
                            "teams_data": teams_data
                        }
                    }

                    self.db.save_prediction(pred_data)
                    self.stats["predictions_saved"] += 1
                    print(f"      ✓ Predição da API salva")

            return match_id

        except Exception as e:
            print(f"      ❌ Erro ao salvar no banco: {e}")
            self.stats["errors"] += 1
            return None

    def step5_save_historical_matches(self, matches: List[Dict], team_name: str):
        """
        Salva partidas históricas no banco

        Args:
            matches: Lista de partidas
            team_name: Nome do time (para log)
        """
        saved_count = 0

        for match in matches:
            try:
                self.step5_save_to_database(match)
                saved_count += 1
            except:
                continue

        if saved_count > 0:
            print(f"      ✓ {saved_count} partidas de {team_name} salvas no banco")

    def calculate_team_stats(self, team_matches: List[Dict], team_id: int) -> Dict:
        """
        Calcula estatísticas de um time a partir de suas partidas

        Args:
            team_matches: Lista de partidas do time
            team_id: ID do time

        Returns:
            Dict com estatísticas
        """
        if not team_matches:
            return {
                "goals_scored_avg": 1.5,
                "goals_conceded_avg": 1.5,
                "wins": 0,
                "draws": 0,
                "losses": 0,
                "matches_played": 0,
                "goals_for_total": 0,
                "goals_against_total": 0
            }

        goals_scored = []
        goals_conceded = []
        wins = draws = losses = 0

        for match in team_matches:
            teams = match["teams"]
            goals = match.get("goals", {})
            score = match.get("score", {}).get("fulltime", {})

            home_goals = score.get("home") or goals.get("home", 0)
            away_goals = score.get("away") or goals.get("away", 0)

            if home_goals is None or away_goals is None:
                continue

            is_home = teams["home"]["id"] == team_id

            if is_home:
                goals_scored.append(home_goals)
                goals_conceded.append(away_goals)
                if home_goals > away_goals:
                    wins += 1
                elif home_goals == away_goals:
                    draws += 1
                else:
                    losses += 1
            else:
                goals_scored.append(away_goals)
                goals_conceded.append(home_goals)
                if away_goals > home_goals:
                    wins += 1
                elif away_goals == home_goals:
                    draws += 1
                else:
                    losses += 1

        return {
            "goals_scored_avg": sum(goals_scored) / len(goals_scored) if goals_scored else 1.5,
            "goals_conceded_avg": sum(goals_conceded) / len(goals_conceded) if goals_conceded else 1.5,
            "wins": wins,
            "draws": draws,
            "losses": losses,
            "matches_played": len(goals_scored),
            "goals_for_total": sum(goals_scored),
            "goals_against_total": sum(goals_conceded)
        }

    def step6_process_with_models(self, match_stats: Dict, match_id: Optional[int] = None) -> Dict:
        """
        STEP 6: Processa com modelos

        Args:
            match_stats: Estatísticas da partida
            match_id: ID da partida no banco

        Returns:
            Dict com predições de todos os modelos
        """
        predictions = {}

        # Poisson
        try:
            pred_poisson = self.poisson.predict_match(
                home_attack=match_stats["home"]["goals_scored_avg"],
                away_attack=match_stats["away"]["goals_scored_avg"],
                home_defense=match_stats["home"]["goals_conceded_avg"],
                away_defense=match_stats["away"]["goals_conceded_avg"]
            )
            predictions["poisson"] = pred_poisson
        except Exception as e:
            print(f"      ⚠️  Erro no Poisson: {e}")

        # XGBoost
        if self.xgboost and self.xgboost.is_trained:
            try:
                pred_xgboost = self.xgboost.predict(match_stats, match_id=match_id)
                predictions["xgboost"] = pred_xgboost
            except Exception as e:
                print(f"      ⚠️  Erro no XGBoost: {e}")

        # Ensemble
        try:
            pred_ensemble = self.ensemble.predict(match_stats, match_id=match_id)
            predictions["ensemble"] = pred_ensemble
        except Exception as e:
            print(f"      ⚠️  Erro no Ensemble: {e}")

        return predictions

    def step7_generate_betting_recommendations(self, predictions: Dict, fixture: Dict) -> Dict:
        """
        STEP 7: Gera recomendações de apostas

        Args:
            predictions: Predições dos modelos
            fixture: Dados da partida

        Returns:
            Dict com recomendações
        """
        # Usa melhor predição disponível
        best_pred = predictions.get("ensemble") or predictions.get("xgboost") or predictions.get("poisson")

        if not best_pred:
            return {}

        result = best_pred.get("result", {})

        # Determinar resultado mais provável
        max_prob = max(result.get('home_win', 0), result.get('draw', 0), result.get('away_win', 0))

        if result.get('home_win', 0) == max_prob:
            outcome = "home_win"
            outcome_name = fixture["teams"]["home"]["name"]
        elif result.get('draw', 0) == max_prob:
            outcome = "draw"
            outcome_name = "Empate"
        else:
            outcome = "away_win"
            outcome_name = fixture["teams"]["away"]["name"]

        confidence = max_prob
        confidence_level = "Alta" if confidence > 0.55 else "Média" if confidence > 0.45 else "Baixa"

        # Mercados de apostas
        betting_markets = {
            "1x2": {
                "recommendation": outcome,
                "recommendation_name": outcome_name,
                "probability": confidence,
                "confidence": confidence_level,
                "probabilities": {
                    "home_win": result.get('home_win', 0),
                    "draw": result.get('draw', 0),
                    "away_win": result.get('away_win', 0)
                }
            }
        }

        # Goals (se disponível)
        if "goals" in best_pred:
            goals = best_pred["goals"]
            over_prob = goals.get("over_2.5", 0)
            under_prob = goals.get("under_2.5", 0)

            betting_markets["over_under_2.5"] = {
                "recommendation": "over" if over_prob > under_prob else "under",
                "probability": max(over_prob, under_prob),
                "confidence": "Alta" if max(over_prob, under_prob) > 0.55 else "Média" if max(over_prob, under_prob) > 0.45 else "Baixa",
                "probabilities": {
                    "over_2.5": over_prob,
                    "under_2.5": under_prob
                }
            }

        # BTTS (se disponível)
        if "both_teams_score" in best_pred:
            btts = best_pred["both_teams_score"]
            yes_prob = btts.get("yes", 0)
            no_prob = btts.get("no", 0)

            betting_markets["btts"] = {
                "recommendation": "yes" if yes_prob > no_prob else "no",
                "probability": max(yes_prob, no_prob),
                "confidence": "Alta" if max(yes_prob, no_prob) > 0.55 else "Média" if max(yes_prob, no_prob) > 0.45 else "Baixa",
                "probabilities": {
                    "yes": yes_prob,
                    "no": no_prob
                }
            }

        return betting_markets

    def process_fixture(self, fixture: Dict) -> Dict:
        """
        Processa uma partida completa (todos os steps)

        Args:
            fixture: Dados da partida

        Returns:
            Dict com análise completa
        """
        fixture_data = fixture["fixture"]
        teams = fixture["teams"]
        league = fixture["league"]

        home_team = teams["home"]["name"]
        away_team = teams["away"]["name"]
        home_team_id = teams["home"]["id"]
        away_team_id = teams["away"]["id"]

        print(f"\n{'='*70}")
        print(f"🏆 {league['name']} - {league['country']}")
        print(f"⚽ {home_team} vs {away_team}")
        print(f"📅 {fixture_data['date'][:16]}")
        print(f"📊 Status: {fixture_data['status']['long']}")
        print(f"{'='*70}")

        result = {
            "fixture_id": fixture_data["id"],
            "league": league["name"],
            "country": league["country"],
            "season": league["season"],
            "home_team": home_team,
            "away_team": away_team,
            "home_team_id": home_team_id,
            "away_team_id": away_team_id,
            "match_date": fixture_data["date"],
            "status": fixture_data["status"]["short"],
            "venue": fixture_data.get("venue", {}).get("name"),
        }

        # STEP 2: Predições da API
        print(f"\n   📡 STEP 2: Buscando predições da API...")
        api_prediction = self.step2_get_api_predictions(fixture)
        result["api_prediction"] = api_prediction

        # STEP 5a: Salvar partida
        print(f"\n   💾 STEP 5: Salvando no banco...")
        match_id = self.step5_save_to_database(fixture, api_prediction)
        result["match_id_db"] = match_id

        # STEP 3: H2H
        print(f"\n   🤝 STEP 3: Buscando confrontos diretos (H2H)...")
        h2h = self.step3_get_h2h(home_team_id, away_team_id)  # Free tier: últimos 2 anos
        result["h2h"] = h2h
        result["h2h_count"] = len(h2h)

        # Salvar H2H no banco
        if h2h:
            self.step5_save_historical_matches(h2h, f"H2H")

        # STEP 4: Últimas partidas de cada time
        print(f"\n   📊 STEP 4: Buscando histórico dos times...")

        print(f"      🏠 {home_team}...")
        home_matches = self.step4_get_team_last_matches(home_team_id, limit=10)
        result["home_last_matches"] = home_matches
        result["home_last_matches_count"] = len(home_matches)

        if home_matches:
            self.step5_save_historical_matches(home_matches, home_team)

        print(f"      ✈️  {away_team}...")
        away_matches = self.step4_get_team_last_matches(away_team_id, limit=10)
        result["away_last_matches"] = away_matches
        result["away_last_matches_count"] = len(away_matches)

        if away_matches:
            self.step5_save_historical_matches(away_matches, away_team)

        # Calcular estatísticas
        print(f"\n   🧮 Calculando estatísticas...")
        home_stats = self.calculate_team_stats(home_matches, home_team_id)
        away_stats = self.calculate_team_stats(away_matches, away_team_id)

        match_stats = {
            "home": home_stats,
            "away": away_stats
        }

        result["statistics"] = match_stats

        # STEP 6: Processar com modelos
        print(f"\n   🤖 STEP 6: Processando com modelos...")
        predictions = self.step6_process_with_models(match_stats, match_id)
        result["model_predictions"] = predictions

        print(f"      ✓ {len(predictions)} modelos processados")

        # STEP 7: Gerar recomendações
        print(f"\n   💰 STEP 7: Gerando recomendações de apostas...")
        betting = self.step7_generate_betting_recommendations(predictions, fixture)
        result["betting_recommendations"] = betting

        print(f"      ✓ {len(betting)} mercados analisados")

        # Mostrar recomendação principal
        if betting.get("1x2"):
            rec = betting["1x2"]
            print(f"\n   🎯 RECOMENDAÇÃO PRINCIPAL:")
            print(f"      Mercado: Resultado Final (1X2)")
            print(f"      Aposta: {rec['recommendation_name']}")
            print(f"      Probabilidade: {rec['probability']:.1%}")
            print(f"      Confiança: {rec['confidence']}")

        self.stats["fixtures_processed"] += 1

        # Rate limiting
        time.sleep(2)

        return result

    def run(self, max_fixtures: int = 10):
        """
        Executa o pipeline completo

        Args:
            max_fixtures: Número máximo de partidas para processar
        """
        self.print_section("INICIANDO PIPELINE DE ANÁLISE DE APOSTAS")

        print("\n🚀 Configuração:")
        print(f"   API: API-Football")
        print(f"   Banco: betting_v2.db")
        print(f"   Modelos: Poisson + {'XGBoost + ' if self.xgboost else ''}Ensemble")
        print(f"   Limite: {max_fixtures} partidas")

        # STEP 1: Buscar partidas
        fixtures = self.step1_get_live_fixtures()

        if not fixtures:
            print("\n⚠️  Nenhuma partida encontrada")
            return

        # Limitar processamento
        if len(fixtures) > max_fixtures:
            print(f"\n⚠️  Limitando processamento a {max_fixtures} primeiras partidas")
            fixtures = fixtures[:max_fixtures]

        # Processar cada partida
        results = []

        for i, fixture in enumerate(fixtures, 1):
            print(f"\n\n{'#'*70}")
            print(f"# PARTIDA {i}/{len(fixtures)}")
            print(f"{'#'*70}")

            try:
                result = self.process_fixture(fixture)
                results.append(result)
            except Exception as e:
                print(f"\n❌ Erro ao processar partida: {e}")
                import traceback
                traceback.print_exc()
                self.stats["errors"] += 1
                continue

        # Resumo final
        self.print_section("RESUMO FINAL")

        print(f"\n📊 Estatísticas:")
        print(f"   Partidas encontradas: {self.stats['fixtures_found']}")
        print(f"   Partidas processadas: {self.stats['fixtures_processed']}")
        print(f"   Predições API obtidas: {self.stats['predictions_fetched']}")
        print(f"   H2H obtidos: {self.stats['h2h_fetched']}")
        print(f"   Históricos obtidos: {self.stats['team_history_fetched']}")
        print(f"   Partidas salvas no banco: {self.stats['matches_saved']}")
        print(f"   Predições salvas no banco: {self.stats['predictions_saved']}")
        print(f"   Erros: {self.stats['errors']}")

        # Salvar output final
        output = {
            "timestamp": datetime.now().isoformat(),
            "pipeline_version": "1.0",
            "statistics": self.stats,
            "fixtures_analyzed": results
        }

        output_file = f"betting_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False, default=str)

        print(f"\n💾 Output final salvo: {output_file}")

        # Top recomendações
        print(f"\n\n{'='*70}")
        print("  🎯 TOP RECOMENDAÇÕES")
        print(f"{'='*70}")

        for i, result in enumerate(results[:5], 1):
            betting = result.get("betting_recommendations", {})
            if not betting:
                continue

            rec_1x2 = betting.get("1x2", {})

            print(f"\n{i}. {result['home_team']} vs {result['away_team']}")
            print(f"   Liga: {result['league']}")
            print(f"   Status: {result['status']}")

            if rec_1x2:
                print(f"   📌 Aposta: {rec_1x2['recommendation_name']}")
                print(f"   📊 Probabilidade: {rec_1x2['probability']:.1%}")
                print(f"   🎯 Confiança: {rec_1x2['confidence']}")

        self.db.close()

        self.print_section("✅ PIPELINE CONCLUÍDO!")


def main():
    """Função principal"""
    print("\n" + "=" * 70)
    print(" " * 10 + "PIPELINE COMPLETO DE ANÁLISE DE APOSTAS")
    print("=" * 70)

    # Carregar configurações
    load_dotenv()
    api_key = os.getenv("API_FOOTBALL_KEY")

    if not api_key:
        print("\n❌ API_FOOTBALL_KEY não encontrada!")
        print("\nConfigure no arquivo .env:")
        print("  API_FOOTBALL_KEY=your_key_here")
        return

    print(f"\n✓ API Key encontrada: {api_key[:10]}...")

    # Parâmetros
    max_str = input("\nNúmero máximo de partidas para processar [10]: ").strip()
    max_fixtures = int(max_str) if max_str else 10

    confirm = input(f"\nProcessar até {max_fixtures} partidas? [S/n]: ").strip().lower()
    if confirm == 'n':
        print("\n⚠️  Cancelado")
        return

    # Criar e executar pipeline
    pipeline = BettingPipeline(api_key)
    pipeline.run(max_fixtures=max_fixtures)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrompido pelo usuário")
    except Exception as e:
        print(f"\n\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
