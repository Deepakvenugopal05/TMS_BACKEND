from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from model.db import db
from model.Register import Register
from model.Task import Task
from model.Project import Project
from utils import role_required

project_route = Blueprint("project",__name__)

# Adding a project
@project_route.route("/project_data",methods=["POST"])
@jwt_required()
@role_required('admin')
def project_data():
    data = request.get_json()

    title = data.get('title')
    description = data.get('description')
    status = data.get('status')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    created_by = get_jwt_identity()

    if not all([title, description, status, start_date, end_date]):
        print('error1')  
        return jsonify({"error": "Missing required fields"}), 400

    try:
        start_date_alter = datetime.strptime(start_date,'%Y-%m-%d').date()
        end_date_alter = datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        print('error2')
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    new_project = Project(
        title=title,
        description=description,
        status=status,
        start_date = start_date_alter,
        end_date=end_date_alter,
        created_by=created_by
    )
    db.session.add(new_project)
    db.session.commit()

    return jsonify({"project_id":new_project.project_id}), 201

# Get projects
@project_route.route('/projects', methods=['GET'])
@jwt_required()
def get_projects():
    projects = Project.query.all()
    
    if not projects:
        return jsonify({"error": "No projects found"}), 404
    
    project_list = [{"project_id": project.project_id, "title": project.title} for project in projects]
    
    return jsonify({"projects": project_list}), 200

# Get all projects
@project_route.route("/get_all_project",methods=["GET"])
@jwt_required()
def get_all_project():
    data = Project.query.all()

    if not data:
        return jsonify(error="No Project is found!!"),404

    projects = [project.to_dict() for project in data]

    return jsonify(projects),200

# Edit project status
@project_route.route('/edit_project_status/<int:project_id>', methods=['PUT'])
@jwt_required()
def update_project_status(project_id):
    current_user_id = get_jwt_identity()
    data = request.get_json()

    project = Project.query.filter_by(project_id=project_id).first()
    
    if not project:
        return jsonify({"message": "Project not found"}), 404
    
    # Check if the current user is allowed to update the project
    if project.created_by != current_user_id:
        return jsonify({"message": "You do not have permission to update this project."}), 403
    
    new_status = data.get("status")
    project.status = new_status

    db.session.commit()
    return jsonify({"message": "Project updated successfully"}), 200


@project_route.route("/update_project_data/<int:project_id>",methods=["PATCH"])
@jwt_required()
@role_required('admin')
def edit_project_data(project_id):
    current_user_id = get_jwt_identity()
    user = Register.query.filter_by(user_id=current_user_id).first()

    if not user:
        return jsonify(error="User not found!"), 404

    project = Project.query.filter_by(project_id=project_id, delete_yn=False).first()

    if not project:
        return jsonify(message="Project not found!"), 404
    
    # Get the updated project data from the request
    data = request.json

    # Update the project details
    project.title = data.get('title', project.title)
    project.description = data.get('description', project.description)
    project.status = data.get('status', project.status)
    startDate_str =  data.get('start_date')
    startDate_date = datetime.strptime(startDate_str, '%Y-%m-%d').date()
    project.start_date = startDate_date
    end_date_str = data.get('end_date')  
    end_date_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    project.end_date = end_date_date
    project.updated_by = user.user_id

    # Commit the changes to the database
    db.session.commit()
    return jsonify(message="project updated successfully!"), 200

@project_route.route("/delete_project/<int:project_id>",methods=['DELETE'])
@jwt_required()
@role_required('admin')
def delete_project(project_id):
    data = Project.query.filter_by(project_id=project_id,delete_yn=False).first()
    if not data:
        return jsonify(message="Given project data is not found!!"), 404
    data.delete_yn = True
    db.session.commit()
    return jsonify(message="The given project is deleted!!"), 200


@project_route.route('/dashboard/summary', methods=['GET'])
@jwt_required()
@role_required(['admin', 'manager'])
def get_dashboard_summary():
    current_user_id = get_jwt_identity()

    current_user = db.session.query(Register).filter_by(user_id=current_user_id).first()
    user_role = current_user.role
    if user_role == 'manager':
        print('inside')
        total_projects = db.session.query(Project).count()
        print(total_projects)
        completed_projects = db.session.query(Project).filter_by(status='Completed').count()
        print(completed_projects)
        created_tasks = db.session.query(Task).filter_by(created_by=current_user_id).count()
        print(created_tasks)
        created_completed_tasks = db.session.query(Task).filter_by(created_by=current_user_id,status='Completed').count()
        print(created_completed_tasks)
        summary = {
        'total_projects': total_projects,
        'completed_projects': completed_projects,
        'created_tasks': created_tasks,
        'created_completed_tasks': created_completed_tasks
        }
        return jsonify(summary), 200
    
    total_projects = db.session.query(Project).count()
    completed_projects = db.session.query(Project).filter_by(status='Completed').count()
    
    total_tasks = db.session.query(Task).filter_by(created_by=current_user_id).count()
    completed_tasks = db.session.query(Task).filter_by(created_by=current_user_id,status='Completed').count()
    
    summary = {
        'total_projects': total_projects,
        'completed_projects': completed_projects,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks
    }
    
    return jsonify(summary), 200

@project_route.route('/dashboard/user_summary', methods=['GET'])
@jwt_required()
def get_user_dashboard_summary():
    current_user_id = get_jwt_identity()

    current_user = db.session.query(Register).filter_by(user_id=current_user_id).first()
    username = current_user.username
    
    total_tasks_created = db.session.query(Task).filter_by(created_by=current_user_id).count()
    completed_tasks_created = db.session.query(Task).filter_by(created_by=current_user_id, status='Completed').count()
    
    total_tasks_assigned = db.session.query(Task).filter_by(assigned_to=current_user_id).count()
    completed_tasks_assigned = db.session.query(Task).filter_by(assigned_to=current_user_id, status='Completed').count()
    
    summary = {
        'user_name' : username,
        'total_tasks_created': total_tasks_created,
        'completed_tasks_created': completed_tasks_created,
        'total_tasks_assigned': total_tasks_assigned,
        'completed_tasks_assigned': completed_tasks_assigned
    }
    
    return jsonify(summary), 200

