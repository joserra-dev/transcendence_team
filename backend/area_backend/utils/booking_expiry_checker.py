import time
import threading
import logging
from datetime import datetime, timedelta

from database import db
from models.booking import Booking, BookingStatus
from services.email_services import EmailService
from models.users import Users

logger = logging.getLogger(__name__)

_app = None
_expiry_minutes = 30
_expiry_running = False
_expiry_thread = None


def configure_expiry(minutes):
    global _expiry_minutes
    _expiry_minutes = int(minutes)


def _expire_stale_bookings():
    while _expiry_running:
        try:
            with _app.app_context():
                cutoff = datetime.utcnow() - timedelta(minutes=_expiry_minutes)
                stale = Booking.query.filter(
                    Booking.status == BookingStatus.PROCESSING,
                    Booking.created_at < cutoff
                ).all()
                for booking in stale:
                    booking.status = BookingStatus.CANCELLED
                    db.session.commit()
                    logger.info(
                        "Reserva %d expirada automaticamente (sin pago en %d min)",
                        booking.id, _expiry_minutes
                    )
                    try:
                        user = Users.query.get(booking.id_user)
                        if user and user.email:
                            space = booking.space
                            parking = space.parking if space else None
                            EmailService.booking_expired(
                                destinatario=user.email,
                                user_name=user.profile.name if user.profile else user.email,
                                booking_code=str(booking.id),
                                service_detail=f"{parking.name if parking else ''} - {space.name if space else ''}",
                                booking_date=f"{booking.start_date} a {booking.end_date}"
                                if booking.start_date and booking.end_date
                                else "fechas no disponibles"
                            )
                    except Exception as email_exc:
                        logger.error(
                            "Error enviando email de expiracion para reserva %d: %s",
                            booking.id, email_exc
                        )
        except Exception as exc:
            logger.error("Error en chequeo de expiracion de reservas: %s", exc)
            try:
                db.session.rollback()
            except Exception:
                pass
        time.sleep(60)


def start_expiry_checker(app):
    global _app, _expiry_running, _expiry_thread
    if _expiry_running:
        return
    _app = app
    configure_expiry(
        app.config.get('BOOKING_EXPIRY_MINUTES', 30)
    )
    _expiry_running = True
    _expiry_thread = threading.Thread(target=_expire_stale_bookings, daemon=True)
    _expiry_thread.name = "booking-expiry-checker"
    _expiry_thread.start()
    logger.info(
        "Chequeo de expiracion de reservas iniciado (timeout: %d min)",
        _expiry_minutes
    )


def stop_expiry_checker():
    global _expiry_running, _expiry_thread
    _expiry_running = False
    if _expiry_thread is not None:
        _expiry_thread.join(timeout=5)
        _expiry_thread = None