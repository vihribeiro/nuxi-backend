from flask import Blueprint, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from src.models.user import User, db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'message': 'Email e senha são obrigatórios'}), 400
    
    user = User.query.filter_by(email=email, ativo=True).first()
    
    if user and user.check_password(password):
        access_token = create_access_token(identity=user.id)
        return jsonify({
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
    
    return jsonify({'message': 'Credenciais inválidas'}), 401

@auth_bp.route('/auth/register', methods=['POST'])
def register():
    data = request.json
    
    # Verificar se o usuário já existe
    existing_user = User.query.filter(
        (User.email == data['email']) | (User.username == data['username'])
    ).first()
    
    if existing_user:
        return jsonify({'message': 'Usuário já existe'}), 400
    
    user = User(
        nome=data['nome'],
        username=data['username'],
        email=data['email'],
        tipo_usuario=data.get('tipo_usuario', 'admin'),
        telefone=data.get('telefone')
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': 'Usuário criado com sucesso', 'user': user.to_dict()}), 201

@auth_bp.route('/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'Usuário não encontrado'}), 404
    
    return jsonify(user.to_dict())

