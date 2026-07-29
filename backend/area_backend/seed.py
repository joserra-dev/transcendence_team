from datetime import date
import os

from database import db
from models.company import Company
from utils.password_hash import hash_password
from models.users import Profiles, UserRole, Users

# CORRECCIÓN: Contraseña que cumple con las nuevas reglas de tu PasswordValidator
SUPER_ADMIN_PASSWORD = os.environ["SUPER_ADMIN_PASSWORD"]

SEED_USERS = [
    {
        "email": "superadmin@hemen-go.com",
        "profile": {
            "name": "Super",
            "last_name": "Admin",
            "dni": "33445825F",
            "birth_day": date(1980, 1, 1),
            "role": UserRole.SUPER_ADMIN,
            "company_id": None,
        },
    },
    {
        "email": "admin@hemen-go.com",
        "profile": {
            "name": "Admin",
            "last_name": "Hemen-go",
            "dni": "49688627W",
            "birth_day": date(1981, 6, 1),
            "role": UserRole.ADMIN,
            "company_name": "Hemen-go",
            "company_cif": "B12345678"
        },
    },
    {
        "email": "jon.doe@example.com",
        "profile": {
            "name": "Jon",
            "last_name": "Doe",
            "dni": "27217336X",
            "birth_day": date(1990, 5, 12),
            "role": UserRole.USER,
            "company_id": None,
        },
    },
    {
        "email": "usuario@example.com",
        "profile": {
            "name": "María",
            "last_name": "García",
            "dni": "94730422T",
            "birth_day": date(1995, 3, 20),
            "role": UserRole.USER,
            "company_id": None,
        },
    },
]

def _get_or_create_company(name: str, cif: str | None = None) -> Company:
    company = Company.query.filter_by(name=name).first()
    if company:
        return company

def _seed_users() -> int:
    password_hash = hash_password(SUPER_ADMIN_PASSWORD)
    created = 0

    for user_data in SEED_USERS:
        existing = Users.query.filter_by(email=user_data["email"]).first()
        profile_data = user_data["profile"].copy()
        company_name = profile_data.pop("company_name", None)
        company_cif = profile_data.pop("company_cif", None)
        
        if company_name:
            company = _get_or_create_company(company_name, company_cif)
            profile_data["company_id"] = company.id

        if existing:
            existing.pass_user = password_hash
            existing.is_verified = True
            if existing.profile:
                for key, value in profile_data.items():
                    setattr(existing.profile, key, value)
            else:
                db.session.add(Profiles(user_id=existing.id, **profile_data))
            continue

        user = Users(
            email=user_data["email"],
            pass_user=password_hash,
            is_verified=True,
        )
        db.session.add(user)
        db.session.flush()

        profile = Profiles(user_id=user.id, **profile_data)
        db.session.add(profile)
        created += 1

    return created


def _ensure_seed_users_verified() -> None:
    seed_emails = [user_data["email"] for user_data in SEED_USERS]
    updated = False
    for email in seed_emails:
        user = Users.query.filter_by(email=email).first()
        if user and not user.is_verified:
            user.is_verified = True
            updated = True
    if updated:
        db.session.commit()


def seed_database() -> None:
    """Inserta datos de desarrollo si las tablas están vacías (SOLO USUARIOS Y PERFILES)."""
    # 1. Cargamos únicamente los usuarios y sus perfiles
    num_users = users_created = _seed_users()
    
    # 2. Nos aseguramos de que queden verificados
    _ensure_seed_users_verified()

    # 3. Guardamos los cambios en la base de datos si se creó algún usuario
    if users_created:
        db.session.commit()
    elif Users.query.filter(Users.email.in_([u["email"] for u in SEED_USERS])).count():
        db.session.commit()

    if users_created:
        print(f" * {num_users} usuarios creados")