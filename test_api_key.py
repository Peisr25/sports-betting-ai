"""
Script de diagnóstico - Testa API key da football-data.org
"""
import requests
import sys

def test_api_key(api_key):
    """Testa se a API key é válida"""
    print("=== DIAGNÓSTICO DA API KEY ===\n")

    if not api_key or api_key == "YOUR_API_KEY_HERE":
        print("❌ API KEY NÃO CONFIGURADA!")
        print("\n📝 Passos para corrigir:")
        print("1. Obtenha sua API key em: https://www.football-data.org/client/register")
        print("2. Copie lite/.env.example para lite/python_api/.env")
        print("3. Edite lite/python_api/.env e substitua YOUR_API_KEY_HERE pela sua key")
        return False

    print(f"✓ API Key encontrada: {api_key[:10]}...{api_key[-4:]}")
    print(f"  Tamanho: {len(api_key)} caracteres\n")

    # Testa conexão com a API
    print("Testando conexão com football-data.org...")

    headers = {"X-Auth-Token": api_key}

    try:
        # Tenta acessar endpoint de competições
        url = "https://api.football-data.org/v4/competitions"
        response = requests.get(url, headers=headers, timeout=10)

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            print("✅ API KEY VÁLIDA!")
            data = response.json()
            count = data.get('count', 0)
            print(f"✓ Acesso autorizado - {count} competições disponíveis")
            return True

        elif response.status_code == 400:
            print("❌ API KEY INVÁLIDA!")
            print("\n🔍 Detalhes do erro:")
            print(response.text)
            print("\n📝 Possíveis causas:")
            print("1. API key incorreta ou expirada")
            print("2. API key com espaços extras ou aspas")
            print("3. Conta não ativada em football-data.org")
            return False

        elif response.status_code == 403:
            print("❌ ACESSO NEGADO!")
            print("Sua key pode não ter permissão para este endpoint")
            print(response.text)
            return False

        elif response.status_code == 429:
            print("⚠️  LIMITE DE REQUISIÇÕES ATINGIDO!")
            print("Tier gratuito: 10 req/min")
            print("Aguarde 1 minuto e tente novamente")
            return False

        else:
            print(f"⚠️  Erro inesperado: {response.status_code}")
            print(response.text)
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
        print("\nVerifique sua conexão com a internet")
        return False

if __name__ == "__main__":
    print("Digite sua API key da football-data.org:")
    print("(ou pressione Enter para testar a configuração atual do .env)\n")

    api_key = input("API Key: ").strip()

    if not api_key:
        # Tenta carregar do .env
        try:
            from dotenv import load_dotenv
            import os

            # Tenta carregar .env de diferentes locais
            env_paths = [
                "lite/python_api/.env",
                "lite/.env",
                ".env"
            ]

            loaded = False
            for path in env_paths:
                if load_dotenv(path):
                    print(f"✓ Carregado de: {path}\n")
                    loaded = True
                    break

            if loaded:
                api_key = os.getenv("FOOTBALL_DATA_API_KEY")
            else:
                print("⚠️  Nenhum arquivo .env encontrado\n")

        except ImportError:
            print("⚠️  python-dotenv não instalado")
            print("Execute: pip install python-dotenv\n")

    if api_key:
        test_api_key(api_key)
    else:
        print("❌ Nenhuma API key fornecida!")
        print("\n📝 Como obter uma API key:")
        print("1. Acesse: https://www.football-data.org/client/register")
        print("2. Preencha o formulário de registro")
        print("3. Confirme seu email")
        print("4. A API key será enviada por email")
