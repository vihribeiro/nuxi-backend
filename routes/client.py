from flask import Blueprint, jsonify, request
from src.models.client import Client, db

client_bp = Blueprint('client', __name__)

@client_bp.route('/clients', methods=['GET'])
def get_clients():
    clients = Client.query.all()
    return jsonify([client.to_dict() for client in clients])

@client_bp.route('/clients', methods=['POST'])
def create_client():
    data = request.json
    
    # Verificar se o cliente já existe pelo telefone
    existing_client = Client.query.filter_by(telefone=data['telefone']).first()
    if existing_client:
        return jsonify({'message': 'Cliente já existe', 'client': existing_client.to_dict()}), 200
    
    client = Client(
        nome=data['nome'],
        telefone=data['telefone']
    )
    db.session.add(client)
    db.session.commit()
    return jsonify({'message': 'Cliente criado com sucesso', 'client': client.to_dict()}), 201

@client_bp.route('/clients/<int:client_id>', methods=['GET'])
def get_client(client_id):
    client = Client.query.get_or_404(client_id)
    return jsonify(client.to_dict())

@client_bp.route('/clients/by_phone/<phone_number>', methods=['GET'])
def get_client_by_phone(phone_number):
    client = Client.query.filter_by(telefone=phone_number).first()
    if not client:
        return jsonify({'message': 'Cliente não encontrado'}), 404
    return jsonify(client.to_dict())

@client_bp.route('/clients/<int:client_id>', methods=['PUT'])
def update_client(client_id):
    client = Client.query.get_or_404(client_id)
    data = request.json
    client.nome = data.get('nome', client.nome)
    client.telefone = data.get('telefone', client.telefone)
    db.session.commit()
    return jsonify(client.to_dict())

@client_bp.route('/clients/<int:client_id>', methods=['DELETE'])
def delete_client(client_id):
    client = Client.query.get_or_404(client_id)
    db.session.delete(client)
    db.session.commit()
    return '', 204

