#!/usr/bin/env python3
"""
Script pour déclencher la population en production via SSH Render
"""

import subprocess
import sys
import time

def run_ssh_command(command):
    """Exécute une commande SSH sur Render"""
    ssh_host = "srv-d322gh2dbo4c73a3d4a0@ssh.frankfurt.render.com"
    full_command = f'ssh {ssh_host} "{command}"'

    print(f"Exécution: {command}")
    try:
        result = subprocess.run(full_command, shell=True, capture_output=True, text=True, timeout=300)
        print("STDOUT:", result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("Timeout de la commande")
        return False
    except Exception as e:
        print(f"Erreur: {e}")
        return False

def main():
    """Peuple la production Render"""
    print("🌿 Population Production Render avec factory_boy + Faker")
    print("=" * 60)

    # Vérifier d'abord l'état actuel
    print("📊 Vérification de l'état actuel...")
    run_ssh_command("cd /opt/render/project/src && python seeders/run.py status")

    # Exécuter le script de population
    print("\n🚀 Lancement de la population automatique...")
    success = run_ssh_command("cd /opt/render/project/src && python populate_production_auto.py")

    if success:
        print("\n✅ Population terminée ! Vérification finale...")
        run_ssh_command("cd /opt/render/project/src && python seeders/run.py status")
    else:
        print("\n❌ Erreur lors de la population")
        return False

    print("\n📋 Comptes de test disponibles:")
    print("   👤 Admin:     root@arosaje.fr     / epsi691")
    print("   🧑 User:      user@arosaje.fr     / epsi691")
    print("   🌿 Botanist:  botanist@arosaje.fr / epsi691")
    print("\n🌐 API Production: https://arosaje-backend-t2x7.onrender.com")

if __name__ == "__main__":
    main()