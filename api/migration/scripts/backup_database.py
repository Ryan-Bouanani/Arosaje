#!/usr/bin/env python3
"""
Script de backup de la base de données avant migration des conseils
"""
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

def create_backup():
    """Créer un backup complet de la base de données PostgreSQL"""
    
    # Configuration de la base de données (à adapter selon l'environnement)
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'arosaje_db')
    DB_USER = os.getenv('DB_USER', 'arosaje')
    
    # Créer le dossier de backup s'il n'existe pas
    backup_dir = Path(__file__).parent.parent.parent / 'backups'
    backup_dir.mkdir(exist_ok=True)
    
    # Nom du fichier de backup avec timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = backup_dir / f'arosaje_backup_before_advice_migration_{timestamp}.sql'
    
    try:
        print(f"🚀 Création du backup de la base de données...")
        print(f"📁 Fichier: {backup_file}")
        
        # Commande pg_dump
        cmd = [
            'pg_dump',
            '-h', DB_HOST,
            '-p', DB_PORT,
            '-U', DB_USER,
            '-d', DB_NAME,
            '--no-password',  # Utilise la variable PGPASSWORD
            '--verbose',
            '--clean',
            '--if-exists',
            '--create',
            '-f', str(backup_file)
        ]
        
        # Exécuter la commande
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        print(f"✅ Backup créé avec succès!")
        print(f"📊 Taille du fichier: {backup_file.stat().st_size / 1024 / 1024:.2f} MB")
        
        # Vérifier le contenu du backup
        with open(backup_file, 'r') as f:
            first_lines = f.readlines()[:10]
            if any('CREATE' in line or 'INSERT' in line for line in first_lines):
                print("✅ Le backup contient des données")
            else:
                print("⚠️  Attention: Le backup semble vide")
        
        return str(backup_file)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de la création du backup:")
        print(f"Exit code: {e.returncode}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        sys.exit(1)

def verify_tables():
    """Vérifier l'existence des tables avant migration"""
    print("\n🔍 Vérification des tables existantes...")
    
    try:
        # Se connecter à la base pour vérifier les tables
        import psycopg2
        
        DB_HOST = os.getenv('DB_HOST', 'localhost')
        DB_PORT = os.getenv('DB_PORT', '5432')
        DB_NAME = os.getenv('DB_NAME', 'arosaje_db')
        DB_USER = os.getenv('DB_USER', 'arosaje')
        DB_PASSWORD = os.getenv('DB_PASSWORD', '')
        
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        
        cursor = conn.cursor()
        
        # Vérifier les tables advice
        cursor.execute("SELECT COUNT(*) FROM advices;")
        advice_count = cursor.fetchone()[0]
        print(f"📋 Table 'advices': {advice_count} enregistrements")
        
        # Vérifier les tables plant_care_advice
        cursor.execute("SELECT COUNT(*) FROM plant_care_advices;")
        plant_care_advice_count = cursor.fetchone()[0]
        print(f"📋 Table 'plant_care_advices': {plant_care_advice_count} enregistrements")
        
        cursor.close()
        conn.close()
        
        return advice_count, plant_care_advice_count
        
    except Exception as e:
        print(f"⚠️  Impossible de vérifier les tables: {e}")
        return None, None

if __name__ == "__main__":
    print("🌿 A'rosa-je - Script de Backup avant Migration")
    print("=" * 50)
    
    # Vérifier les tables
    advice_count, plant_care_count = verify_tables()
    
    if advice_count is not None:
        print(f"\n📊 Résumé:")
        print(f"   • {advice_count} conseils dans l'ancien système")
        print(f"   • {plant_care_count} conseils dans le nouveau système")
        print(f"   • Migration nécessaire: {advice_count > 0}")
    
    # Créer le backup
    backup_file = create_backup()
    
    print(f"\n🎉 Backup terminé avec succès!")
    print(f"📁 Fichier sauvegardé: {backup_file}")
    print(f"⚠️  Conserver ce fichier précieusement avant de continuer la migration!")