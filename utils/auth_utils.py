from functools import wraps
from flask import session, jsonify


def login_required(f):
    """Decorator para rotas que requerem autenticação"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'message': 'Autenticação necessária'}), 401
        return f(*args, **kwargs)
    return decorated_function


def get_current_user_id():
    """Retorna o ID do usuário logado"""
    return session.get('user_id')


def get_current_username():
    """Retorna o username do usuário logado"""
    return session.get('username')
