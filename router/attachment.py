from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from model.Attachments import Attachment
from model.db import db
from model.Task import Task
import os
import hashlib
import bleach

tags = {"div"}

attachment_route = Blueprint("attachment",__name__)

@attachment_route.route('/get_attached_files/<int:task_id>', methods=['GET'])
@jwt_required()
def get_attachments(task_id):
    current_user_id = get_jwt_identity()

    task = Task.query.filter_by(task_id=task_id).first()
    if not task:
        return jsonify({"message": "Task not found"}), 404

    attachments = Attachment.query.filter_by(task_id=task_id, delete_yn=False).all()
    attachment_list = [attachment.to_dict() for attachment in attachments]

    return jsonify(attachment_list), 200

@attachment_route.route('/post_attachment/<int:task_id>', methods=['POST'])
@jwt_required()
def post_attachment(task_id):
    current_user_id = get_jwt_identity()

    if 'status' not in request.form or 'attachments' not in request.files:
        return jsonify({"message": "Status and attachments are required"}), 400
    
    def sanitize(input_value):
        return bleach.clean(input_value.strip(),tags=tags, strip=True) if input_value else None
    
    status = sanitize(request.form['status'])
    files = sanitize(request.files.getlist('attachments'))

    status = request.form['status']
    files = request.files.getlist('attachments')
    print(files)

    task = Task.query.filter_by(task_id=task_id).first()
    if not task:
        return jsonify({"message": "Task not found"}), 404

    upload_directory = os.path.join('static', 'uploads', 'files')
    os.makedirs(upload_directory, exist_ok=True)

    for file in files:
        print(f"{file},Inside loop")
        file_path = os.path.join(upload_directory, file.filename)
        file.save(file_path)

        with open(file_path, 'rb') as f:
            file_content = f.read()
        sha256_hash = hashlib.sha256(file_content).hexdigest()

        task.attachment = file_path.replace('\\', '/')
        print(task.attachment)

        new_attachment = Attachment(
            task_id=task_id,
            status=status,
            attachment=task.attachment,
            file_name=file.filename,
            img_hash=sha256_hash,
            created_by=current_user_id
        )
        db.session.add(new_attachment)

    db.session.commit()

    return jsonify({"message": "Files attached and status updated successfully"}), 201


@attachment_route.route('/sha256_search', methods=['POST'])
@jwt_required()
def sha256_search():
    current_user_id = get_jwt_identity()
    query = request.args.get('hash')

    if not query:
        return jsonify(message="Query is not given"), 400

    base = db.session.query(Attachment).join(Task, Attachment.task_id == Task.task_id).filter(
        Attachment.img_hash.ilike(f"%{query}%"),
        Attachment.delete_yn == False,
        (Attachment.created_by == current_user_id) | (Task.assigned_to == current_user_id)
    ).all()
    
    attachment_list = [attachment.to_dict() for attachment in base]

    return jsonify(attachment_list), 200

 
@attachment_route.route('/search', methods=['GET'])
@jwt_required()
def search():
    current_user_id = get_jwt_identity()
    query = request.args.get('title')
    
    if not query:
        return jsonify(message= "Filename query parameter is required"), 400

    attachments = db.session.query(Attachment).join(Task, Attachment.task_id == Task.task_id).filter(
        Attachment.attachment.ilike(f"%{query}%"),
        Attachment.delete_yn == False,
        (Attachment.created_by == current_user_id) | (Task.assigned_to == current_user_id)
    ).all()

    if not attachments:
        return jsonify({"message": "No attachments found matching the query"}), 404

    attachment_list = [attachment.to_dict() for attachment in attachments]
    print(attachment_list)

    return jsonify(attachment_list), 200


@attachment_route.route('/delete_attach/<int:attachment_id>',methods=['DELETE'])
def delete_attachment(attachment_id):
    attachment = Attachment.query.filter_by(attachment_id=attachment_id).first()
    if attachment:
        db.session.delete(attachment)
        db.session.commit()
        return 'deleted'
    else:
        return 'attachment not found', 404