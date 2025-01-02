from flask import Blueprint, request, jsonify, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from config import UPLOAD_FOLDER
from werkzeug.utils import secure_filename
from model.db import db
from model.Register import Register
from model.Task import Task
import os
from utils import role_required

profile_route = Blueprint("profile",__name__)


# For Profile.js
@profile_route.route('/user/data', methods=['GET'])
@jwt_required()
def get_user_data():
    current_user_id = get_jwt_identity()
    user = Register.query.filter_by(user_id=current_user_id).first()
    if user:
        return jsonify({
            'username': user.username,
            'profile_img': user.profile_img,
            'role': user.role
        }), 200
    return jsonify({'message': 'User not found'}), 404

@profile_route.route('/get_profile', methods=['GET'])
@jwt_required()
def get_profile():
    current_user_id = get_jwt_identity()
    user = Register.query.filter_by(user_id=current_user_id).first()
    
    if user:
        created_tasks = Task.query.filter_by(created_by=current_user_id).count()
        assigned_tasks = Task.query.filter_by(assigned_to=current_user_id).count()
        completed_tasks = Task.query.filter_by(assigned_to=current_user_id, status='Completed').count()

        profile_img_url = url_for('static', filename=user.profile_img)  

        return jsonify({
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'profile_img': profile_img_url,
            'total_tasks_created': created_tasks,
            'total_tasks_assigned': assigned_tasks,
            'completed_tasks': completed_tasks
        }), 200
    
    return jsonify({'message': 'User not found'}), 404

@profile_route.route('/update_profile_picture', methods=['POST'])
@jwt_required()
def update_profile_picture():
    current_user_id = get_jwt_identity()
    user = Register.query.filter_by(user_id=current_user_id).first()

    if 'profile_img' not in request.files:
        return jsonify({'message': 'No file part'}), 400

    file = request.files['profile_img']

    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    if file:
        if user.profile_img:
            old_image_path = os.path.join(UPLOAD_FOLDER, user.profile_img.split('/')[-1])
            if os.path.exists(old_image_path):
                os.remove(old_image_path)

        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        user.profile_img = f'uploads/{filename}'
        db.session.commit()

        return jsonify({'profile_img': f'static/uploads/{filename}'}), 200
    return jsonify({'message': 'File type not allowed'}), 400


@profile_route.route('/users', methods=['GET'])
@jwt_required()
@role_required('admin')
def users():
    users = Register.query.filter_by(delete_yn=False).with_entities(Register.user_id, Register.username, Register.role, Register.email).all()

    if not users:
        return jsonify(message="No Users Found!!"), 404
    
    user_list = [{
        'user_id': user.user_id,
        'username': user.username,
        'role': user.role,
        'email': user.email
    } for user in users]
    
    return jsonify(user_list), 200


@profile_route.route('/managers',methods=['GET'])
def managers():
    managers = Register.query.filter_by(role='manager').all()
    if not managers:
        return jsonify(message="No managers found!!!"), 404
    manager_list = [{'user_id':manager.user_id,'username': manager.username}for manager in managers]
    return jsonify(manager_list),200

@profile_route.route('/get_users_under_manager', methods=['GET'])
@jwt_required()
def get_users_under_manager():
    manager_id = get_jwt_identity()
    users = Register.query.filter_by(manager_id=manager_id).all()
    if not users:
        return jsonify(message="No users under this manager"), 404
    users_list = [{'username': user.username,'user_id':user.user_id, 'email':user.email }for user in users]
    return jsonify(users_list),200

@profile_route.route('/get_users_and_managers', methods=['GET'])
@jwt_required()
def get_users_and_managers():
    print("inside!!")
    current_user_id = get_jwt_identity()
    
    current_user = Register.query.filter_by(user_id=current_user_id).first()
    
    if not current_user:
        return jsonify({"error": "User not found."}), 404

    if current_user.role == 'manager':
        users = Register.query.filter(
            Register.delete_yn == False,
            Register.role == 'user',
            Register.manager_id == current_user_id
        ).all()
        managers = [current_user]

    elif current_user.role == 'admin':
        users = Register.query.filter(Register.delete_yn == False, Register.role == 'user').all()
        managers = Register.query.filter(Register.delete_yn == False, Register.role == 'manager').all()
    else:
        return jsonify({"error": "Unauthorized access!!"}), 403
    print("MIDelle!!")
    # Serialize the results
    users_data = [{"id": user.user_id, "username": user.username, "email":user.email} for user in users]
    managers_data = [{"id": manager.user_id, "username": manager.username,"email":manager.email} for manager in managers]

    return jsonify({"users": users_data, "managers": managers_data}), 200

@profile_route.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    current_user_id = get_jwt_identity()
    
    users = Register.query.filter(Register.role != 'admin').all()
    if not users:
        return jsonify(message = "You are an admin"),404
    users_list = [
        {
            'username': user.username,
            'role': user.role,
            'email': user.email
        } for user in users
    ]
    
    return jsonify(users_list), 200



