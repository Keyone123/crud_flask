from flask import Blueprint, render_template, send_file

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Página principal - Dashboard"""
    return render_template('index.html')


@main_bp.route('/kanban')
def kanban():
    """Página do Kanban (legado - redireciona para trabalho)"""
    return render_template('kanban.html')


@main_bp.route('/finance')
def finance():
    """Página de gestão financeira"""
    return render_template('finance.html')


@main_bp.route('/kanban-university')
def kanban_university():
    """Página do Kanban para atividades universitárias"""
    return render_template('kanban-university.html')


@main_bp.route('/kanban-work')
def kanban_work():
    """Página do Kanban para atividades de trabalho"""
    return render_template('kanban-work.html')

# Rotas para arquivos estáticos


@main_bp.route('/static/css/<filename>')
def css_files(filename):
    """Serve arquivos CSS"""
    return send_file(f'static/css/{filename}')


@main_bp.route('/static/js/<filename>')
def js_files(filename):
    """Serve arquivos JavaScript"""
    return send_file(f'static/js/{filename}')
