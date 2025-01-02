import pytest
from model.Project import Project
from model.Sprint import Sprint
from model.db import db
from flask_jwt_extended import create_access_token



def test_get_sprints_on_project(client):
    with client.application.app_context():
        access_token = create_access_token(identity=1)
    response = client.get("/sprint/sprints/1",headers={"Authorization":f"Bearer {access_token}"})
    data = response.json
    expected_data = {'sprints': [{'created_by': None, 'created_username': None, 'delete_yn': False, 'end_date': '2024-11-14', 'project_id': 1, 'project_name': None, 'sprint_id': 1, 'sprint_name': 'project1-sprint1', 'start_date': '2024-11-01', 'updated_by': None}]}
    print(data)
    assert response.status_code == 200
    assert data == expected_data


def test_get_all_sprints(client):
        with client.application.app_context():
            access_token = create_access_token(identity=2)
        response = client.get("/sprint/get_all_sprints",headers={"Authorization":f"Bearer {access_token}"})
        data = response.json
        expected_data = {'sprints': [{'created_by': 1, 'created_username': 'testuser', 'delete_yn': False, 'end_date': '2024-11-14', 'project_id': 1, 'project_name': 'project-1', 'sprint_id': 1, 'sprint_name': 'project1-sprint1', 'start_date': '2024-11-01', 'updated_by': None}]}
        assert response.status_code == 200
        assert data == expected_data


def test_get_all_projects(client):
    with client.application.app_context():
        access_token = create_access_token(identity=1)
    response = client.get("/sprint/get_projects",headers={"Authorization":f"Bearer {access_token}"})
    data = response.json
    expected_data = {'projects': [{'project_id': 1, 'project_name': 'project-1'}]}
    assert response.status_code == 200
    assert data == expected_data


def test_get_sprint_tasks(client):
    with client.application.app_context():
        access_token = create_access_token(identity=1)
    response = client.get("/sprint/get_sprint_tasks/1",headers={"Authorization":f"Bearer {access_token}"})
    data = response.json
    print(data)
    expected_data = {'tasks': [
        {'assigned_to': 2, 'assigned_to_username': 'testuser2', 'created_by': 1, 'created_username': 'testuser', 'deadline': '2024-12-02', 'description': 'Do this in hono', 'priority': 'Medium', 'start_date': '2024-11-18', 'status': 'Pending', 'task_id': 1, 'title': 'Hono js', 'updated_by': None}, 
        {'assigned_to': 3, 'assigned_to_username': 'testuser3', 'created_by': 2, 'created_username': 'testuser2', 'deadline': '2024-12-02', 'description': 'Do this in React', 'priority': 'High', 'start_date': '2024-11-18', 'status': 'In Progress', 'task_id': 2, 'title': 'React', 'updated_by': None}
        ]}
    assert response.status_code == 200
    assert data == expected_data


def test_edit_sprint(client):
    with client.application.app_context():
        access_token = create_access_token(identity=1)
    response = client.patch("/sprint/edit_sprint/1",json={
        "title" : "project_1Sprint____1",
        "start_date" : "2024-11-02",
        "end_date" : "2024-11-15"
    },headers={"Authorization":f"Bearer {access_token}"})

    data = response.data
    print(data)
    assert response.status_code == 200
    assert data["message"] == "sprint updated successfully!"


def test_create_sprint(client):
    with client.application.app_context():
        access_token = create_access_token(identity=1)
    response = client.post("/sprint/create_sprint/1",json={
        "title" : "project1-sprint2",
        "start_date" : "2024-11-14",
        "end_date" : "2024-11-21",
        "created_by" : 1,
        "project_id" : 1
    },headers={"Authorization":f"Bearer {access_token}"})

    data = response.data
    print(data)
    expected_data = b'{\n  "project_id": 1,\n  "sprint_id": 2\n}\n'
    assert response.status_code == 201
    assert data == expected_data


