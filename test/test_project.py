import pytest
from model.Project import Project
from model.db import db
from flask_jwt_extended import create_access_token


def test_project_data(client):
    with client.application.app_context():
        access_token = create_access_token(identity=1)
    response = client.post("/project/project_data",json = {
        "title" : "project-2",
        "description" : "This is project-2",
        "status" : "Pending",
        "start_date" : "2024-12-01",
        "end_date" : "2025-01-01",
        "created_by" : 1
    },headers={"Authorization":f"Bearer {access_token}"})
    print(response.json)

    assert response.status_code == 201
    data = response.json
    print(data)
    assert data == {'project_id': 2}


def test_get_projects(client):
    with client.application.app_context():
        access_token = create_access_token(identity=2)
    
    response = client.get("/project/projects", headers = {"Authorization":f"Bearer {access_token}"})

    assert response.status_code == 200
    data = response.json
    print(data)
    assert data == {'projects': [{'project_id': 1, 'title': 'project-1'}]}


def test_get_all_project(client):
    with client.application.app_context():
        access_token = create_access_token(identity=2)
    
    response = client.get("/project/get_all_project", headers = {"Authorization":f"Bearer {access_token}"})

    assert response.status_code == 200
    data = response.json
    print(data)
    expected_data = [{'comments': [], 'completed_tasks': 0, 'created_by': 'testuser', 'description': 'This is project-1', 'duration': 30, 'end_date': '2024-12-01', 'project_id': 1, 'start_date': '2024-11-01', 'status': 'Pending', 'title': 'project-1', 'total_tasks': 0, 'updated_by': None}]
    assert data == expected_data


def test_edit_project_status(client):
    with client.application.app_context():
        access_token = create_access_token(identity=1)
    
    response = client.put("/project/edit_project_status/1",json = {
        "status" : "In Progress"
    }, headers={"Authorization":f"Bearer {access_token}"})

    assert response.status_code == 200
    data = response.json
    assert data["message"] == "Project updated successfully"


def test_edit_project_data(client):
    with client.application.app_context():
        access_token = create_access_token(identity=1)
    
    response = client.patch("/project/update_project_data/1",json={
        "start_date" : "2024-11-02",
        "end_date" : "2024-11-02"
    }, headers = {"Authorization":f"Bearer {access_token}"})
    
    print(response.status_code)
    assert response.status_code == 200
    data = response.json
    assert data["message"] == "project updated successfully!"


def test_delete_project(client):
    with client.application.app_context():
        access_token = create_access_token(identity=1)
    
    response = client.delete("/project/delete_project/1",headers={"Authorization":f"Bearer {access_token}"})
    print(response.json)
    assert response.status_code == 200
    data = response.json 
    assert data["message"] == "The given project is deleted!!"


def test_get_dashboard_summary(client):
    with client.application.app_context():
        access_token = create_access_token(identity=2)

    response = client.get("/project/dashboard/summary",headers={"Authorization":f"Bearer {access_token}"})
    print(response.json)
    assert response.status_code == 200
    data = response.json
    expected_data = {'completed_projects': 0, 'created_completed_tasks': 0, 'created_tasks': 0, 'total_projects': 1}
    assert data == expected_data


def test_get_user_dashboard_summary(client):
    with client.application.app_context():
        access_token = create_access_token(identity=2)
    
    response = client.get("/project/dashboard/user_summary",headers = {"Authorization":f"Bearer {access_token}"})
    print(response.json)
    assert response.status_code == 200
    data = response.json
    expected_data = {'user_name' : "testuser2",
        'total_tasks_created': 0,
        'completed_tasks_created': 0,
        'total_tasks_assigned': 1,
        'completed_tasks_assigned': 0}
    assert data == expected_data


def test_project_data_failure(client):
    with client.application.app_context():
        access_token = create_access_token(identity=1)

    response = client.post("/project/project_data",json = {
        "title" : "project-2",
        "description" : "This is project-2",
        "status" : "Pending",
        "end_date" : "2025-01-01",
        "created_by" : 1
    },headers={"Authorization":f"Bearer {access_token}"})
    print(response.json)

    assert response.status_code == 400
    data = response.json
    print(data)
    assert data["error"] == "Missing required fields"

def delete_user_and_generate_token(client,project_id,user_id):
    """
    Used because of the same code is repeating 
    """
    with client.application.app_context():
        Project.query.filter_by(project_id=project_id).delete()
        db.session.commit()

        return create_access_token(identity=user_id)


def test_get_projects_failure(client):
    access_token = delete_user_and_generate_token(client,1,2)

    response = client.get("/project/projects", headers = {"Authorization":f"Bearer {access_token}"})

    assert response.status_code == 404
    data = response.json
    print(data)
    assert data["error"] == "No projects found"


def test_get_all_project_failure(client):
    access_token = delete_user_and_generate_token(client,1,2)

    response = client.get("/project/get_all_project", headers = {"Authorization":f"Bearer {access_token}"})

    assert response.status_code == 404
    data = response.json
    print(data)
    assert data["error"] == "No Project is found!!"


def test_edit_project_status_failure(client):
    access_token = delete_user_and_generate_token(client,1,2)

    response = client.put("/project/edit_project_status/1",json = {
        "status" : "In Progress"
    }, headers={"Authorization":f"Bearer {access_token}"})

    assert response.status_code == 404
    data = response.json
    assert data["message"] == "Project not found"


def test_edit_project_data_failure(client):
    access_token = delete_user_and_generate_token(client,1,1)

    response = client.patch("/project/update_project_data/1",json={
        "start_date" : "2024-11-02",
        "end_date" : "2024-11-02"
    }, headers = {"Authorization":f"Bearer {access_token}"})
    
    print(response.json)
    assert response.status_code == 404
    data = response.json
    assert data["message"] == "Project not found!"


def test_delete_project_failure(client):
    access_token = delete_user_and_generate_token(client,1,1)

    response = client.delete("/project/delete_project/1",headers={"Authorization":f"Bearer {access_token}"})
    print(response.json)
    assert response.status_code == 404
    data = response.json 
    assert data["message"] == "Given project data is not found!!"


def test_get_dashboard_summary_failure(client):
    access_token = delete_user_and_generate_token(client,1,3)

    response = client.get("/project/dashboard/summary",headers={"Authorization":f"Bearer {access_token}"})
    print(response.json)
    assert response.status_code == 403
    data = response.json
    assert data["message"] == "'Access forbidden: insufficient permissions"

