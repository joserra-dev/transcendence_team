from models.booking import Booking
from models.users import Users


def customer_name_from_user(user: Users | None) -> str:
    if not user or not user.profile:
        return ""
    profile = user.profile
    return f"{profile.name or ''} {profile.last_name or ''}".strip()


def apply_customer_snapshot(booking: Booking, user: Users | None) -> None:
    if not user:
        return
    if user.email:
        booking.customer_email = user.email
    name = customer_name_from_user(user)
    if name:
        booking.customer_name = name


def booking_customer_email(booking: Booking) -> str:
    if booking.customer_email:
        return booking.customer_email
    if booking.user:
        return booking.user.email or ""
    return ""


def booking_customer_name(booking: Booking) -> str:
    if booking.customer_name:
        return booking.customer_name
    return customer_name_from_user(booking.user)


def detach_user_bookings(user: Users) -> None:
    email = user.email or ""
    name = customer_name_from_user(user)
    for booking in Booking.query.filter_by(id_user=user.id).all():
        booking.customer_email = booking.customer_email or email
        booking.customer_name = booking.customer_name or name
        booking.id_user = None
