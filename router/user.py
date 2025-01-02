from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required,get_jwt_identity
from werkzeug.utils import secure_filename
from model.db import db
from model.Register import Register
from config import UPLOAD_FOLDER
import os
from utils import role_required


user_route = Blueprint("user",__name__)


# CRUD for user
@user_route.route('/users_list',methods=['GET'])
def users_list():
    users = Register.query.filter_by(role='user').all()
    if not users:
        return jsonify(message = "No Users Found!!!"), 404
    user_list = [{'user_id':user.user_id,'username':user.username}for user in users]
    return jsonify(user_list),200

@user_route.route('/update_user_img/<int:user_id>',methods=['POST'])
@jwt_required()
def update_user_img(user_id):
    user = Register.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify(message="The given user not available!!"), 404
    profile_img = request.files['profile_image']
    if profile_img:
        filename = secure_filename(profile_img.filename)
        processed_filename = os.path.splitext(filename)[0]
        save_path = os.path.join(UPLOAD_FOLDER, processed_filename)
        profile_img.save(save_path)
        image_path = os.path.join('static', 'uploads', processed_filename)
        user.profile_img = image_path
        
        db.session.commit()
    return jsonify(message="updated the user!!"),200

@user_route.route('/update_user/<int:user_id>', methods=['PATCH'])
@jwt_required()
@role_required('admin')
def update_user(user_id):
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    username = data.get('username')
    email = data.get('email')
    role = data.get('role')
    
    user = Register.query.filter_by(user_id=user_id).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if username:
        user.username = username
    if email:
        user.email = email
    if role:
        user.role = role
    
    db.session.commit()
    
    return jsonify({'user': {'username': user.username, 'email': user.email, 'role': user.role}}), 200


@user_route.route('/delete_user/<int:user_id>', methods=['DELETE'])
@jwt_required()
@role_required(['admin'])
def delete_user(user_id):
    current_user_id = get_jwt_identity()
    user_delete = Register.query.filter_by(user_id=user_id, delete_yn=False).first()

    if current_user_id == user_delete :
        return jsonify(message="You cannot delete youeself!!")
    
    if not user_delete:
        return jsonify(message="User not found or already deleted!"), 404
    
    user_delete.delete_yn = True

    try:
        db.session.commit()
        return jsonify(message="User is deleted!!!"), 200
    except Exception as e:
        db.session.rollback()
        return jsonify(message="An error occurred: " + str(e)), 500

