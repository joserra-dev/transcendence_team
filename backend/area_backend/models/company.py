from database import db

class Company(db.Model):
    __tablename__ = 'company'
    __table_args__ = {'schema': 'public'}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    cif = db.Column(db.String(15), nullable=True)
    
    tbai_enabled = db.Column(db.Boolean, default=False, nullable=False)
    tbai_software_license = db.Column(db.String(100), nullable=True) 

    users = db.relationship('Profiles', back_populates='company', lazy=True)
    parkings = db.relationship('Parking', back_populates='company', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "cif": self.cif,
            "tbai_enabled": self.tbai_enabled,
            "tbai_software_license": self.tbai_software_license
        }
   