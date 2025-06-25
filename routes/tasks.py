from flask import Blueprint, request, jsonify
from datetime import datetime
from models.task import Task, TaskHistory
from __init__ import db

tasks_bp = Blueprint('tasks', __name__)


@tasks_bp.route('/tasks', methods=['GET', 'OPTIONS'])
def get_tasks():
    """Lista todas as tarefas"""
    if request.method == 'OPTIONS':
        return '', 200
        
    tasks = Task.query.all()
    return jsonify([task.to_dict() for task in tasks])


@tasks_bp.route('/tasks/<task_type>', methods=['GET', 'OPTIONS'])
def get_tasks_by_type(task_type):
    """Lista tarefas por tipo (university/work)"""
    if request.method == 'OPTIONS':
        return '', 200
        
    tasks = Task.query.filter_by(type=task_type.upper()).all()
    return jsonify([task.to_dict() for task in tasks])


@tasks_bp.route('/tasks', methods=['POST', 'OPTIONS'])
def create_task():
    """Cria uma nova tarefa"""
    if request.method == 'OPTIONS':
        return '', 200
        
    data = request.get_json()
    
    # Validação básica
    if not data.get('title'):
        return jsonify({'message': 'Título é obrigatório'}), 400
    
    try:
        new_task = Task(
            title=data['title'],
            description=data.get('description', ''),
            status=data.get('status', 'TO_DO'),
            priority=data.get('priority', 'MEDIUM'),
            type=data.get('type', 'WORK'),
            due_date=(
                datetime.strptime(data['due_date'], '%Y-%m-%d').date()
                if data.get('due_date') else None
            ),
            created_by=data.get('created_by'),
            assigned_to=data.get('assigned_to'),
            tags=data.get('tags', ''),
            category_id=data.get('category_id')
        )
        
        db.session.add(new_task)
        db.session.commit()
        
        return jsonify({
            'id': new_task.id,
            'message': 'Tarefa criada com sucesso!',
            'task': new_task.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao criar tarefa: {str(e)}'}), 500
    

@tasks_bp.route('/tasks/<int:task_id>', methods=['PUT', 'OPTIONS'])
def update_task(task_id):
    """Atualiza uma tarefa existente"""
    if request.method == 'OPTIONS':
        return '', 200
        
    data = request.get_json()
    task = Task.query.get_or_404(task_id)
    old_status = task.status

    try:
        # Atualiza os campos
        task.title = data.get('title', task.title)
        task.description = data.get('description', task.description)
        task.status = data.get('status', task.status)
        task.priority = data.get('priority', task.priority)
        
        if data.get('due_date'):
            task.due_date = (
                datetime.strptime(data['due_date'], '%Y-%m-%d').date()
            )
        
        task.assigned_to = data.get('assigned_to', task.assigned_to)
        task.tags = data.get('tags', task.tags)
        task.updated_at = datetime.utcnow()

        db.session.commit()

        # Registra mudança de status no histórico
        if old_status != task.status:
            history = TaskHistory(
                task_id=task.id,
                old_status=old_status,
                new_status=task.status,
                observation='Status atualizado via API'
            )
            db.session.add(history)
            db.session.commit()

        return jsonify({
            'message': 'Tarefa atualizada com sucesso!',
            'task': task.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao atualizar tarefa: {str(e)}'}), 500
    

@tasks_bp.route('/tasks/<int:task_id>', methods=['DELETE', 'OPTIONS'])
def delete_task(task_id):
    """Deleta uma tarefa"""
    if request.method == 'OPTIONS':
        return '', 200
        
    task = Task.query.get_or_404(task_id)
    
    try:
        db.session.delete(task)
        db.session.commit()
        return jsonify({'message': 'Tarefa deletada com sucesso!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao deletar tarefa: {str(e)}'}), 500
    

@tasks_bp.route('/tasks/month/<int:month>', methods=['GET', 'OPTIONS'])
def get_tasks_by_month(month):
    """Lista tarefas por mês"""
    if request.method == 'OPTIONS':
        return '', 200
        
    tasks = Task.query.filter(
        db.extract('month', Task.due_date) == month
    ).all()
    
    return jsonify([
        {
            'id': task.id,
            'title': task.title,
            'due_date': task.due_date.isoformat() if task.due_date else None
        }
        for task in tasks
    ])


@tasks_bp.route('/tasks/<int:task_id>/history', methods=['GET', 'OPTIONS'])
def get_task_history(task_id):
    """Retorna o histórico de uma tarefa"""
    if request.method == 'OPTIONS':
        return '', 200
    
    Task.query.get_or_404(task_id)
    histories = (
        TaskHistory.query
        .filter_by(task_id=task_id)
        .order_by(TaskHistory.changed_at.desc())
        .all()
    )
    
    return jsonify([history.to_dict() for history in histories])
