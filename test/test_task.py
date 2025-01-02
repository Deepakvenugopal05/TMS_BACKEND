import pytest
from flask_jwt_extended import create_access_token
from model.db import db
from model.Task import Task
from datetime import datetime


def test_dashboard_form_data(client):
    with client.application.app_context():
        access_token = create_access_token(identity=2)
    
    response = client.post("/task/dashboard/form_data",json={
        "project_id" : 1,
        "sprint_id" : 1,
        "title" : "Marketing",
        "description" : "Do the digital marketing for this!!",
        "priority" : "Low",
        "status" : "Pending",
        "start_date" : "2024-11-03",
        "deadline" : "2024-11-11",
        "estimated_hours" : "64",
        "assigned_to" : "3",
        "created_by" : 2,
    },headers={"Authorization":f"Bearer {access_token}"})

    data = response.json
    print(data)
    assert response.status_code == 201
    assert data["message"] == "Task added successfully"


def test_form_data(client):
    with client.application.app_context():
        access_token = create_access_token(identity=2)
    
    response = client.post("/task/form_data/1/1",json={
        "project_id" : 1,
        "sprint_id" : 1,
        "title" : "Marketing",
        "description" : "Do the digital marketing for this!!",
        "priority" : "Low",
        "status" : "Pending",
        "start_date" : "2024-11-03",
        "deadline" : "2024-11-11",
        "estimated_hours" : "64",
        "assigned_to" : "3",
        "created_by" : 2,
    },headers={"Authorization":f"Bearer {access_token}"})

    data = response.json
    print(data)
    assert response.status_code == 201
    assert data["message"] == "Task added successfully"


def test_get_users_for_assigned(client):
    with client.application.app_context():
        access_token = create_access_token(identity=2)
    response = client.get("/task/forms_assigned",headers={"Authorization":f"Bearer {access_token}"})
    data = response.json
    print(data)
    expected_data = ['testuser3']
    assert response.status_code == 200
    assert data == expected_data


def test_update_task_status(client):
    with client.application.app_context():
        access_token = create_access_token(identity=2)
    response = client.patch("/task/edit_status/1",json={
        "status":"In Progress"
    },headers={"Authorization":f"Bearer {access_token}"})
    data = response.json
    print(data)
    assert response.status_code == 200
    assert data["message"] == "Task updated successfully"


def test_update_task_work_hours(client):
    with client.application.app_context():
        access_token = create_access_token(identity=2)
    response = client.put("/task/edit_work_hours/1",json={
        "work_hours" : 56
    },headers={"Authorization":f"Bearer {access_token}"})
    data = response.json
    print(data)
    assert response.status_code == 200
    assert data["message"] == "Task updated successfully"


def test_edit_task(client):
    with client.application.app_context():
        access_token = create_access_token(identity=2)
    response = client.put("/task/edit_task/2",json={
        "project_id" : 1,
        "sprint_id" : 1,
        "title" : "Marketing",
        "description" : "Do the digital marketing for this!!",
        "priority" : "Low",
        "status" : "Pending",
        "start_date" : "2024-11-03",
        "deadline" : "2024-11-11",
        "estimated_hours" : "64",
        "assigned_to" : "3",
        "created_by" : 2,
    },headers={"Authorization":f"Bearer {access_token}"})
    data = response.json
    print(data)
    assert response.status_code == 200
    assert data["message"] == "Task updated successfully!"


def test_delete_task(client):
    with client.application.app_context():
        access_token = create_access_token(identity=2)
    response = client.delete("/task/delete_task/3",headers={"Authorization":f"Bearer {access_token}"})
    data = response.json
    assert response.status_code == 200
    assert data["message"] == "task is deleted!!!"


