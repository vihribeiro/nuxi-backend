from flask import Blueprint, jsonify, request
from src.models.service import Service, db

service_bp = Blueprint('service', __name__)

@service_bp.route('/services', methods=['GET'])
def get_services():
    services = Service.query.filter_by(ativo=True).all()
    return jsonify([service.to_dict() for service in services])

@service_bp.route('/services', methods=['POST'])
def create_service():
    data = request.json
    service = Service(
        nome=data['nome'],
        descricao=data.get('descricao'),
        duracao_minutos=data['duracao_minutos'],
        preco=data['preco'],
        ativo=data.get('ativo', True)
    )
    db.session.add(service)
    db.session.commit()
    return jsonify({'message': 'Serviço criado com sucesso', 'service': service.to_dict()}), 201

@service_bp.route('/services/<int:service_id>', methods=['GET'])
def get_service(service_id):
    service = Service.query.get_or_404(service_id)
    return jsonify(service.to_dict())

@service_bp.route('/services/<int:service_id>', methods=['PUT'])
def update_service(service_id):
    service = Service.query.get_or_404(service_id)
    data = request.json
    service.nome = data.get('nome', service.nome)
    service.descricao = data.get('descricao', service.descricao)
    service.duracao_minutos = data.get('duracao_minutos', service.duracao_minutos)
    service.preco = data.get('preco', service.preco)
    service.ativo = data.get('ativo', service.ativo)
    db.session.commit()
    return jsonify(service.to_dict())

@service_bp.route('/services/<int:service_id>', methods=['DELETE'])
def delete_service(service_id):
    service = Service.query.get_or_404(service_id)
    service.ativo = False  # Soft delete
    db.session.commit()
    return '', 204

