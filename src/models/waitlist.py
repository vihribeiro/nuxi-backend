from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Waitlist(db.Model):
    __tablename__ = 'waitlist'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    periodo = db.Column(db.String(10), nullable=False)  # manha, tarde, noite
    data_desejada = db.Column(db.Date)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'))
    professional_id = db.Column(db.Integer, db.ForeignKey('professionals.id'))
    posicao = db.Column(db.Integer, nullable=False)
    data_entrada = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default='ativo')  # ativo, atendido, cancelado
    
    # Relacionamentos
    service = db.relationship('Service', backref='waitlist_entries', lazy=True)
    professional = db.relationship('Professional', backref='waitlist_entries', lazy=True)

    def __repr__(self):
        return f'<Waitlist {self.id} - Client:{self.client_id} Position:{self.posicao}>'

    def to_dict(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'client_nome': self.client.nome if self.client else None,
            'periodo': self.periodo,
            'data_desejada': self.data_desejada.isoformat() if self.data_desejada else None,
            'service_id': self.service_id,
            'service_nome': self.service.nome if self.service else None,
            'professional_id': self.professional_id,
            'professional_nome': self.professional.user.username if self.professional and self.professional.user else None,
            'posicao': self.posicao,
            'data_entrada': self.data_entrada.isoformat() if self.data_entrada else None,
            'status': self.status
        }

