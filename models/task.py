from __init__ import db
from datetime import datetime


class TaskCategory(db.Model):
    """Modelo para categorias de tarefas"""
    __tablename__ = 'task_category'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    def __repr__(self):
        return f'<TaskCategory {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }
    

class Task(db.Model):
    """Modelo para tarefas do sistema Kanban"""
    __tablename__ = 'task'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default='TO_DO')
    priority = db.Column(db.String(20), nullable=False, default='MEDIUM')
    type = db.Column(
        db.String(20), nullable=False, default='WORK'
    )  # UNIVERSITY ou WORK
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    due_date = db.Column(db.Date)
    created_by = db.Column(db.String(100))
    assigned_to = db.Column(db.String(100))
    tags = db.Column(db.String(255))
    category_id = db.Column(db.Integer, db.ForeignKey('task_category.id'))

    # Relacionamentos
    category = db.relationship(
        'TaskCategory',
        backref=db.backref('tasks', lazy=True)
    )
    
    def __repr__(self):
        return f'<Task {self.title}>'
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'type': self.type,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'created_by': self.created_by,
            'assigned_to': self.assigned_to,
            'tags': self.tags,
            'category_id': self.category_id
        }
    

class TaskHistory(db.Model):
    """Modelo para histórico de mudanças nas tarefas"""
    __tablename__ = 'task_history'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    old_status = db.Column(db.String(20))
    new_status = db.Column(db.String(20))
    observation = db.Column(db.Text)

    # Relacionamentos
    task = db.relationship('Task', backref=db.backref('histories', lazy=True))
    
    def __repr__(self):
        return (
            f'<TaskHistory {self.task_id}: '
            f'{self.old_status} -> {self.new_status}>'
        )
    
    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'changed_at': self.changed_at.isoformat(),
            'old_status': self.old_status,
            'new_status': self.new_status,
            'observation': self.observation
        }
