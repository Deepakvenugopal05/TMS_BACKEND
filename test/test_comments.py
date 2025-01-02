import pytest
from flask_jwt_extended import create_access_token

def test_add_comment(client):
    with client.application.app_context():
        access_token = create_access_token(identity=3)
    
    response = client.post("/comments/post_tasks_comments/2", json={
        "comment" : "This is a great comments"
    },headers = {"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 201
    data = response.json
    assert data["message"] == "Comment added successfully"

def test_get_comments(client):
    with client.application.app_context():
        access_token = create_access_token(identity=3)
    response = client.get("/comments/tasks/2/comment",headers = {"Authorization":f"Bearer {access_token}"})

    assert response.status_code == 200
    data = response.json
    print(data)
    expected_data = [{'comment_id': 2, 'content': 'This is comment2', 'created_by': 3, 'created_by_username': 'testuser3'}]
    assert data == expected_data

def test_edit_comments(client):
    with client.application.app_context():
        access_token = create_access_token(identity=2)
    response = client.patch("/comments/edit_comments/1",json={
        "content" : "this is edited!!"
    },headers={"Authorization":f"Bearer {access_token}"})

    assert response.status_code == 200
    data = response.json
    assert data["message"] == "updated!!"

def test_add_comment_failure(client):
    with client.application.app_context():
        access_token = create_access_token(identity=3)

    response = client.post("/comments/post_tasks_comments/1", json={
        "comment" : "This is a great comments"
    },headers = {"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 403
    data = response.json
    assert data["message"] == "You do not have permission to comment on this task"

def test_get_comments_failure(client):
    with client.application.app_context():
        access_token = create_access_token(identity=3)

    response = client.get("/comments/tasks/1/comment",headers = {"Authorization":f"Bearer {access_token}"})

    assert response.status_code == 403
    data = response.json
    print(data)
    assert data["message"] == "You do not have permission to comment on this task"

def test_edit_comments_failure(client):
    with client.application.app_context():
        access_token = create_access_token(identity=3)

    response = client.patch("/comments/edit_comments/1",json={
        "content" : "this is edited!!"
    },headers={"Authorization":f"Bearer {access_token}"})

    assert response.status_code == 403
    data = response.json
    assert data["message"] == "This is not created by you"