def test_get_current_sprint(client):
    with client.application.app_context():
        access_token = create_access_token(identity=1)

    response = client.get("/sprint/current_sprint/1",headers={"Authorization":f"Bearer {access_token}"})
    data = response.data
    expected_data = b'{\n  "created_by": 1,\n  "created_username": "testuser",\n  "delete_yn": false,\n  "end_date": "2024-11-21",\n  "project_id": 1,\n  "project_name": "project-1",\n  "sprint_id": 2,\n  "sprint_name": "project1-sprint2",\n  "start_date": "2024-11-14",\n  "updated_by": null\n}\n'
    print(f"current_sprint_data : {data}")
    assert response.status_code == 200
    assert data == expected_data


def test_delete_sprint(client):
    with client.application.app_context():
        access_token = create_access_token(identity=1)
    
    response = client.delete("/sprint/delete_sprint/2",headers={"Authorization":f"Bearer {access_token}"})
    data = response.json
    assert response.status_code == 200
    assert data["message"] == "Sprint is deleted!!!"


def test_get_sprints_on_project_failure(client):
    with client.application.app_context():
        access_token = create_access_token(identity=1)

    response = client.get("/sprint/sprints/10",headers={"Authorization":f"Bearer {access_token}"})
    data = response.json
    print(data)
    assert response.status_code == 400
    assert data["message"] == "No sprints Found!!"


def test_get_all_sprints_failure(client):
    with client.application.app_context():
        db.session.query(Sprint).delete()
        db.session.commit()
        access_token = create_access_token(identity=1)
    response = client.get("/sprint/get_all_sprints",headers={"Authorization":f"Bearer {access_token}"})
    data = response.json

    assert response.status_code == 400
    assert data["message"] == "No sprints found!!"


def test_get_all_projects_failure(client):
    with client.application.app_context():
        db.session.query(Project).delete()
        db.session.commit()
        access_token = create_access_token(identity=1)
    response = client.get("/sprint/get_projects",headers={"Authorization":f"Bearer {access_token}"})
    data = response.json

    assert response.status_code == 400
    assert data["message"] == "No Projects with the sprints"


def test_get_sprint_tasks_failure(client):
    with client.application.app_context():
        access_token = create_access_token(identity=1)
    response = client.get("/sprint/get_sprint_tasks/4",headers={"Authorization":f"Bearer {access_token}"})
    data = response.json
    print(data)
    assert response.status_code == 400
    assert data["message"] == "No tasks are under this Sprint"


def test_edit_sprint_failure(client):
    with client.application.app_context():
        access_token = create_access_token(identity=1)
    response = client.patch("/sprint/edit_sprint/4",json={
        "title" : "",
        "start_date" : "",
        "end_date" : ""
    },headers={"Authorization":f"Bearer {access_token}"})

    data = response.data
    expected_data = b'{\n  "message": "sprint not found!"\n}\n'
    assert response.status_code == 404
    assert data == expected_data


def test_create_sprint_failure(client):
    with client.application.app_context():
        access_token = create_access_token(identity=1)
    response = client.post("/sprint/create_sprint/1",json={
        "title" : "project1-sprint2",
        "start_date" : "2024-11-14",
        "end_date" : "2024-11-29",
        "created_by" : 1,
        "project_id" : 1
    },headers={"Authorization":f"Bearer {access_token}"})

    data = response.data
    print(data)
    expected_data = b'{\n  "message": "End date must not exceed 2 weeks from the start date"\n}\n'
    assert response.status_code == 400
    assert data == expected_data


def test_get_current_sprint_failure(client):
    with client.application.app_context():
        sprint = Sprint.query.filter_by(sprint_id=2, delete_yn=False).first()
        if sprint:
            db.session.delete(sprint)
            db.session.commit()
        access_token = create_access_token(identity=1)
    
    response = client.get("/sprint/current_sprint/1",headers={"Authorization":f"Bearer {access_token}"})
    data = response.data
    expected_data = b'{\n  "message": "No current sprint found"\n}\n'
    print(f"current_sprint_data : {data}")
    assert response.status_code == 404
    assert data == expected_data

def test_delete_sprint_failure(client):
    with client.application.app_context():
        access_token = create_access_token(identity=1)
    response = client.delete("/sprint/delete_sprint/3",headers={"Authorization":f"Bearer {access_token}"})
    data = response.json
    assert response.status_code == 400
    assert data["message"] == "There is no sprint in this id!!"