from flask import Blueprint, jsonify, request
from src.models.professional import Professional, db
from src.models.work_schedule import WorkSchedule
from datetime import time

professional_bp = Blueprint('professional', __name__)

@professional_bp.route('/professionals', methods=['GET'])
def get_professionals():
    professionals = Professional.query.filter_by(ativo=True).all()
    return jsonify([professional.to_dict() for professional in professionals])

@professional_bp.route('/professionals', methods=['POST'])
def create_professional():
    data = request.json
    professional = Professional(
        user_id=data['user_id'],
        especialidade=data.get('especialidade'),
        ativo=data.get('ativo', True)
    )
    db.session.add(professional)
    db.session.commit()
    return jsonify({'message': 'Profissional criado com sucesso', 'professional': professional.to_dict()}), 201

@professional_bp.route('/professionals/<int:professional_id>', methods=['GET'])
def get_professional(professional_id):
    professional = Professional.query.get_or_404(professional_id)
    return jsonify(professional.to_dict())

@professional_bp.route('/professionals/<int:professional_id>', methods=['PUT'])
def update_professional(professional_id):
    professional = Professional.query.get_or_404(professional_id)
    data = request.json
    professional.especialidade = data.get('especialidade', professional.especialidade)
    professional.ativo = data.get('ativo', professional.ativo)
    db.session.commit()
    return jsonify(professional.to_dict())

@professional_bp.route('/work_schedules', methods=['POST'])
def create_work_schedule():
    data = request.json
    work_schedule = WorkSchedule(
        professional_id=data['professional_id'],
        dia_semana=data['dia_semana'],
        hora_inicio=time.fromisoformat(data['hora_inicio']),
        hora_fim=time.fromisoformat(data['hora_fim'])
    )
    db.session.add(work_schedule)
    db.session.commit()
    return jsonify({'message': 'Horário de trabalho criado com sucesso', 'work_schedule': work_schedule.to_dict()}), 201

@professional_bp.route('/work_schedules/professional/<int:professional_id>', methods=['GET'])
def get_work_schedules(professional_id):
    work_schedules = WorkSchedule.query.filter_by(professional_id=professional_id).all()
    return jsonify([schedule.to_dict() for schedule in work_schedules])

