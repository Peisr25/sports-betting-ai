"""
Sports Betting AI API - Versão Lite
FastAPI com modelo de Poisson usando football-data.org
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Optional
import uvicorn
from datetime import datetime

from data.collector import FootballDataCollector
from models.poisson import PoissonModel
from config import config, validate_config

# Inicializa FastAPI
app = FastAPI(
    title="Sports Betting AI - Lite",
    description="API de predições de apostas usando modelo de Poisson e football-data.org",
    version="1.0.0-lite",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializa componentes
collector = FootballDataCollector(config.FOOTBALL_DATA_API_KEY)
poisson_model = PoissonModel()


class PredictRequest(BaseModel):
    """Modelo de requisição de predição"""
    home_team: str
    away_team: str
    competition: str = "PL"


@app.on_event("startup")
async def startup_event():
    """Evento de inicialização"""
    print("\n" + "=" * 60)
    print("SPORTS BETTING AI - VERSÃO LITE")
    print("=" * 60)
    print(f"Modelo: Poisson Distribution")
    print(f"API: football-data.org")
    print(f"Servidor: http://{config.APP_HOST}:{config.APP_PORT}")
    print(f"Docs: http://{config.APP_HOST}:{config.APP_PORT}/docs")
    print("=" * 60 + "\n")

    # Valida configuração
    if not validate_config():
        print("⚠️  Configure o arquivo .env antes de fazer predições!\n")


@app.get("/")
async def root():
    """Rota raiz - informações da API"""
    return {
        "name": "Sports Betting AI - Lite",
        "version": "1.0.0-lite",
        "model": "Poisson Distribution",
        "api_provider": "football-data.org",
        "status": "online",
        "docs": "/docs",
        "endpoints": {
            "competitions": "/competitions",
            "teams": "/teams/{competition_code}",
            "matches": "/matches/{competition_code}",
            "standings": "/standings/{competition_code}",
            "predict": "/predict (POST)"
        }
    }


@app.get("/health")
async def health_check():
    """Verifica saúde da API"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "requests_made": collector.get_request_count()
    }


