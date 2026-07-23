from datetime import date
import os
# pyrefly: ignore [missing-import]
from werkzeug.security import generate_password_hash

from database import db
from models.company import Company
from utils.password_hash import hash_password
from models.parking import Parking
from models.space import Space
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
            "company_cif": "B12345678",
            # Datos de inicialización TicketBAI para la empresa
            "tbai_enabled": True,
            "tbai_software_license": "TBAI-HEMENGO-99882",
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

SEED_PARKINGS = [
    {
        "company_name": "hemen-go",
        "company_cif": "B12345678",
        "name": "Parking La Galea beach",
        "province": "Bizkaia",
        "municipality": "Getxo",
        "isactive": True,
        "web_parking": "https://www.la-galea-caravaning.com",
        "telephone": "688745692",
        "email": "info@la-galea-caravaning.com",
        "contact_person": "Mikel Basurko",
        "has_electricity": True,
        "has_waste_disposal": True,
        "has_vip_spots": True,
        # NUEVOS CAMPOS: TicketBAI, Ubicación y Descripción
        "tbai_serie_facturacion": "GALEA26",
        "latitude": 43.3712,
        "longitude": -3.0345,
        "description": "Estupendo parking frente a los acantilados de La Galea. Ideal para autocaravanas con vistas al mar de Getxo.",
        "spaces": [
            {"name": "A1", "isvip": True, "has_electr": True, "status": "0", "price": 25.0},
            {"name": "A2", "isvip": False, "has_electr": True, "status": "0", "price": 27.5},
            {"name": "B1", "isvip": False, "has_electr": False, "status": "0", "price": 20.0},
        ],
    },
    {
        "company_name": "hemen-go",
        "name": "Parking Zarautz Costa",
        "province": "Gipuzkoa",
        "municipality": "Zarautz",
        "isactive": True,
        "web_parking": "https://www.zarautz-camper.com",
        "telephone": "943123456",
        "email": "info@zarautz-camper.com",
        "contact_person": "Ane Mendizabal",
        "has_electricity": True,
        "has_waste_disposal": False,
        "has_vip_spots": True,
        # NUEVOS CAMPOS: TicketBAI, Ubicación y Descripción
        "tbai_serie_facturacion": "ZARAUTZ26",
        "latitude": 43.2844,
        "longitude": -2.1691,
        "description": "Ubicación privilegiada en la costa vasca. A pocos metros de la playa de Zarautz, ideal para surfistas.",
        "spaces": [
            {"name": "C1", "isvip": True, "has_electr": True, "status": "0", "price": 30.0},
            {"name": "C2", "isvip": False, "has_electr": True, "status": "0", "price": 22.0},
        ],
    },
    {
        "company_name": "hemen-go",
        "name": "Parking Hondarribia Puerto",
        "province": "Gipuzkoa",
        "municipality": "Hondarribia",
        "isactive": True,
        "telephone": "943654321",
        "email": "info@hondarribia-parking.com",
        "contact_person": "Iñaki Agirre",
        "has_electricity": False,
        "has_waste_disposal": True,
        "has_vip_spots": False,
        # NUEVOS CAMPOS: TicketBAI, Ubicación y Descripción
        "tbai_serie_facturacion": "HONDA26",
        "latitude": 43.3789,
        "longitude": -1.7925,
        "description": "Ubicado junto al puerto deportivo de Hondarribia. Zona tranquila vigilada las 24 horas y con todos los servicios básicos.",
        "spaces": [
            {"name": "D1", "isvip": False, "has_electr": False, "status": "0", "price": 18.0},
        ],
    },
]


def _get_or_create_company(name: str, cif: str | None = None, tbai_enabled: bool = False, tbai_license: str | None = None) -> Company:
    company = Company.query.filter_by(name=name).first()
    if company:
        return company

    # Pasamos las nuevas propiedades añadidas al modelo Company
    company = Company(
        name=name, 
        cif=cif, 
        tbai_enabled=tbai_enabled, 
        tbai_software_license=tbai_license
    )
    db.session.add(company)
    db.session.flush()
    return company


def _seed_users() -> int:
    password_hash = hash_password(SUPER_ADMIN_PASSWORD)
    created = 0

    for user_data in SEED_USERS:
        existing = Users.query.filter_by(email=user_data["email"]).first()
        profile_data = user_data["profile"].copy()
        company_name = profile_data.pop("company_name", None)
        company_cif = profile_data.pop("company_cif", None)
        tbai_enabled = profile_data.pop("tbai_enabled", False)
        tbai_license = profile_data.pop("tbai_software_license", None)

        if company_name:
            company = _get_or_create_company(company_name, company_cif, tbai_enabled, tbai_license)
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


def _seed_parkings() -> int:
    if Parking.query.first():
        return 0

    created = 0

    for parking_data in SEED_PARKINGS:
        data = parking_data.copy()
        spaces_data = data.pop("spaces")
        company_name = data.pop("company_name")
        company_cif = data.pop("company_cif", None)

        # Las compañías que se crean desde los parkings por defecto no tienen tbai (hasta que se configure)
        company = _get_or_create_company(company_name, company_cif)
        
        # El desempaquetado (**data) ahora incluye automáticamente la serie, coordenadas y descripción
        parking = Parking(id_company=company.id, **data)
        db.session.add(parking)
        db.session.flush()

        for space_data in spaces_data:
            space = Space(id_parking=parking.id, **space_data)
            db.session.add(space)

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