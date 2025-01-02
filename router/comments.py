from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from model.db import db
from model.Register import Register
from model.Comments import Comments
from model.Task import Task


comment_route = Blueprint("comments",__name__)


@comment_route.route('/post_tasks_comments/<int:task_id>', methods=['POST'])
@jwt_required()
def add_comment(task_id):
    current_user_id = get_jwt_identity()
    data = request.get_json()
    comment_text = data.get('comment')

    if comment_text is None or comment_text.strip() == "":
        return jsonify(message= "Add Comment!!!"), 400

    task = Task.query.filter_by(task_id=task_id).first()
    if not task:
        return jsonify(message = "Task not found"), 404

    if task.created_by != current_user_id and task.assigned_to != current_user_id:
        return jsonify(message = "You do not have permission to comment on this task"), 403

    new_comment = Comments(content=comment_text, task_id=task_id, created_by=current_user_id)
    db.session.add(new_comment)
    db.session.commit()

    return jsonify({"message": "Comment added successfully"}), 201


# Route to get comments for a task
@comment_route.route('/tasks/<int:task_id>/comment', methods=['GET'])
@jwt_required()
def get_comments(task_id):
    current_user_id = get_jwt_identity()
    comments = db.session.query(Comments, Register).join(Register, Comments.created_by == Register.user_id).filter(Comments.task_id == task_id).all()

    if not comments:
        return jsonify(message = "No Comments found!!"),400
    
    task = Task.query.filter_by(task_id=task_id).first()
    if not task:
        return jsonify(message = "Task not found"), 404

    if task.created_by != current_user_id and task.assigned_to != current_user_id:
        return jsonify(message = "You do not have permission to comment on this task"), 403
    
    return jsonify([{
        'comment_id': comment.Comments.comment_id,
        'content': comment.Comments.content,
        'created_by': comment.Comments.created_by,
        'created_by_username': comment.Register.username
    } for comment in comments]), 200

# Editing the comments
@comment_route.route('/edit_comments/<int:comment_id>',methods=['PATCH'])
@jwt_required()
def edit_comments(comment_id):
    current_user_id = get_jwt_identity()
    comment = Comments.query.filter_by(comment_id=comment_id).first()

    if comment.created_by != current_user_id:
        return jsonify(message="This is not created by you"), 403

    if comment:
        req_data = request.json
        print(req_data)
        if 'content' in req_data:
            comment.content = req_data['content']
        db.session.commit()
        return jsonify(message='updated!!'), 200

@comment_route.route('/delete_comment/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    comment = Comments.query.filter_by(comment_id=comment_id).first()
    if comment:
        db.session.delete(comment)
        db.session.commit()
        return 'deleted'
    else:
        return 'comment not found', 404