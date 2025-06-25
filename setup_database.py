#!/usr/bin/env python3
"""
Script para configurar o banco de dados com dados iniciais
"""

from app import app, db, User, Task, TaskCategory, Finance, FinanceCategory
from werkzeug.security import generate_password_hash
from datetime import date


def setup_complete_database():
    """
    Configura o banco de dados completo com dados de exemplo
    """
    with app.app_context():
        try:
            print("🗑️  Removendo banco existente...")
            db.drop_all()
            
            print("🏗️  Criando tabelas...")
            db.create_all()
            
            print("👤 Criando usuário administrador...")
            create_admin_user()
            
            print("📂 Criando categorias...")
            create_categories()
            
            print("📝 Criando tarefas de exemplo...")
            create_sample_tasks()
            
            print("💰 Criando movimentações financeiras...")
            create_sample_finances()
            
            print("✅ Banco de dados configurado com sucesso!")
            verify_setup()
            
        except Exception as e:
            print(f"❌ Erro na configuração: {e}")
            db.session.rollback()


def create_admin_user():
    """Cria usuário administrador"""
    admin_user = User(
        username='admin',
        password=generate_password_hash('123456', method='pbkdf2:sha256')
    )
    
    db.session.add(admin_user)
    db.session.commit()


def create_categories():
    """Cria categorias de exemplo"""
    # Categorias de tarefas
    task_categories = [
        TaskCategory(name='Desenvolvimento', description='Tarefas de desenvolvimento'),
        TaskCategory(name='Design', description='Tarefas de design'),
        TaskCategory(name='Teste', description='Tarefas de teste'),
        TaskCategory(name='Estudos', description='Atividades acadêmicas'),
        TaskCategory(name='Projetos', description='Projetos pessoais')
    ]
    
    # Categorias financeiras
    finance_categories = [
        FinanceCategory(name='Receita', type='INCOME'),
        FinanceCategory(name='Despesa', type='EXPENSE'),
        FinanceCategory(name='Investimento', type='INVESTMENT')
    ]
    
    for category in task_categories + finance_categories:
        db.session.add(category)
    
    db.session.commit()


def create_sample_tasks():
    """Cria tarefas de exemplo"""
    # Tarefas da Universidade
    university_tasks = [
        Task(
            title='Estudar para Prova de Cálculo',
            description='Revisar derivadas e integrais para a prova',
            status='TO_DO',
            priority='HIGH',
            type='UNIVERSITY',
            created_by='admin',
            assigned_to='Cálculo I - Prof. Maria',
            tags='prova,matemática,urgente',
            due_date=date(2024, 7, 15),
            category_id=4
        ),
        Task(
            title='Trabalho de História',
            description='Pesquisa sobre Segunda Guerra Mundial',
            status='IN_PROGRESS',
            priority='MEDIUM',
            type='UNIVERSITY',
            created_by='admin',
            assigned_to='História - Prof. João',
            tags='trabalho,pesquisa',
            due_date=date(2024, 7, 20),
            category_id=4
        ),
        Task(
            title='Seminário de Física',
            description='Apresentação sobre mecânica quântica',
            status='DONE',
            priority='LOW',
            type='UNIVERSITY',
            created_by='admin',
            assigned_to='Física II - Prof. Ana',
            tags='seminário,apresentação',
            due_date=date(2024, 7, 10),
            category_id=4
        )
    ]
    
    # Tarefas do Trabalho
    work_tasks = [
        Task(
            title='Desenvolver API de Usuários',
            description='Criar endpoints para CRUD de usuários',
            status='TO_DO',
            priority='HIGH',
            type='WORK',
            created_by='admin',
            assigned_to='Cliente ABC - Projeto Sistema',
            tags='backend,api,urgente',
            due_date=date(2024, 7, 15),
            category_id=1
        ),
        Task(
            title='Corrigir Bug no Frontend',
            description='Resolver problema de responsividade',
            status='IN_PROGRESS',
            priority='MEDIUM',
            type='WORK',
            created_by='admin',
            assigned_to='Equipe Frontend',
            tags='frontend,bug,css',
            due_date=date(2024, 7, 18),
            category_id=1
        ),
        Task(
            title='Deploy em Produção',
            description='Fazer deploy da versão 2.0',
            status='DONE',
            priority='HIGH',
            type='WORK',
            created_by='admin',
            assigned_to='DevOps Team',
            tags='deploy,produção',
            due_date=date(2024, 7, 12),
            category_id=1
        )
    ]
    
    for task in university_tasks + work_tasks:
        db.session.add(task)
    
    db.session.commit()


def create_sample_finances():
    """Cria movimentações financeiras de exemplo"""
    finances = [
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
        ),
        Finance(
            title='Curso Online',
            description='Curso de Python - 12x',
            value=-99.90,
            transaction_date=date(2024, 6, 20),
            recurrence='INSTALLMENT',
            installments_total=12,
            installment_current=1,
            category_id=2
        )
    ]
    
    for finance in finances:
        db.session.add(finance)
    
    db.session.commit()


def verify_setup():
    """Verifica se a configuração foi bem-sucedida"""
    users = User.query.count()
    university_tasks = Task.query.filter_by(type='UNIVERSITY').count()
    work_tasks = Task.query.filter_by(type='WORK').count()
    finances = Finance.query.count()
    task_categories = TaskCategory.query.count()
    finance_categories = FinanceCategory.query.count()
    
    print(f"\n📊 Resumo da configuração:")
    print(f"   👥 Usuários: {users}")
    print(f"   📝 Tarefas Universidade: {university_tasks}")
    print(f"   💼 Tarefas Trabalho: {work_tasks}")
    print(f"   💰 Movimentações Financeiras: {finances}")
    print(f"   📂 Categorias de Tarefas: {task_categories}")
    print(f"   💼 Categorias Financeiras: {finance_categories}")


if __name__ == '__main__':
    print("=== Configuração do Banco de Dados ===")
    setup_complete_database()
    print("\n🚀 Agora você pode:")
    print("   1. Executar: python app.py")
    print("   2. Ou executar: flask run")
    print("   3. Acessar: http://127.0.0.1:5000")
    print("   4. Fazer login com: admin / 123456")
