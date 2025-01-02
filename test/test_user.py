import pytest
from model.Register import Register
from model.db import db
from flask_jwt_extended import create_access_token


def test_user_list(client):
    with client.application.app_context():
        access_token = create_access_token(identity=1)
    response = client.get("/user/users_list",headers = {"Authorization":f"Bearer {access_token}"})

    assert response.status_code == 200
    data = response.json
    expected_data = [{'user_id': 3, 'username': 'testuser3'}, {'user_id': 4, 'username': 'testuser4'}]
    assert data == expected_data

def test_update_user_img(client):
    with client.application.app_context():
        access_token = create_access_token(identity=2)
    response = client.post("/user/update_user_img/2",data = {
        "profile_image": (open("C:/Users/deepa/Pictures/car.jpeg", "rb"), "car.jpeg")
    },headers={"Authorization":f"Bearer {access_token}"})

    assert response.status_code == 200
    data =response.json
    print(data)
    assert data["message"] == "updated the user!!"

def test_update_user(client):
    with client.application.app_context():
        access_token = create_access_token(identity=1)
    response = client.patch("/user/update_user/2", json={
        "username" : "venky",
        "email" : "venky@gmail.com"
    },headers={"Authorization":f"Bearer {access_token}"})

    assert response.status_code == 200
    data = response.json
    expected_data = {'user': {'username': "venky", 'email': "venky@gmail.com", 'role': "manager"}}
    assert data == expected_data

def test_delete_user(client):
    with client.application.app_context():
        access_token = create_access_token(identity=1)
    response = client.delete("/user/delete_user/4",headers={"Authorization":f"Bearer {access_token}"})

    assert response.status_code == 200
    data = response.json
    assert data["message"] == "User is deleted!!!"


# Failure Test

def delete_user_and_generate_token(client,user_id_delete,user_id):
    """
    Used because of the same code is repeating 
    """
    with client.application.app_context():
        Register.query.filter_by(user_id=user_id_delete).delete()
        db.session.commit()

        return create_access_token(identity=user_id)


def test_userlist_failure(client):
    with client.application.app_context():
        db.session.query(Register).filter(Register.role == 'user').delete()
        db.session.commit()

        access_token = create_access_token(identity=1)
    response = client.get("/user/users_list",headers = {"Authorization":f"Bearer {access_token}"})

    assert response.status_code == 404
    data = response.json
    assert data ["message"] == "No Users Found!!!" 

def test_update_user_img_failure (client):
    access_token = delete_user_and_generate_token(client,user_id_delete=4, user_id=1)

    response = client.post("/user/update_user_img/4",data = {
        "profile_image": (open("C:/Users/deepa/Pictures/car.jpeg", "rb"), "car.jpeg")
    },headers={"Authorization":f"Bearer {access_token}"})

    assert response.status_code == 404
    data =response.json
    print(data)
    assert data["message"] == "The given user not available!!"

def test_update_user_failure(client):
    access_token = delete_user_and_generate_token(client,user_id_delete=4, user_id=1)

    response = client.patch("/user/update_user/4", json={
        "username" : "kumaran",
        "email" : "kumaran@gmail.com"
    },headers={"Authorization":f"Bearer {access_token}"})

    assert response.status_code == 404
    data = response.json
    assert data["error"] == "User not found"

def test_delete_user_failure(client):
    access_token = delete_user_and_generate_token(client, user_id_delete=4, user_id=1)
    
    response = client.delete("/user/delete_user/4",headers={"Authorization":f"Bearer {access_token}"})

    print(response.json)

    assert response.status_code == 404
    data = response.json
    assert data["message"] == "User not found or already deleted!"
    