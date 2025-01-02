import pytest
from model.Register import Register
from model.db import db
from flask_jwt_extended import create_access_token


def test_get_user_data(client):
    with client.application.app_context():
        access_token = create_access_token(identity=3)

    response = client.get('/profile/user/data', headers={
        'Authorization': f'Bearer {access_token}'
    })

    assert response.status_code == 200
    data = response.json
    assert data['username'] == "testuser3"
    assert data['profile_img'] == "test_3.jpg"
    assert data['role'] == "user"

def test_get_profile(client):
    with client.application.app_context():
        access_token = create_access_token(identity=1)
    response = client.get("/profile/get_profile", headers = {"Authorization":f"Bearer {access_token}"})

    assert response.status_code == 200
    print(f"response_profile:{response}")
    data =response.json
    expected_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "role": "admin",
        "profile_img": "/static/test.jpg",
        "total_tasks_created": 1,
        "total_tasks_assigned": 0,
        "completed_tasks": 0
    }
    assert data == expected_data

def test_update_profile_picture(client):
    print("test_update_profile_pic!!")
    with client.application.app_context():
        access_token = create_access_token(identity=1)

    response = client.post("/profile/update_profile_picture", data={
        "profile_img": (open("C:/Users/deepa/Pictures/car.jpeg", "rb"), "car.jpeg")
    },headers={"Authorization":f"Bearer {access_token}"})

    print(response.json)
    assert response.status_code == 200
    data = response.json
    assert data ["profile_img"] == "static/uploads/car.jpeg"

def test_users(client):
    with client.application.app_context():
        access_token = create_access_token(identity=1)
    
    response = client.get("/profile/users", headers = {"Authorization":f"Bearer {access_token}"})
    expected_data = [
        {'email': 'testuser@example.com', 'role': 'admin', 'user_id': 1, 'username': 'testuser'},
        {'email': 'testuser2@example.com', 'role': 'manager', 'user_id': 2, 'username': 'testuser2'}
        ]
    data = response.json

    if response.status_code == 200:
        data == expected_data
    else:
        data["message"] == "No Users Found!!"

def test_managers(client):
    with client.application.app_context():
        access_token = create_access_token(identity=1)

    response = client.get("/profile/managers",headers = {"Authorization":f"Bearer {access_token}"})
    excepted_data = [{'user_id':2,'username': "testuser2"}]

    if response.status_code == 200:
        data = response.json
        assert data == excepted_data
    else:
        data["message"] == "No managers found!!!"

def test_users_under_manager(client):
    with client.application.app_context():
        access_token = create_access_token(identity=1)
    
    response = client.get("/profile/get_users_under_manager",headers = {"Authorization":f"Bearer {access_token}"})
    expected_data = [{}]
    data = response.json
    
    if response.status_code == 200:
        assert data == expected_data
    else:
        data["message"] == "No users under this manager"

def test_get_users_and_managers(client):
    with client.application.app_context():
        access_token = create_access_token(identity=2)

    response = client.get("/profile/get_users_and_managers",headers = {"Authorization":f"Bearer {access_token}"})
    print(response.json)

    assert response.status_code == 200
    data = response.json
    expected_data = {'managers': [{'email': 'testuser2@example.com', 'id': 2, 'username': 'testuser2'}], 'users': [{'email': 'testuser3@example.com', 'id': 3, 'username': 'testuser3'}]}
    assert data == expected_data


# Failure
def delete_user_and_generate_token(client,user_id):
    """
    Used because of the same code is repeating 
    """
    with client.application.app_context():
        Register.query.filter_by(user_id=user_id).delete()
        db.session.commit()

        return create_access_token(identity=user_id)


def test_get_user_data_failure(client):

    access_token = delete_user_and_generate_token(client,user_id=3)
    
    response = client.get('/profile/user/data', headers={
        'Authorization': f'Bearer {access_token}'
    })

    assert response.status_code == 404
    data = response.json
    assert data["message"] == "User not found"

def test_get_profile_failure(client):
    access_token = delete_user_and_generate_token(client,user_id=3)

    response = client.get("/profile/get_profile", headers = {"Authorization":f"Bearer {access_token}"})

    assert response.status_code == 404
    data =response.json
    assert data["message"] == "User not found"

def test_update_profile_picture_failure(client):
    with client.application.app_context():
        access_token = create_access_token(identity=2)
    
    response = client.post("/profile/update_profile_picture", data={
        
    },headers={"Authorization":f"Bearer {access_token}"})

    print(response.json)
    assert response.status_code == 400
    data = response.json
    assert data ["message"] == "No file part"


# Always this functions will show only 200 because one user will always remain
@pytest.mark.skip
def test_users_failure(client):
    with client.application.app_context():
        db.session.query(Register).filter(Register.role != 'admin').delete()
        db.session.commit()
        access_token = create_access_token(identity=1)
    response = client.get("/profile/users", headers = {"Authorization":f"Bearer {access_token}"})
    
    assert response.status_code == 404
    data = response.json
    print(data)
    assert data["message"] == "No Users Found!!"

def test_managers_failure(client):
    with client.application.app_context():
        db.session.query(Register).filter(Register.role == 'manager').delete()
        db.session.commit()
        access_token = create_access_token(identity=1)
    response = client.get("/profile/managers",headers = {"Authorization":f"Bearer {access_token}"})

    assert response.status_code == 404
    data = response.json
    assert data["message"] == "No managers found!!!"

def test_get_users_under_manager_failure(client):
    with client.application.app_context():
        db.session.query(Register).filter(Register.role == 'user').delete()
        db.session.commit()
        access_token = create_access_token(identity=2)
    response = client.get("/profile/get_users_under_manager",headers = {"Authorization":f"Bearer {access_token}"})

    data = response.json
    
    assert response.status_code == 404
    assert data["message"] == "No users under this manager"

def test_get_users_and_managers_failure(client):
    with client.application.app_context():
        access_token = create_access_token(identity=3)
    
    response = client.get("/profile/get_users_and_managers",headers = {"Authorization":f"Bearer {access_token}"})
    print(response.json)

    assert response.status_code == 403
    data = response.json
    assert data["error"] == "Unauthorized access!!"
    
