#!/usr/bin/env python3
"""
Script pour exécuter la suite complète de tests A'rosa-je
"""
import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Exécute une commande et affiche le résultat"""
    print(f"\n{'='*60}")
    print(f"Test: {description}")
    print("=" * 60)

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent,
        )

        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)

        if result.returncode == 0:
            print(f"[SUCCESS] {description}")
            return True
        else:
            print(f"[FAILED] {description} - Error code: {result.returncode}")
            return False

    except Exception as e:
        print(f"[ERROR] Execution error: {e}")
        return False


def main():
    """Fonction principale"""
    print("A'rosa-je - Suite de Tests Complete")
    print("=" * 60)

    # Changer vers le répertoire de l'API
    api_dir = Path(__file__).parent
    os.chdir(api_dir)

    success_count = 0
    total_tests = 0

    # 1. Tests unitaires
    if run_command("python -m pytest tests/unit/ -v -m unit", "Tests Unitaires"):
        success_count += 1
    total_tests += 1

    # 2. Tests d'intégration (nécessitent la DB)
    if run_command(
        "python -m pytest tests/integration/ -v -m integration", "Tests d'Intégration"
    ):
        success_count += 1
    total_tests += 1

    # 3. Tests de workflow avec Tavern (nécessitent l'API en cours d'exécution)
    print("\n" + "=" * 60)
    print("⚠️  Tests de Workflow (Tavern)")
    print("   ATTENTION: Ces tests nécessitent que l'API soit en cours d'exécution")
    print("   Lancez './bin/up api' dans un autre terminal avant d'exécuter ces tests")
    print("=" * 60)

    user_choice = (
        input("Voulez-vous exécuter les tests Tavern? (y/N): ").lower().strip()
    )
    if user_choice in ["y", "yes", "oui"]:
        if run_command(
            "python -m pytest tests/workflows/ -v --tb=short",
            "Tests de Workflow (Tavern)",
        ):
            success_count += 1
        total_tests += 1
    else:
        print("⏭️  Tests Tavern ignorés")

    # 4. Tests avec couverture (si coverage est installé)
    print("\n" + "=" * 60)
    print("📊 Génération du rapport de couverture")
    print("=" * 60)

    # Vérifier si coverage est installé
    coverage_available = False
    try:
        import coverage

        coverage_available = True
    except ImportError:
        print("⚠️  Package 'coverage' non installé")
        print("   Installez-le avec: pip install coverage")

    if coverage_available:
        if run_command(
            "python -m pytest tests/unit/ tests/integration/ --cov=. --cov-report=html --cov-report=term",
            "Tests avec Couverture de Code",
        ):
            print("📋 Rapport de couverture HTML généré dans htmlcov/")
            success_count += 1
        total_tests += 1

    # Résumé final
    print("\n" + "=" * 60)
    print("📋 RÉSUMÉ DES TESTS")
    print("=" * 60)
    print(f"✅ Tests réussis: {success_count}/{total_tests}")
    print(f"❌ Tests échoués: {total_tests - success_count}/{total_tests}")

    if success_count == total_tests:
        print("\n🎉 TOUS LES TESTS ONT RÉUSSI!")
        return 0
    else:
        print(f"\n⚠️  {total_tests - success_count} test(s) ont échoué")
        return 1


if __name__ == "__main__":
    sys.exit(main())
