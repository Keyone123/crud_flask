from flask import Blueprint, request, jsonify
from datetime import datetime
from models.finance import Finance
from utils.finance_utils import create_future_installments
from __init__ import db

finances_bp = Blueprint('finances', __name__)


@finances_bp.route('/finances', methods=['GET', 'OPTIONS'])
def get_finances():
    """Lista todas as movimentações financeiras"""
    if request.method == 'OPTIONS':
        return '', 200
        
    finances = Finance.query.all()
    return jsonify([finance.to_dict() for finance in finances])


@finances_bp.route('/finances', methods=['POST', 'OPTIONS'])
def create_finance():
    """Cria uma nova movimentação financeira"""
    if request.method == 'OPTIONS':
        return '', 200
        
    data = request.get_json()
    
    # Validação básica
    if (
        not data.get('title')
        or not data.get('value')
        or not data.get('transaction_date')
    ):
        return jsonify({
            'message': 'Título, valor e data são obrigatórios'
        }), 400
    
    try:
        new_finance = Finance(
            title=data['title'],
            description=data.get('description', ''),
            value=float(data['value']),
            transaction_date=(
                datetime.strptime(
                    data['transaction_date'], '%Y-%m-%d'
                ).date()
            ),
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
        return jsonify({
            'message': (
                f'Erro ao criar movimentação: {str(e)}'
            )
        }), 500
    

@finances_bp.route('/finances/<int:finance_id>', methods=['PUT', 'OPTIONS'])
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
            finance.transaction_date = (
                datetime.strptime(
                    data['transaction_date'], '%Y-%m-%d'
                ).date()
            )
        
        finance.recurrence = data.get('recurrence', finance.recurrence)
        finance.installments_total = data.get(
            'installments_total', finance.installments_total
        )
        finance.installment_current = data.get(
            'installment_current', finance.installment_current
        )
        finance.category_id = data.get('category_id', finance.category_id)

        db.session.commit()
        
        return jsonify({
            'message': 'Movimentação atualizada com sucesso!',
            'finance': finance.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'message': (
                f'Erro ao atualizar movimentação: {str(e)}'
            )
        }), 500
    

@finances_bp.route('/finances/<int:finance_id>', methods=['DELETE', 'OPTIONS'])
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
        return jsonify({
            'message': (
                f'Erro ao deletar movimentação: {str(e)}'
            )
        }), 500
    

@finances_bp.route('/finances/month/<int:month>', methods=['GET', 'OPTIONS'])
def get_finances_by_month(month):
    """Lista movimentações por mês"""
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


@finances_bp.route(
    '/finances/upcoming-installments',
    methods=['GET', 'OPTIONS']
)
def get_upcoming_installments():
    """Lista próximas parcelas"""
    if request.method == 'OPTIONS':
        return '', 200
    
    from datetime import date
    today = date.today()
    
    upcoming = Finance.query.filter(
        Finance.transaction_date >= today,
        Finance.recurrence == 'INSTALLMENT'
    ).order_by(Finance.transaction_date).limit(10).all()
    
    return jsonify([finance.to_dict() for finance in upcoming])
