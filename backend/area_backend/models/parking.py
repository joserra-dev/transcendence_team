import logging
from database import db
from flask import current_app

# Logger para el módulo
logger = logging.getLogger(__name__)

class Parking(db.Model):
    __tablename__ = 'parking'
    __table_args__ = {'schema': 'public'}

    id = db.Column(db.BigInteger, primary_key=True)
    id_company = db.Column(db.Integer, db.ForeignKey('public.company.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    province = db.Column(db.String(255), nullable=True)
    municipality = db.Column(db.String(255), nullable=True)
    isactive = db.Column(db.Boolean, nullable=True)
    web_parking = db.Column(db.String(255), nullable=True)
    telephone = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    contact_person = db.Column(db.String(255), nullable=True)
    has_electricity = db.Column(db.Boolean, nullable=True)
    has_waste_disposal = db.Column(db.Boolean, nullable=True)
    has_vip_spots = db.Column(db.Boolean, nullable=True)
      
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    description = db.Column(db.String(255), nullable=True)

    company = db.relationship('Company', back_populates='parkings')
    spaces = db.relationship('Space', back_populates='parking', lazy=True)

    def to_dict(self, include_spaces=True, from_date=None, to_date=None):
        data = {
            "id": self.id,
            "id_company": self.id_company,
            "name": self.name,
            "municipality": self.municipality,
            "province": self.province,
            "active": self.isactive,
            "web": self.web_parking,
            "telephone": self.telephone,
            "email": self.email,
            "description": self.description,
            "longitude": self.longitude,
            "latitude": self.latitude,
            "personaContacto": self.contact_person,
            "has_electricity": self.has_electricity,
            "has_waste_disposal": self.has_waste_disposal,
            "has_vip_spots": self.has_vip_spots
        }
        if include_spaces:
            space_list = []
            for space in self.spaces:
                space_data = space.to_dict()
                if from_date and to_date:
                    from datetime import datetime
                    try:
                        if isinstance(from_date, str):
                            fd = datetime.strptime(from_date, "%Y-%m-%d").date()
                        else:
                            fd = from_date
                        if isinstance(to_date, str):
                            fh = datetime.strptime(to_date, "%Y-%m-%d").date()
                        else:
                            fh = to_date
                        
                        from models.booking import Booking
                        from models.space_blocked_day import SpaceBlockedDay
                        overlap = Booking.query.filter(
                            Booking.id_space == space.id,
                            Booking.start_date < fh,
                            Booking.end_date > fd,
                            Booking.status.in_(['1', '2'])
                        ).first()
                        blocked = SpaceBlockedDay.is_blocked_in_range(space.id, fd, fh)
                        if overlap or blocked or space_data["status"] == "1":
                            space_data["status"] = "1"
                        else:
                            space_data["status"] = "0"
                    except Exception as e:
                        current_app.logger.error(f"Error checking space occupancy for space_id {space.id}: {e}")
                space_list.append(space_data)
            data["spaces"] = space_list
        return data