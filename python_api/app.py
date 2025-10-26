"""
API REST para o sistema de apostas esportivas
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
from prediction.predictor import PredictionEngine
from config import config

# Inicializa FastAPI
app = FastAPI(
    title="Sports Betting AI API",
    description="API para predição de apostas esportivas usando IA",
    version="1.0.0"
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializa engine de predição
prediction_engine = PredictionEngine()


# Modelos de request/response
class PredictionRequest(BaseModel):
    """Modelo de requisição para predição"""
    home_team: str
    away_team: str
    league: Optional[str] = "Brasileirão Série A"
    season: Optional[int] = 2025


class UpdateRequest(BaseModel):
    """Modelo de requisição para atualização de dados"""
    league: Optional[str] = "Brasileirão Série A"
    season: Optional[int] = 2025


# Endpoints
@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": "Sports Betting AI API",
        "version": "1.0.0",
        "endpoints": {
            "predict": "/predict",
            "update": "/update",
            "health": "/health",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Verifica saúde da API"""
    return {
        "status": "healthy",
        "api_key_configured": bool(config.API_FOOTBALL_KEY),
        "database_url": config.DATABASE_URL.split("///")[-1]
    }


@app.post("/predict")
async def predict_match(request: PredictionRequest):
    """
    Faz predição para uma partida
    
    Args:
        request: Dados da partida
        
    Returns:
        Predições e recomendações
    """
    try:
        result = prediction_engine.predict_match(
            home_team_name=request.home_team,
            away_team_name=request.away_team,
            league_name=request.league,
            season=request.season
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/update")
async def update_data(request: UpdateRequest):
    """
    Atualiza banco de dados com dados recentes
    
    Args:
        request: Dados da liga
        
    Returns:
        Status da atualização
    """
    try:
        prediction_engine.update_database(
            league_name=request.league,
            season=request.season
        )
        
        return {
            "status": "success",
            "message": f"Dados da {request.league} atualizados",
            "api_requests_used": prediction_engine.collector.get_request_count()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/leagues")
async def get_supported_leagues():
    """Retorna ligas suportadas"""
    return {
        "leagues": [
            {
                "name": "Brasileirão Série A",
                "country": "Brazil",
                "api_id": 71
            },
            {
                "name": "Premier League",
                "country": "England",
                "api_id": 39
            },
            {
                "name": "La Liga",
                "country": "Spain",
                "api_id": 140
            },
            {
                "name": "Bundesliga",
                "country": "Germany",
                "api_id": 78
            },
            {
                "name": "Serie A",
                "country": "Italy",
                "api_id": 135
            },
            {
                "name": "Ligue 1",
                "country": "France",
                "api_id": 61
            }
        ]
    }


@app.get("/stats")
async def get_api_stats():
    """Retorna estatísticas de uso da API"""
    return {
        "api_requests_used": prediction_engine.collector.get_request_count(),
        "api_requests_limit": config.API_RATE_LIMIT_PER_DAY,
        "api_requests_remaining": config.API_RATE_LIMIT_PER_DAY - prediction_engine.collector.get_request_count()
    }


# Inicialização
if __name__ == "__main__":
    print("=" * 60)
    print("SPORTS BETTING AI API")
    print("=" * 60)
    print(f"Servidor iniciando em http://{config.HOST}:{config.PORT}")
    print(f"Documentação disponível em http://{config.HOST}:{config.PORT}/docs")
    print("=" * 60)
    
    uvicorn.run(
        "app:app",
        host=config.HOST,
        port=config.PORT,
        reload=True
    )

