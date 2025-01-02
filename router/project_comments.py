from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from model.db import db
from model.Register import Register
from model.Project_comments import ProjectComments
from utils import role_required

project_comments_route = Blueprint("project_comments",__name__)

# Adding comments to specific project
@project_comments_route.route('/create_project_comments/<int:project_id>',methods=["POST"])
@jwt_required()
@role_required(['admin','manager'])
def add_project_comments(project_id):
    current_user_id = get_jwt_identity()
    data = request.get_json()
    comment_text = data.get('comments')

    if comment_text.strip()=="":
        return jsonify(message="Add Comment!!!"),400
    
    new_comment = ProjectComments(content=comment_text, project_id=project_id, created_by=current_user_id)
    db.session.add(new_comment)
    db.session.commit()
    return jsonify(message = 'Comment added successfully'), 201

@project_comments_route.route('/update/<int:comment_id>/project_comments', methods=["PUT"])
@jwt_required()
@role_required('admin')
def update_project_comment(comment_id):
    current_user_id = get_jwt_identity()
    data = request.get_json()
    new_comment_text = data.get('comments')
    
    if not new_comment_text or new_comment_text.strip() == "":
        return jsonify(message="Comment cannot be empty"), 400
    
    comment = ProjectComments.query.filter_by(project_comment_id=comment_id, created_by=current_user_id).first()
    
    if not comment:
        return jsonify(message="Comment not found"), 404
    
    comment.content = new_comment_text
    db.session.commit()
    
    return jsonify(message = 'Comment updated successfully'), 200

@project_comments_route.route('/get_project_comments/<int:project_id>', methods=["GET"])
@jwt_required()
def get_project_comments(project_id):
    comments = db.session.query(ProjectComments, Register).join(Register, ProjectComments.created_by == Register.user_id).filter(ProjectComments.project_id == project_id).all()
    
    if not comments:
        return jsonify(message="No comments found for this project"), 404
    
    comments_list = [{
        'project_comment_id': comment.ProjectComments.project_comment_id,
        'content': comment.ProjectComments.content,
        'created_by': comment.ProjectComments.created_by,
        'created_by_username': comment.Register.username
    } for comment in comments]
    
    return jsonify(comments_list), 200


@project_comments_route.route('/delete/<int:comment_id>/project_comments', methods=["DELETE"])
@jwt_required()
@role_required('admin')
def delete_project_comment(comment_id):
    current_user_id = get_jwt_identity()
    
    comment = ProjectComments.query.filter_by(project_comment_id=comment_id,delete_yn=False).first()
    
    if not comment:
        return jsonify(message="Comment not found"), 404
    
    comment.delete_yn = True
    db.session.commit()
    
    return jsonify(message = 'Comment deleted successfully'), 200
