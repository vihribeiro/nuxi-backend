from flask_sqlalchemy import SQLAlchemy
from src.models.user import db

class Service(db.Model):
    __tablename__ = 'services'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), unique=True, nullable=False)
    descricao = db.Column(db.Text)
    duracao_minutos = db.Column(db.Integer, nullable=False)
    preco = db.Column(db.Numeric(10, 2), nullable=False)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    
    # Relacionamentos
    agendamentos = db.relationship('Appointment', backref='service', lazy=True)

    def __repr__(self):
        return f'<Service {self.nome}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'duracao_minutos': self.duracao_minutos,
            'preco': float(self.preco) if self.preco else None,
            'ativo': self.ativo
        }

