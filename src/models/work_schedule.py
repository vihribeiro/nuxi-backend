from flask_sqlalchemy import SQLAlchemy
from src.models.user import db

class WorkSchedule(db.Model):
    __tablename__ = 'work_schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    professional_id = db.Column(db.Integer, db.ForeignKey('professionals.id'), nullable=False)
    dia_semana = db.Column(db.Integer, nullable=False)  # 0=Segunda, 6=Domingo
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fim = db.Column(db.Time, nullable=False)

    def __repr__(self):
        return f'<WorkSchedule Professional:{self.professional_id} Day:{self.dia_semana}>'

    def to_dict(self):
        return {
            'id': self.id,
            'professional_id': self.professional_id,
            'dia_semana': self.dia_semana,
            'hora_inicio': self.hora_inicio.strftime('%H:%M') if self.hora_inicio else None,
            'hora_fim': self.hora_fim.strftime('%H:%M') if self.hora_fim else None
        }

