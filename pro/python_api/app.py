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
from models.poisson import PoissonModel
from models.ensemble import EnsembleModel
from analysis.value_analysis import ValueAnalyzer
from config import config, validate_config

app = FastAPI(
    title="Sports Betting AI - PRO",
    description="API avançada com Ensemble, XGBoost e análise de valor",
    version="2.0.0-pro"
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
ensemble = EnsembleModel()
value_analyzer = ValueAnalyzer()
database = Database()


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
    print("\n" + "=" * 60)
    print("SPORTS BETTING AI - VERSÃO PRO")
    print("=" * 60)
    print("Modelos: Poisson + Ensemble + XGBoost")
    print("Análise: Valor Esperado (EV) + Kelly Criterion")
    print("=" * 60 + "\n")
    validate_config()


@app.get("/")
async def root():
    return {
        "name": "Sports Betting AI - PRO",
        "version": "2.0.0-pro",
        "features": [
            "Modelo Ensemble (Poisson + XGBoost)",
            "Análise de Valor Esperado",
            "Critério de Kelly",
            "Banco de dados SQLite",
            "7+ mercados de apostas"
        ]
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

        # Predição
        if request.use_ensemble:
            predictions = ensemble.predict(match_stats)
        else:
            poisson = PoissonModel()
            predictions = poisson.predict_match(
                home_attack=home_stats["goals_scored_avg"],
                away_attack=away_stats["goals_scored_avg"],
                home_defense=home_stats["goals_conceded_avg"],
                away_defense=away_stats["goals_conceded_avg"]
            )

        return {
            "match": {
                "home_team": home_team["name"],
                "away_team": away_team["name"],
                "competition": comp_code
            },
            "statistics": {
                "home": home_stats,
                "away": away_stats
            },
            "predictions": predictions
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
