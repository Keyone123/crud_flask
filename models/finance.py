from __init__ import db
from datetime import datetime


class FinanceCategory(db.Model):
    """Modelo para categorias financeiras"""
    __tablename__ = 'finance_category'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(
        db.String(20), nullable=False
    )  # INCOME, EXPENSE, INVESTMENT
    
    def __repr__(self):
        return f'<FinanceCategory {self.name}>'
    
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
    installments_total = db.Column(db.Integer, default=1)  # Total de parcelas
    installment_current = db.Column(db.Integer, default=1)  # Parcela atual
    parent_finance_id = db.Column(
        db.Integer,
        db.ForeignKey('finance.id')
    )  # Para parcelas futuras
    category_id = db.Column(db.Integer, db.ForeignKey('finance_category.id'))

    # Relacionamentos
    category = db.relationship(
        'FinanceCategory',
        backref=db.backref('finances', lazy=True)
    )
    parent_finance = db.relationship('Finance', remote_side=[id])
    
    def __repr__(self):
        return f'<Finance {self.title}: {self.value}>'
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
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
