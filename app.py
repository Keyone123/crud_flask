from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuração do banco SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Modelo User
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

# Criar tabelas antes da primeira requisição


@app.before_first_request
def create_tables():
    db.create_all()

# Rota GET - retorna todos os usuários em JSON


@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{'id': user.id, 'name': user.name} for user in users])


# Rota POST - cria um novo usuário
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    new_user = User(name=data['name'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'id': new_user.id, 'name': new_user.name}), 201


# Página HTML com listagem de usuários
@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', name='Keyone', users=users)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
