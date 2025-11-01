"""Teste de leitura do .env"""
import os
from dotenv import load_dotenv

# Carregar .env da pasta pai
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
print(f"Procurando .env em: {env_path}")
print(f"Arquivo existe? {os.path.exists(env_path)}")

load_dotenv(env_path)

api_key = os.getenv('API_FOOTBALL_KEY')
football_data_key = os.getenv('FOOTBALL_DATA_API_KEY')

print(f"\nAPI_FOOTBALL_KEY: {api_key[:20]}... (encontrada)" if api_key else "API_FOOTBALL_KEY: NÃO ENCONTRADA")
print(f"FOOTBALL_DATA_API_KEY: {football_data_key[:20]}... (encontrada)" if football_data_key else "FOOTBALL_DATA_API_KEY: NÃO ENCONTRADA")
