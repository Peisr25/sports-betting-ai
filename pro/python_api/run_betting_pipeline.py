"""
Script de execução completa do pipeline de apostas
Executa todas as etapas em sequência
"""
import os
import sys
import subprocess
from datetime import datetime


def print_header(text: str):
    """Imprime cabeçalho formatado"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")


def run_script(script_name: str, args: list = None) -> bool:
    """
    Executa um script Python
    
    Args:
        script_name: Nome do script
        args: Argumentos adicionais
        
    Returns:
        True se sucesso, False caso contrário
    """
    if args is None:
        args = []
    
    cmd = [sys.executable, script_name] + args
    
    print(f"▶️  Executando: {script_name}")
    print(f"   Comando: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(
            cmd,
            check=True,
            text=True,
            capture_output=False  # Mostrar output em tempo real
        )
        
        print(f"\n✅ {script_name} concluído com sucesso!\n")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Erro ao executar {script_name}")
        print(f"   Código de saída: {e.returncode}\n")
        return False
    except FileNotFoundError:
        print(f"\n❌ Script não encontrado: {script_name}\n")
        return False
    except KeyboardInterrupt:
        print(f"\n⚠️  Execução interrompida pelo usuário\n")
        return False


def check_files_exist(files: list) -> bool:
    """Verifica se arquivos necessários existem"""
    missing = []
    for file in files:
        if not os.path.exists(file):
            missing.append(file)
    
    if missing:
        print("❌ Arquivos necessários não encontrados:")
        for file in missing:
            print(f"   - {file}")
        return False
    
    return True


def main():
    """Pipeline completo"""
    print("\n" + "🎯"*35)
    print("  PIPELINE COMPLETO DE APOSTAS ESPORTIVAS")
    print("🎯"*35)
    
    start_time = datetime.now()
    
    # Verificar scripts necessários
    scripts = [
        "find_live_and_upcoming.py",
        "collect_team_history.py",
        "calculate_predictions.py",
        "generate_betting_recommendations.py"
    ]
    
    print("\n📋 Verificando scripts...")
    if not check_files_exist(scripts):
        print("\n❌ Execute este script da pasta pro/python_api/")
        return 1
    
    print("✅ Todos os scripts encontrados!\n")
    
    # Passo 1: Encontrar fixtures
    print_header("ETAPA 1/4: Descobrir Partidas Ao Vivo/Agendadas")
    
    if not run_script("find_live_and_upcoming.py"):
        print("❌ Pipeline interrompido na etapa 1")
        return 1
    
    # Verificar se fixtures foram encontradas
    if not os.path.exists("live_and_upcoming_fixtures.json"):
        print("❌ Nenhuma fixture encontrada. Pipeline interrompido.")
        return 1
    
    # Passo 2: Coletar dados históricos
    print_header("ETAPA 2/4: Coletar Dados Históricos dos Times")
    
    if not run_script("collect_team_history.py", ["--from-live-fixtures"]):
        print("❌ Pipeline interrompido na etapa 2")
        return 1
    
    # Passo 3: Calcular previsões
    print_header("ETAPA 3/4: Calcular Previsões")
    
    if not run_script("calculate_predictions.py", ["--from-live-fixtures"]):
        print("❌ Pipeline interrompido na etapa 3")
        return 1
    
    # Verificar se previsões foram geradas
    if not os.path.exists("betting_predictions.json"):
        print("❌ Nenhuma previsão gerada. Pipeline interrompido.")
        return 1
    
    # Passo 4: Gerar recomendações
    print_header("ETAPA 4/4: Gerar Recomendações de Apostas")
    
    if not run_script("generate_betting_recommendations.py"):
        print("❌ Pipeline interrompido na etapa 4")
        return 1
    
    # Resumo final
    end_time = datetime.now()
    duration = end_time - start_time
    
    print("\n" + "🎉"*35)
    print("  PIPELINE CONCLUÍDO COM SUCESSO!")
    print("🎉"*35)
    
    print(f"\n⏱️  Tempo total: {duration.seconds // 60}min {duration.seconds % 60}s")
    print(f"📅 Início: {start_time.strftime('%H:%M:%S')}")
    print(f"📅 Fim: {end_time.strftime('%H:%M:%S')}")
    
    # Listar arquivos gerados
    print("\n📁 Arquivos gerados:")
    
    files = [
        ("live_and_upcoming_fixtures.json", "Fixtures disponíveis"),
        ("betting_predictions.json", "Previsões calculadas"),
        ("betting_recommendations.json", "Recomendações de apostas"),
        ("database/betting.db", "Banco de dados atualizado")
    ]
    
    for file, desc in files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            size_kb = size / 1024
            print(f"   ✅ {file:<35} ({size_kb:.1f} KB) - {desc}")
        else:
            print(f"   ⚠️ {file:<35} (não encontrado)")
    
    print("\n💡 Próximos passos:")
    print("   1. Abra betting_recommendations.json para ver as recomendações")
    print("   2. Use a calculadora de apostas mostrada no console")
    print("   3. Execute novamente para atualizar (recomendado a cada 30min)")
    
    print("\n" + "="*70 + "\n")
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrompido pelo usuário")
        sys.exit(1)
