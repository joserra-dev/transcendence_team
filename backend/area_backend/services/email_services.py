from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

from flask import current_app, render_template
from flask_babel import _, get_locale   
import os

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

class EmailService:
    @staticmethod
    def _get_sender() -> str:
        sender = current_app.config.get('MAIL_DEFAULT_SENDER') or current_app.config.get('MAIL_USERNAME')
        return f"HEMEN-GO <{sender}>"

    @staticmethod
    def _send(msg: MIMEMultipart) -> bool:
        server = current_app.config.get('MAIL_SERVER')
        port = int(current_app.config.get('MAIL_PORT', 587))
        username = current_app.config.get('MAIL_USERNAME')
        password = current_app.config.get('MAIL_PASSWORD')
        use_tls = current_app.config.get('MAIL_USE_TLS', True)

        try:
            with smtplib.SMTP(server, port, timeout=20) as smtp:
                smtp.ehlo()
                if use_tls:
                    smtp.starttls()
                    smtp.ehlo()
                smtp.login(username, password)
                refused = smtp.send_message(msg)
                if refused:
                    raise smtplib.SMTPException(f"Destinatarios rechazados: {refused}")
            current_app.logger.info(
                f"Correo enviado correctamente desde {username} a {msg['To']}"
            )
            return True
        except Exception as e:
            current_app.logger.error(f"Error enviando correo a {msg.get('To')}: {e}")
            raise e

    @classmethod
    def base_mail(cls, destinatario: str, asunto: str, content_html: str, plain_txt: str = "Texto plano alternativo"):
        sender = cls._get_sender()
        msg = MIMEMultipart('alternative')
        msg['Subject'] = asunto
        msg['From'] = sender
        msg['To'] = destinatario
        msg.attach(MIMEText(plain_txt, 'plain', 'utf-8'))
        msg.attach(MIMEText(content_html, 'html', 'utf-8'))
        return cls._send(msg)

    @classmethod
    def welcome(cls, destinatario: str, token: str, asunto: str = "Bienvenido a nuestra plataforma"):
        """
        Método especializado (ejemplo) para correos de bienvenida.
        Mantiene limpia la lógica de tus vistas/rutas.
        """
        actual_locale = get_locale()
        idioma = actual_locale.language if actual_locale else 'es'
        base_url = os.getenv('URL_BACK')
        verification_url = f"{base_url}/api/users/verify?token={token}"
        html_content = render_template(
            f'email/{idioma}/bienvenida.html', 
            nombre=destinatario, 
            email=destinatario,
            verification_url=verification_url
        )

        plain_txt = (
            f"Hola {destinatario}, bienvenido a HEMEN-GO.\n\n"
            f"Verifica tu cuenta accediendo a este enlace:\n{verification_url}"
        )
        return cls.base_mail(destinatario, asunto, html_content, plain_txt)

    @classmethod
    def admin_welcome(
        cls,
        destinatario: str,
        token: str,
        nombre: str | None = None,
        company_name: str | None = None,
    ):
        actual_locale = get_locale()
        idioma = actual_locale.language 
        display_name = nombre or destinatario
        base_url = os.getenv('URL_BACK')
        verification_url = f"{base_url}/api/users/verify?token={token}"
        html_content = render_template(
            f'email/{idioma}/bienvenida_admin.html', 
            nombre=display_name,
            company_name=company_name,
            verification_url=verification_url,
        )

        company_line = f" de {company_name}" if company_name else ""
        plain_txt = (
            f"Hola {display_name},\n\n"
            f"Has sido registrado como administrador{company_line} en HEMEN-GO.\n"
            f"Verifica tu cuenta accediendo a este enlace:\n{verification_url}"
        )
        asunto = "HEMEN-GO - Bienvenido, administrador"
        return cls.base_mail(destinatario, asunto, html_content, plain_txt)
    
    @classmethod
    def booking(cls, destinatario: str, user_name: str, booking_code: str, service_detail: str, booking_date: str, total_paid: str, management_url: str):
        actual_locale = get_locale()
        idioma = actual_locale.language 
        asunto = _("HEMEN-GO - Reserva confirmada")
        html_content = render_template(
            f'email/{idioma}/booking.html',
            nombre=user_name,
            codigo_reserva=booking_code,
            detalle_servicio=service_detail,
            fecha_reserva=booking_date,
            total_pagado=total_paid,
            enlace_gestion=management_url
        )
        plain_txt = (
            f"Hola {user_name},\n\n"
            f"Tu reserva #{booking_code} ha sido confirmada.\n"
            f"Servicio: {service_detail}\n"
            f"Fechas: {booking_date}\n"
            f"Total: {total_paid}\n\n"
            f"Puedes gestionarla en: {management_url}"
        )
        return cls.base_mail(destinatario, asunto, html_content, plain_txt)

    @classmethod
    def forgot(cls, destinatario: str, user_name: str, recovery_url: str):
        actual_locale = get_locale()
        idioma = actual_locale.language  # 'es', 'en', 'eu'

        # 1. Asunto traducido automáticamente según el idioma actual
        asunto = _("HEMEN-GO - Recuperar acceso a tu cuenta")

        # 2. Renderizado de la plantilla HTML organizada por carpetas de idioma
        html_content = render_template(
            f'email/{idioma}/forgot.html',
            user_name=user_name,
            recovery_url=recovery_url
        )

        # 3. Texto plano utilizando la función de traducción con variables inyectadas
        plain_txt = _(
            "Hola %(user_name)s,\n\n"
            "Hemos recibido una solicitud para restablecer tu contraseña en HEMEN-GO.\n"
            "Abre este enlace para crear una nueva contraseña:\n%(recovery_url)s\n\n"
            "El enlace caduca en 1 hora.\n"
            "Si no solicitaste este cambio, ignora este correo.",
            user_name=user_name,
            recovery_url=recovery_url
        )

        return cls.base_mail(destinatario, asunto, html_content, plain_txt)

    # base_email para enviar ficheros adjuntos
    @classmethod
    def attach_mail(cls, destinatario: str, asunto: str, name: str, bill: bytes):
        sender = cls._get_sender()
        msg = MIMEMultipart()
        msg['Subject'] = asunto
        msg['From'] = sender
        msg['To'] = destinatario
        
        # Adjuntar PDF
        pdf = MIMEApplication(bill, _subtype="pdf")
        pdf.add_header(
            "Content-Disposition",
            "attachment",
            filename=name
        )
        msg.attach(pdf)

        return cls._send(msg)

    # Funcion para enviar el email con la factura en pdf
    @classmethod
    def send_bill(cls, destinatario: str, bill: bytes):
        asunto = "HEMEN-GO - PDF factura"
        
        
        return cls.attach_mail(destinatario, asunto, "factura.pdf", bill)