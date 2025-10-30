"""
Configurações da API - Versão Lite
"""
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do .env
load_dotenv()


class Config:
    """Configurações da aplicação"""

    # API football-data.org
    FOOTBALL_DATA_API_KEY = os.getenv("FOOTBALL_DATA_API_KEY", "YOUR_API_KEY_HERE")
    FOOTBALL_DATA_BASE_URL = "https://api.football-data.org/v4"

    # Limites da API (tier gratuito)
    API_RATE_LIMIT_PER_MINUTE = 10
    API_RATE_LIMIT_PER_DAY = 100

    # Configurações da aplicação
    APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT = int(os.getenv("APP_PORT", 5000))
    APP_DEBUG = os.getenv("APP_DEBUG", "False").lower() == "true"

    # Logs
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR = "logs"

    # Cache (em memória apenas - sem banco de dados na versão Lite)
    CACHE_TTL_SECONDS = 300  # 5 minutos

    # Predições
    DEFAULT_HISTORY_MATCHES = 10  # Número de partidas para análise
    MIN_CONFIDENCE_THRESHOLD = 0.55  # Confiança mínima para recomendações

    # Competições suportadas
    SUPPORTED_COMPETITIONS = {
        "PL": {"name": "Premier League", "id": 2021},
        "PD": {"name": "La Liga", "id": 2014},
        "BL1": {"name": "Bundesliga", "id": 2002},
        "SA": {"name": "Serie A", "id": 2019},
        "FL1": {"name": "Ligue 1", "id": 2015},
        "CL": {"name": "Champions League", "id": 2001},
        "BSA": {"name": "Brasileirão Série A", "id": 2013},
        "PPL": {"name": "Primeira Liga", "id": 2017},
        "DED": {"name": "Eredivisie", "id": 2003},
    }


# Instância global de configuração
config = Config()


# Validação de configuração
def validate_config():
    """Valida se as configurações estão corretas"""
    errors = []

    if config.FOOTBALL_DATA_API_KEY == "YOUR_API_KEY_HERE":
        errors.append("FOOTBALL_DATA_API_KEY não configurada no .env")

    if errors:
        print("⚠️  AVISOS DE CONFIGURAÇÃO:")
        for error in errors:
            print(f"   - {error}")
        print("\nConfigure as variáveis no arquivo .env antes de usar a API.\n")
        return False

    return True


if __name__ == "__main__":
    print("=== Configurações da API ===\n")
    print(f"API Key: {'✓ Configurada' if config.FOOTBALL_DATA_API_KEY != 'YOUR_API_KEY_HERE' else '✗ Não configurada'}")
    print(f"Base URL: {config.FOOTBALL_DATA_BASE_URL}")
    print(f"Rate Limit: {config.API_RATE_LIMIT_PER_MINUTE} req/min")
    print(f"Host: {config.APP_HOST}:{config.APP_PORT}")
    print(f"\nCompetições Suportadas: {len(config.SUPPORTED_COMPETITIONS)}")
    for code, info in list(config.SUPPORTED_COMPETITIONS.items())[:3]:
        print(f"  {code}: {info['name']}")

    print("\n")
    validate_config()
