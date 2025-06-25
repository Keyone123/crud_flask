from models.finance import Finance
from __init__ import db


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
                title=(
                    (
                        f"{finance.title} - Parcela {i}/"
                        f"{finance.installments_total}"
                    )
                ),
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
            # Se a data for inválida (ex: 31 de fevereiro),
            # ajusta para o último dia do mês
            import calendar
            last_day = calendar.monthrange(year, month)[1]
            day = min(future_date.day, last_day)
            
            future_finance = Finance(
                title=(
                    (
                        f"{finance.title} - Parcela {i}/"
                        f"{finance.installments_total}"
                    )
                ),
                description=finance.description,
                value=finance.value,
                transaction_date=future_date.replace(
                    year=year, month=month, day=day
                ),
                recurrence='INSTALLMENT',
                installments_total=finance.installments_total,
                installment_current=i,
                parent_finance_id=finance.id,
                category_id=finance.category_id
            )
            db.session.add(future_finance)


def calculate_monthly_summary(month, year):
    """Calcula resumo financeiro de um mês específico"""
    
    finances = Finance.query.filter(
        db.extract('month', Finance.transaction_date) == month,
        db.extract('year', Finance.transaction_date) == year
    ).all()
    
    income = sum(f.value for f in finances if f.value > 0)
    expense = sum(abs(f.value) for f in finances if f.value < 0)
    balance = income - expense
    
    return {
        'income': income,
        'expense': expense,
        'balance': balance,
        'transactions_count': len(finances)
    }
