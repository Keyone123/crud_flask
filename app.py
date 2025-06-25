#!/usr/bin/env python3
"""
Sistema Kanban & Finanças - Versão Refatorada
Aplicação Flask para gestão de tarefas e controle financeiro
"""

from flask import Flask, jsonify, render_template, request, send_file, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os

# =========================
# Configuração da Aplicação
# =========================

def create_app():
    """Factory function para criar a aplicação Flask"""
    app = Flask(__name__)
    
    # Configurações
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banco.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'uploads/'
    app.config['SECRET_KEY'] = 'minha_chave_secreta'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Configurar CORS
    CORS(app, origins=['http://127.0.0.1:5000', 'http://localhost:5000'])
    
    # Criar diretório de uploads
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    return app

# Criar a aplicação
app = create_app()
db = SQLAlchemy(app)

# =========================
# Modelos do Banco de Dados
# =========================

class User(db.Model):
    """Modelo para usuários do sistema"""
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username
        }

class TaskCategory(db.Model):
    """Modelo para categorias de tarefas"""
    __tablename__ = 'task_category'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

class Task(db.Model):
    """Modelo para tarefas do sistema Kanban"""
    __tablename__ = 'task'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default='TO_DO')
    priority = db.Column(db.String(20), nullable=False, default='MEDIUM')
    type = db.Column(db.String(20), nullable=False, default='WORK')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    due_date = db.Column(db.Date)
    created_by = db.Column(db.String(100))
    assigned_to = db.Column(db.String(100))
    tags = db.Column(db.String(255))
    category_id = db.Column(db.Integer, db.ForeignKey('task_category.id'))

    category = db.relationship('TaskCategory', backref=db.backref('tasks', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'type': self.type,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'created_by': self.created_by,
            'assigned_to': self.assigned_to,
            'tags': self.tags,
            'category_id': self.category_id
        }

class TaskHistory(db.Model):
    """Modelo para histórico de mudanças nas tarefas"""
    __tablename__ = 'task_history'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    old_status = db.Column(db.String(20))
    new_status = db.Column(db.String(20))
    observation = db.Column(db.Text)

    task = db.relationship('Task', backref=db.backref('histories', lazy=True))

class FinanceCategory(db.Model):
    """Modelo para categorias financeiras"""
    __tablename__ = 'finance_category'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type
        }

