from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pathlib import Path
from typing import List, Dict, Any
import jinja2
from utils import settings

class EmailService:
    def __init__(self):
        self.config = ConnectionConfig(
            MAIL_USERNAME=settings.MAIL_USERNAME,
            MAIL_PASSWORD=settings.MAIL_PASSWORD,
            MAIL_FROM=settings.MAIL_FROM,
            MAIL_PORT=settings.MAIL_PORT,
            MAIL_SERVER=settings.MAIL_SERVER,
            MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
            MAIL_STARTTLS=settings.MAIL_STARTTLS,
            MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
            USE_CREDENTIALS=settings.USE_CREDENTIALS,
            VALIDATE_CERTS=settings.VALIDATE_CERTS,
            TEMPLATE_FOLDER=Path(__file__).parent / "templates"
        )
        self.fastmail = FastMail(self.config)
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(Path(__file__).parent / "templates"))
        )

    async def send_email(
        self,
        recipients: List[str],
        subject: str,
        template_name: str,
        template_data: Dict[str, Any]
    ) -> None:
        """
        Envoie un email en utilisant un template.
        
        Args:
            recipients: Liste des destinataires
            subject: Sujet de l'email
            template_name: Nom du template à utiliser
            template_data: Données à injecter dans le template
        """
        template = self.template_env.get_template(f"{template_name}.html")
        html_content = template.render(**template_data)

        message = MessageSchema(
            subject=subject,
            recipients=recipients,
            body=html_content,
            subtype=MessageType.html
        )

        await self.fastmail.send_message(message)

    async def send_new_message_notification(
        self,
        recipient_email: str,
        sender_name: str,
        conversation_id: str
    ) -> None:
        """
        Envoie une notification pour un nouveau message.
        """
        await self.send_email(
            recipients=[recipient_email],
            subject=f"Nouveau message de {sender_name}",
            template_name="new_message",
            template_data={
                "sender_name": sender_name,
                "conversation_link": f"/conversations/{conversation_id}"
            }
        )

    async def send_password_reset(
        self,
        recipient_email: str,
        reset_token: str
    ) -> None:
        """
        Envoie un email de réinitialisation de mot de passe.
        """
        await self.send_email(
            recipients=[recipient_email],
            subject="Réinitialisation de votre mot de passe",
            template_name="password_reset",
            template_data={
                "reset_link": f"/reset-password?token={reset_token}"
            }
        )

    async def send_welcome_email(
        self,
        recipient_email: str,
        user_name: str
    ) -> None:
        """
        Envoie un email de bienvenue après l'inscription.
        """
        await self.send_email(
            recipients=[recipient_email],
            subject="Bienvenue sur A'rosa-je !",
            template_name="welcome",
            template_data={
                "user_name": user_name
            }
        )

    async def send_account_validated_email(
        self,
        recipient_email: str,
        user_name: str
    ) -> None:
        """
        Envoie un email de confirmation de validation du compte.
        """
        await self.send_email(
            recipients=[recipient_email],
            subject="Votre compte A'rosa-je a été validé !",
            template_name="account_validated",
            template_data={
                "user_name": user_name
            }
        )

    async def send_account_rejected_email(
        self,
        recipient_email: str,
        user_name: str
    ) -> None:
        """
        Envoie un email de notification de rejet du compte.
        """
        await self.send_email(
            recipients=[recipient_email],
            subject="Information concernant votre compte A'rosa-je",
            template_name="account_rejected",
            template_data={
                "user_name": user_name
            }
        ) 