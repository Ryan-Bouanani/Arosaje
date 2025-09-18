from sqlalchemy.orm import Session
from models.user import User
from models.plant_care import PlantCare
from models.advice import Advice, AdvicePriority, ValidationStatus
from services.email.email_service import EmailService


class NotificationService:
    def __init__(self):
        self.email_service = EmailService()

    async def send_advice_notification(
        self,
        db: Session,
        plant_care_id: int,
        botanist_name: str,
        advice_title: str,
        priority: AdvicePriority,
    ):
        """Envoyer une notification au propriétaire quand un conseil est donné"""

        # Récupérer la garde et le propriétaire
        plant_care = db.query(PlantCare).filter(PlantCare.id == plant_care_id).first()
        if not plant_care:
            return

        owner = db.query(User).filter(User.id == plant_care.owner_id).first()
        if not owner:
            return

        # Déterminer le niveau d'urgence du message
        priority_text = {
            AdvicePriority.URGENT: "🚨 URGENT",
            AdvicePriority.FOLLOW_UP: "📋 Suivi nécessaire",
            AdvicePriority.NORMAL: "💡 Nouveau conseil",
        }.get(priority, "💡 Nouveau conseil")

        subject = f"{priority_text} - Conseil botanique pour votre plante"

        # Construire le message email
        email_content = f"""
        <h2>📱 A'rosa-je - Nouveau conseil botanique</h2>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin: 15px 0;">
            <h3 style="color: #28a745; margin-top: 0;">
                {priority_text} {advice_title}
            </h3>
            
            <p><strong>Botaniste :</strong> {botanist_name}</p>
            <p><strong>Plante concernée :</strong> {plant_care.plant.name if plant_care.plant else 'Votre plante'}</p>
            <p><strong>Période de garde :</strong> {plant_care.start_date.strftime('%d/%m/%Y')} - {plant_care.end_date.strftime('%d/%m/%Y')}</p>
        </div>
        
        <p>Un botaniste expert a examiné votre demande et vous a fourni des conseils personnalisés pour l'entretien de votre plante.</p>
        
        <div style="text-align: center; margin: 25px 0;">
            <a href="#" style="background-color: #28a745; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                📱 Voir les conseils dans l'app
            </a>
        </div>
        
        <hr style="margin: 25px 0; border: none; border-top: 1px solid #dee2e6;">
        
        <p style="color: #6c757d; font-size: 0.9em;">
            <em>💡 Conseil :</em> Les conseils {priority.value} nécessitent votre attention rapide pour assurer la bonne santé de votre plante.
        </p>
        
        <p style="color: #6c757d; font-size: 0.8em;">
            Vous recevez ce message car vous avez une garde de plante active sur A'rosa-je.
            <br>Si vous ne souhaitez plus recevoir ces notifications, vous pouvez les désactiver dans les paramètres de l'application.
        </p>
        """

        try:
            await self.email_service.send_email(
                to_email=owner.email, subject=subject, html_content=email_content
            )

            # Marquer comme notifié dans la base
            advice = (
                db.query(Advice)
                .filter(
                    Advice.plant_care_id == plant_care_id,
                    Advice.is_current_version,
                )
                .first()
            )
            if advice:
                advice.owner_notified = True
                db.commit()

        except Exception as e:
            print(f"Erreur notification propriétaire: {e}")

    async def send_advice_update_notification(
        self, db: Session, advice_id: int, botanist_name: str
    ):
        """Notifier le propriétaire qu'un conseil a été mis à jour"""

        advice = db.query(Advice).filter(Advice.id == advice_id).first()
        if not advice:
            return

        plant_care = (
            db.query(PlantCare).filter(PlantCare.id == advice.plant_care_id).first()
        )
        if not plant_care:
            return

        owner = db.query(User).filter(User.id == plant_care.owner_id).first()
        if not owner:
            return

        subject = "📝 Mise à jour - Conseil botanique pour votre plante"

        email_content = f"""
        <h2>📱 A'rosa-je - Conseil mis à jour</h2>
        
        <div style="background-color: #e3f2fd; padding: 15px; border-radius: 8px; margin: 15px 0;">
            <h3 style="color: #1976d2; margin-top: 0;">
                📝 {advice.title}
            </h3>
            
            <p><strong>Botaniste :</strong> {botanist_name}</p>
            <p><strong>Version :</strong> {advice.version}</p>
            <p><strong>Plante :</strong> {plant_care.plant.name if plant_care.plant else 'Votre plante'}</p>
        </div>
        
        <p>Le botaniste a mis à jour ses conseils avec de nouvelles informations importantes pour votre plante.</p>
        
        <div style="text-align: center; margin: 25px 0;">
            <a href="#" style="background-color: #1976d2; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                📱 Voir la mise à jour
            </a>
        </div>
        """

        try:
            await self.email_service.send_email(
                to_email=owner.email, subject=subject, html_content=email_content
            )
        except Exception as e:
            print(f"Erreur notification mise à jour: {e}")

    async def send_validation_notification(
        self,
        db: Session,
        advice_id: int,
        validator_name: str,
        validation_status: ValidationStatus,
    ):
        """Notifier le botaniste auteur qu'un collègue a validé son conseil"""

        advice = db.query(Advice).filter(Advice.id == advice_id).first()
        if not advice:
            return

        author = db.query(User).filter(User.id == advice.botanist_id).first()
        if not author:
            return

        # Message selon le statut de validation
        status_messages = {
            ValidationStatus.VALIDATED: {
                "emoji": "✅",
                "title": "Conseil validé",
                "color": "#28a745",
                "message": "Félicitations ! Un collègue botaniste a validé votre conseil.",
            },
            ValidationStatus.REJECTED: {
                "emoji": "❌",
                "title": "Conseil rejeté",
                "color": "#dc3545",
                "message": "Un collègue botaniste a des réserves sur votre conseil.",
            },
            ValidationStatus.NEEDS_REVISION: {
                "emoji": "⚠️",
                "title": "Révision nécessaire",
                "color": "#ffc107",
                "message": "Un collègue botaniste suggère des améliorations à votre conseil.",
            },
        }

        status_info = status_messages.get(
            validation_status, status_messages[ValidationStatus.VALIDATED]
        )

        subject = f"{status_info['emoji']} {status_info['title']} - A'rosa-je"

        email_content = f"""
        <h2>📱 A'rosa-je - Validation par les pairs</h2>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid {status_info['color']};">
            <h3 style="color: {status_info['color']}; margin-top: 0;">
                {status_info['emoji']} {status_info['title']}
            </h3>
            
            <p><strong>Votre conseil :</strong> {advice.title}</p>
            <p><strong>Validé par :</strong> {validator_name}</p>
            <p><strong>Statut :</strong> {validation_status.value}</p>
        </div>
        
        <p>{status_info['message']}</p>
        
        {f'<div style="background-color: #fff3cd; padding: 10px; border-radius: 5px; margin: 15px 0;"><strong>Commentaire :</strong> {advice.validation_comment}</div>' if advice.validation_comment else ''}
        
        <div style="text-align: center; margin: 25px 0;">
            <a href="#" style="background-color: {status_info['color']}; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                📱 Voir les détails
            </a>
        </div>
        
        <p style="color: #6c757d; font-size: 0.9em;">
            La validation par les pairs améliore la qualité des conseils botaniques sur A'rosa-je.
        </p>
        """

        try:
            await self.email_service.send_email(
                to_email=author.email, subject=subject, html_content=email_content
            )

            # Marquer comme notifié
            advice.botanist_notified = True
            db.commit()

        except Exception as e:
            print(f"Erreur notification validation: {e}")

    async def send_urgent_advice_alert(
        self, db: Session, plant_care_id: int, botanist_name: str
    ):
        """Envoyer une alerte immédiate pour un conseil urgent"""

        # Cette fonction peut être étendue pour envoyer des notifications push
        # via Firebase, SMS, ou autres services

        plant_care = db.query(PlantCare).filter(PlantCare.id == plant_care_id).first()
        if not plant_care:
            return

        owner = db.query(User).filter(User.id == plant_care.owner_id).first()
        if not owner:
            return

        subject = "🚨 ALERTE URGENTE - Votre plante a besoin d'attention immédiate"

        email_content = f"""
        <div style="background-color: #721c24; color: white; padding: 20px; text-align: center; border-radius: 8px;">
            <h1 style="margin: 0; color: white;">🚨 ALERTE URGENTE 🚨</h1>
            <h2 style="margin: 10px 0; color: white;">Votre plante nécessite une attention IMMÉDIATE</h2>
        </div>
        
        <div style="background-color: #f8d7da; padding: 15px; border-radius: 8px; margin: 15px 0; border: 1px solid #f5c6cb;">
            <p><strong>Botaniste expert :</strong> {botanist_name}</p>
            <p><strong>Plante concernée :</strong> {plant_care.plant.name if plant_care.plant else 'Votre plante'}</p>
            <p><strong>Action requise :</strong> IMMÉDIATE</p>
        </div>
        
        <p style="font-size: 1.1em; font-weight: bold; color: #721c24;">
            Un botaniste a identifié un problème urgent nécessitant votre intervention rapide pour sauver votre plante.
        </p>
        
        <div style="text-align: center; margin: 25px 0;">
            <a href="#" style="background-color: #dc3545; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 1.1em;">
                🚨 VOIR L'ALERTE MAINTENANT
            </a>
        </div>
        
        <p style="color: #721c24; font-weight: bold;">
            ⏰ Temps de réaction recommandé : IMMÉDIAT
        </p>
        """

        try:
            await self.email_service.send_email(
                to_email=owner.email,
                subject=subject,
                html_content=email_content,
                priority=True,  # Email haute priorité
            )
        except Exception as e:
            print(f"Erreur alerte urgente: {e}")
