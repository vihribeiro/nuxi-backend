from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Client(db.Model):
    __tablename__ = 'clients'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    telefone = db.Column(db.String(20), unique=True, nullable=False)
    data_cadastro = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relacionamentos
    agendamentos = db.relationship('Appointment', backref='client', lazy=True)
    fila_espera = db.relationship('Waitlist', backref='client', lazy=True)

    def __repr__(self):
        return f'<Client {self.nome}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'telefone': self.telefone,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None
        }

