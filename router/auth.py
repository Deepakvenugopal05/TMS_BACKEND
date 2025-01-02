from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity,create_access_token
from werkzeug.utils import secure_filename
from datetime import timedelta
from extensions import bcrypt
from model.db import db
from model.Register import Register
from config import UPLOAD_FOLDER
from utils import role_required
import os
import bleach

auth_route = Blueprint("auth",__name__)

tags = {"div"}

@auth_route.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        required_fields = ["username", "email", "password", "role"]
        if not all(field in request.form for field in required_fields):
            return jsonify(message="Missing fields required"), 400

        def sanitize(input_value):
            return bleach.clean(input_value.strip(),tags=tags, strip=True) if input_value else None

        # Sanitize inputs
        username = sanitize(request.form.get('username'))
        email = sanitize(request.form.get('email'))
        password = request.form.get('password')
        role = sanitize(request.form.get('role'))
        manager_id = sanitize(request.form.get('manager_id'))

        profile_img = request.files.get('profile_image')
        if profile_img:
            filename = secure_filename(bleach.clean(profile_img.filename, strip=True))
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            profile_img.save(save_path)
            image_path = os.path.join('uploads', filename)
        else:
            image_path = None

        # Handle role and manager_id
        if role == 'user':
            if not manager_id:
                return jsonify(message="Manager ID not provided for user!"), 400

            manager = Register.query.filter_by(user_id=manager_id, role='manager').first()
            if not manager:
                return jsonify(message="Manager not found!"), 404

        check_email = Register.query.filter_by(email=email).first()
        if check_email:
            return jsonify(message="Email already exists!"), 400

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = Register(
            username=username,
            email=email,
            password=hashed_password,
            profile_img=image_path,
            role=role,
            manager_id=manager_id  # Either None or the selected manager's ID
        )

        db.session.add(new_user)        
        users = Register.query.all()
        for user in users:
            if user.profile_img:
                user.profile_img = user.profile_img.replace('\\', '/')
        db.session.commit()

        return jsonify(message="User registered successfully!"), 201
    
@auth_route.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        # Sanitize Inputs
        def sanitize(input_value):
            return bleach.clean(input_value.strip(), tags=tags, strip=True) if input_value else None

        email = sanitize(email)
        
        # Fetch user by email
        user = Register.query.filter_by(email=email).first()
        
        if not user:
            return jsonify(message="User not found"), 404

        # Check if the user exists and verify the password
        if bcrypt.check_password_hash(user.password, password):
            access_token = create_access_token(identity=user.user_id, expires_delta=timedelta(hours=4))
            return jsonify(access_token=access_token, user_role=user.role, user_id=user.user_id), 200
        
        return jsonify(message='Invalid credentials'), 401

    
@auth_route.route('/change_password', methods=['POST'])
@jwt_required()
def change_password():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    new_password = data.get('new_password')
    
    if not new_password or new_password.strip() == '':
        return jsonify(message='New password cannot be empty'), 400

    user = Register.query.filter_by(user_id=current_user_id).first()

    if not user:
        return jsonify(message = 'User not found'), 404
    
    hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
    user.password = hashed_password
    db.session.commit()
    
    return jsonify(message ='Password changed successfully'), 200

@auth_route.route('/delete_user_regis/<int:user_id>', methods=['DELETE'])
def delete_user_register(user_id):
    user = Register.query.filter_by(user_id=user_id).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        return 'deleted'
    else:
        return 'user not found', 404