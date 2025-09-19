#!/usr/bin/env python3
"""
Dataset français ENRICHI avec données réalistes pour A'rosa-je
- Utilise les 8 vraies images de plantes
- 30+ gardes variées
- Conversations réalistes
- Conseils botaniques diversifiés
- Rapports détaillés
"""

import base64
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import random

# Configuration database
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://neondb_owner:Eh4SSpPaFHhx@ep-spring-bonus-agd7s9t1-pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require')

# Imports des modèles
from models.user import User, UserRole
from models.plant import Plant
from models.plant_care import PlantCare, CareStatus
from models.advice import Advice, AdvicePriority, ValidationStatus
from models.care_report import CareReport, HealthLevel
from utils.password import get_password_hash

def image_to_base64(image_path):
    """Convertit une image en data URL base64"""
    try:
        with open(image_path, 'rb') as f:
            data = f.read()

        # Déterminer l'extension
        ext = os.path.splitext(image_path)[1].lower()
        mime_type = 'image/jpeg' if ext == '.jpg' else 'image/png'

        # Encoder en base64
        b64_data = base64.b64encode(data).decode('utf-8')

        return f'data:{mime_type};base64,{b64_data}'
    except Exception as e:
        print(f'Erreur conversion image {image_path}: {e}')
        return None

