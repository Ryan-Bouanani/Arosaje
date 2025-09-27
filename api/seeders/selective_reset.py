#!/usr/bin/env python3
"""
Script de reset sélectif pour A'rosa-je
Préserve uniquement les 5 comptes spécifiés et reset toutes les autres données
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.database import SessionLocal
from models.user import User
from models.plant import Plant
from models.plant_care import PlantCare
from models.care_report import CareReport
from models.advice import Advice
from models.message import Message, Conversation, ConversationParticipant

class SelectiveReset:
    """Reset sélectif préservant les comptes de base uniquement"""

    PRESERVED_ACCOUNTS = [
        'root@arosaje.fr',
        'user@arosaje.fr',
        'gardien@arosaje.fr',
        'botanist@arosaje.fr',
        'botanist2@arosaje.fr'
    ]

    def __init__(self):
        self.session = SessionLocal()

    def reset_with_preservation(self):
        """
        Reset complet en préservant uniquement les 5 comptes spécifiés
        """
        print("🧹 Début du reset sélectif...")
        print(f"Comptes préservés: {', '.join(self.PRESERVED_ACCOUNTS)}")

        try:
            # 1. Obtenir les IDs des comptes à préserver
            preserved_user_ids = self._get_preserved_user_ids()
            print(f"IDs des comptes préservés: {preserved_user_ids}")

            # 2. Reset en ordre des dépendances (foreign keys)
            self._reset_advices()
            self._reset_care_reports()
            self._reset_conversations_and_messages()
            self._reset_plant_cares()
            self._reset_plants()
            self._reset_non_preserved_users(preserved_user_ids)

            self.session.commit()
            print("✅ Reset sélectif terminé avec succès")

        except Exception as e:
            self.session.rollback()
            print(f"❌ Erreur pendant le reset: {e}")
            raise
        finally:
            self.session.close()

    def _get_preserved_user_ids(self):
        """Récupère les IDs des utilisateurs à préserver"""
        preserved_users = self.session.query(User).filter(
            User.email.in_(self.PRESERVED_ACCOUNTS)
        ).all()

        return [user.id for user in preserved_users]

    def _reset_advices(self):
        """Supprime tous les conseils botaniques"""
        count = self.session.query(Advice).count()
        self.session.query(Advice).delete()
        print(f"🗑️  Conseils supprimés: {count}")

    def _reset_care_reports(self):
        """Supprime tous les rapports de garde"""
        count = self.session.query(CareReport).count()
        self.session.query(CareReport).delete()
        print(f"🗑️  Rapports de garde supprimés: {count}")

    def _reset_conversations_and_messages(self):
        """Supprime toutes les conversations et messages"""
        msg_count = self.session.query(Message).count()
        conv_count = self.session.query(Conversation).count()

        # Les messages et participants seront supprimés en cascade
        self.session.query(Conversation).delete()

        print(f"🗑️  Messages supprimés: {msg_count}")
        print(f"🗑️  Conversations supprimées: {conv_count}")

    def _reset_plant_cares(self):
        """Supprime toutes les gardes de plantes"""
        count = self.session.query(PlantCare).count()
        self.session.query(PlantCare).delete()
        print(f"🗑️  Gardes de plantes supprimées: {count}")

    def _reset_plants(self):
        """Supprime toutes les plantes"""
        count = self.session.query(Plant).count()
        self.session.query(Plant).delete()
        print(f"🗑️  Plantes supprimées: {count}")

    def _reset_non_preserved_users(self, preserved_user_ids):
        """Supprime tous les utilisateurs sauf ceux préservés"""
        total_users = self.session.query(User).count()

        # Supprimer tous les utilisateurs sauf ceux préservés
        deleted_count = self.session.query(User).filter(
            ~User.id.in_(preserved_user_ids)
        ).delete(synchronize_session=False)

        print(f"🗑️  Utilisateurs supprimés: {deleted_count}/{total_users}")
        print(f"✅ Utilisateurs préservés: {len(preserved_user_ids)}")


def main():
    """Point d'entrée principal"""
    print("=" * 60)
    print("🌿 A'rosa-je - Reset Sélectif de la Base de Données")
    print("=" * 60)

    try:
        reset_manager = SelectiveReset()
        reset_manager.reset_with_preservation()

        print("\n🎯 Reset sélectif terminé!")
        print("Les comptes de base ont été préservés.")
        print("Vous pouvez maintenant lancer un seed demo pour repeupler les données.")

    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())