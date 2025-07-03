from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professionals.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    data_agendamento = db.Column(db.Date, nullable=False)
    hora_agendamento = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pendente')  # pendente, confirmado, cancelado, concluido, reagendado
    data_criacao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Appointment {self.id} - {self.data_agendamento} {self.hora_agendamento}>'

    def to_dict(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'client_nome': self.client.nome if self.client else None,
            'professional_id': self.professional_id,
            'professional_nome': self.professional.user.username if self.professional and self.professional.user else None,
            'service_id': self.service_id,
            'service_nome': self.service.nome if self.service else None,
            'service_preco': float(self.service.preco) if self.service and self.service.preco else None,
            'data_agendamento': self.data_agendamento.isoformat() if self.data_agendamento else None,
            'hora_agendamento': self.hora_agendamento.strftime('%H:%M') if self.hora_agendamento else None,
            'status': self.status,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None
        }