def create_rich_french_dataset():
    """Crée un dataset français enrichi avec beaucoup de données réalistes"""

    print('Creation du dataset francais ENRICHI pour A\'rosa-je...')

    # Configuration database
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)

    with Session() as db:
        # === NETTOYAGE (garde les utilisateurs existants) ===
        print('Nettoyage des donnees (garde les utilisateurs)...')

        db.execute(text('DELETE FROM care_reports'))
        db.execute(text('DELETE FROM advices'))
        db.execute(text('DELETE FROM plant_cares'))
        db.execute(text('DELETE FROM plants'))
        db.commit()

        # === RÉCUPÉRATION UTILISATEURS EXISTANTS ===
        print('Recuperation des utilisateurs existants...')
        users_existants = db.query(User).all()
        print(f'   {len(users_existants)} utilisateurs existants recuperes')

        # === CRÉATION NOUVEAUX UTILISATEURS DIVERSIFIÉS ===
        print('Creation de nouveaux utilisateurs diversifies...')

        nouveaux_users = [
            # Propriétaires additionnels
            User(email='alexandra.martin@gmail.com', password_hash=get_password_hash('motdepasse123'), first_name='Alexandra', last_name='Martin', role=UserRole.USER, is_verified=True),
            User(email='thomas.bernard@yahoo.fr', password_hash=get_password_hash('motdepasse123'), first_name='Thomas', last_name='Bernard', role=UserRole.USER, is_verified=True),
            User(email='emma.petit@hotmail.com', password_hash=get_password_hash('motdepasse123'), first_name='Emma', last_name='Petit', role=UserRole.USER, is_verified=True),
            User(email='louis.garcia@gmail.com', password_hash=get_password_hash('motdepasse123'), first_name='Louis', last_name='Garcia', role=UserRole.USER, is_verified=True),
            User(email='chloe.roux@outlook.fr', password_hash=get_password_hash('motdepasse123'), first_name='Chloé', last_name='Roux', role=UserRole.USER, is_verified=True),

            # Gardiens additionnels
            User(email='maxime.lambert@gmail.com', password_hash=get_password_hash('motdepasse123'), first_name='Maxime', last_name='Lambert', role=UserRole.USER, is_verified=True),
            User(email='lea.moreau@yahoo.fr', password_hash=get_password_hash('motdepasse123'), first_name='Léa', last_name='Moreau', role=UserRole.USER, is_verified=True),
            User(email='hugo.fournier@gmail.com', password_hash=get_password_hash('motdepasse123'), first_name='Hugo', last_name='Fournier', role=UserRole.USER, is_verified=True),
            User(email='clara.michel@hotmail.fr', password_hash=get_password_hash('motdepasse123'), first_name='Clara', last_name='Michel', role=UserRole.USER, is_verified=True),
            User(email='antoine.lefebvre@outlook.com', password_hash=get_password_hash('motdepasse123'), first_name='Antoine', last_name='Lefebvre', role=UserRole.USER, is_verified=True),

            # Botanistes additionnels
            User(email='dr.marine.dupuis@jardin-toulouse.fr', password_hash=get_password_hash('botaniste123'), first_name='Marine', last_name='Dupuis', role=UserRole.BOTANIST, is_verified=True),
            User(email='prof.julien.blanc@bio-montpellier.edu', password_hash=get_password_hash('botaniste123'), first_name='Julien', last_name='Blanc', role=UserRole.BOTANIST, is_verified=True),
        ]

        for user in nouveaux_users:
            db.add(user)

        db.commit()
        for user in nouveaux_users:
            db.refresh(user)

        print(f'   {len(nouveaux_users)} nouveaux utilisateurs crees')

        # === RÉCUPÉRATION TOUS LES UTILISATEURS ===
        tous_users = db.query(User).all()
        proprietaires = [u for u in tous_users if u.role == UserRole.USER][:8]  # 8 propriétaires
        gardiens = [u for u in tous_users if u.role == UserRole.USER][-8:]      # 8 gardiens (peut se chevaucher)
        botanistes = [u for u in tous_users if u.role == UserRole.BOTANIST]

        print(f'   Total: {len(proprietaires)} proprietaires, {len(gardiens)} gardiens, {len(botanistes)} botanistes')

        # === PLANTES AVEC TOUTES LES 8 IMAGES ===
        print('Creation des plantes avec les 8 vraies images...')

        # Conversion des 8 images
        images = {
            'monstera': image_to_base64('/app/assets/plants/c30fa0f2-f6f5-49ae-831d-db6f2e101156.jpg'),
            'ficus': image_to_base64('/app/assets/plants/f7250849-a325-4d8f-aff0-6938a440c4ab.jpg'),
            'sansevieria': image_to_base64('/app/assets/plants/b928e83d-d68e-4be2-af5d-53a37c589f92.jpg'),
            'pothos': image_to_base64('/app/assets/plants/3ec6b4c8-f0bd-44e5-929e-3000b28e891c.jpg'),  # 8ème image !
            'philodendron': image_to_base64('/app/assets/plants/fe70ee54-62c7-49ff-a1cc-ed1cbf7b0092.jpg'),
            'palmier': image_to_base64('/app/assets/plants/plante-de-palmier-en-pot.jpg'),
            'strelitzia': image_to_base64('/app/assets/plants/11471878.png'),
            'cactus': image_to_base64('/app/assets/plants/11471877.png'),
        }

        fallback_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

        # 20+ plantes variées
        plantes_enrichies = [
            # Plantes originales améliorées
            Plant(nom='Monstera de Mamie', espece='Monstera deliciosa', name='Monstera de Mamie', species='Monstera deliciosa', photo_base64=images['monstera'] or fallback_image, owner_id=proprietaires[0].id),
            Plant(nom='Ficus Benjamina "Léon"', espece='Ficus benjamina', name='Ficus Benjamina "Léon"', species='Ficus benjamina', photo_base64=images['ficus'] or fallback_image, owner_id=proprietaires[0].id),
            Plant(nom='Langue de Belle-Mère', espece='Sansevieria trifasciata', name='Langue de Belle-Mère', species='Sansevieria trifasciata', photo_base64=images['sansevieria'] or fallback_image, owner_id=proprietaires[1].id),
            Plant(nom='Lierre du Diable', espece='Epipremnum aureum', name='Lierre du Diable', species='Epipremnum aureum', photo_base64=images['pothos'] or fallback_image, owner_id=proprietaires[1].id),
            Plant(nom='Philodendron "Cœur"', espece='Philodendron hederaceum', name='Philodendron "Cœur"', species='Philodendron hederaceum', photo_base64=images['philodendron'] or fallback_image, owner_id=proprietaires[2].id),
            Plant(nom='Palmier Nain du Salon', espece='Chamaedorea elegans', name='Palmier Nain du Salon', species='Chamaedorea elegans', photo_base64=images['palmier'] or fallback_image, owner_id=proprietaires[2].id),
            Plant(nom='Oiseau de Paradis', espece='Strelitzia reginae', name='Oiseau de Paradis', species='Strelitzia reginae', photo_base64=images['strelitzia'] or fallback_image, owner_id=proprietaires[3].id),
            Plant(nom='Cactus de Bureau', espece='Echinopsis chamaecereus', name='Cactus de Bureau', species='Echinopsis chamaecereus', photo_base64=images['cactus'] or fallback_image, owner_id=proprietaires[3].id),

            # Plantes additionnelles pour varier
            Plant(nom='Monstera "Fenêtres"', espece='Monstera deliciosa', name='Monstera "Fenêtres"', species='Monstera deliciosa', photo_base64=images['monstera'] or fallback_image, owner_id=proprietaires[4].id),
            Plant(nom='Ficus "Elastica"', espece='Ficus elastica', name='Ficus "Elastica"', species='Ficus elastica', photo_base64=images['ficus'] or fallback_image, owner_id=proprietaires[4].id),
            Plant(nom='Sansevieria "Cylindrica"', espece='Sansevieria cylindrica', name='Sansevieria "Cylindrica"', species='Sansevieria cylindrica', photo_base64=images['sansevieria'] or fallback_image, owner_id=proprietaires[5].id),
            Plant(nom='Pothos Doré', espece='Epipremnum aureum', name='Pothos Doré', species='Epipremnum aureum', photo_base64=images['pothos'] or fallback_image, owner_id=proprietaires[5].id),
            Plant(nom='Philodendron "Brasil"', espece='Philodendron hederaceum', name='Philodendron "Brasil"', species='Philodendron hederaceum', photo_base64=images['philodendron'] or fallback_image, owner_id=proprietaires[6].id),
            Plant(nom='Palmier Areca', espece='Dypsis lutescens', name='Palmier Areca', species='Dypsis lutescens', photo_base64=images['palmier'] or fallback_image, owner_id=proprietaires[6].id),
            Plant(nom='Strelitzia "Nicolai"', espece='Strelitzia nicolai', name='Strelitzia "Nicolai"', species='Strelitzia nicolai', photo_base64=images['strelitzia'] or fallback_image, owner_id=proprietaires[7].id),
            Plant(nom='Cactus "Barrel"', espece='Echinocactus grusonii', name='Cactus "Barrel"', species='Echinocactus grusonii', photo_base64=images['cactus'] or fallback_image, owner_id=proprietaires[7].id),
        ]

        for plante in plantes_enrichies:
            db.add(plante)

        db.commit()
        for plante in plantes_enrichies:
            db.refresh(plante)

        print(f'   {len(plantes_enrichies)} plantes creees avec les 8 vraies images !')

        # === CRÉATION DE 30+ GARDES VARIÉES ===
        print('🏠 Création de 30+ gardes variées...')

        # Dates variées
        today = datetime.now()

        gardes_enrichies = []

        # Créer 35 gardes avec statuts et dates variés
        for i in range(35):
            plante = random.choice(plantes_enrichies)
            proprietaire = next(u for u in proprietaires if u.id == plante.owner_id)
            gardien = random.choice(gardiens)

            # Dates variées
            if i < 5:  # Gardes terminées récemment
                start_date = today - timedelta(days=random.randint(15, 45))
                end_date = start_date + timedelta(days=random.randint(3, 14))
                status = CareStatus.COMPLETED
                caretaker_id = gardien.id
            elif i < 10:  # Gardes en cours
                start_date = today - timedelta(days=random.randint(1, 5))
                end_date = today + timedelta(days=random.randint(5, 15))
                status = CareStatus.IN_PROGRESS
                caretaker_id = gardien.id
            elif i < 15:  # Gardes acceptées (futures)
                start_date = today + timedelta(days=random.randint(1, 10))
                end_date = start_date + timedelta(days=random.randint(7, 21))
                status = CareStatus.ACCEPTED
                caretaker_id = gardien.id
            elif i < 25:  # Gardes en attente
                start_date = today + timedelta(days=random.randint(3, 30))
                end_date = start_date + timedelta(days=random.randint(5, 20))
                status = CareStatus.PENDING
                caretaker_id = None
            else:  # Quelques annulées
                start_date = today + timedelta(days=random.randint(1, 20))
                end_date = start_date + timedelta(days=random.randint(7, 14))
                status = CareStatus.CANCELLED
                caretaker_id = gardien.id if random.choice([True, False]) else None

            instructions_variees = [
                f"Arrosage modéré pour {plante.nom}. Attention à ne pas trop arroser !",
                f"Cette {plante.espece} aime la lumière indirecte. Vaporiser les feuilles occasionnellement.",
                f"Garde facile ! {plante.nom} est très résistante. Arrosage une fois par semaine.",
                f"Plante capricieuse ! {plante.nom} n'aime pas les courants d'air. Placer dans un endroit stable.",
                f"Garde d'urgence pour {plante.nom}. Partir en voyage imprévu !",
                f"Première garde pour cette {plante.espece}. Suivre les instructions à la lettre SVP.",
                f"Plante précieuse ! {plante.nom} est un cadeau de ma grand-mère. Prendre soin s'il vous plaît.",
            ]

            lieux_varies = [
                "12 rue de la République, 69001 Lyon",
                "25 avenue Jean Jaurès, 31000 Toulouse",
                "8 promenade des Anglais, 06000 Nice",
                "45 rue de Rivoli, 75001 Paris",
                "33 cours Mirabeau, 13100 Aix-en-Provence",
                "18 place Bellecour, 69002 Lyon",
                "67 rue Sainte-Catherine, 33000 Bordeaux",
                "21 place Stanislas, 54000 Nancy",
            ]

            garde = PlantCare(
                plant_id=plante.id,
                owner_id=proprietaire.id,
                caretaker_id=caretaker_id,
                start_date=start_date,
                end_date=end_date,
                care_instructions=random.choice(instructions_variees),
                location=random.choice(lieux_varies),
                status=status
            )

            gardes_enrichies.append(garde)

        for garde in gardes_enrichies:
            db.add(garde)

        db.commit()
        for garde in gardes_enrichies:
            db.refresh(garde)

        print(f'   {len(gardes_enrichies)} gardes creees avec statuts varies !')

        # === CONSEILS BOTANIQUES ENRICHIS ===
        print('💡 Création de conseils botaniques enrichis...')

        conseils_enrichis = []

        # Sélectionner des gardes pour les conseils
        gardes_pour_conseils = random.sample(gardes_enrichies, min(20, len(gardes_enrichies)))

        conseils_templates = [
            {
                'title': 'Diagnostic de santé général',
                'content': 'La plante présente un bon état général. Les feuilles sont bien vertes et fermes. Continuez l\'arrosage actuel et surveillez l\'exposition à la lumière.',
                'priority': AdvicePriority.NORMAL,
                'validation_status': ValidationStatus.VALIDATED
            },
            {
                'title': 'ATTENTION - Signes de sur-arrosage',
                'content': 'Je constate des signes de sur-arrosage : jaunissement des feuilles et terre humide en permanence. RÉDUIRE immédiatement la fréquence d\'arrosage.',
                'priority': AdvicePriority.URGENT,
                'validation_status': ValidationStatus.PENDING
            },
            {
                'title': 'Recommandations d\'entretien',
                'content': 'Excellente garde ! Pour l\'avenir, cette espèce bénéficiera d\'un engrais liquide dilué une fois par mois pendant la période de croissance.',
                'priority': AdvicePriority.FOLLOW_UP,
                'validation_status': ValidationStatus.VALIDATED
            },
            {
                'title': 'Problème d\'exposition lumineuse',
                'content': 'Les feuilles montrent des signes d\'étiolement. Cette plante a besoin de plus de lumière indirecte. Déplacer près d\'une fenêtre sans soleil direct.',
                'priority': AdvicePriority.NORMAL,
                'validation_status': ValidationStatus.PENDING
            },
            {
                'title': 'Parasites détectés',
                'content': 'URGENT : Présence de petits insectes sur les feuilles. Traiter immédiatement avec un savon insecticide dilué. Isoler la plante si possible.',
                'priority': AdvicePriority.URGENT,
                'validation_status': ValidationStatus.VALIDATED
            }
        ]

        for i, garde in enumerate(gardes_pour_conseils):
            template = random.choice(conseils_templates)
            botaniste = random.choice(botanistes)
            validateur = random.choice(botanistes) if template['validation_status'] == ValidationStatus.VALIDATED else None

            conseil = Advice(
                plant_care_id=garde.id,
                botanist_id=botaniste.id,
                title=template['title'],
                content=template['content'],
                priority=template['priority'],
                version=1,
                is_current_version=True,
                validation_status=template['validation_status'],
                validator_id=validateur.id if validateur else None,
                validated_at=datetime.now() - timedelta(hours=random.randint(1, 48)) if validateur else None,
                validation_comment="Diagnostic précis et recommandations appropriées." if validateur else None
            )

            conseils_enrichis.append(conseil)

        for conseil in conseils_enrichis:
            db.add(conseil)

        db.commit()
        print(f'   {len(conseils_enrichis)} conseils botaniques crees !')

        # === RAPPORTS DE GARDE ENRICHIS ===
        print('📋 Création de rapports de garde enrichis...')

        rapports_enrichis = []

        # Rapports pour gardes en cours et terminées
        gardes_avec_rapports = [g for g in gardes_enrichies if g.status in [CareStatus.IN_PROGRESS, CareStatus.COMPLETED] and g.caretaker_id]

        descriptions_rapports = [
            "Tout va parfaitement bien ! La plante semble très heureuse. Arrosage effectué comme prévu.",
            "Petite inquiétude : quelques feuilles jaunissent. J'ai réduit l'arrosage par précaution.",
            "Excellente semaine ! La plante a même fait de nouvelles pousses. Très gratifiant !",
            "RAS, entretien de routine effectué. La plante est stable et en bonne santé.",
            "J'ai remarqué que la plante penche vers la fenêtre. Je l'ai tournée pour une croissance uniforme.",
            "Week-end pluvieux, j'ai rentré la plante qui était sur le balcon. Bonne décision !",
            "Garde terminée avec succès ! J'ai adoré m'occuper de cette belle plante.",
        ]

        for garde in random.sample(gardes_avec_rapports, min(15, len(gardes_avec_rapports))):
            for i in range(random.randint(1, 3)):  # 1 à 3 rapports par garde
                rapport = CareReport(
                    plant_care_id=garde.id,
                    caretaker_id=garde.caretaker_id,
                    session_date=garde.start_date + timedelta(days=random.randint(0, 7)),
                    description=random.choice(descriptions_rapports),
                    photo_base64=random.choice(list(images.values())),
                    health_level=random.choice([HealthLevel.BON, HealthLevel.MOYEN, HealthLevel.EXCELLENT]),
                    hydration_level=random.choice([HealthLevel.BON, HealthLevel.MOYEN]),
                    vitality_level=random.choice([HealthLevel.BON, HealthLevel.EXCELLENT])
                )
                rapports_enrichis.append(rapport)

        for rapport in rapports_enrichis:
            db.add(rapport)

        db.commit()
        print(f'   {len(rapports_enrichis)} rapports de garde crees !')

        # === RÉSUMÉ FINAL ===
        print('\n🎉 Dataset français ENRICHI créé avec succès !')
        print(f'''
Resume des donnees enrichies :
   Utilisateurs : {len(tous_users)} (proprietaires, gardiens, botanistes, admin)
   Plantes : {len(plantes_enrichies)} avec les 8 vraies images
   🏠 Gardes : {len(gardes_enrichies)} (tous statuts variés)
   💡 Conseils : {len(conseils_enrichis)} (validés, urgents, suivi)
   📋 Rapports : {len(rapports_enrichis)} de garde détaillés

🔐 Comptes de test enrichis :
   🔑 Admin : root@arosaje.fr / epsi691
   👩 Propriétaires : marie.dubois@email.fr, alexandra.martin@gmail.com, etc.
   🧑 Gardiens : lucas.petit@email.fr, maxime.lambert@gmail.com, etc.
   Botanistes : dr.claire.moreau@jardin-botanique.fr, dr.marine.dupuis@jardin-toulouse.fr, etc.

Les 8 images utilisees :
   • Monstera, Ficus, Sansevieria, Pothos (8ème !)
   • Philodendron, Palmier, Strelitzia, Cactus

L'application est maintenant VIVANTE avec des données réalistes ! 🚀
        ''')

if __name__ == "__main__":
    create_rich_french_dataset()