def test_search_tasks(client):
    with client.application.app_context():
        access_token = create_access_token(identity=2)
    response = client.get("/task/search?title=react",headers={"Authorization":f"Bearer {access_token}"})
    data = response.json
    print(data)
    expected_data = [{'assigned_to': 3, 'attachments': [{'attachment': 'static/uploads/files/Dash.png', 'attachment_id': 2, 'image_hash': 'e6693ba57c956e9045fcf1d0d075f7a7a220e3da0d611513217188ae3b63d34f', 'file_name': 'Dash.png', 'status': 'In Progress', 'task_id': 2}], 'comments': [{'comment_id': 2, 'content': 'This is comment2'}], 'created_by': 2, 'deadline': '2024-12-02', 'description': 'Do this in React', 'duration': 14, 'estimated_hours': None, 'parent_id': None, 'priority': 'High', 'start_date': '2024-11-18', 'status': 'In Progress', 'task_id': 2, 'title': 'React', 'updated_by': None, 'working_hours': 0.0}]
    assert response.status_code == 200
    assert data == expected_data


def test_get_all_tasks(client):
    with client.application.app_context():
        access_token = create_access_token(identity=2)
    response = client.get("/task/get_all_tasks",headers={"Authorization":f"Bearer {access_token}"})
    data = response.json
    expected_data = {'tasks': [{'assigned_to': 2, 'assigned_to_username': 'testuser2', 'attachments': [{'attachment': 'static/uploads/files/Dash_copy.png', 'attachment_id': 1, 'file_name': 'Dash_copy.png', 'image_hash': 'e6693ba57c956e9045fcf1d0d075f7a7a220e3da0d611513217188ae3b63d34f', 'status': 'Pending', 'task_id': 1}], 'comments': [{'comment_id': 1, 'content': 'This is comment1'}, {'comment_id': 3, 'content': 'This is comment3'}], 'created_by': 1, 'created_username': 'testuser', 'deadline': '2024-12-02', 'description': 'Do this in hono', 'duration': 14, 'estimated_hours': None, 'parent_id': None, 'priority': 'Medium', 'project_id': None, 'project_name': None, 'sprint_id': 1, 'sprint_name': 'project1-sprint1', 'start_date': '2024-11-18', 'status': 'Pending', 'task_id': 1, 'title': 'Hono js', 'updated_by': None, 'working_hours': 0.0}, 
                               {'assigned_to': 3, 'assigned_to_username': 'testuser3', 'attachments': [{'attachment': 'static/uploads/files/Dash.png', 'attachment_id': 2, 'file_name': 'Dash.png', 'image_hash': 'e6693ba57c956e9045fcf1d0d075f7a7a220e3da0d611513217188ae3b63d34f', 'status': 'In Progress', 'task_id': 2}], 'comments': [{'comment_id': 2, 'content': 'This is comment2'}], 'created_by': 2, 'created_username': 'testuser2', 'deadline': '2024-12-02', 'description': 'Do this in React', 'duration': 14, 'estimated_hours': None, 'parent_id': None, 'priority': 'High', 'project_id': None, 'project_name': None, 'sprint_id': 1, 'sprint_name': 'project1-sprint1', 'start_date': '2024-11-18', 'status': 'In Progress', 'task_id': 2, 'title': 'React', 'updated_by': None, 'working_hours': 0.0}, 
                               {'assigned_to': 3, 'assigned_to_username': 'testuser3', 'attachments': [], 'comments': [], 'created_by': 2, 'created_username': 'testuser2', 'deadline': '2024-12-02', 'description': 'Do the Testing', 'duration': 14, 'estimated_hours': None, 'parent_id': None, 'priority': 'High', 'project_id': None, 'project_name': None, 'sprint_id': 2, 'sprint_name': 'project1-sprint2', 'start_date': '2024-11-18', 'status': 'In Progress', 'task_id': 3, 'title': 'Testing', 'updated_by': None, 'working_hours': 0.0}]}
    print(data)
    assert response.status_code == 200
    assert data == expected_data


