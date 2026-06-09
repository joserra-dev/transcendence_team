from database import db

class Parking(db.Model):
    __tablename__ = 'parking'
    __table_args__ = {'schema': 'public'}

    id = db.Column(db.BigInteger, primary_key=True)
    id_company = db.Column(db.Integer, db.ForeignKey('public.company.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    provincia_parking = db.Column(db.String(255), nullable=True)
    municipio_parking = db.Column(db.String(255), nullable=True)
    isactive = db.Column(db.Boolean, nullable=True)
    web_parking = db.Column(db.String(255), nullable=True)
    telephone = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    contact_person = db.Column(db.String(255), nullable=True)
    tiene_electricidad_parking = db.Column(db.Boolean, nullable=True)
    tiene_residuales_parking = db.Column(db.Boolean, nullable=True)
    tiene_plazas_vip_parking = db.Column(db.Boolean, nullable=True)

    # Relación hacia las plazas
    plazas = db.relationship('Space', backref='parking', cascade="all, delete-orphan", lazy=True)

    def to_dict(self, include_spaces=True):
        data = {
            "id": self.id,
            "nombre": self.name,
            "municipio": self.municipio_parking,
            "provincia": self.provincia_parking,
            "activo": self.isactive,
            "web": self.web_parking,
            "telefono": self.telephone,
            "email": self.email,
            "personaContacto": self.contact_person,
            "tieneElectricidad": self.tiene_electricidad_parking,
            "tieneResiduales": self.tiene_residuales_parking,
            "tieneVips": self.tiene_plazas_vip_parking,
        }
        if include_spaces:
            data["plazas"] = [plaza.to_dict() for plaza in self.plazas]
        return data