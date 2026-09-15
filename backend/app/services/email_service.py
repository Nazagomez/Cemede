"""Email delivery service for user credentials."""

import smtplib
from email.mime.text import MIMEText

from app.config import settings


def enviar_credenciales(destinatario_email: str, destinatario_nombre: str, password_temporal: str) -> bool:
    """Send temporary credentials by email. Returns True if it was sent, False otherwise."""
    if not settings.smtp_user or not settings.smtp_password:
        print("[email_service] SMTP_USER o SMTP_PASSWORD vacíos en el .env")
        return False

    cuerpo = (
        f"Hola {destinatario_nombre},\n\n"
        f"Se creó una cuenta para vos en SITEC (CEMEDE).\n\n"
        f"Usuario: {destinatario_email}\n"
        f"Contraseña temporal: {password_temporal}\n\n"
        f"Al iniciar sesión por primera vez, el sistema te va a pedir que elijas una contraseña nueva.\n\n"
        f"Saludos,\nSITEC - CEMEDE"
    )

    mensaje = MIMEText(cuerpo, "plain", "utf-8")
    mensaje["Subject"] = "Tu cuenta en SITEC"
    mensaje["From"] = settings.smtp_from or settings.smtp_user
    mensaje["To"] = destinatario_email

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as servidor:
            if settings.smtp_use_tls:
                servidor.starttls()
            servidor.login(settings.smtp_user, settings.smtp_password)
            servidor.sendmail(mensaje["From"], [destinatario_email], mensaje.as_string())
        return True
    except Exception as error:
        print(f"[email_service] ERROR al enviar correo: {type(error).__name__}: {error}")
        return False