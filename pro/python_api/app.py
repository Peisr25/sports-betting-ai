"""
Sports Betting AI API - Versão PRO
FastAPI com Ensemble (Poisson + XGBoost) e análise de valor
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Optional
import uvicorn

from data.collector import FootballDataCollector
from data.database import Database
from data.database_v2 import Database as DatabaseV2
from features.api_predictions_features import APIPredictionFeatures
from models.poisson import PoissonModel
from models.ensemble import EnsembleModel
from models.xgboost_model import XGBoostModel
from analysis.value_analysis import ValueAnalyzer
from config import config, validate_config

app = FastAPI(
    title="Sports Betting AI - PRO",
    description="API avançada com Ensemble, XGBoost e análise de valor + API-Football",
    version="3.0.0-pro"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializa componentes
collector = FootballDataCollector(config.FOOTBALL_DATA_API_KEY)
database = Database()

# NOVO: Database V2 com suporte a predições da API
database_v2 = DatabaseV2("database/betting_v2.db")
feature_extractor = APIPredictionFeatures(database_v2)

# NOVO: Ensemble com suporte a API-Football
# Tenta carregar XGBoost se existir modelo treinado
xgboost_model = None
try:
    import os
    import glob
    model_files = glob.glob("models/saved/xgboost_with_api_*.pkl")
    if model_files:
        latest_model = max(model_files, key=os.path.getctime)
        xgboost_model = XGBoostModel(
            model_path=latest_model,
            feature_extractor=feature_extractor,
            use_api_features=True
        )
        print(f"✓ XGBoost carregado: {latest_model}")
except Exception as e:
    print(f"ℹ️  XGBoost não carregado: {e}")

# Inicializa ensemble (com ou sem XGBoost)
ensemble = EnsembleModel(
    database=database_v2,
    include_api_predictions=True
)

if xgboost_model and xgboost_model.is_trained:
    ensemble.add_model("xgboost", xgboost_model, weight=0.3)

value_analyzer = ValueAnalyzer()


class PredictRequest(BaseModel):
    home_team: str
    away_team: str
    competition: str = "PL"
    use_ensemble: bool = True


class ValueAnalysisRequest(BaseModel):
    home_team: str
    away_team: str
    competition: str = "PL"
    odds: Dict  # {"result": {"home_win": 2.0, "draw": 3.5, "away_win": 4.0}, ...}


@app.on_event("startup")
async def startup():
    print("\n" + "=" * 70)
    print("SPORTS BETTING AI - VERSÃO PRO 3.0")
    print("=" * 70)
    print("Modelos:")
    print("  ✓ Poisson Distribution")
    if xgboost_model and xgboost_model.is_trained:
        print("  ✓ XGBoost (com features da API-Football)")
    else:
        print("  - XGBoost (não treinado)")
    print("  ✓ API-Football Predictions (direto da API)")
    print("  ✓ Ensemble (combina todos os modelos)")
    print("\nFeatures:")
    print("  ✓ Features básicas (21 features)")
    print(f"  ✓ Features da API-Football ({feature_extractor.get_feature_count()} features)")
    print("\nAnálise:")
    print("  ✓ Valor Esperado (EV)")
    print("  ✓ Kelly Criterion")
    print("\nEndpoints:")
    print("  /predict - Predição com ensemble")
    print("  /predict-detailed - Mostra cada modelo individualmente ⭐ NOVO")
    print("  /value-analysis - Análise de valor com odds")
    print("=" * 70 + "\n")
    validate_config()


@app.get("/")
async def root():
    models_active = ["Poisson", "API-Football Predictions", "Ensemble"]
    if xgboost_model and xgboost_model.is_trained:
        models_active.append("XGBoost (com features da API)")

    return {
        "name": "Sports Betting AI - PRO",
        "version": "3.0.0-pro",
        "models": models_active,
        "features": [
            "⭐ API-Football Predictions (direto da API)",
            "⭐ Features enriquecidas (47+ features)",
            "Modelo Ensemble (Poisson + XGBoost + API)",
            "Análise de Valor Esperado (EV)",
            "Critério de Kelly",
            "Dual-API (football-data.org + API-Football)",
            "Banco de dados SQLite V2",
            "10+ mercados de apostas"
        ],
        "endpoints": {
            "/predict": "Predição com ensemble",
            "/predict-detailed": "⭐ NOVO - Mostra cada modelo individualmente",
            "/value-analysis": "Análise de valor com odds",
            "/matches/{competition_code}": "Partidas agendadas",
            "/standings/{competition_code}": "Classificação"
        }
    }


@app.get("/competitions")
async def get_competitions():
    return {"competitions": config.SUPPORTED_COMPETITIONS}


@app.get("/teams/{competition_code}")
async def get_teams(competition_code: str):
    try:
        teams = collector.get_teams(competition_code.upper())
        return {"competition": competition_code, "teams": teams}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/matches/{competition_code}")
async def get_matches(competition_code: str, status: str = "SCHEDULED"):
    try:
        matches = collector.get_matches(
            competition_code=competition_code.upper(),
            status=status.upper()
        )
        return {"matches": matches}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/standings/{competition_code}")
async def get_standings(competition_code: str):
    try:
        return collector.get_standings(competition_code.upper())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def calculate_team_stats(team_id: int) -> Dict:
    """Calcula estatísticas de um time"""
    try:
        matches = collector.get_team_matches_history(team_id, last_n=10)

        if not matches:
            return {
                "goals_scored_avg": 1.5,
                "goals_conceded_avg": 1.5,
                "matches_played": 0,
                "wins": 0,
                "draws": 0,
                "losses": 0
            }

        goals_scored, goals_conceded = [], []
        wins, draws, losses = 0, 0, 0

        for match in matches:
            score = match.get("score", {}).get("fullTime", {})
            home_goals = score.get("home")
            away_goals = score.get("away")

            if home_goals is None or away_goals is None:
                continue

            home_team_id = match.get("homeTeam", {}).get("id")

            if home_team_id == team_id:
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
            "matches_played": len(goals_scored),
            "wins": wins,
            "draws": draws,
            "losses": losses,
            "goals_for_total": sum(goals_scored),
            "goals_against_total": sum(goals_conceded)
        }
    except:
        return {
            "goals_scored_avg": 1.5,
            "goals_conceded_avg": 1.5,
            "matches_played": 0,
            "wins": 0,
            "draws": 0,
            "losses": 0
        }


@app.post("/predict")
async def predict(request: PredictRequest):
    try:
        comp_code = request.competition.upper()
        teams = collector.get_teams(comp_code)

        home_team, away_team = None, None

        for team in teams:
            name = team.get("name", "").lower()
            short = team.get("shortName", "").lower()

            if request.home_team.lower() in name or request.home_team.lower() in short:
                home_team = team
            if request.away_team.lower() in name or request.away_team.lower() in short:
                away_team = team

        if not home_team or not away_team:
            raise HTTPException(404, "Time(s) não encontrado(s)")

        # Estatísticas
        home_stats = calculate_team_stats(home_team["id"])
        away_stats = calculate_team_stats(away_team["id"])

        match_stats = {"home": home_stats, "away": away_stats}

        # NOVO: Buscar match_id se a partida existir no banco v2
        match_id = None
        try:
            from data.database_v2 import Match
            match = database_v2.session.query(Match).filter(
                Match.home_team.like(f"%{home_team['name']}%"),
                Match.away_team.like(f"%{away_team['name']}%"),
                Match.competition == comp_code
            ).first()
            if match:
                match_id = match.id
        except:
            pass

        # Predição (agora com match_id para usar features da API!)
        if request.use_ensemble:
            predictions = ensemble.predict(match_stats, match_id=match_id)
        else:
            poisson = PoissonModel()
            predictions = poisson.predict_match(
                home_attack=home_stats["goals_scored_avg"],
                away_attack=away_stats["goals_scored_avg"],
                home_defense=home_stats["goals_conceded_avg"],
                away_defense=away_stats["goals_conceded_avg"]
            )

        response = {
            "match": {
                "home_team": home_team["name"],
                "away_team": away_team["name"],
                "competition": comp_code,
                "match_id": match_id  # Inclui match_id
            },
            "statistics": {
                "home": home_stats,
                "away": away_stats
            },
            "predictions": predictions
        }

        # Indica se usou features da API
        if match_id and "api_features_used" in predictions:
            response["api_features_used"] = predictions["api_features_used"]

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/predict-detailed")
async def predict_detailed(request: PredictRequest):
    """
    ⭐ NOVO: Predições detalhadas mostrando cada modelo individualmente

    Retorna:
    - Predições individuais de cada modelo (Poisson, XGBoost, API-Football)
    - Predição final do ensemble
    - Indicação de quais features da API foram usadas
    """
    try:
        comp_code = request.competition.upper()
        teams = collector.get_teams(comp_code)

        home_team, away_team = None, None

        for team in teams:
            name = team.get("name", "").lower()
            short = team.get("shortName", "").lower()

            if request.home_team.lower() in name or request.home_team.lower() in short:
                home_team = team
            if request.away_team.lower() in name or request.away_team.lower() in short:
                away_team = team

        if not home_team or not away_team:
            raise HTTPException(404, "Time(s) não encontrado(s)")

        # Estatísticas
        home_stats = calculate_team_stats(home_team["id"])
        away_stats = calculate_team_stats(away_team["id"])
        match_stats = {"home": home_stats, "away": away_stats}

        # Buscar match_id
        match_id = None
        try:
            from data.database_v2 import Match
            match = database_v2.session.query(Match).filter(
                Match.home_team.like(f"%{home_team['name']}%"),
                Match.away_team.like(f"%{away_team['name']}%"),
                Match.competition == comp_code
            ).first()
            if match:
                match_id = match.id
        except:
            pass

        # Predições individuais de cada modelo
        individual_predictions = ensemble.get_model_predictions(match_stats, match_id=match_id)

        # Predição combinada do ensemble
        ensemble_prediction = ensemble.predict(match_stats, match_id=match_id)

        # Verifica se tem predições da API
        has_api_predictions = "api-football" in individual_predictions

        return {
            "match": {
                "home_team": home_team["name"],
                "away_team": away_team["name"],
                "competition": comp_code,
                "match_id": match_id
            },
            "statistics": {
                "home": home_stats,
                "away": away_stats
            },
            "individual_predictions": individual_predictions,
            "ensemble_prediction": ensemble_prediction,
            "models_used": list(individual_predictions.keys()),
            "has_api_predictions": has_api_predictions,
            "ensemble_weights": ensemble.weights
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/value-analysis")
async def value_analysis(request: ValueAnalysisRequest):
    """Análise de valor esperado com odds"""
    try:
        # Busca predições primeiro
        pred_req = PredictRequest(
            home_team=request.home_team,
            away_team=request.away_team,
            competition=request.competition
        )

        pred_response = await predict(pred_req)
        predictions = pred_response["predictions"]

        # Analisa valor
        analyses = value_analyzer.analyze_match(
            predictions=predictions,
            odds=request.odds,
            stake=100
        )

        best_bets = value_analyzer.get_best_bets(analyses, top_n=5)

        return {
            "match": pred_response["match"],
            "all_analyses": analyses,
            "best_bets": best_bets,
            "total_analyzed": len(analyses),
            "value_bets_found": len([a for a in analyses if a["has_value"]])
        }

    except Exception as e:
        raise HTTPException(500, str(e))


if __name__ == "__main__":
    uvicorn.run(app, host=config.APP_HOST, port=config.APP_PORT)
