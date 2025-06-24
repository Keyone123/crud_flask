import sqlite3
from werkzeug.security import generate_password_hash


def create_user_directly():
    """
    Cria usuário diretamente no banco SQLite
    """
    try:
        # Conecta ao banco
        conn = sqlite3.connect('banco.db')
        cursor = conn.cursor()
        
        # Verifica se a tabela user existe
        cursor.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name='user';"
        )
        if not cursor.fetchone():
            print(
                "Tabela 'user' não existe. "
                "Execute o Flask primeiro para criar as tabelas."
            )
            return
        
        # Remove usuário admin se existir
        cursor.execute("DELETE FROM user WHERE username = 'admin'")
        
        # Cria hash da senha
        password_hash = generate_password_hash(
            '123456', method='pbkdf2:sha256'
        )
        
        # Insere novo usuário
        cursor.execute(
            "INSERT INTO user (username, password) VALUES (?, ?)",
            ('admin', password_hash)
        )
        
        # Confirma as alterações
        conn.commit()
        
        print("✅ Usuário criado com sucesso!")
        print("Username: admin")
        print("Password: 123456")
        
        # Verifica se foi criado
        cursor.execute("SELECT * FROM user WHERE username = 'admin'")
        user = cursor.fetchone()
        if user:
            print(f"✅ Verificação: Usuário {user[1]} encontrado no banco")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
    finally:
        conn.close()


def list_all_users():
    """
    Lista todos os usuários do banco
    """
    try:
        conn = sqlite3.connect('banco.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM user")
        users = cursor.fetchall()
        
        print(f"\n📋 Total de usuários no banco: {len(users)}")
        for user in users:
            print(
                f"ID: {user[0]}, Username: {user[1]}, "
                f"Password: {user[2][:50]}..."
            )
            
    except Exception as e:
        print(f"❌ Erro ao listar usuários: {e}")
    finally:
        conn.close()


if __name__ == '__main__':
    print("=== Criação de Usuário Direta ===")
    
    print("\n1. Listando usuários existentes...")
    list_all_users()
    
    print("\n2. Criando usuário admin...")
    create_user_directly()
    
    print("\n3. Verificando usuários após criação...")
    list_all_users()
