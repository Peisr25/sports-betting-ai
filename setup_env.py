"""
Script de configuração - Cria arquivo .env com API key
"""
import os
import sys

def setup_env(version="lite"):
    """Configura arquivo .env"""
    print(f"=== CONFIGURAÇÃO DO .ENV - VERSÃO {version.upper()} ===\n")

    # Define caminhos
    example_path = f"{version}/.env.example"
    env_path = f"{version}/python_api/.env"

    # Verifica se .env.example existe
    if not os.path.exists(example_path):
        print(f"❌ Arquivo {example_path} não encontrado!")
        return False

    # Verifica se .env já existe
    if os.path.exists(env_path):
        print(f"⚠️  Arquivo {env_path} já existe!")
        overwrite = input("Deseja sobrescrever? (s/n): ").strip().lower()
        if overwrite != 's':
            print("Operação cancelada.")
            return False

    # Lê o template
    with open(example_path, 'r') as f:
        content = f.read()

    # Solicita API key
    print("\n📝 Para obter sua API key:")
    print("1. Acesse: https://www.football-data.org/client/register")
    print("2. Preencha o formulário e confirme seu email")
    print("3. Copie a API key que receberá por email\n")

    api_key = input("Digite sua API key: ").strip()

    if not api_key or api_key == "YOUR_API_KEY_HERE":
        print("❌ API key inválida!")
        return False

    # Substitui no template
    content = content.replace("YOUR_API_KEY_HERE", api_key)

    # Cria diretório se não existir
    os.makedirs(os.path.dirname(env_path), exist_ok=True)

    # Salva .env
    with open(env_path, 'w') as f:
        f.write(content)

    print(f"\n✅ Arquivo {env_path} criado com sucesso!")
    print("\n🎯 Próximos passos:")
    print(f"1. cd {version}/python_api")
    print("2. python -m venv venv")
    print("3. source venv/bin/activate  # Windows: venv\\Scripts\\activate")
    print("4. pip install -r requirements.txt")
    print("5. python app.py")

    return True

if __name__ == "__main__":
    version = sys.argv[1] if len(sys.argv) > 1 else "lite"

    if version not in ["lite", "pro"]:
        print("❌ Versão inválida! Use: lite ou pro")
        print("\nExemplo:")
        print("  python setup_env.py lite")
        print("  python setup_env.py pro")
        sys.exit(1)

    setup_env(version)
