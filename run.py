from flask import Flask
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_talisman import Talisman
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

# Import extensions and utilities
from model.db import db
from extensions import bcrypt
from email_scheduler import mail, send_email

# Import configuration
from config import DevelopmentConfig, TestingConfig

# Import blueprints
from router.task import task_route
from router.auth import auth_route
from router.comments import comment_route
from router.profile import profile_route
from router.user import user_route
from router.project import project_route
from router.project_comments import project_comments_route
from router.sprint import sprint_route
from router.attachment import attachment_route

# Import models
from model.Task import Task
from model.Register import Register


def create_app(config_name=None):
    """
    Application Factory to create and configure the Flask app.
    """
    app = Flask(__name__)

    # Load configuration
    if config_name == "testing":
        app.config.from_object(TestingConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    # Initialize extensions
    db.init_app(app)
    Migrate(app, db)
    JWTManager(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    Talisman(app)

    # Register blueprints
    app.register_blueprint(task_route, url_prefix="/task")
    app.register_blueprint(auth_route, url_prefix="/auth")
    app.register_blueprint(user_route, url_prefix="/user")
    app.register_blueprint(profile_route, url_prefix="/profile")
    app.register_blueprint(comment_route, url_prefix="/comments")
    app.register_blueprint(project_route, url_prefix="/project")
    app.register_blueprint(project_comments_route, url_prefix="/ProjectComments")
    app.register_blueprint(sprint_route, url_prefix="/sprint")
    app.register_blueprint(attachment_route, url_prefix="/attachment")

    # Enable CORS for React Frontend
    CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

    return app


# Background task to check for tasks due tomorrow and send reminders.
def check_due_tasks():
    try:
        app = create_app()
        with app.app_context():
            tomorrow = datetime.now() + timedelta(days=1)
            tasks_due_tomorrow = Task.query.filter(
                db.func.date(Task.deadline) == tomorrow.date()
            ).all()

            for task in tasks_due_tomorrow:
                assigned_user = Register.query.filter_by(user_id=task.assigned_to).first()

                if assigned_user:
                    subject = f"Reminder: Task '{task.title}' is due tomorrow!"
                    body = (
                        f"Hi {assigned_user.username},\n\n"
                        f"Your task '{task.title}' is due tomorrow. "
                        f"Please ensure it's completed.\n\nBest regards,\nYour Task Management System"
                    )
                    send_email(subject, assigned_user.email, body)

    except Exception as e:
        print(f"Error in check_due_tasks: {e}")


# Setup the background scheduler for periodic tasks.
def setup_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=check_due_tasks, trigger="interval", days=1)
    scheduler.start()
    return scheduler


if __name__ == "__main__":
    # Create the app and setup the scheduler
    app = create_app()
    scheduler = setup_scheduler()

    # Initialize the database and run the application
    with app.app_context():
        db.create_all()

    # Run the application
    app.run(debug=True, port=5000)
