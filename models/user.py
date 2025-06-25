from __init__ import db


class User(db.Model):
    """Modelo para usuários do sistema"""
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'username': self.username
        }
