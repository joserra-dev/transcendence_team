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

    spaces = db.relationship('Space', back_populates='parking', lazy=True)

    def to_dict(self, include_spaces=True, fecha_desde=None, fecha_hasta=None):
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
            plazas_list = []
            for plaza in self.spaces:
                plaza_data = plaza.to_dict()
                if fecha_desde and fecha_hasta:
                    from datetime import datetime
                    try:
                        if isinstance(fecha_desde, str):
                            fd = datetime.strptime(fecha_desde, "%Y-%m-%d").date()
                        else:
                            fd = fecha_desde
                        if isinstance(fecha_hasta, str):
                            fh = datetime.strptime(fecha_hasta, "%Y-%m-%d").date()
                        else:
                            fh = fecha_hasta
                        
                        from models.booking import Booking
                        overlap = Booking.query.filter(
                            Booking.id_space == plaza.id,
                            Booking.fecha_inicio_reserva <= fh,
                            Booking.fecha_fin_reserva >= fd
                        ).first()
                        if overlap:
                            plaza_data["estado"] = "1"
                        else:
                            plaza_data["estado"] = "0"
                    except Exception as e:
                        print(f"Error checking space occupancy: {e}")
                plazas_list.append(plaza_data)
            data["plazas"] = plazas_list
        return data