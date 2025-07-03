from flask_sqlalchemy import SQLAlchemy
from src.models.user import db

class Professional(db.Model):
    __tablename__ = 'professionals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    especialidade = db.Column(db.String(255))
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    
    # Relacionamentos
    user = db.relationship('User', backref='professional', lazy=True)
    horarios_trabalho = db.relationship('WorkSchedule', backref='professional', lazy=True)
    agendamentos = db.relationship('Appointment', backref='professional', lazy=True)

    def __repr__(self):
        return f'<Professional {self.user.username if self.user else "Unknown"}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'nome': self.user.username if self.user else None,
            'especialidade': self.especialidade,
            'ativo': self.ativo
        }

