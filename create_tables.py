#!/usr/bin/env python3
"""
Script simples para criar apenas as tabelas do banco
"""

from app import app, db, User
from werkzeug.security import generate_password_hash

def create_basic_setup():
    """Cria apenas as tabelas básicas e usuário admin"""
    with app.app_context():
        try:
            print("🏗️  Criando tabelas...")
            db.create_all()
            
            # Verifica se já existe usuário admin
            existing_admin = User.query.filter_by(username='admin').first()
            if not existing_admin:
                print("👤 Criando usuário admin...")
                admin_user = User(
                    username='admin',
                    password=generate_password_hash('123456', method='pbkdf2:sha256')
                )
                
                db.session.add(admin_user)
                db.session.commit()
                
                print("✅ Usuário admin criado!")
            else:
                print("ℹ️  Usuário admin já existe")
            
            print("✅ Configuração básica concluída!")
            print("👤 Username: admin")
            print("🔑 Password: 123456")
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            db.session.rollback()

if __name__ == '__main__':
    print("=== Criação de Tabelas Básicas ===")
    create_basic_setup()
