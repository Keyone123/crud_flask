from flask import (
    Flask, jsonify, render_template, request, send_file, session
)
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configurações gerais
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banco.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['SECRET_KEY'] = 'minha_chave_secreta'

# Configurar CORS
CORS(app, origins=['http://127.0.0.1:5000', 'http://localhost:5000'])

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db = SQLAlchemy(app)

# =========================
# Modelos do Sistema
# =========================


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


class TaskCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default='TO_DO')
    priority = db.Column(db.String(20), nullable=False, default='MEDIUM')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    due_date = db.Column(db.Date)
    created_by = db.Column(db.String(100))
    assigned_to = db.Column(db.String(100))
    tags = db.Column(db.String(255))
    category_id = db.Column(db.Integer, db.ForeignKey('task_category.id'))

    category = db.relationship(
        'TaskCategory',
        backref=db.backref('tasks', lazy=True)
    )


class TaskHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    old_status = db.Column(db.String(20))
    new_status = db.Column(db.String(20))
    observation = db.Column(db.Text)

    task = db.relationship('Task', backref=db.backref('histories', lazy=True))


class FinanceCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)


class Finance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    value = db.Column(db.Float, nullable=False)
    transaction_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    recurrence = db.Column(db.String(20), default='NONE')
    category_id = db.Column(db.Integer, db.ForeignKey('finance_category.id'))

    category = db.relationship(
        'FinanceCategory',
        backref=db.backref('finances', lazy=True)
    )


class Attachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    finance_id = db.Column(db.Integer, db.ForeignKey('finance.id'))

    task = db.relationship(
        'Task',
        backref=db.backref('attachments', lazy=True)
    )
    finance = db.relationship(
        'Finance',
        backref=db.backref('attachments', lazy=True)
    )


with app.app_context():
    db.create_all()

# =========================
# Rotas das Páginas
# =========================


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/kanban')
def kanban():
    return render_template('kanban.html')


@app.route('/finance')
def finance():
    return render_template('finance.html')

# =========================
# Rotas de Arquivos Estáticos
# =========================


@app.route('/static/css/<filename>')
def css_files(filename):
    return send_file(f'static/css/{filename}')


@app.route('/static/js/<filename>')
def js_files(filename):
    return send_file(f'static/js/{filename}')

# =========================
# Sistema de Login
# =========================


