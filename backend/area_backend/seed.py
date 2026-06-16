from datetime import date
# pyrefly: ignore [missing-import]
from werkzeug.security import generate_password_hash

from database import db
from models.company import Company
from models.parking import Parking
from models.space import Space
from models.users import Profiles, UserRole, Users

# CORRECCIÓN: Contraseña que cumple con las nuevas reglas de tu PasswordValidator
DEFAULT_PASSWORD = "password123"

SEED_USERS = [
    {
        "email": "superadmin@hemen-go.com",
        "profile": {
            "name": "Super",
            "last_name": "Admin",
            "dni": "00000000S",
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
            "dni": "11111111H",
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
            "dni": "12345678A",
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
            "dni": "87654321B",
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
    if Users.query.first():
        return 0

    password_hash = generate_password_hash(DEFAULT_PASSWORD)
    created = 0

    for user_data in SEED_USERS:
        profile_data = user_data["profile"].copy()
        company_name = profile_data.pop("company_name", None)
        company_cif = profile_data.pop("company_cif", None)
        tbai_enabled = profile_data.pop("tbai_enabled", False)
        tbai_license = profile_data.pop("tbai_software_license", None)

        if company_name:
            company = _get_or_create_company(company_name, company_cif, tbai_enabled, tbai_license)
            profile_data["company_id"] = company.id

        user = Users(email=user_data["email"], pass_user=password_hash)
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


def seed_database() -> None:
    """Inserta datos de desarrollo si las tablas están vacías."""
    users_created = _seed_users()
    parkings_created = _seed_parkings()

    if users_created or parkings_created:
        db.session.commit()

    if users_created:
        print(f" * {users_created} usuarios creados (contraseña: {DEFAULT_PASSWORD!r})")
    if parkings_created:
        print(f" * {parkings_created} parkings creados con sus plazas")