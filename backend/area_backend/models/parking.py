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

    def to_dict(self):
        return {
            "id": self.id,
            "id_company": self.id_company,
            "name": self.name,
            "provincia_parking": self.provincia_parking,
            "municipio_parking": self.municipio_parking,
            "isactive": self.isactive,
            "web_parking": self.web_parking,
            "telephone": self.telephone,
            "email": self.email,
            "contact_person": self.contact_person,
            "tiene_electricidad_parking": self.tiene_electricidad_parking,
            "tiene_residuales_parking": self.tiene_residuales_parking,
            "tiene_plazas_vip_parking": self.tiene_plazas_vip_parking
        }