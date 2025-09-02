#!/usr/bin/env python3
"""
Script de migration des conseils de l'ancien vers le nouveau système
Migre les données de 'advices' vers 'plant_care_advice' avec toutes les fonctionnalités avancées
"""
import os
import sys
import psycopg2
from datetime import datetime
from pathlib import Path

# Ajouter le chemin parent pour les imports
sys.path.append(str(Path(__file__).parent.parent.parent))

def connect_db():
    """Connexion à la base de données"""
    try:
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
        conn.autocommit = False
        return conn
    except Exception as e:
        print(f"❌ Impossible de se connecter à la base: {e}")
        sys.exit(1)

def get_plant_care_mapping(cursor):
    """
    Créer une correspondance entre plant_id et plant_care_id
    En choisissant la garde la plus récente pour chaque plante
    """
    print("🔍 Analyse de la correspondance plantes <-> gardes...")
    
    query = """
    WITH latest_care AS (
        SELECT 
            plant_id,
            id as plant_care_id,
            ROW_NUMBER() OVER (PARTITION BY plant_id ORDER BY created_at DESC) as rn
        FROM plant_cares
    )
    SELECT plant_id, plant_care_id 
    FROM latest_care 
    WHERE rn = 1
    """
    
    cursor.execute(query)
    mapping = dict(cursor.fetchall())
    
    print(f"📋 {len(mapping)} correspondances plante/garde trouvées")
    return mapping

def migrate_advice_data(cursor, plant_care_mapping):
    """Migrer les données de advices vers plant_care_advices"""
    
    # 1. Récupérer tous les conseils à migrer
    cursor.execute("""
        SELECT id, texte, plant_id, botanist_id, status, created_at, updated_at
        FROM advices
        ORDER BY created_at
    """)
    
    old_advices = cursor.fetchall()
    print(f"📦 {len(old_advices)} conseils à migrer")
    
    if not old_advices:
        print("ℹ️  Aucun conseil à migrer")
        return 0
    
    migrated_count = 0
    skipped_count = 0
    
    for advice in old_advices:
        advice_id, texte, plant_id, botanist_id, status, created_at, updated_at = advice
        
        # Trouver le plant_care_id correspondant
        plant_care_id = plant_care_mapping.get(plant_id)
        
        if not plant_care_id:
            print(f"⚠️  Aucune garde trouvée pour la plante {plant_id}, conseil {advice_id} ignoré")
            skipped_count += 1
            continue
        
        try:
            # Insérer dans plant_care_advices avec les nouvelles colonnes
            insert_query = """
                INSERT INTO plant_care_advices (
                    title, content, plant_care_id, botanist_id, priority,
                    validation_status, version, is_current_version,
                    owner_notified, botanist_notified, created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """
            
            # Générer un titre basé sur le contenu
            title = texte[:100] + "..." if len(texte) > 100 else texte
            if len(title.split()) > 0:
                title = " ".join(title.split()[:8]) + "..."
            
            # Mapper le statut ancien vers nouveau
            status_mapping = {
                'PENDING': 'PENDING',
                'VALIDATED': 'VALIDATED', 
                'REJECTED': 'REJECTED'
            }
            validation_status = status_mapping.get(status, 'PENDING')
            
            cursor.execute(insert_query, (
                title,                      # title
                texte,                      # content
                plant_care_id,             # plant_care_id
                botanist_id,               # botanist_id
                'NORMAL',                  # priority (par défaut)
                validation_status,         # validation_status
                1,                         # version (première version)
                True,                      # is_current_version
                False,                     # owner_notified
                False,                     # botanist_notified
                created_at,                # created_at
                updated_at                 # updated_at
            ))
            
            migrated_count += 1
            
        except Exception as e:
            print(f"❌ Erreur lors de la migration du conseil {advice_id}: {e}")
            skipped_count += 1
            continue
    
    print(f"✅ Migration terminée:")
    print(f"   • {migrated_count} conseils migrés avec succès")
    print(f"   • {skipped_count} conseils ignorés")
    
    return migrated_count

def verify_migration(cursor):
    """Vérifier que la migration s'est bien déroulée"""
    print("\n🔍 Vérification de la migration...")
    
    # Compter les anciens conseils
    cursor.execute("SELECT COUNT(*) FROM advices")
    old_count = cursor.fetchone()[0]
    
    # Compter les nouveaux conseils
    cursor.execute("SELECT COUNT(*) FROM plant_care_advices")
    new_count = cursor.fetchone()[0]
    
    # Vérifier quelques échantillons
    cursor.execute("""
        SELECT title, content, validation_status 
        FROM plant_care_advices 
        ORDER BY created_at 
        LIMIT 3
    """)
    samples = cursor.fetchall()
    
    print(f"📊 Statistiques finales:")
    print(f"   • Conseils anciens: {old_count}")
    print(f"   • Conseils nouveaux: {new_count}")
    
    if samples:
        print(f"\n📋 Échantillons migrés:")
        for i, (title, content, status) in enumerate(samples, 1):
            print(f"   {i}. [{status}] {title}")
            print(f"      Content: {content[:50]}...")
    
    return old_count, new_count

def main():
    print("🌿 A'rosa-je - Migration des Conseils")
    print("=" * 50)
    print("Migration: advices → plant_care_advices")
    
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        # 1. Analyser la correspondance plantes/gardes
        plant_care_mapping = get_plant_care_mapping(cursor)
        
        if not plant_care_mapping:
            print("❌ Aucune garde trouvée, migration impossible")
            return
        
        # 2. Effectuer la migration
        print(f"\n🚀 Début de la migration...")
        migrated_count = migrate_advice_data(cursor, plant_care_mapping)
        
        if migrated_count > 0:
            # 3. Vérifier la migration
            old_count, new_count = verify_migration(cursor)
            
            # 4. Confirmer la transaction
            print(f"\n❓ Valider la migration? (y/N): ", end="")
            response = input().strip().lower()
            
            if response == 'y':
                conn.commit()
                print("✅ Migration confirmée et validée!")
                print("⚠️  Vous pouvez maintenant procéder à la suppression de l'ancien système")
            else:
                conn.rollback()
                print("🔄 Migration annulée, données restaurées")
        else:
            conn.rollback()
            print("❌ Aucune donnée migrée, transaction annulée")
            
    except Exception as e:
        conn.rollback()
        print(f"❌ Erreur pendant la migration: {e}")
        sys.exit(1)
        
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()