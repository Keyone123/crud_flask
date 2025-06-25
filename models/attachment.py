from __init__ import db
from datetime import datetime


class Attachment(db.Model):
    """Modelo para anexos de tarefas e finanças"""
    __tablename__ = 'attachment'
    
    id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    finance_id = db.Column(db.Integer, db.ForeignKey('finance.id'))

    # Relacionamentos
    task = db.relationship(
        'Task',
        backref=db.backref('attachments', lazy=True)
    )
    finance = db.relationship(
        'Finance',
        backref=db.backref('attachments', lazy=True)
    )
    
    def __repr__(self):
        return f'<Attachment {self.file_path}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'file_path': self.file_path,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'task_id': self.task_id,
            'finance_id': self.finance_id
        }
