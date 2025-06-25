from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from models.attachment import Attachment
from __init__ import db
import os

uploads_bp = Blueprint('uploads', __name__)

ALLOWED_EXTENSIONS = {
    'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif',
    'doc', 'docx', 'xls', 'xlsx'
}


def allowed_file(filename):
    """Verifica se o arquivo tem uma extensão permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@uploads_bp.route('/upload', methods=['POST', 'OPTIONS'])
def upload_file():
    """Faz upload de um arquivo"""
    if request.method == 'OPTIONS':
        return '', 200
        
    if 'file' not in request.files:
        return jsonify({'message': 'Nenhum arquivo encontrado'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'Arquivo inválido'}), 400

    if not allowed_file(file.filename):
        return jsonify({'message': 'Tipo de arquivo não permitido'}), 400

    try:
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        new_attachment = Attachment(
            file_path=file_path,
            description=request.form.get('description', ''),
            task_id=(
                request.form.get('task_id')
                if request.form.get('task_id') else None
            ),
            finance_id=(
                request.form.get('finance_id')
                if request.form.get('finance_id') else None
            )
        )
        
        db.session.add(new_attachment)
        db.session.commit()

        return jsonify({
            'message': 'Arquivo enviado com sucesso!',
            'attachment': new_attachment.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao fazer upload: {str(e)}'}), 500
    

@uploads_bp.route(
    '/attachments/<int:attachment_id>',
    methods=['DELETE', 'OPTIONS']
)
def delete_attachment(attachment_id):
    """Deleta um anexo"""
    if request.method == 'OPTIONS':
        return '', 200
    
    attachment = Attachment.query.get_or_404(attachment_id)
    
    try:
        # Remove o arquivo do sistema de arquivos
        if os.path.exists(attachment.file_path):
            os.remove(attachment.file_path)
        
        db.session.delete(attachment)
        db.session.commit()
        
        return jsonify({'message': 'Anexo deletado com sucesso!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao deletar anexo: {str(e)}'}), 500
