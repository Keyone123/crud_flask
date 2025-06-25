#!/usr/bin/env python3
"""
Script para verificar o status atual do banco de dados
"""

import os
import sqlite3
from app import app, db, User, Task, Finance

def check_database_files():
    """Verifica quais arquivos de banco existem"""
    print("🔍 Verificando arquivos de banco...")
    
    possible_db_files = [
        'banco.db',
        'instance/banco.db',
        'app.db',
        'database.db'
    ]
    
    for db_file in possible_db_files:
        if os.path.exists(db_file):
            size = os.path.getsize(db_file)
            print(f"✅ Encontrado: {db_file} ({size} bytes)")
            
            # Verificar tabelas no arquivo
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                print(f"   📋 Tabelas: {[table[0] for table in tables]}")
                
                # Verificar usuários se a tabela existir
                if any('user' in table[0] for table in tables):
                    cursor.execute("SELECT username FROM user;")
                    users = cursor.fetchall()
                    print(f"   👥 Usuários: {[user[0] for user in users]}")
                
                conn.close()
            except Exception as e:
                print(f"   ❌ Erro ao ler {db_file}: {e}")
        else:
            print(f"❌ Não encontrado: {db_file}")

def check_flask_context():
    """Verifica o contexto do Flask"""
    print("\n🔍 Verificando contexto do Flask...")
    
    with app.app_context():
        try:
            # Verificar configuração do banco
            print(f"📍 Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
            
            # Tentar conectar
            users = User.query.all()
            print(f"✅ Conexão OK - {len(users)} usuários encontrados")
            
            for user in users:
                print(f"   👤 {user.username}")
                
            # Verificar tarefas
            tasks = Task.query.all()
            print(f"📝 {len(tasks)} tarefas encontradas")
            
            # Verificar finanças
            finances = Finance.query.all()
            print(f"💰 {len(finances)} movimentações encontradas")
            
        except Exception as e:
            print(f"❌ Erro no contexto Flask: {e}")

def fix_database_location():
    """Tenta corrigir a localização do banco"""
    print("\n🔧 Tentando corrigir localização do banco...")
    
    with app.app_context():
        try:
            # Forçar criação das tabelas
            db.create_all()
            print("✅ Tabelas criadas/verificadas")
            
            # Verificar se existe usuário admin
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                print("👤 Criando usuário admin...")
                from werkzeug.security import generate_password_hash
                
                admin = User(
                    username='admin',
                    password=generate_password_hash('123456', method='pbkdf2:sha256')
                )
                db.session.add(admin)
                db.session.commit()
                print("✅ Usuário admin criado!")
            else:
                print("ℹ️  Usuário admin já existe")
                
        except Exception as e:
            print(f"❌ Erro ao corrigir: {e}")

if __name__ == '__main__':
    print("=== Diagnóstico do Banco de Dados ===")
    
    check_database_files()
    check_flask_context()
    fix_database_location()
    
    print("\n=== Verificação Final ===")
    check_flask_context()
