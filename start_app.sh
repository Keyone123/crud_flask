#!/bin/bash

echo "🚀 Iniciando Sistema Kanban & Finanças..."

# Verificar se o ambiente virtual está ativo
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Ambiente virtual ativo: $VIRTUAL_ENV"
else
    echo "⚠️  Ativando ambiente virtual..."
    source venv/bin/activate
fi

# Verificar dependências
echo "📦 Verificando dependências..."
pip install flask flask-sqlalchemy flask-cors werkzeug > /dev/null 2>&1

# Executar diagnóstico
echo "🔍 Executando diagnóstico..."
python check_database_status.py

echo ""
echo "🚀 Iniciando aplicação..."
python run_app.py
