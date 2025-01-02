import pytest
from model.Project_comments import ProjectComments
from model.db import db
from flask_jwt_extended import create_access_token


def test_add_project_comments(client):
    with client.application.app_context():
        access_token = create_access_token(identity=1)

    response = client.post("/ProjectComments/create_project_comments/1", json = {
        "comments" : "This is a great project!!"
    },headers={"Authorization": f"Bearer {access_token}"})

    data = response.json
    assert response.status_code == 201
    assert data["message"] == "Comment added successfully"


def test_update_project_comment(client):
    with client.application.app_context():
        access_token = create_access_token(identity=1)
    
    response = client.put("/ProjectComments/update/1/project_comments",json = {
        "comments" : "This is good!!"
    },headers = {"Authorization":f"Bearer {access_token}"})

    data = response.json
    assert response.status_code == 200
    assert data["message"] == "Comment updated successfully"


def test_get_project_comments(client):
    with client.application.app_context():
        access_token = create_access_token(identity=1)

    response = client.get("/ProjectComments/get_project_comments/1",headers={"Authorization":f"Bearer {access_token}"})

    data = response.json
    print(data)
    expected_data = [{"project_comment_id": 1,
        "content": "This is project_1",
        "created_by":1,
        "created_by_username" : "testuser"}]
    assert response.status_code == 200
    assert data == expected_data


def test_delete_project_comment(client):
    with client.application.app_context():
        access_token = create_access_token(identity=1)
    
    response = client.delete("/ProjectComments/delete/1/project_comments",headers={"Authorization":f"Bearer {access_token}"})
    data = response.json
    assert response.status_code == 200
    assert data["message"] == "Comment deleted successfully"

def delete_and_generate_token(client,project_comment_id,user_id):
    """
    Used because of the same code is repeating 
    """
    with client.application.app_context():
        ProjectComments.query.filter_by(project_comment_id=project_comment_id).delete()
        db.session.commit()

        return create_access_token(identity=user_id)


def test_add_project_comments_failure(client):
    access_token = delete_and_generate_token(client,1,1)

    response = client.post("/ProjectComments/create_project_comments/1", json = {
        "comments" : ""
    },headers={"Authorization": f"Bearer {access_token}"})

    data = response.json
    assert response.status_code == 400
    assert data["message"] == "Add Comment!!!"


def test_update_project_comment_failure(client):
    access_token = delete_and_generate_token(client,1,1)

    response = client.put("/ProjectComments/update/1/project_comments",json = {
        "comments" : ""
    },headers = {"Authorization":f"Bearer {access_token}"})

    data = response.json
    assert response.status_code == 400
    assert data["message"] == "Comment cannot be empty"


def test_get_project_comments_failure(client):
    access_token = delete_and_generate_token(client,1,1)

    response = client.get("/ProjectComments/get_project_comments/2",headers={"Authorization":f"Bearer {access_token}"})

    data = response.json
    assert response.status_code == 404
    assert data["message"] == "No comments found for this project"

def test_delete_project_comment_failure(client):
    access_token = delete_and_generate_token(client,1,1)

    response = client.delete("/ProjectComments/delete/2/project_comments",headers={"Authorization":f"Bearer {access_token}"})
    data = response.json
    assert response.status_code == 404
    assert data["message"] == "Comment not found"