@app.route('/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        return '', 200
        
    data = request.get_json()
    
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
    

@app.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200
        
    data = request.get_json()
    
    print(f"Tentativa de login para: {data.get('username')}")
    
    user = User.query.filter_by(username=data['username']).first()
    
    if user:
        print(f"Usuário encontrado: {user.username}")
        print("Verificando senha...")
        
        # Verifica se a senha está hasheada ou em texto plano
        if user.password.startswith('pbkdf2:sha256$'):
            # Senha hasheada - usa check_password_hash
            if check_password_hash(user.password, data['password']):
                session['user_id'] = user.id
                session['username'] = user.username
                print("Login bem-sucedido!")
                return jsonify({'message': 'Login realizado com sucesso!'})
            else:
                print("Senha incorreta (hasheada)")
        else:
            # Senha em texto plano - compara diretamente
            if user.password == data['password']:
                session['user_id'] = user.id
                session['username'] = user.username
                print("Login bem-sucedido!")
                return jsonify({'message': 'Login realizado com sucesso!'})
            else:
                print("Senha incorreta (texto plano)")
    else:
        print("Usuário não encontrado")
    
    return jsonify({'message': 'Credenciais inválidas'}), 401

# =========================
# CRUD Tarefas
# =========================


@app.route('/tasks', methods=['GET', 'OPTIONS'])
def get_tasks():
    if request.method == 'OPTIONS':
        return '', 200
        
    tasks = Task.query.all()
    return jsonify([
        {
            'id': t.id,
            'title': t.title,
            'description': t.description,
            'status': t.status,
            'priority': t.priority,
            'created_at': t.created_at.isoformat(),
            'updated_at': t.updated_at.isoformat(),
            'due_date': t.due_date.isoformat() if t.due_date else None,
            'created_by': t.created_by,
            'assigned_to': t.assigned_to,
            'tags': t.tags,
            'category_id': t.category_id
        }
        for t in tasks
    ])


@app.route('/tasks', methods=['POST', 'OPTIONS'])
def create_task():
    if request.method == 'OPTIONS':
        return '', 200
        
    data = request.get_json()
    new_task = Task(
        title=data['title'],
        description=data.get('description', ''),
        status=data.get('status', 'TO_DO'),
        priority=data.get('priority', 'MEDIUM'),
        due_date=(
            datetime.strptime(data['due_date'], '%Y-%m-%d').date()
            if data.get('due_date') else None
        ),
        created_by=data.get('created_by'),
        assigned_to=data.get('assigned_to'),
        tags=data.get('tags', ''),
        category_id=data.get('category_id')
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify({
        'id': new_task.id,
        'message': 'Tarefa criada com sucesso!'
    })


@app.route('/tasks/<int:task_id>', methods=['PUT', 'OPTIONS'])
def update_task(task_id):
    if request.method == 'OPTIONS':
        return '', 200
        
    data = request.get_json()
    task = Task.query.get_or_404(task_id)
    old_status = task.status

    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.status = data.get('status', task.status)
    task.priority = data.get('priority', task.priority)
    if data.get('due_date'):
        task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
    task.assigned_to = data.get('assigned_to', task.assigned_to)
    task.tags = data.get('tags', task.tags)
    task.updated_at = datetime.utcnow()

    db.session.commit()

    if old_status != task.status:
        history = TaskHistory(
            task_id=task.id,
            old_status=old_status,
            new_status=task.status,
            observation='Status atualizado via API'
        )
        db.session.add(history)
        db.session.commit()

    return jsonify({'message': 'Tarefa atualizada com sucesso!'})


@app.route('/tasks/<int:task_id>', methods=['DELETE', 'OPTIONS'])
def delete_task(task_id):
    if request.method == 'OPTIONS':
        return '', 200
        
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Tarefa deletada com sucesso!'})


@app.route('/tasks/month/<int:month>', methods=['GET', 'OPTIONS'])
def get_tasks_by_month(month):
    if request.method == 'OPTIONS':
        return '', 200
        
    tasks = Task.query.filter(
        db.extract('month', Task.due_date) == month
    ).all()
    return jsonify([
        {
            'id': task.id,
            'title': task.title,
            'due_date': task.due_date.isoformat()
        }
        for task in tasks
    ])

# =========================
# CRUD Finanças
# =========================


@app.route('/finances', methods=['GET', 'OPTIONS'])
def get_finances():
    if request.method == 'OPTIONS':
        return '', 200
        
    finances = Finance.query.all()
    return jsonify([
        {
            'id': f.id,
            'title': f.title,
            'description': f.description,
            'value': f.value,
            'transaction_date': f.transaction_date.isoformat(),
            'created_at': f.created_at.isoformat(),
            'recurrence': f.recurrence,
            'category_id': f.category_id
        }
        for f in finances
    ])


@app.route('/finances', methods=['POST', 'OPTIONS'])
def create_finance():
    if request.method == 'OPTIONS':
        return '', 200
        
    data = request.get_json()
    new_finance = Finance(
        title=data['title'],
        description=data.get('description', ''),
        value=data['value'],
        transaction_date=(
            datetime.strptime(
                data['transaction_date'], '%Y-%m-%d'
            ).date()
        ),
        recurrence=data.get('recurrence', 'NONE'),
        category_id=data.get('category_id')
    )
    db.session.add(new_finance)
    db.session.commit()
    return jsonify({
        'id': new_finance.id,
        'message': 'Movimentação financeira criada com sucesso!'
    })


@app.route('/finances/<int:finance_id>', methods=['PUT', 'OPTIONS'])
def update_finance(finance_id):
    if request.method == 'OPTIONS':
        return '', 200
        
    data = request.get_json()
    finance = Finance.query.get_or_404(finance_id)

    finance.title = data.get('title', finance.title)
    finance.description = data.get('description', finance.description)
    finance.value = data.get('value', finance.value)
    if data.get('transaction_date'):
        finance.transaction_date = (
            datetime.strptime(data['transaction_date'], '%Y-%m-%d').date()
        )
    finance.recurrence = data.get('recurrence', finance.recurrence)
    finance.category_id = data.get('category_id', finance.category_id)

    db.session.commit()
    return jsonify({'message': 'Movimentação atualizada com sucesso!'})


@app.route('/finances/<int:finance_id>', methods=['DELETE', 'OPTIONS'])
def delete_finance(finance_id):
    if request.method == 'OPTIONS':
        return '', 200
        
    finance = Finance.query.get_or_404(finance_id)
    db.session.delete(finance)
    db.session.commit()
    return jsonify({'message': 'Movimentação deletada com sucesso!'})


@app.route('/finances/month/<int:month>', methods=['GET', 'OPTIONS'])
def get_finances_by_month(month):
    if request.method == 'OPTIONS':
        return '', 200
        
    finances = Finance.query.filter(
        db.extract('month', Finance.transaction_date) == month
    ).all()
    return jsonify([
        {
            'id': f.id,
            'title': f.title,
            'value': f.value,
            'transaction_date': f.transaction_date.isoformat()
        }
        for f in finances
    ])

# =========================
# Upload de Anexos
# =========================


@app.route('/upload', methods=['POST', 'OPTIONS'])
def upload_file():
    if request.method == 'OPTIONS':
        return '', 200
        
    if 'file' not in request.files:
        return jsonify({'message': 'Nenhum arquivo encontrado'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'Arquivo inválido'}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    new_attachment = Attachment(
        file_path=file_path,
        description=request.form.get('description', ''),
        task_id=request.form.get('task_id'),
        finance_id=request.form.get('finance_id')
    )
    db.session.add(new_attachment)
    db.session.commit()

    return jsonify({
        'message': 'Arquivo enviado com sucesso!',
        'file_path': file_path
    })

# =========================
# Execução
# =========================


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
