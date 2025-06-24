from app import app, db, User
from werkzeug.security import generate_password_hash


def init_database():
    """
    Inicializa o banco de dados e cria as tabelas
    """
    with app.app_context():
        try:
            # Remove todas as tabelas existentes
            print("🗑️  Removendo tabelas existentes...")
            db.drop_all()
            
            # Cria todas as tabelas
            print("🏗️  Criando tabelas...")
            db.create_all()
            
            print("✅ Tabelas criadas com sucesso!")
            
            # Lista as tabelas criadas
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📋 Tabelas criadas: {', '.join(tables)}")
            
        except Exception as e:
            print(f"❌ Erro ao criar tabelas: {e}")


def create_admin_user():
    """
    Cria usuário administrador
    """
    with app.app_context():
        try:
            # Verifica se já existe um usuário admin
            existing_admin = User.query.filter_by(username='admin').first()
            if existing_admin:
                print("⚠️  Usuário admin já existe. Removendo...")
                db.session.delete(existing_admin)
                db.session.commit()
            
            # Cria novo usuário admin
            admin_user = User(
                username='admin',
                password=generate_password_hash(
                    '123456', method='pbkdf2:sha256'
                )
            )
            
            db.session.add(admin_user)
            db.session.commit()
            
            print("✅ Usuário admin criado com sucesso!")
            print("👤 Username: admin")
            print("🔑 Password: 123456")
            
        except Exception as e:
            print(f"❌ Erro ao criar usuário admin: {e}")
            db.session.rollback()


def create_sample_data():
    """
    Cria dados de exemplo para teste
    """
    with app.app_context():
        try:
            from app import Task, Finance, TaskCategory, FinanceCategory
            from datetime import date
            
            # Criar categorias de tarefas
            task_categories = [
                TaskCategory(
                    name='Desenvolvimento',
                    description='Tarefas de desenvolvimento'
                ),
                TaskCategory(name='Design', description='Tarefas de design'),
                TaskCategory(name='Teste', description='Tarefas de teste')
            ]
            
            for category in task_categories:
                db.session.add(category)
            
            # Criar categorias financeiras
            finance_categories = [
                FinanceCategory(name='Receita', type='INCOME'),
                FinanceCategory(name='Despesa', type='EXPENSE'),
                FinanceCategory(name='Investimento', type='INVESTMENT')
            ]
            
            for category in finance_categories:
                db.session.add(category)
            
            db.session.commit()
            
            # Criar tarefas de exemplo
            sample_tasks = [
                Task(
                    title='Implementar autenticação',
                    description=(
                        'Criar sistema de login e registro de usuários'
                    ),
                    status='TO_DO',
                    priority='HIGH',
                    created_by='admin',
                    assigned_to='João',
                    tags='backend,segurança',
                    due_date=date(2024, 7, 15),
                    category_id=1
                ),
                Task(
                    title='Design da interface',
                    description='Criar mockups das telas principais',
                    status='IN_PROGRESS',
                    priority='MEDIUM',
                    created_by='admin',
                    assigned_to='Maria',
                    tags='frontend,design',
                    due_date=date(2024, 7, 20),
                    category_id=2
                ),
                Task(
                    title='Testes unitários',
                    description='Implementar testes para as APIs',
                    status='DONE',
                    priority='LOW',
                    created_by='admin',
                    assigned_to='Pedro',
                    tags='testes,qualidade',
                    due_date=date(2024, 7, 10),
                    category_id=3
                )
            ]
            
            for task in sample_tasks:
                db.session.add(task)
            
            # Criar movimentações financeiras de exemplo
            sample_finances = [
                Finance(
                    title='Salário',
                    description='Salário mensal',
                    value=5000.00,
                    transaction_date=date(2024, 6, 1),
                    recurrence='MONTHLY',
                    category_id=1
                ),
                Finance(
                    title='Aluguel',
                    description='Pagamento do aluguel',
                    value=-1200.00,
                    transaction_date=date(2024, 6, 5),
                    recurrence='MONTHLY',
                    category_id=2
                ),
                Finance(
                    title='Freelance',
                    description='Projeto de desenvolvimento web',
                    value=2500.00,
                    transaction_date=date(2024, 6, 10),
                    recurrence='NONE',
                    category_id=1
                ),
                Finance(
                    title='Supermercado',
                    description='Compras do mês',
                    value=-450.00,
                    transaction_date=date(2024, 6, 15),
                    recurrence='NONE',
                    category_id=2
                )
            ]
            
            for finance in sample_finances:
                db.session.add(finance)
            
            db.session.commit()
            
            print("✅ Dados de exemplo criados com sucesso!")
            print(f"📝 {len(sample_tasks)} tarefas criadas")
            print(
                f"💰 {len(sample_finances)} movimentações financeiras "
                "criadas"
            )
            
        except Exception as e:
            print(f"❌ Erro ao criar dados de exemplo: {e}")
            db.session.rollback()


def verify_database():
    """
    Verifica se o banco foi criado corretamente
    """
    with app.app_context():
        try:
            # Verificar usuários
            users = User.query.all()
            print(f"\n👥 Usuários no banco: {len(users)}")
            for user in users:
                print(f"   - {user.username}")
            
            # Verificar tarefas
            from app import Task
            tasks = Task.query.all()
            print(f"\n📝 Tarefas no banco: {len(tasks)}")
            for task in tasks:
                print(f"   - {task.title} ({task.status})")
            
            # Verificar finanças
            from app import Finance
            finances = Finance.query.all()
            print(f"\n💰 Movimentações no banco: {len(finances)}")
            for finance in finances:
                print(f"   - {finance.title}: R$ {finance.value}")
            
        except Exception as e:
            print(f"❌ Erro ao verificar banco: {e}")


if __name__ == '__main__':
    print("=== Inicialização do Banco de Dados ===")
    
    print("\n1. Inicializando banco de dados...")
    init_database()
    
    print("\n2. Criando usuário administrador...")
    create_admin_user()
    
    print("\n3. Criando dados de exemplo...")
    create_sample_data()
    
    print("\n4. Verificando banco de dados...")
    verify_database()
    
    print("\n=== Inicialização Concluída ===")
    print("\n🚀 Agora você pode:")
    print("   1. Executar: flask run")
    print("   2. Acessar: http://127.0.0.1:5000")
    print("   3. Fazer login com: admin / 123456")
