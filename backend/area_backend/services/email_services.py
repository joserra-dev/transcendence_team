from flask import current_app, render_template
from flask_mailman import EmailMessage

class EmailService:
    @staticmethod
    def _send(msg: EmailMessage) -> bool:
        """
        Método interno privado para manejar el envío y capturar errores.
        """
        try:
            msg.send()
            return True
        except Exception as e:
            # Aquí podrías usar el logger de Flask para registrar el error real
            current_app.logger.error(f"Error enviando correo: {str(e)}")
            raise e

    @classmethod
    def base_mail(cls, destinatario: str, asunto: str, content_html: str, plain_txt: str = "Texto plano alternativo"):
        """
        Método genérico para send cualquier tipo de correo electrónico.
        """
        msg = EmailMessage(
            subject=asunto,
            body=content_html,
            from_email=current_app.config.get('MAIL_DEFAULT_SENDER'),
            to=[destinatario]
        )
        msg.content_subtype = "html"
        msg.body = content_html
        
        return cls._send(msg)

    @classmethod
    def welcome(cls, destinatario: str, asunto: str = "Bienvenido a nuestra plataforma"):
        """
        Método especializado (ejemplo) para correos de bienvenida.
        Mantiene limpia la lógica de tus vistas/rutas.
        """
        html_content = render_template(
            'email/bienvenida.html', 
            nombre=destinatario, 
            email=destinatario
        )
        return cls.base_mail(destinatario, asunto, html_content)

    @classmethod
    def forgot(cls, destinatario: str, user_name: str, recovery_url: str):
        """
        Envía el correo para restablecer la contraseña utilizando su respectivo template.
        """
        asunto = "Restablecer tu contraseña"
        
        # Renderizamos la nueva plantilla pasando las variables requeridas
        html_content = render_template(
            'email/recuperar_password.html', 
            user_name=user_name, 
            recovery_link=recovery_url
        )
        
        plain_txt = f"Hola {user_name}, restablece tu contraseña ingresando aquí: {recovery_url}"
        
        return cls.base_mail(destinatario, asunto, html_content, plain_txt)