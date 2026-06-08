from database import db

class Company(db.Model):
    __tablename__ = 'company'
    __table_args__ = {'schema': 'public'}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    cif = db.Column(db.String(15), nullable=True)

    # Relaciones para acceder fácilmente desde el objeto
    users = db.relationship('Profiles', backref='company', lazy=True)
    
    parkings = db.relationship('Parking', backref='company', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "cif": self.cif
        }
        
   