import pytest
from flask_jwt_extended import create_access_token



def test_get_attachments(client):
    with client.application.app_context():
        access_token = create_access_token(identity=3)

    response = client.get("/attachment/get_attached_files/1",headers={"Authorization":f"Bearer {access_token}"})
    print(response.json)
    assert response.status_code == 200
    data = response.json
    expected_data = [{'attachment': 'static/uploads/files/Dash_copy.png', 'attachment_id': 1, 'base64_image': 'e6693ba57c956e9045fcf1d0d075f7a7a220e3da0d611513217188ae3b63d34f', 'file_name': 'Dash_copy.png', 'status': 'Pending', 'task_id': 1}]
    assert data == expected_data


def test_post_attachment(client):
    with client.application.app_context():
        access_token = create_access_token(identity=3)
    
    response = client.post("/attachment/post_attachment/1",data={
        "status": "In Progress",
        "attachments":(open("C:/Users/deepa/Pictures/car.jpeg", "rb"), "car.jpeg") 
    },headers={"Authorization":f"Bearer {access_token}"})
    assert response.status_code == 201
    data = response.data
    print(data)
    expected_data = b'{\n  "message": "Files attached and status updated successfully"\n}\n'
    assert data == expected_data


def test_sha256_search(client):
    with client.application.app_context():
        access_token = create_access_token(identity=3)

    response = client.post("/attachment/sha256_search?hash=e6693ba57c956e9045fcf1d0d075f7a7a220e3da0d611513217188ae3b63d34f"
    ,headers={"Authorization":f"Bearer {access_token}"})

    assert response.status_code == 200
    data= response.json
    print(data)
    expected_data = [{'attachment': 'static/uploads/files/Dash.png', 'attachment_id': 2, 'base64_image': 'e6693ba57c956e9045fcf1d0d075f7a7a220e3da0d611513217188ae3b63d34f', 'file_name': 'Dash.png', 'status': 'In Progress', 'task_id': 2}]
    assert data == expected_data


def test_search(client):
    with client.application.app_context():
        access_token = create_access_token(identity=3)
    
    response = client.get("/attachment/search?title=Dash",headers={"Authorization":f"Bearer {access_token}"})

    print(response.json)

    assert response.status_code == 200
    data = response.json
    expected_data = [{'attachment': 'static/uploads/files/Dash.png', 'attachment_id': 2, 'base64_image': 'e6693ba57c956e9045fcf1d0d075f7a7a220e3da0d611513217188ae3b63d34f', 'file_name': 'Dash.png', 'status': 'In Progress', 'task_id': 2}]
    assert data == expected_data


def test_get_attachments_failure(client):
    with client.application.app_context():
        access_token = create_access_token(identity=3)

    response = client.get("/attachment/get_attached_files/5",headers={"Authorization":f"Bearer {access_token}"})
    print(response.json)
    assert response.status_code == 404
    data = response.json
    assert data["message"] == "Task not found"


def test_post_attachment_failure(client):
    with client.application.app_context():
        access_token = create_access_token(identity=3)
    
    response = client.post("/attachment/post_attachment/1",data={
        "status": "In Progress"
    },headers={"Authorization":f"Bearer {access_token}"})
    assert response.status_code == 400
    data = response.data
    print(data)
    expected_data = b'{\n  "message": "Status and attachments are required"\n}\n'
    assert data == expected_data


def test_sha256_search_failure(client):
    with client.application.app_context():
        access_token = create_access_token(identity=1)

    response = client.post("/attachment/sha256_search"
    ,headers={"Authorization":f"Bearer {access_token}"})

    print(response.json)

    assert response.status_code == 400
    data= response.json
    print(data)
    assert data["message"] == "Query is not given"

def test_search_failure(client):
    with client.application.app_context():
        access_token = create_access_token(identity=1)
    
    response = client.get("/attachment/search?title=",headers={"Authorization":f"Bearer {access_token}"})

    print(response.json)

    assert response.status_code == 400
    data = response.json
    assert data["message"] == "Filename query parameter is required"

