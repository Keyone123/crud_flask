#!/usr/bin/env python3
"""
Script alternativo para executar a aplicação
"""

from app import app

if __name__ == '__main__':
    print("🚀 Iniciando aplicação via run_app.py...")
    
    # Inicializar banco dentro do contexto da aplicação
    with app.app_context():
        from app import db, User
        from werkzeug.security import generate_password_hash
        
        try:
            # Criar tabelas se não existirem
            db.create_all()
            print("✅ Tabelas verificadas/criadas")
            
            # Verificar usuário admin
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(
                    username='admin',
                    password=generate_password_hash('123456', method='pbkdf2:sha256')
                )
                db.session.add(admin)
                db.session.commit()
                print("✅ Usuário admin criado")
            else:
                print("ℹ️  Usuário admin já existe")
                
        except Exception as e:
            print(f"⚠️  Aviso: {e}")
    
    print("📍 Servidor rodando em: http://127.0.0.1:5000")
    print("👤 Login: admin")
    print("🔑 Senha: 123456")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
