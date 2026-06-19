import pytest
from flask import Flask
from services.email_services import EmailService

# 1. Configuración del entorno de pruebas (Fixture)
@pytest.fixture
def app():
    """Crea un contexto de aplicación de Flask configurado para pruebas."""
    app = Flask(__name__, template_folder='../templates') # Apuntamos a la carpeta de templates
    app.config.update({
        "TESTING": True,
        "MAIL_DEFAULT_SENDER": "test@desarrollo.com"
    })
    
    # Retornamos la app dentro del contexto de Flask
    with app.app_context():
        yield app

# 2. Test para verificar que el correo se construye correctamente
def test_enviar_bienvenida_exitoso(app, mocker):
    """
    Prueba que el método enviar_bienvenida renderice el HTML 
    y llame al método de envío físico de Flask-Mailman.
    """
    # 🌟 CAMBIO AQUÍ: Usamos la ruta en formato string 'modulo.Clase.metodo'
    mock_enviar = mocker.patch('services.email_services.EmailService._send', return_value=True)

    # Ejecutamos la acción de nuestra clase
    resultado = EmailService.welcome(
        destinatario="cliente@test.com",
        token="test-token"
        ##url_verificacion="https://link-de-prueba.com"
    )

    # Verificar resultados (Aserciones)
    assert resultado is True
    mock_enviar.assert_called_once()
    
    msg_generado = mock_enviar.call_args[0][0]
    assert msg_generado['Subject'] == "Bienvenido a nuestra plataforma"
    assert msg_generado['To'] == "cliente@test.com"
    


# 3. Test para verificar manejo de errores
def test_enviar_bienvenida_falla_servidor(app, mocker):
    """Prueba el comportamiento si el servidor SMTP falla."""
    # 🌟 CAMBIO AQUÍ TAMBIÉN: Ruta en formato string
    mocker.patch('services.email_services.EmailService._send', side_effect=Exception("Error de conexión SMTP"))

    with pytest.raises(Exception) as exc_info:
        EmailService.welcome("test@test.com", "User", "http://link.com")
        
    assert "Error de conexión SMTP" in str(exc_info.value)