def test_tasks(client):
    with client.application.app_context():
        access_token = create_access_token(identity=2)
    
    response = client.get("/task/get_tasks",headers={"Authorization":f"Bearer {access_token}"})
    data = response.json
    expected_data = {'assigned_tasks': [{'assigned_to': 2, 'assigned_username': 'testuser2', 'attachments': [{'attachment': 'static/uploads/files/Dash_copy.png', 'attachment_id': 1, 'file_name': 'Dash_copy.png', 'image_hash': 'e6693ba57c956e9045fcf1d0d075f7a7a220e3da0d611513217188ae3b63d34f', 'status': 'Pending', 'task_id': 1}], 'comments': [{'comment_id': 1, 'content': 'This is comment1'}, {'comment_id': 3, 'content': 'This is comment3'}], 'created_by': 1, 'created_by_username': 'testuser', 'deadline': '2024-12-02', 'description': 'Do this in hono', 'duration': 14, 'estimated_hours': None, 'parent_id': None, 'priority': 'Medium', 'project_id': None, 'project_name': None, 'sprint_id': 1, 'sprint_name': 'project1-sprint1', 'start_date': '2024-11-18', 'status': 'Pending', 'task_id': 1, 'title': 'Hono js', 'updated_by': None, 'working_hours': 0.0}], 'created_tasks': [{'assigned_to': 3, 'assigned_to_username': 'testuser3', 'attachments': [{'attachment': 'static/uploads/files/Dash.png', 'attachment_id': 2, 'file_name': 'Dash.png', 'image_hash': 'e6693ba57c956e9045fcf1d0d075f7a7a220e3da0d611513217188ae3b63d34f', 'status': 'In Progress', 'task_id': 2}], 'comments': [{'comment_id': 2, 'content': 'This is comment2'}], 'created_by': 2, 'created_username': 'testuser2', 'deadline': '2024-12-02', 'description': 'Do this in React', 'duration': 14, 'estimated_hours': None, 'parent_id': None, 'priority': 'High', 'project_id': None, 'project_name': None, 'sprint_id': 1, 'sprint_name': 'project1-sprint1', 'start_date': '2024-11-18', 'status': 'In Progress', 'task_id': 2, 'title': 'React', 'updated_by': None, 'working_hours': 0.0}, {'assigned_to': 3, 'assigned_to_username': 'testuser3', 'attachments': [], 'comments': [], 'created_by': 2, 'created_username': 'testuser2', 'deadline': '2024-12-02', 'description': 'Do the Testing', 'duration': 14, 'estimated_hours': None, 'parent_id': None, 'priority': 'High', 'project_id': None, 'project_name': None, 'sprint_id': 2, 'sprint_name': 'project1-sprint2', 'start_date': '2024-11-18', 'status': 'In Progress', 'task_id': 3, 'title': 'Testing', 'updated_by': None, 'working_hours': 0.0}]}
    assert response.status_code == 200
    assert data == expected_data


def test_task_specific(client):
    with client.application.app_context():
        access_token = create_access_token(identity=2)
    
    response = client.get("/task/task_specific/2",headers={"Authorization":f"Bearer {access_token}"})
    data = response.json
    print(data)
    expected_data = {'assigned_to': 3, 'assigned_to_username': 'testuser3', 'attachments': [{'attachment': 'static/uploads/files/Dash.png', 'attachment_id': 2, 'file_name': 'Dash.png', 'image_hash': 'e6693ba57c956e9045fcf1d0d075f7a7a220e3da0d611513217188ae3b63d34f', 'status': 'In Progress', 'task_id': 2}], 'comments': [{'comment_id': 2, 'content': 'This is comment2'}], 'created_by': 2, 'deadline': '2024-12-02', 'description': 'Do this in React', 'duration': 14, 'estimated_hours': None, 'parent_id': None, 'parent_title': None, 'priority': 'High', 'sprint_name': 'project1-sprint1', 'start_date': '2024-11-18', 'status': 'In Progress', 'task_id': 2, 'title': 'React', 'updated_by': None, 'working_hours': 0.0}
    assert response.status_code == 200
    assert data == expected_data


def test_attach_file(client):
    with client.application.app_context():
        access_token = create_access_token(identity=2)
        
    with open("C:/Users/deepa/Pictures/car.jpeg", "rb") as file:
        data = {
            "task_id": "1",
            "status": "pending",
            "file": file
        }

        response = client.post("/task/attach_file", data=data, content_type='multipart/form-data', headers={
            "Authorization": f"Bearer {access_token}"
        })

    data = response.json
    print(data)
    assert response.status_code == 200
    assert data["message"] == "File attached successfully"

# Want to solve the error in this!!!

