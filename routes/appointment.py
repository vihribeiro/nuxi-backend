from flask import Blueprint, jsonify, request
from src.models.appointment import Appointment, db
from src.models.professional import Professional
from src.models.work_schedule import WorkSchedule
from src.models.client import Client
from src.models.service import Service
from datetime import datetime, date, time, timedelta
from sqlalchemy import and_, or_

appointment_bp = Blueprint('appointment', __name__)

@appointment_bp.route('/appointments', methods=['GET'])
def get_appointments():
    appointments = Appointment.query.all()
    return jsonify([appointment.to_dict() for appointment in appointments])

@appointment_bp.route('/appointments', methods=['POST'])
def create_appointment():
    data = request.json
    
    # Verificar se o horário está disponível
    existing_appointment = Appointment.query.filter(
        and_(
            Appointment.professional_id == data['professional_id'],
            Appointment.data_agendamento == datetime.strptime(data['data_agendamento'], '%Y-%m-%d').date(),
            Appointment.hora_agendamento == time.fromisoformat(data['hora_agendamento']),
            Appointment.status.in_(['pendente', 'confirmado'])
        )
    ).first()
    
    if existing_appointment:
        return jsonify({'message': 'Horário não disponível'}), 400
    
    appointment = Appointment(
        client_id=data['client_id'],
        professional_id=data['professional_id'],
        service_id=data['service_id'],
        data_agendamento=datetime.strptime(data['data_agendamento'], '%Y-%m-%d').date(),
        hora_agendamento=time.fromisoformat(data['hora_agendamento']),
        status=data.get('status', 'pendente')
    )
    db.session.add(appointment)
    db.session.commit()
    return jsonify({'message': 'Agendamento criado com sucesso', 'appointment': appointment.to_dict()}), 201

@appointment_bp.route('/appointments/available_times', methods=['GET'])
def get_available_times():
    date_str = request.args.get('date')
    period = request.args.get('period')  # manha, tarde, noite
    professional_id = request.args.get('professional_id')
    
    if not date_str:
        return jsonify({'message': 'Data é obrigatória'}), 400
    
    target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    day_of_week = target_date.weekday()  # 0=Monday, 6=Sunday
    
    # Definir períodos (personalizável)
    periods = {
        'manha': (time(8, 0), time(12, 0)),
        'tarde': (time(13, 0), time(18, 0)),
        'noite': (time(19, 0), time(22, 0))
    }
    
    if period and period not in periods:
        return jsonify({'message': 'Período inválido'}), 400
    
    # Buscar profissionais disponíveis
    query = Professional.query.filter_by(ativo=True)
    if professional_id:
        query = query.filter_by(id=professional_id)
    
    professionals = query.all()
    available_times = []
    
    for prof in professionals:
        # Buscar horários de trabalho do profissional para o dia da semana
        work_schedules = WorkSchedule.query.filter(
            and_(
                WorkSchedule.professional_id == prof.id,
                WorkSchedule.dia_semana == day_of_week
            )
        ).all()
        
        for schedule in work_schedules:
            # Gerar slots de 30 minutos
            current_time = schedule.hora_inicio
            end_time = schedule.hora_fim
            
            while current_time < end_time:
                # Verificar se está no período solicitado
                if period:
                    period_start, period_end = periods[period]
                    if not (period_start <= current_time < period_end):
                        current_time = (datetime.combine(date.today(), current_time) + timedelta(minutes=30)).time()
                        continue
                
                # Verificar se o horário está ocupado
                existing_appointment = Appointment.query.filter(
                    and_(
                        Appointment.professional_id == prof.id,
                        Appointment.data_agendamento == target_date,
                        Appointment.hora_agendamento == current_time,
                        Appointment.status.in_(['pendente', 'confirmado'])
                    )
                ).first()
                
                if not existing_appointment:
                    available_times.append({
                        'time': current_time.strftime('%H:%M'),
                        'professional_id': prof.id,
                        'professional_name': prof.user.username if prof.user else 'Desconhecido'
                    })
                
                current_time = (datetime.combine(date.today(), current_time) + timedelta(minutes=30)).time()
    
    return jsonify(available_times)

@appointment_bp.route('/appointments/client/<int:client_id>', methods=['GET'])
def get_client_appointments(client_id):
    appointments = Appointment.query.filter_by(client_id=client_id).all()
    return jsonify([appointment.to_dict() for appointment in appointments])

@appointment_bp.route('/appointments/<int:appointment_id>/cancel', methods=['PUT'])
def cancel_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    appointment.status = 'cancelado'
    db.session.commit()
    return jsonify({'message': 'Agendamento cancelado com sucesso', 'appointment': appointment.to_dict()})

@appointment_bp.route('/appointments/<int:appointment_id>/confirm', methods=['PUT'])
def confirm_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    appointment.status = 'confirmado'
    db.session.commit()
    return jsonify({'message': 'Agendamento confirmado com sucesso', 'appointment': appointment.to_dict()})

@appointment_bp.route('/appointments/<int:appointment_id>/reschedule', methods=['PUT'])
def reschedule_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    data = request.json
    
    # Verificar se o novo horário está disponível
    new_date = datetime.strptime(data['new_date'], '%Y-%m-%d').date()
    new_time = time.fromisoformat(data['new_time'])
    
    existing_appointment = Appointment.query.filter(
        and_(
            Appointment.professional_id == appointment.professional_id,
            Appointment.data_agendamento == new_date,
            Appointment.hora_agendamento == new_time,
            Appointment.status.in_(['pendente', 'confirmado']),
            Appointment.id != appointment_id
        )
    ).first()
    
    if existing_appointment:
        return jsonify({'message': 'Novo horário não disponível'}), 400
    
    appointment.data_agendamento = new_date
    appointment.hora_agendamento = new_time
    appointment.status = 'reagendado'
    db.session.commit()
    
    return jsonify({'message': 'Agendamento reagendado com sucesso', 'appointment': appointment.to_dict()})

