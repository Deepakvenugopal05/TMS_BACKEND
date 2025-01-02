import pytest
from flask_jwt_extended import create_access_token
from model.db import db
from model.Register import Register
from config import UPLOAD_FOLDER


def test_login_success(client):
    response = client.post("/auth/login", json={
        "email": "testuser@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json
    assert "access_token" in data


def test_forget_password_success(client):
    print("Inside Forget_pasword!!!")
    response = client.post("/auth/forget_password", json = {
        "email":"testuser@example.com",
        "new_password":"new123"
    })
    assert response.status_code == 200
    data = response.json
    print(f"data_forget_password: {data}")
    assert data["message"] == "Password updated successfully!"


def test_change_password_success(client):
    with client.application.app_context():
        access_token = create_access_token(identity=1)

    response = client.post('/auth/change_password', json={
        'new_password': 'newpassword123'
    }, headers={'Authorization': f'Bearer {access_token}'})

    assert response.status_code == 200
    data = response.json
    assert data['message'] == 'Password changed successfully'

@pytest.mark.parametrize(
        "email,new_password,expected_status, expected_message",
        [
            ("test@example.com","123",401,"Invalid credentials")
        ]
)
def test_login_failure(client,email,new_password,expected_status,expected_message):
    response = client.post("/auth/login", json={
        "email": email,
        "password": new_password
    })

    assert response.status_code == expected_status
    data = response.json
    assert data["message"] == expected_message

@pytest.mark.parametrize(
        "user_id,email,new_password,expected_status, expected_message",
        [
            (2,"","123",400,"Email is required!"),
            (2,"testuser3@example.com","",400,"New password is required!"),
            (3,"testuser3@example.com","123",404,"No user found with this email!"),
        ]
)
def test_forget_password_failure(client,user_id,email,new_password,expected_status,expected_message):
    with client.application.app_context():
        if user_id == 3:
            Register.query.filter_by(user_id=user_id).delete()
            db.session.commit()

    response = client.post("/auth/forget_password", 
    json = {
        "email":email,
        "new_password":new_password
    }
    )

    assert response.status_code == expected_status
    data = response.json
    assert data["message"] == expected_message

@pytest.mark.parametrize(
    "user_id, new_password, expected_status, expected_message",
    [
        (2, None, 400, "New password cannot be empty"),         # Case: No password provided
        (2, "", 400, "New password cannot be empty"),           # Case: Empty password
        (2, "   ", 400, "New password cannot be empty"),        # Case: Whitespace password
        (3, "new123", 404, "User not found"),                   # Case: User does not exist
    ]
)
def test_change_password_failures(client, user_id, new_password, expected_status, expected_message):
    with client.application.app_context():
        if user_id == 3:
            Register.query.filter_by(user_id=user_id).delete()
            db.session.commit()
        access_token = create_access_token(identity=user_id)

    response = client.post(
        "/auth/change_password",
        json={"new_password": new_password},
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == expected_status
    data = response.json
    assert data["message"] == expected_message

def test_register_duplicate_email(client):
    response = client.post('/auth/register', data={
        'username': 'newuser',
        'email': 'testuser@example.com',
        'password': 'newpassword123',
        'role': 'user',
        'manager_id': 2
    })
    print(response.json)
    assert response.status_code == 400
    assert response.json['message'] == 'Email already exists!'

def test_change_password_invalid_token(client):    
    response_login = client.post('/auth/login', json={
        'email': 'testuser@example.com',
        'password': 'password123'
    })
    print(response_login.json)
    token = response_login.json['access_token']

    invalid_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'
    
    response = client.post('/auth/change_password', json={
        'new_password': 'newpassword123'
    }, headers={'Authorization': f'Bearer {invalid_token}'})
    
    print(response.json)
    assert response.status_code == 422
    assert response.json['msg'] == 'Signature verification failed'


def test_register_missing_manager(client):
    response = client.post('/auth/register', data={
        'username': 'userwithoutmanager',
        'email': 'userwithoutmanager@example.com',
        'password': 'password123',
        'role': 'user',
        # Missing manager_id
    })
    assert response.status_code == 400
    assert response.json['message'] == 'Manager ID not provided for user!'

import os
from io import BytesIO
from werkzeug.datastructures import FileStorage
import pytest

@pytest.mark.parametrize("data, file_data, expected_status, expected_message", [
    # Test Case 1: Missing required fields
    ({}, None, 400, "Missing fields required"),

    # Test Case 2: Missing email
    ({
        'username': 'testuser',
        'password': 'Test1234!',
        'role': 'user',
        'manager_id': 1
    }, None, 400, "Missing fields required"),

    # Test Case 3: Missing manager_id for user role
    ({
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'Test1234!',
        'role': 'user'
    }, None, 400, "Manager ID not provided for user!"),

    # Test Case 4: Manager not found
    ({
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'Test1234!',
        'role': 'user',
        'manager_id': 999
    }, None, 404, "Manager not found!"),

    # Test Case 5: Successfully register without profile image
    ({
        'username': 'testuser4',
        'email': 'testuser4@example.com',
        'password': 'Test1234!',
        'role': 'user',
        'manager_id': 2
    }, None, 201, "User registered successfully!"),

])
def test_register_failures(client, data, file_data, expected_status, expected_message):
    if file_data:
        file_storage = FileStorage(stream=BytesIO(file_data), filename="profile_img.jpg", content_type="image/jpeg")
        data['profile_image'] = file_storage

    response = client.post('/auth/register', data=data, content_type='multipart/form-data')
    assert response.status_code == expected_status
    assert response.json['message'] == expected_message

    if expected_status == 201:
        user = Register.query.filter_by(email=data['email']).first()
        assert user is not None
        assert user.username == data['username']
        assert user.email == data['email']
        assert user.role == data['role']
        assert user.manager_id == data['manager_id']

        if 'profile_image' in data:
            assert user.profile_img == os.path.join('uploads', 'profile_img.jpg')

            uploaded_file_path = os.path.join(UPLOAD_FOLDER, 'profile_img.jpg')
            assert os.path.exists(uploaded_file_path)
            os.remove(uploaded_file_path)
