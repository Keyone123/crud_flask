from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

# Mock de dados
users = [
    {'id': 1, 'name': 'Keyone'},
    {'id': 2, 'name': 'ChatGPT'}
]

# Rota GET


@app.route('/users', methods=['GET'])
def get_users():
    return jsonify(users)


# Rota POST
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    new_user = {'id': len(users) + 1, 'name': data['name']}
    users.append(new_user)
    return jsonify(new_user), 201


@app.route('/')
def index():
    return render_template('index.html', name='Keyone')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
