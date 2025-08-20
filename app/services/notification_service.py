from sqlalchemy.orm import Session
from app.repositories.notification_repository import get_expiring_foods
from app.config.config_email import send_email

def list_notifications(db: Session, user_email: str, days_before_expiry: int = 2):
    notifications = get_expiring_foods(db, days_before_expiry)

    # Construir el mensaje del correo
    if notifications:
        body = "Hola 👋\n\nEstos alimentos están por caducar:\n\n"
        for n in notifications:
            body += f"- {n['message']}\n"
        body += "\nRevisa tu despensa y evita desperdicios 🍽️."

        send_email(
            to_email=user_email,
            subject="⚠️ Alimentos próximos a caducar",
            body=body
        )

    return notifications