@app.get("/competitions")
async def get_competitions():
    """Lista competições disponíveis"""
    try:
        return {
            "competitions": config.SUPPORTED_COMPETITIONS,
            "total": len(config.SUPPORTED_COMPETITIONS)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/teams/{competition_code}")
async def get_teams(competition_code: str):
    """
    Busca times de uma competição

    Args:
        competition_code: Código da competição (PL, BSA, CL, etc)
    """
    try:
        teams = collector.get_teams(competition_code.upper())
        return {
            "competition": competition_code.upper(),
            "teams": teams,
            "total": len(teams)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/matches/{competition_code}")
async def get_matches(
    competition_code: str,
    status: str = "SCHEDULED"
):
    """
    Busca partidas de uma competição

    Args:
        competition_code: Código da competição (PL, BSA, CL, etc)
        status: Status das partidas (SCHEDULED, LIVE, FINISHED)
    """
    try:
        matches = collector.get_matches(
            competition_code=competition_code.upper(),
            status=status.upper()
        )
        return {
            "competition": competition_code.upper(),
            "status": status.upper(),
            "matches": matches,
            "total": len(matches)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/standings/{competition_code}")
async def get_standings(competition_code: str):
    """
    Busca classificação de uma competição

    Args:
        competition_code: Código da competição (PL, BSA, CL, etc)
    """
    try:
        standings = collector.get_standings(competition_code.upper())
        return standings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def calculate_team_stats(team_id: int, last_n: int = 10) -> Dict:
    """
    Calcula estatísticas de um time baseado em partidas recentes

    Args:
        team_id: ID do time
        last_n: Número de partidas para analisar

    Returns:
        Estatísticas do time
    """
    try:
        matches = collector.get_team_matches_history(team_id, last_n=last_n)

        if not matches:
            # Retorna valores padrão se não houver histórico
            return {
                "goals_scored_avg": 1.5,
                "goals_conceded_avg": 1.5,
                "matches_played": 0,
                "wins": 0,
                "draws": 0,
                "losses": 0
            }

        goals_scored = []
        goals_conceded = []
        wins = 0
        draws = 0
        losses = 0

        for match in matches:
            score = match.get("score", {}).get("fullTime", {})
            home_goals = score.get("home")
            away_goals = score.get("away")

            if home_goals is None or away_goals is None:
                continue

            home_team_id = match.get("homeTeam", {}).get("id")

            if home_team_id == team_id:
                # Time jogou em casa
                goals_scored.append(home_goals)
                goals_conceded.append(away_goals)

                if home_goals > away_goals:
                    wins += 1
                elif home_goals == away_goals:
                    draws += 1
                else:
                    losses += 1
            else:
                # Time jogou fora
                goals_scored.append(away_goals)
                goals_conceded.append(home_goals)

                if away_goals > home_goals:
                    wins += 1
                elif away_goals == home_goals:
                    draws += 1
                else:
                    losses += 1

        if not goals_scored:
            return {
                "goals_scored_avg": 1.5,
                "goals_conceded_avg": 1.5,
                "matches_played": 0,
                "wins": 0,
                "draws": 0,
                "losses": 0
            }

        return {
            "goals_scored_avg": sum(goals_scored) / len(goals_scored),
            "goals_conceded_avg": sum(goals_conceded) / len(goals_conceded),
            "matches_played": len(goals_scored),
            "wins": wins,
            "draws": draws,
            "losses": losses
        }

    except Exception as e:
        print(f"Erro ao calcular estatísticas: {e}")
        return {
            "goals_scored_avg": 1.5,
            "goals_conceded_avg": 1.5,
            "matches_played": 0,
            "wins": 0,
            "draws": 0,
            "losses": 0
        }


def generate_recommendations(predictions: Dict, home_team: str, away_team: str) -> list:
    """
    Gera recomendações de apostas baseadas nas predições

    Args:
        predictions: Predições do modelo
        home_team: Nome do time da casa
        away_team: Nome do time visitante

    Returns:
        Lista de recomendações
    """
    recommendations = []
    confidence_threshold = config.MIN_CONFIDENCE_THRESHOLD

    # Resultado (1X2)
    result = predictions["result"]
    max_result_prob = max(result.values())

    if max_result_prob >= confidence_threshold:
        result_bet = max(result, key=result.get)
        confidence = "Alta" if max_result_prob >= 0.60 else "Média"

        bet_name = {
            "home_win": f"Vitória {home_team}",
            "draw": "Empate",
            "away_win": f"Vitória {away_team}"
        }.get(result_bet, "Desconhecido")

        recommendations.append({
            "market": "Resultado (1X2)",
            "bet": bet_name,
            "confidence": confidence,
            "probability": max_result_prob
        })

    # Total de Gols
    over_25 = predictions["goals"]["over_2.5"]
    if over_25 >= confidence_threshold or over_25 <= (1 - confidence_threshold):
        bet = "Over 2.5" if over_25 >= confidence_threshold else "Under 2.5"
        confidence = "Alta" if abs(over_25 - 0.5) >= 0.15 else "Média"
        prob = over_25 if over_25 >= confidence_threshold else (1 - over_25)

        recommendations.append({
            "market": "Total de Gols",
            "bet": bet,
            "confidence": confidence,
            "probability": prob
        })

    # Ambos Marcam
    btts_yes = predictions["both_teams_score"]["yes"]
    if btts_yes >= confidence_threshold or btts_yes <= (1 - confidence_threshold):
        bet = "Sim" if btts_yes >= confidence_threshold else "Não"
        confidence = "Alta" if abs(btts_yes - 0.5) >= 0.15 else "Média"
        prob = btts_yes if btts_yes >= confidence_threshold else (1 - btts_yes)

        recommendations.append({
            "market": "Ambos Marcam",
            "bet": bet,
            "confidence": confidence,
            "probability": prob
        })

    return recommendations


@app.post("/predict")
async def predict(request: PredictRequest):
    """
    Faz predição de uma partida

    Args:
        request: Dados da partida (times e competição)

    Returns:
        Predições e recomendações
    """
    try:
        comp_code = request.competition.upper()

        print(f"\n{'=' * 60}")
        print(f"PREDIÇÃO: {request.home_team} vs {request.away_team}")
        print(f"Competição: {comp_code}")
        print(f"{'=' * 60}")

        # Busca times da competição
        print(f"Buscando times da competição {comp_code}...")
        teams = collector.get_teams(comp_code)

        # Procura os times
        home_team = None
        away_team = None

        for team in teams:
            team_name = team.get("name", "").lower()
            team_short = team.get("shortName", "").lower()

            if request.home_team.lower() in team_name or request.home_team.lower() in team_short:
                home_team = team
                print(f"✓ Casa: {team['name']} (ID: {team['id']})")

            if request.away_team.lower() in team_name or request.away_team.lower() in team_short:
                away_team = team
                print(f"✓ Fora: {team['name']} (ID: {team['id']})")

        if not home_team:
            raise HTTPException(
                status_code=404,
                detail=f"Time da casa '{request.home_team}' não encontrado na competição {comp_code}"
            )

        if not away_team:
            raise HTTPException(
                status_code=404,
                detail=f"Time visitante '{request.away_team}' não encontrado na competição {comp_code}"
            )

        # Calcula estatísticas dos times
        print("Calculando estatísticas...")
        home_stats = calculate_team_stats(home_team["id"], config.DEFAULT_HISTORY_MATCHES)
        away_stats = calculate_team_stats(away_team["id"], config.DEFAULT_HISTORY_MATCHES)

        print(f"  {home_team['name']}: {home_stats['goals_scored_avg']:.2f} gols/jogo")
        print(f"  {away_team['name']}: {away_stats['goals_scored_avg']:.2f} gols/jogo")

        # Faz predição usando Poisson
        print("Gerando predição com Poisson...")
        predictions = poisson_model.predict_match(
            home_attack=home_stats["goals_scored_avg"],
            away_attack=away_stats["goals_scored_avg"],
            home_defense=home_stats["goals_conceded_avg"],
            away_defense=away_stats["goals_conceded_avg"]
        )

        # Gera recomendações
        recommendations = generate_recommendations(
            predictions,
            home_team["name"],
            away_team["name"]
        )

        # Monta resposta
        result = {
            "match": {
                "home_team": home_team["name"],
                "away_team": away_team["name"],
                "competition": comp_code
            },
            "statistics": {
                "home": {
                    "goals_avg": round(home_stats["goals_scored_avg"], 2),
                    "conceded_avg": round(home_stats["goals_conceded_avg"], 2),
                    "matches": home_stats["matches_played"],
                    "form": f"{home_stats['wins']}W-{home_stats['draws']}D-{home_stats['losses']}L"
                },
                "away": {
                    "goals_avg": round(away_stats["goals_scored_avg"], 2),
                    "conceded_avg": round(away_stats["goals_conceded_avg"], 2),
                    "matches": away_stats["matches_played"],
                    "form": f"{away_stats['wins']}W-{away_stats['draws']}D-{away_stats['losses']}L"
                }
            },
            "predictions": predictions,
            "recommendations": recommendations,
            "confidence": "Alta" if min(home_stats["matches_played"], away_stats["matches_played"]) >= 5 else "Média"
        }

        print(f"✓ Predição gerada com sucesso!")
        print(f"{'=' * 60}\n")

        return result

    except HTTPException:
        raise
    except Exception as e:
        print(f"✗ ERRO: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=config.APP_HOST,
        port=config.APP_PORT,
        reload=False
    )