def test_download_attachment(client):
    with client.application.app_context():
        access_token = create_access_token(identity=2)

    response = client.get("/task/download/1", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    assert 'attachment' in response.headers['Content-Disposition']
    assert 'car.jpeg' in response.headers['Content-Disposition']


def test_create_subtask(client):
    with client.application.app_context():
        access_token = create_access_token(identity=2)
    
    response = client.post("/task/create_subtask",json={
        "project_id" : 1,
        "sprint_id" : 2,
        "title" : "Unit Testing",
        "description" : "Do the unit testing for this!!",
        "priority" : "Low",
        "status" : "Pending",
        "start_date" : "2024-11-03",
        "deadline" : "2024-11-11",
        "estimated_hours" : "64",
        "assigned_to" : "3",
        "created_by" : 2,
        "parent_task_id" : 3
    },headers={"Authorization":f"Bearer {access_token}"})

    data = response.json
    print(data)
    assert response.status_code == 200
    assert data["message"] == "Subtask created successfully"


def test_get_subtasks(client):
    with client.application.app_context():
        access_token = create_access_token(identity=2)
    
    response = client.get("/task/tasks/3/subtasks",headers={"Authorization":f"Bearer {access_token}"})
    data = response.json
    expected_data = [{'assigned_to': 3, 'assigned_username': 'testuser3', 'attachments': [], 'comments': [], 'created_by': 2, 'created_username': 'testuser2', 'deadline': '2024-11-30', 'description': 'Do the Unit Testing', 'duration': 10, 'estimated_hours': None, 'parent_id': 3, 'parent_title': 'Unit Testing', 'priority': 'Medium', 'start_date': '2024-11-20', 'status': 'In Progress', 'task_id': 4, 'title': 'Unit Testing', 'updated_by': None, 'working_hours': 0.0}]
    assert response.status_code == 200
    assert data == expected_data


def test_dashboard_form_data_failure(client):
    with client.application.app_context():
        access_token = create_access_token(identity=2)
    
    response = client.post("/task/dashboard/form_data",json={
        "project_id" : 1,
        "sprint_id" : 1,
        "title" : "Marketing",
        "description" : "Do the digital marketing for this!!",
        "priority" : "Low",
        "assigned_to" : "3",
        "created_by" : 2,
    },headers={"Authorization":f"Bearer {access_token}"})

    data = response.json
    assert response.status_code == 400
    assert data["message"] == "Missing required fields"


def test_form_data_failure(client):
    with client.application.app_context():
        access_token = create_access_token(identity=2)
    
    response = client.post("/task/form_data/1/1",json={
        "project_id" : 1,
        "sprint_id" : 1,
        "title" : "Marketing",
        "description" : "Do the digital marketing for this!!",
        "priority" : "Low",
        "estimated_hours" : "64",
        "assigned_to" : "3",
        "created_by" : 2,
    },headers={"Authorization":f"Bearer {access_token}"})

    data = response.json
    assert response.status_code == 400
    assert data["message"] == "Missing required fields"


def test_get_users_for_assigned_failure(client):
    with client.application.app_context():
        access_token = create_access_token(identity=3)

    response = client.get("/task/forms_assigned",headers={"Authorization":f"Bearer {access_token}"})
    data = response.json
    print(data)
    assert response.status_code == 404
    assert data["message"] == "No users found"


def test_update_task_status_failure(client):
    with client.application.app_context():
        access_token = create_access_token(identity=2)
    response = client.patch("/task/edit_status/5",json={
        "status":"In Progress"
    },headers={"Authorization":f"Bearer {access_token}"})
    data = response.json
    print(data)
    assert response.status_code == 404
    assert data["message"] == "Task not found"


def test_update_task_work_hours_failure(client):
    with client.application.app_context():
        access_token = create_access_token(identity=2)
    response = client.put("/task/edit_work_hours/5",json={
        "work_hours" : 56
    },headers={"Authorization":f"Bearer {access_token}"})
    data = response.json
    print(data)
    assert response.status_code == 404
    assert data["message"] == "Task not found"


def test_edit_task_failure(client):
    with client.application.app_context():
        access_token = create_access_token(identity=2)
    response = client.put("/task/edit_task/5",json={
        "project_id" : 1,
        "sprint_id" : 1,
        "title" : "Marketing",
        "description" : "Do the digital marketing for this!!",
        "priority" : "Low",
        "status" : "Pending",
        "start_date" : "2024-11-03",
        "deadline" : "2024-11-11",
        "estimated_hours" : "64",
        "assigned_to" : "3",
        "created_by" : 2,
    },headers={"Authorization":f"Bearer {access_token}"})
    data = response.json
    print(data)
    assert response.status_code == 404
    assert data["message"] == "Task not found!"


def test_search_tasks_failure(client):
    with client.application.app_context():
        access_token = create_access_token(identity=2)
    response = client.get("/task/search?title=",headers={"Authorization":f"Bearer {access_token}"})
    data = response.json
    print(data)
    assert response.status_code == 400
    assert data["message"] == "Query parameter 'title' is missing"


def teat_get_all_tasks_failure(client):
    with client.application.app_context():
        access_token = create_access_token(identity=2)
    response = client.get("/task/get_all_tasks",headers={"Authorization":f"Bearer {access_token}"})
    data = response.json
    assert response.status_code == 400
    assert data["message"] == "Task not found"


def test_tasks_failure(client):
    with client.application.app_context():
        db.session.query(Task).delete()
        db.session.commit()

        access_token = create_access_token(identity=2)
    
    response = client.get("/task/get_tasks",headers={"Authorization":f"Bearer {access_token}"})
    data = response.json
    print(data)
    assert response.status_code == 400
    assert data["message"] == "No Task Found!!"


def test_task_specific_failure(client):
    with client.application.app_context():
        Task.query.filter_by(task_id=1).delete()
        db.session.commit()

        access_token = create_access_token(identity=2)
    response = client.get("/task/task_specific/1",headers={"Authorization":f"Bearer {access_token}"})
    data = response.json
    print(data)
    assert response.status_code == 404
    assert data["message"] == "Task not found"


def test_attach_file_failure(client):
    with client.application.app_context():
        Task.query.filter_by(task_id=1).delete()
        db.session.commit()
        access_token = create_access_token(identity=2)

    with open("C:/Users/deepa/Pictures/car.jpeg", "rb") as file:
        data = {
            "task_id": "1",
            "status": "pending",
            "file": file
        }

        response = client.post("/task/attach_file", data=data, content_type='multipart/form-data', headers={
            "Authorization": f"Bearer {access_token}"
        })


    data = response.json
    print(data)
    assert response.status_code == 404
    assert data["message"] == "Task not found"


def test_download_attachment_failure(client):
    with client.application.app_context():
        Task.query.filter_by(task_id=1).delete()
        db.session.commit()
        access_token = create_access_token(identity=2)

    response = client.get("/task/download/1", headers={"Authorization": f"Bearer {access_token}"})
    data = response.json
    assert response.status_code == 404
    assert data["message"] == "Task not found"


def test_create_subtask_failure(client):
    with client.application.app_context():
        Task.query.filter_by(task_id=1).delete()
        db.session.commit()
        access_token = create_access_token(identity=2)

    response = client.post("/task/create_subtask",json={
        "project_id" : 1,
        "sprint_id" : 2,
        "title" : "Unit Testing",
        "description" : "Do the unit testing for this!!",
        "priority" : "Low",
        "status" : "Pending",
        "start_date" : "2024-11-03",
        "deadline" : "2024-11-11",
        "estimated_hours" : "64",
        "assigned_to" : "3",
        "created_by" : 2,
        "parent_task_id" : 1
    },headers={"Authorization":f"Bearer {access_token}"})

    data = response.json
    print(data)
    assert response.status_code == 404
    assert data["message"] == "Parent task not found or you don't have permission to create a subtask"


def test_get_subtasks_failure(client):
    with client.application.app_context():
        Task.query.filter_by(task_id=3).delete()
        db.session.commit()
        access_token = create_access_token(identity=2)
    
    response = client.get("/task/tasks/3/subtasks",headers={"Authorization":f"Bearer {access_token}"})
    data = response.json
    print(data)
    assert response.status_code == 404
    assert data["message"] == "Parent task not found or you don't have permission to view its subtasks"