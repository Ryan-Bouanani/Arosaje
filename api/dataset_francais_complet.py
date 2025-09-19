#!/usr/bin/env python3
"""
Dataset complet en français pour A'rosa-je
Utilisateurs, plantes, gardes, conseils, rapports - tout en français !
"""

import sys
sys.path.append('/app')

import base64
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import os

# Models
from models.user import User, UserRole
from models.plant import Plant
from models.plant_care import PlantCare, CareStatus
from models.advice import Advice, AdvicePriority, ValidationStatus
from models.care_report import CareReport, HealthLevel
from utils.password import get_password_hash

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://neondb_owner:npg_nSZE6jjB7cgm@ep-spring-bonus-agd7s9t1-pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def image_to_base64(image_path):
    """Convert image file to base64 string"""
    try:
        with open(image_path, 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            ext = image_path.split('.')[-1].lower()
            mime_type = f"image/{ext}" if ext in ['jpg', 'jpeg', 'png', 'gif'] else "image/jpeg"
            return f"data:{mime_type};base64,{encoded_string}"
    except Exception as e:
        print(f"   ⚠️ Erreur conversion {image_path}: {e}")
        return None


def create_french_dataset():
    """Créer un dataset complet en français"""
    db = SessionLocal()

    try:
        print('🇫🇷 Création du dataset français complet pour A\'rosa-je...')

        # === NETTOYAGE PARTIEL ===
        print('🗑️ Nettoyage des données (garde les utilisateurs)...')

        # Supprimer seulement les données, pas les utilisateurs
        db.query(CareReport).delete()
        db.query(Advice).delete()
        db.query(PlantCare).delete()
        db.query(Plant).delete()
        # Garder TOUS les utilisateurs existants
        db.commit()

        # === RÉCUPÉRATION DES UTILISATEURS EXISTANTS ===
        print('👥 Récupération des utilisateurs existants...')

        # Récupérer tous les utilisateurs existants
        tous_users = db.query(User).all()

        # Séparer par rôle pour attribution des plantes
        proprietaires = [u for u in tous_users if u.role == UserRole.USER][:3]  # Prendre max 3 users
        botanistes = [u for u in tous_users if u.role == UserRole.BOTANIST][:2]  # Prendre max 2 botanistes
        gardiens = proprietaires  # Les users peuvent être gardiens aussi

        # Si pas assez d'utilisateurs, utiliser les premiers disponibles
        if not proprietaires:
            proprietaires = tous_users[:3] if len(tous_users) >= 3 else tous_users
        if not botanistes:
            botanistes = tous_users[:2] if len(tous_users) >= 2 else tous_users
        if not gardiens:
            gardiens = tous_users

        print(f'   ✅ {len(tous_users)} utilisateurs existants récupérés')

        # === PLANTES FRANÇAISES AVEC VRAIES IMAGES ===
        print('🌿 Création des plantes françaises avec images...')

        # Conversion des images
        images = {
            'monstera': image_to_base64('/app/assets/plants/b928e83d-d68e-4be2-af5d-53a37c589f92.jpg'),
            'sansevieria': image_to_base64('/app/assets/plants/11471877.png'),
            'pothos': image_to_base64('/app/assets/plants/fe70ee54-62c7-49ff-a1cc-ed1cbf7b0092.jpg'),
            'strelitzia': image_to_base64('/app/assets/plants/11471878.png'),
            'philodendron': image_to_base64('/app/assets/plants/c30fa0f2-f6f5-49ae-831d-db6f2e101156.jpg'),
            'palmier': image_to_base64('/app/assets/plants/f7250849-a325-4d8f-aff0-6938a440c4ab.jpg'),
            'dracaena': image_to_base64('/app/assets/plants/plante-de-palmier-en-pot.jpg')
        }

        fallback_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

        plantes_francaises = [
            # Plantes de Marie (Lyon)
            Plant(
                nom='Monstera de Mamie',
                espece='Monstera deliciosa',
                name='Monstera de Mamie',
                species='Monstera deliciosa',
                photo_base64=images['monstera'] or fallback_image,
                owner_id=proprietaires[0].id
            ),
            Plant(
                nom='Ficus Benjamina "Léon"',
                espece='Ficus benjamina',
                name='Ficus Benjamina "Léon"',
                species='Ficus benjamina',
                photo_base64=images['strelitzia'] or fallback_image,
                owner_id=proprietaires[0].id
            ),

            # Plantes de Pierre (Toulouse)
            Plant(
                nom='Langue de Belle-Mère',
                espece='Sansevieria trifasciata',
                name='Langue de Belle-Mère',
                species='Sansevieria trifasciata',
                photo_base64=images['sansevieria'] or fallback_image,
                owner_id=proprietaires[1].id
            ),
            Plant(
                nom='Lierre du Diable',
                espece='Epipremnum aureum',
                name='Lierre du Diable',
                species='Epipremnum aureum',
                photo_base64=images['pothos'] or fallback_image,
                owner_id=proprietaires[1].id
            ),

            # Plantes de Sophie (Nice)
            Plant(
                nom='Philodendron "Coeur"',
                espece='Philodendron hederaceum',
                name='Philodendron "Coeur"',
                species='Philodendron hederaceum',
                photo_base64=images['philodendron'] or fallback_image,
                owner_id=proprietaires[2].id
            ),
            Plant(
                nom='Palmier Nain du Salon',
                espece='Chamaedorea elegans',
                name='Palmier Nain du Salon',
                species='Chamaedorea elegans',
                photo_base64=images['palmier'] or fallback_image,
                owner_id=proprietaires[2].id
            ),
            Plant(
                nom='Dragon Tree "Yuki"',
                espece='Dracaena marginata',
                name='Dragon Tree "Yuki"',
                species='Dracaena marginata',
                photo_base64=images['dracaena'] or fallback_image,
                owner_id=proprietaires[2].id
            )
        ]

        for plante in plantes_francaises:
            db.add(plante)

        db.commit()
        for plante in plantes_francaises:
            db.refresh(plante)

        print(f'   ✅ {len(plantes_francaises)} plantes créées avec vraies images !')

        # === GARDES DE PLANTES ===
        print('🏠 Création des gardes de plantes...')

        gardes = [
            # Garde en cours - Marie laisse ses plantes à Lucas
            PlantCare(
                plant_id=plantes_francaises[0].id,  # Monstera de Mamie
                owner_id=proprietaires[0].id,  # Marie
                caretaker_id=gardiens[0].id,  # Lucas
                start_date=datetime.now() - timedelta(days=3),
                end_date=datetime.now() + timedelta(days=4),
                care_instructions='Arrosage une fois par semaine, vaporiser les feuilles. Attention, Mamie tient beaucoup à cette plante ! Elle n\'aime pas trop de soleil direct.',
                location='12 rue de la République, 69001 Lyon',
                status=CareStatus.IN_PROGRESS
            ),

            # Garde urgente - Ficus de Marie en urgence
            PlantCare(
                plant_id=plantes_francaises[1].id,  # Ficus Léon
                owner_id=proprietaires[0].id,  # Marie
                start_date=datetime.now() + timedelta(days=1),
                end_date=datetime.now() + timedelta(days=10),
                care_instructions='URGENT ! Départ imprévu en vacances. Léon a besoin d\'eau régulière mais pas trop. Il perd ses feuilles quand il est stressé.',
                location='12 rue de la République, 69001 Lyon',
                status=CareStatus.PENDING
            ),

            # Garde acceptée - Pierre confie à Camille
            PlantCare(
                plant_id=plantes_francaises[2].id,  # Sansevieria
                owner_id=proprietaires[1].id,  # Pierre
                caretaker_id=gardiens[1].id,  # Camille
                start_date=datetime.now() + timedelta(days=5),
                end_date=datetime.now() + timedelta(days=12),
                care_instructions='Très facile ! Arrosage minimal, une fois toutes les 2 semaines maximum. Résistante à tout.',
                location='25 allée Jean Jaurès, 31000 Toulouse',
                status=CareStatus.ACCEPTED
            ),

            # Garde terminée avec succès
            PlantCare(
                plant_id=plantes_francaises[4].id,  # Philodendron
                owner_id=proprietaires[2].id,  # Sophie
                caretaker_id=gardiens[0].id,  # Lucas
                start_date=datetime.now() - timedelta(days=14),
                end_date=datetime.now() - timedelta(days=2),
                care_instructions='Philodendron facile, arrosage quand la terre sèche. Aime la lumière tamisée.',
                location='8 promenade des Anglais, 06000 Nice',
                status=CareStatus.COMPLETED
            )
        ]

        for garde in gardes:
            db.add(garde)

        db.commit()
        for garde in gardes:
            db.refresh(garde)

        print(f'   ✅ {len(gardes)} gardes créées (en cours, urgente, acceptée, terminée)')

        # === CONSEILS BOTANIQUES ===
        print('💡 Création des conseils botaniques...')

        conseils = [
            # Conseil validé pour le Monstera
            Advice(
                plant_care_id=gardes[0].id,
                botanist_id=botanistes[0].id,  # Dr Claire
                title='Entretien optimal du Monstera',
                content='Votre Monstera "de Mamie" est magnifique ! Les fenestrations (trous dans les feuilles) indiquent une plante mature et en bonne santé. Continuez l\'arrosage hebdomadaire et la vaporisation. Attention aux courants d\'air qui peuvent stresser la plante.',
                priority=AdvicePriority.NORMAL,
                version=1,
                is_current_version=True,
                validation_status=ValidationStatus.VALIDATED,
                validator_id=botanistes[1].id,  # Prof Jean
                validated_at=datetime.now() - timedelta(hours=6),
                validation_comment='Diagnostic excellent et complet. Recommandations parfaitement adaptées.'
            ),

            # Conseil urgent en attente
            Advice(
                plant_care_id=gardes[1].id,
                botanist_id=botanistes[1].id,  # Prof Jean
                title='URGENT - Diagnostic chute des feuilles',
                content='La chute de feuilles du Ficus "Léon" est typique du stress de déplacement. IMPORTANT : évitez l\'arrosage excessif qui aggraverait le problème. Placez-le dans un endroit stable, lumière indirecte, et attendez qu\'il s\'adapte. Les nouvelles pousses indiqueront sa récupération.',
                priority=AdvicePriority.URGENT,
                version=1,
                is_current_version=True,
                validation_status=ValidationStatus.PENDING
            ),

            # Conseil de suivi pour garde terminée
            Advice(
                plant_care_id=gardes[3].id,
                botanist_id=botanistes[0].id,  # Dr Claire
                title='Bilan de garde - Philodendron',
                content='Excellente garde ! Le Philodendron présente une croissance active avec de nouvelles feuilles bien formées. Le gardien a parfaitement respecté les consignes d\'arrosage. Conseil pour la suite : rempoter dans 6 mois avec un terreau drainant.',
                priority=AdvicePriority.FOLLOW_UP,
                version=1,
                is_current_version=True,
                validation_status=ValidationStatus.VALIDATED,
                validator_id=botanistes[1].id,
                validated_at=datetime.now() - timedelta(days=1),
                validation_comment='Bilan complet et recommandations pertinentes pour l\'avenir.'
            )
        ]

        for conseil in conseils:
            db.add(conseil)

        db.commit()
        print(f'   ✅ {len(conseils)} conseils botaniques créés')

        # === RAPPORTS DE GARDE ===
        print('📋 Création des rapports de garde...')

        rapports = [
            # Rapport pour la garde en cours
            CareReport(
                plant_care_id=gardes[0].id,
                caretaker_id=gardiens[0].id,  # Lucas
                description='Tout va bien pour le Monstera de Mamie ! Arrosage effectué lundi comme convenu. Les feuilles sont bien vertes et brillantes. J\'ai vaporisé délicatement et tourné le pot d\'un quart pour une exposition uniforme. Aucun signe de stress.',
                photo_base64=images['monstera'] or fallback_image,
                health_level=HealthLevel.BON,
                hydration_level=HealthLevel.BON,
                vitality_level=HealthLevel.BON
            ),

            # Rapport pour la garde terminée
            CareReport(
                plant_care_id=gardes[3].id,
                caretaker_id=gardiens[0].id,  # Lucas
                description='Garde terminée avec succès ! Le Philodendron a été arrosé 3 fois pendant les 2 semaines. J\'ai remarqué 2 nouvelles feuilles qui ont poussé. La plante était très facile à entretenir. Sophie peut être rassurée !',
                photo_base64=images['philodendron'] or fallback_image,
                health_level=HealthLevel.BON,
                hydration_level=HealthLevel.BON,
                vitality_level=HealthLevel.BON
            )
        ]

        for rapport in rapports:
            db.add(rapport)

        db.commit()
        print(f'   ✅ {len(rapports)} rapports de garde créés')

        print('\n🎉 Dataset français complet créé avec succès !')

        print('\n📊 Résumé des données :')
        print(f'   👥 Utilisateurs : {len(tous_users) + 1} (propriétaires, gardiens, botanistes, admin)')
        print(f'   🌿 Plantes : {len(plantes_francaises)} avec vraies images')
        print(f'   🏠 Gardes : {len(gardes)} (tous statuts)')
        print(f'   💡 Conseils : {len(conseils)} (validés, urgents, suivi)')
        print(f'   📋 Rapports : {len(rapports)} de garde')

        print('\n🔐 Comptes de test :')
        print('   🔑 Admin : root@arosaje.fr / epsi691')
        print('   👩 Propriétaire : marie.dubois@email.fr / motdepasse123')
        print('   👨 Propriétaire : pierre.martin@email.fr / motdepasse123')
        print('   👩 Propriétaire : sophie.bernard@email.fr / motdepasse123')
        print('   🧑 Gardien : lucas.petit@email.fr / motdepasse123')
        print('   👩 Gardienne : camille.rousseau@email.fr / motdepasse123')
        print('   🌿 Botaniste : dr.claire.moreau@jardin-botanique.fr / botaniste123')
        print('   🌿 Botaniste : prof.jean.forestier@universite.fr / botaniste123')

        print('\n🌱 Plantes avec vraies images :')
        print('   • Monstera de Mamie (Marie)')
        print('   • Ficus Benjamina "Léon" (Marie)')
        print('   • Langue de Belle-Mère (Pierre)')
        print('   • Lierre du Diable (Pierre)')
        print('   • Philodendron "Coeur" (Sophie)')
        print('   • Palmier Nain du Salon (Sophie)')
        print('   • Dragon Tree "Yuki" (Sophie)')

    except Exception as e:
        db.rollback()
        print(f'❌ Erreur : {e}')
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_french_dataset()