import pytest
from model.Register import Register
from model.Task import Task
from model.Attachments import Attachment
from model.Comments import Comments
from model.Project import Project
from model.Project_comments import ProjectComments
from model.Sprint import Sprint
from model.db import db
from extensions import bcrypt
from run import create_app
from datetime import datetime

@pytest.fixture
def client():
    app = create_app("testing")

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Add a test user
            hashed_password = bcrypt.generate_password_hash("password123").decode('utf-8')
            users = [Register(
                username="testuser",
                email="testuser@example.com",
                password= hashed_password,
                role = "admin",
                profile_img = "test.jpg"
            ),Register(
                username="testuser2",
                email="testuser2@example.com",
                password= hashed_password,
                role = "manager",
                profile_img = "test_2.jpg"
            ),Register(
                username="testuser3",
                email="testuser3@example.com",
                password= hashed_password,
                role = "user",
                profile_img = "test_3.jpg",
                manager_id = 2
            )]
            
            tasks = [Task(
                title = "Hono js",
                description = "Do this in hono",
                priority = "Medium",
                status = "Pending",
                start_date=datetime.strptime("2024-11-18", "%Y-%m-%d").date(),
                deadline=datetime.strptime("2024-12-02", "%Y-%m-%d").date(), 
                created_by = 1 ,
                assigned_to = 2,
                sprint_id = 1,
            ),Task(
                title = "React",
                description = "Do this in React",
                priority = "High",
                status = "In Progress",
                start_date=datetime.strptime("2024-11-18", "%Y-%m-%d").date(),
                deadline=datetime.strptime("2024-12-02", "%Y-%m-%d").date(), 
                created_by = 2 ,
                assigned_to = 3,
                sprint_id = 1,
            ),Task(
                title = "Testing",
                description = "Do the Testing",
                priority = "High",
                status = "In Progress",
                start_date=datetime.strptime("2024-11-18", "%Y-%m-%d").date(),
                deadline=datetime.strptime("2024-12-02", "%Y-%m-%d").date(), 
                created_by = 2 ,
                assigned_to = 3,
                sprint_id = 2
            ),Task(
                title = "Unit Testing",
                description = "Do the Unit Testing",
                priority = "Medium",
                status = "In Progress",
                start_date=datetime.strptime("2024-11-20", "%Y-%m-%d").date(),
                deadline=datetime.strptime("2024-11-30", "%Y-%m-%d").date(), 
                created_by = 2 ,
                assigned_to = 3,
                sprint_id = 2,
                parent_id = 3
            )]

            attachments = [Attachment(
                task_id = 1,
                status = "Pending",
                file_name = "Dash_copy.png",
                img_hash = "e6693ba57c956e9045fcf1d0d075f7a7a220e3da0d611513217188ae3b63d34f",
                attachment = "static/uploads/files/Dash_copy.png",
                created_by = 2
            ),Attachment(
                task_id = 2,
                status = "In Progress",
                file_name = "Dash.png",
                img_hash = "e6693ba57c956e9045fcf1d0d075f7a7a220e3da0d611513217188ae3b63d34f",
                attachment = "static/uploads/files/Dash.png",
                created_by = 3
            )]

            comments = [Comments(
                content = "This is comment1",
                task_id = 1,
                created_by = 2
            ),Comments(
                content = "This is comment2",
                task_id = 2,
                created_by = 3
            ),Comments(
                content = "This is comment3",
                task_id = 1,
                created_by = 1
            )]

            project_comments = [ProjectComments(
                content = "This is project_1",
                project_id = 1,
                created_by = 1
            )]

            projects = [Project(
                title = "project-1",
                description = "This is project-1",
                status = "Pending",
                start_date = datetime.strptime("2024-11-01", "%Y-%m-%d").date(),
                end_date = datetime.strptime("2024-12-01", "%Y-%m-%d").date(),
                created_by = 1
            )]

            sprints = [Sprint(
                sprint_name = "project1-sprint1",
                start_date=datetime.strptime("2024-11-01", "%Y-%m-%d").date(),
                end_date=datetime.strptime("2024-11-14", "%Y-%m-%d").date(),
                project_id = 1,
                created_by = 1
            ),Sprint(
                sprint_name = "project1-sprint2",
                start_date=datetime.strptime("2024-11-14", "%Y-%m-%d").date(),
                end_date=datetime.strptime("2024-11-21", "%Y-%m-%d").date(),
                project_id = 1,
                created_by = 1
            )]
            db.session.bulk_save_objects(users + tasks + attachments + projects + comments + project_comments + sprints)
            db.session.commit()
            print("Tables Created!!!")
        yield client
        with app.app_context():
            db.drop_all()