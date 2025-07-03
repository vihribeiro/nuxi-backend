from flask import Blueprint, jsonify, request
from src.models.waitlist import Waitlist, db
from datetime import datetime

waitlist_bp = Blueprint('waitlist', __name__)

@waitlist_bp.route('/waitlist', methods=['GET'])
def get_waitlist():
    waitlist_entries = Waitlist.query.filter_by(status='ativo').order_by(Waitlist.posicao).all()
    return jsonify([entry.to_dict() for entry in waitlist_entries])

@waitlist_bp.route('/waitlist', methods=['POST'])
def add_to_waitlist():
    data = request.json
    
    # Calcular próxima posição na fila para o período
    max_position = db.session.query(db.func.max(Waitlist.posicao)).filter(
        Waitlist.periodo == data['periodo'],
        Waitlist.status == 'ativo'
    ).scalar() or 0
    
    # Verificar se já existe 20 pessoas na fila para o período
    current_count = Waitlist.query.filter(
        Waitlist.periodo == data['periodo'],
        Waitlist.status == 'ativo'
    ).count()
    
    if current_count >= 20:
        return jsonify({'message': 'Fila de espera lotada para este período'}), 400
    
    waitlist_entry = Waitlist(
        client_id=data['client_id'],
        periodo=data['periodo'],
        data_desejada=datetime.strptime(data['data_desejada'], '%Y-%m-%d').date() if data.get('data_desejada') else None,
        service_id=data.get('service_id'),
        professional_id=data.get('professional_id'),
        posicao=max_position + 1,
        status='ativo'
    )
    
    db.session.add(waitlist_entry)
    db.session.commit()
    
    return jsonify({'message': 'Adicionado à fila de espera', 'waitlist_entry': waitlist_entry.to_dict()}), 201

@waitlist_bp.route('/waitlist/next_in_line/<period>', methods=['GET'])
def get_next_in_line(period):
    next_entry = Waitlist.query.filter(
        Waitlist.periodo == period,
        Waitlist.status == 'ativo'
    ).order_by(Waitlist.posicao).first()
    
    if not next_entry:
        return jsonify({'message': 'Nenhum cliente na fila de espera para este período'}), 404
    
    return jsonify(next_entry.to_dict())

@waitlist_bp.route('/waitlist/<int:waitlist_id>/status', methods=['PUT'])
def update_waitlist_status(waitlist_id):
    waitlist_entry = Waitlist.query.get_or_404(waitlist_id)
    data = request.json
    
    old_status = waitlist_entry.status
    waitlist_entry.status = data['status']
    
    # Se o status mudou para 'atendido' ou 'cancelado', reorganizar posições
    if old_status == 'ativo' and waitlist_entry.status in ['atendido', 'cancelado']:
        # Atualizar posições dos clientes restantes na fila
        remaining_entries = Waitlist.query.filter(
            Waitlist.periodo == waitlist_entry.periodo,
            Waitlist.status == 'ativo',
            Waitlist.posicao > waitlist_entry.posicao
        ).all()
        
        for entry in remaining_entries:
            entry.posicao -= 1
    
    db.session.commit()
    
    return jsonify({'message': 'Status da fila de espera atualizado', 'waitlist_entry': waitlist_entry.to_dict()})

@waitlist_bp.route('/waitlist/client/<int:client_id>', methods=['GET'])
def get_client_waitlist(client_id):
    waitlist_entries = Waitlist.query.filter_by(client_id=client_id, status='ativo').all()
    return jsonify([entry.to_dict() for entry in waitlist_entries])