class Finance(db.Model):
    """Modelo para movimentações financeiras"""
    __tablename__ = 'finance'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    value = db.Column(db.Float, nullable=False)
    transaction_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    recurrence = db.Column(db.String(20), default='NONE')
    installments_total = db.Column(db.Integer, default=1)
    installment_current = db.Column(db.Integer, default=1)
    parent_finance_id = db.Column(db.Integer, db.ForeignKey('finance.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('finance_category.id'))

    category = db.relationship('FinanceCategory', backref=db.backref('finances', lazy=True))
    parent_finance = db.relationship('Finance', remote_side=[id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'value': self.value,
            'transaction_date': self.transaction_date.isoformat(),
            'created_at': self.created_at.isoformat(),
            'recurrence': self.recurrence,
            'installments_total': self.installments_total,
            'installment_current': self.installment_current,
            'parent_finance_id': self.parent_finance_id,
            'category_id': self.category_id
        }

class Attachment(db.Model):
    """Modelo para anexos de tarefas e finanças"""
    __tablename__ = 'attachment'
    
    id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    finance_id = db.Column(db.Integer, db.ForeignKey('finance.id'))

    task = db.relationship('Task', backref=db.backref('attachments', lazy=True))
    finance = db.relationship('Finance', backref=db.backref('attachments', lazy=True))

# =========================
# Funções Utilitárias
# =========================

def create_future_installments(finance):
    """Cria as parcelas futuras de uma movimentação parcelada"""
    if finance.installments_total <= 1:
        return
    
    for i in range(2, finance.installments_total + 1):
        future_date = finance.transaction_date
        
        # Adiciona meses para cada parcela
        month = future_date.month + (i - 1)
        year = future_date.year + (month - 1) // 12
        month = ((month - 1) % 12) + 1
        
        try:
            future_finance = Finance(
                title=f"{finance.title} - Parcela {i}/{finance.installments_total}",
                description=finance.description,
                value=finance.value,
                transaction_date=future_date.replace(year=year, month=month),
                recurrence='INSTALLMENT',
                installments_total=finance.installments_total,
                installment_current=i,
                parent_finance_id=finance.id,
                category_id=finance.category_id
            )
            db.session.add(future_finance)
        except ValueError:
            # Se a data for inválida, ajusta para o último dia do mês
            import calendar
            last_day = calendar.monthrange(year, month)[1]
            day = min(future_date.day, last_day)
            
            future_finance = Finance(
                title=f"{finance.title} - Parcela {i}/{finance.installments_total}",
                description=finance.description,
                value=finance.value,
                transaction_date=future_date.replace(year=year, month=month, day=day),
                recurrence='INSTALLMENT',
                installments_total=finance.installments_total,
                installment_current=i,
                parent_finance_id=finance.id,
                category_id=finance.category_id
            )
            db.session.add(future_finance)

def validate_request_data(data, required_fields):
    """Valida se os campos obrigatórios estão presentes"""
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return False, f"Campos obrigatórios ausentes: {', '.join(missing_fields)}"
    return True, None

# =========================
# Rotas das Páginas
# =========================

@app.route('/')
def index():
    """Página principal - Dashboard"""
    return render_template('index.html')

@app.route('/kanban')
def kanban():
    """Página do Kanban (legado)"""
    return render_template('kanban.html')

@app.route('/finance')
def finance():
    """Página de gestão financeira"""
    return render_template('finance.html')

@app.route('/kanban-university')
def kanban_university():
    """Página do Kanban para atividades universitárias"""
    return render_template('kanban-university.html')

@app.route('/kanban-work')
def kanban_work():
    """Página do Kanban para atividades de trabalho"""
    return render_template('kanban-work.html')

# =========================
# Rotas de Arquivos Estáticos
# =========================

@app.route('/static/css/<filename>')
def css_files(filename):
    """Serve arquivos CSS"""
    return send_file(f'static/css/{filename}')

@app.route('/static/js/<filename>')
def js_files(filename):
    """Serve arquivos JavaScript"""
    return send_file(f'static/js/{filename}')

# =========================
# Sistema de Autenticação
# =========================

@app.route('/register', methods=['POST', 'OPTIONS'])
def register():
    """Registra um novo usuário"""
    if request.method == 'OPTIONS':
        return '', 200
        
    data = request.get_json()
    
    # Validação
    is_valid, error_msg = validate_request_data(data, ['username', 'password'])
    if not is_valid:
        return jsonify({'message': error_msg}), 400
    
    # Verifica se o usuário já existe
    existing_user = User.query.filter_by(username=data['username']).first()
    if existing_user:
        return jsonify({'message': 'Usuário já existe'}), 400
    
    try:
        # Cria hash da senha
        hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
        new_user = User(username=data['username'], password=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({'message': 'Usuário registrado com sucesso!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao registrar usuário: {str(e)}'}), 500

@app.route('/login', methods=['POST', 'OPTIONS'])
def login():
    """Autentica um usuário"""
    if request.method == 'OPTIONS':
        return '', 200
        
    data = request.get_json()
    
    # Validação
    is_valid, error_msg = validate_request_data(data, ['username', 'password'])
    if not is_valid:
        return jsonify({'message': error_msg}), 400
    
    print(f"Tentativa de login para: {data.get('username')}")
    
    user = User.query.filter_by(username=data['username']).first()
    
    if user:
        print(f"Usuário encontrado: {user.username}")
        
        # Verifica senha
        if user.password.startswith('pbkdf2:sha256$'):
            # Senha hasheada
            if check_password_hash(user.password, data['password']):
                session['user_id'] = user.id
                session['username'] = user.username
                print("Login bem-sucedido!")
                return jsonify({
                    'message': 'Login realizado com sucesso!',
                    'user': user.to_dict()
                })
        else:
            # Senha em texto plano (compatibilidade)
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

@app.route('/logout', methods=['POST', 'OPTIONS'])
def logout():
    """Faz logout do usuário"""
    if request.method == 'OPTIONS':
        return '', 200
    
    session.clear()
    return jsonify({'message': 'Logout realizado com sucesso!'})

# =========================
# CRUD de Tarefas
# =========================

@app.route('/tasks', methods=['GET', 'OPTIONS'])
def get_tasks():
    """Lista todas as tarefas"""
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        tasks = Task.query.all()
        return jsonify([task.to_dict() for task in tasks])
    except Exception as e:
        return jsonify({'message': f'Erro ao buscar tarefas: {str(e)}'}), 500

@app.route('/tasks/<task_type>', methods=['GET', 'OPTIONS'])
def get_tasks_by_type(task_type):
    """Lista tarefas por tipo (university/work)"""
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        tasks = Task.query.filter_by(type=task_type.upper()).all()
        return jsonify([task.to_dict() for task in tasks])
    except Exception as e:
        return jsonify({'message': f'Erro ao buscar tarefas: {str(e)}'}), 500

@app.route('/tasks', methods=['POST', 'OPTIONS'])
def create_task():
    """Cria uma nova tarefa"""
    if request.method == 'OPTIONS':
        return '', 200
        
    data = request.get_json()
    
    # Validação
    is_valid, error_msg = validate_request_data(data, ['title'])
    if not is_valid:
        return jsonify({'message': error_msg}), 400
    
    try:
        new_task = Task(
            title=data['title'],
            description=data.get('description', ''),
            status=data.get('status', 'TO_DO'),
            priority=data.get('priority', 'MEDIUM'),
            type=data.get('type', 'WORK'),
            due_date=datetime.strptime(data['due_date'], '%Y-%m-%d').date() if data.get('due_date') else None,
            created_by=data.get('created_by'),
            assigned_to=data.get('assigned_to'),
            tags=data.get('tags', ''),
            category_id=data.get('category_id')
        )
        
        db.session.add(new_task)
        db.session.commit()
        
        return jsonify({
            'id': new_task.id,
            'message': 'Tarefa criada com sucesso!',
            'task': new_task.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao criar tarefa: {str(e)}'}), 500

@app.route('/tasks/<int:task_id>', methods=['PUT', 'OPTIONS'])
def update_task(task_id):
    """Atualiza uma tarefa existente"""
    if request.method == 'OPTIONS':
        return '', 200
        
    data = request.get_json()
    task = Task.query.get_or_404(task_id)
    old_status = task.status

    try:
        # Atualiza os campos
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

        # Registra mudança de status no histórico
        if old_status != task.status:
            history = TaskHistory(
                task_id=task.id,
                old_status=old_status,
                new_status=task.status,
                observation='Status atualizado via API'
            )
            db.session.add(history)
            db.session.commit()

        return jsonify({
            'message': 'Tarefa atualizada com sucesso!',
            'task': task.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao atualizar tarefa: {str(e)}'}), 500

@app.route('/tasks/<int:task_id>', methods=['DELETE', 'OPTIONS'])
def delete_task(task_id):
    """Deleta uma tarefa"""
    if request.method == 'OPTIONS':
        return '', 200
        
    task = Task.query.get_or_404(task_id)
    
    try:
        db.session.delete(task)
        db.session.commit()
        return jsonify({'message': 'Tarefa deletada com sucesso!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao deletar tarefa: {str(e)}'}), 500

@app.route('/tasks/month/<int:month>', methods=['GET', 'OPTIONS'])
def get_tasks_by_month(month):
    """Lista tarefas por mês"""
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        tasks = Task.query.filter(
            db.extract('month', Task.due_date) == month
        ).all()
        
        return jsonify([
            {
                'id': task.id,
                'title': task.title,
                'due_date': task.due_date.isoformat() if task.due_date else None
            }
            for task in tasks
        ])
    except Exception as e:
        return jsonify({'message': f'Erro ao buscar tarefas: {str(e)}'}), 500

# =========================
# CRUD de Finanças
# =========================

@app.route('/finances', methods=['GET', 'OPTIONS'])
def get_finances():
    """Lista todas as movimentações financeiras"""
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        finances = Finance.query.all()
        return jsonify([finance.to_dict() for finance in finances])
    except Exception as e:
        return jsonify({'message': f'Erro ao buscar finanças: {str(e)}'}), 500

@app.route('/finances', methods=['POST', 'OPTIONS'])
def create_finance():
    """Cria uma nova movimentação financeira"""
    if request.method == 'OPTIONS':
        return '', 200
        
    data = request.get_json()
    
    # Validação
    is_valid, error_msg = validate_request_data(data, ['title', 'value', 'transaction_date'])
    if not is_valid:
        return jsonify({'message': error_msg}), 400
    
    try:
        new_finance = Finance(
            title=data['title'],
            description=data.get('description', ''),
            value=float(data['value']),
            transaction_date=datetime.strptime(data['transaction_date'], '%Y-%m-%d').date(),
            recurrence=data.get('recurrence', 'NONE'),
            installments_total=data.get('installments_total', 1),
            installment_current=data.get('installment_current', 1),
            category_id=data.get('category_id')
        )
        
        db.session.add(new_finance)
        db.session.commit()

        # Cria parcelas futuras, se for parcelado
        if new_finance.installments_total > 1:
            create_future_installments(new_finance)
            db.session.commit()

        return jsonify({
            'id': new_finance.id,
            'message': 'Movimentação financeira criada com sucesso!',
            'finance': new_finance.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao criar movimentação: {str(e)}'}), 500

@app.route('/finances/<int:finance_id>', methods=['PUT', 'OPTIONS'])
def update_finance(finance_id):
    """Atualiza uma movimentação financeira"""
    if request.method == 'OPTIONS':
        return '', 200
        
    data = request.get_json()
    finance = Finance.query.get_or_404(finance_id)

    try:
        finance.title = data.get('title', finance.title)
        finance.description = data.get('description', finance.description)
        finance.value = float(data.get('value', finance.value))
        
        if data.get('transaction_date'):
            finance.transaction_date = datetime.strptime(data['transaction_date'], '%Y-%m-%d').date()
        
        finance.recurrence = data.get('recurrence', finance.recurrence)
        finance.installments_total = data.get('installments_total', finance.installments_total)
        finance.installment_current = data.get('installment_current', finance.installment_current)
        finance.category_id = data.get('category_id', finance.category_id)

        db.session.commit()
        
        return jsonify({
            'message': 'Movimentação atualizada com sucesso!',
            'finance': finance.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao atualizar movimentação: {str(e)}'}), 500

@app.route('/finances/<int:finance_id>', methods=['DELETE', 'OPTIONS'])
def delete_finance(finance_id):
    """Deleta uma movimentação financeira"""
    if request.method == 'OPTIONS':
        return '', 200
        
    finance = Finance.query.get_or_404(finance_id)
    
    try:
        db.session.delete(finance)
        db.session.commit()
        return jsonify({'message': 'Movimentação deletada com sucesso!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao deletar movimentação: {str(e)}'}), 500

@app.route('/finances/month/<int:month>', methods=['GET', 'OPTIONS'])
def get_finances_by_month(month):
    """Lista movimentações por mês"""
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
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
    except Exception as e:
        return jsonify({'message': f'Erro ao buscar finanças: {str(e)}'}), 500

@app.route('/finances/upcoming-installments', methods=['GET', 'OPTIONS'])
def get_upcoming_installments():
    """Lista próximas parcelas"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        from datetime import date
        today = date.today()
        
        upcoming = Finance.query.filter(
            Finance.transaction_date >= today,
            Finance.recurrence == 'INSTALLMENT'
        ).order_by(Finance.transaction_date).limit(10).all()
        
        return jsonify([finance.to_dict() for finance in upcoming])
    except Exception as e:
        return jsonify({'message': f'Erro ao buscar parcelas: {str(e)}'}), 500

# =========================
# Upload de Arquivos
# =========================

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx'}

def allowed_file(filename):
    """Verifica se o arquivo tem uma extensão permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST', 'OPTIONS'])
def upload_file():
    """Faz upload de um arquivo"""
    if request.method == 'OPTIONS':
        return '', 200
        
    if 'file' not in request.files:
        return jsonify({'message': 'Nenhum arquivo encontrado'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'Arquivo inválido'}), 400

    if not allowed_file(file.filename):
        return jsonify({'message': 'Tipo de arquivo não permitido'}), 400

    try:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        new_attachment = Attachment(
            file_path=file_path,
            description=request.form.get('description', ''),
            task_id=request.form.get('task_id') if request.form.get('task_id') else None,
            finance_id=request.form.get('finance_id') if request.form.get('finance_id') else None
        )
        
        db.session.add(new_attachment)
        db.session.commit()

        return jsonify({
            'message': 'Arquivo enviado com sucesso!',
            'attachment': {
                'id': new_attachment.id,
                'file_path': new_attachment.file_path,
                'description': new_attachment.description
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao fazer upload: {str(e)}'}), 500

# =========================
# Inicialização do Banco
# =========================

def init_database():
    """Inicializa o banco de dados"""
    with app.app_context():
        try:
            db.create_all()
            print("✅ Banco de dados inicializado!")
            
            # Verifica se existe pelo menos um usuário
            user_count = User.query.count()
            if user_count == 0:
                print("🔧 Criando usuário administrador padrão...")
                create_default_admin()
                
        except Exception as e:
            print(f"❌ Erro ao inicializar banco: {e}")

def create_default_admin():
    """Cria usuário administrador padrão se não existir"""
    try:
        admin_user = User(
            username='admin',
            password=generate_password_hash('123456', method='pbkdf2:sha256')
        )
        
        db.session.add(admin_user)
        db.session.commit()
        
        print("✅ Usuário admin criado!")
        print("👤 Username: admin")
        print("🔑 Password: 123456")
        
    except Exception as e:
        print(f"❌ Erro ao criar usuário admin: {e}")
        db.session.rollback()

# =========================
# Execução da Aplicação
# =========================

if __name__ == '__main__':
    # Inicializar banco de dados
    init_database()
    
    # Configurações para execução
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print("🚀 Iniciando Sistema Kanban & Finanças...")
    print(f"📍 Servidor rodando em: http://127.0.0.1:{port}")
    print(f"🔧 Modo debug: {'Ativado' if debug else 'Desativado'}")
    print("📋 Funcionalidades disponíveis:")
    print("   - Dashboard integrado")
    print("   - Kanban para Universidade e Trabalho")
    print("   - Gestão financeira com parcelas")
    print("   - Upload de arquivos")
    print("   - Sistema de autenticação")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True
    )
