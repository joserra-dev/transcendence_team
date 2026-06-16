from database import db

class InvoiceSequence(db.Model):
    __tablename__ = 'invoice_sequences'

    id = db.Column(db.Integer, primary_key=True)
    id_company = db.Column(db.Integer, db.ForeignKey('public.company.id', ondelete='CASCADE'), nullable=False)
    serie = db.Column(db.String(20), nullable=False)
    last_number = db.Column(db.Integer, default=0, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('id_company', 'serie', name='_company_serie_uc'),
        {'schema': 'public'}
    )

    company = db.relationship('Company', back_populates='sequences')