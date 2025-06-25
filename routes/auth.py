from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User
from __init__ import db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST', 'OPTIONS'])
def register():
    """Registra um novo usuário"""
    if request.method == 'OPTIONS':
        return '', 200
        
    data = request.get_json()
    
    # Validação básica
    if not data.get('username') or not data.get('password'):
        return jsonify(
            {'message': 'Username e password são obrigatórios'}
        ), 400
    
    # Verifica se o usuário já existe
    existing_user = User.query.filter_by(username=data['username']).first()
    if existing_user:
        return jsonify({'message': 'Usuário já existe'}), 400
    
    # Cria hash da senha
    hashed_password = generate_password_hash(
        data['password'], method='pbkdf2:sha256'
    )
    new_user = User(username=data['username'], password=hashed_password)
    
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'Usuário registrado com sucesso!'})
    except Exception:
        db.session.rollback()
        return jsonify({'message': 'Erro ao registrar usuário'}), 500
    

@auth_bp.route('/login', methods=['POST', 'OPTIONS'])
def login():
    """Autentica um usuário"""
    if request.method == 'OPTIONS':
        return '', 200
        
    data = request.get_json()
    
    # Validação básica
    if not data.get('username') or not data.get('password'):
        return jsonify(
            {'message': 'Username e password são obrigatórios'}
        ), 400
    
    print(f"Tentativa de login para: {data.get('username')}")
    
    user = User.query.filter_by(username=data['username']).first()
    
    if user:
        print(f"Usuário encontrado: {user.username}")
        
        # Verifica se a senha está hasheada ou em texto plano
        if user.password.startswith('pbkdf2:sha256$'):
            # Senha hasheada - usa check_password_hash
            if check_password_hash(user.password, data['password']):
                session['user_id'] = user.id
                session['username'] = user.username
                print("Login bem-sucedido!")
                return jsonify({
                    'message': 'Login realizado com sucesso!',
                    'user': user.to_dict()
                })
        else:
            # Senha em texto plano - compara diretamente (compatibilidade)
            if user.password == data['password']:
                session['user_id'] = user.id
                session['username'] = user.username
                print("Login bem-sucedido!")
                return jsonify({
                    'message': 'Login realizado com sucesso!',
                    'user': user.to_dict()
                })
    
    print("Credenciais inválidas")
    return jsonify({'message': 'Credenciais inválidas'}), 401


@auth_bp.route('/logout', methods=['POST', 'OPTIONS'])
def logout():
    """Faz logout do usuário"""
    if request.method == 'OPTIONS':
        return '', 200
    
    session.clear()
    return jsonify({'message': 'Logout realizado com sucesso!'})


@auth_bp.route('/me', methods=['GET', 'OPTIONS'])
def get_current_user():
    """Retorna informações do usuário logado"""
    if request.method == 'OPTIONS':
        return '', 200
    
    if 'user_id' not in session:
        return jsonify({'message': 'Usuário não autenticado'}), 401
    
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'message': 'Usuário não encontrado'}), 404
    
    return jsonify({'user': user.to_dict()})
