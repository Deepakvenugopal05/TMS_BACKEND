from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime,timedelta

from model.db import db
from model.Register import Register
from model.Task import Task
from model.Project import Project
from model.Sprint import Sprint
from utils import role_required

sprint_route = Blueprint("sprint",__name__)

@sprint_route.route("/sprints/<int:project_id>", methods=["GET"])
@jwt_required()
def get_sprints_on_project(project_id):
    sprints = Sprint.query.filter_by(project_id=project_id).all()
    if not sprints:
        return jsonify(message="No sprints Found!!"), 400
    return jsonify({'sprints': [sprint.to_dict() for sprint in sprints]}), 200

@sprint_route.route("/get_all_sprints",methods=["GET"])
@jwt_required()
def get_all_sprints():
    all_sprints = Sprint.query.filter(Sprint.delete_yn == False).all()
    if not all_sprints:
        return jsonify(message="No sprints found!!"), 400
    return jsonify({"sprints": [sprint.to_dict() for sprint in all_sprints]
}),200

@sprint_route.route("/get_projects", methods=["GET"])
@jwt_required()
def get_all_projects():
    projects = db.session.query(Project.project_id, Project.title).all()

    if not projects:
        return (jsonify(message="No Projects with the sprints")),400

    project_list = [
        {
            "project_id": project.project_id,
            "project_name": project.title
        } for project in projects
    ]

    return jsonify({"projects": project_list}), 200

    

@sprint_route.route("/get_sprint_tasks/<int:sprint_id>", methods=["GET"])
@jwt_required()
def get_sprint_tasks(sprint_id):
    
    tasks_under_sprint = (
        db.session.query(Task, Register.username.label('assigned_to_username'))
        .join(Register, Task.assigned_to == Register.user_id)
        .filter(Task.sprint_id == sprint_id, Task.delete_yn == False)
        .all()
    )

    if not tasks_under_sprint:
        return jsonify(message="No tasks are under this Sprint"),400
    
    tasks_list = [
        {
            'task_id': task.Task.task_id,
            'title': task.Task.title,
            'description': task.Task.description,
            'priority': task.Task.priority,
            'status': task.Task.status,
            'start_date': task.Task.start_date.isoformat() if task.Task.start_date else None,
            'deadline': task.Task.deadline.isoformat() if task.Task.deadline else None,
            'assigned_to': task.Task.assigned_to,
            'assigned_to_username': task.assigned_to_username,
            'created_by': task.Task.created_by,
            'updated_by': task.Task.updated_by,
            'created_username': Register.query.filter_by(user_id=task.Task.created_by).first().username if task.Task.created_by else None,

        } for task in tasks_under_sprint
    ]
    
    return jsonify({'tasks': tasks_list}), 200

@sprint_route.route('/edit_sprint/<int:sprint_id>', methods=['PATCH'])
@jwt_required()
def edit_sprint(sprint_id):

    current_user_id = get_jwt_identity()
    user = Register.query.filter_by(user_id=current_user_id).first()

    if not user:
        return jsonify(message="User not found!"), 404

    sprint = Sprint.query.filter_by(sprint_id=sprint_id, delete_yn=False).first()

    if not sprint:
        return jsonify(message="sprint not found!"), 404

    # Get the updated sprint data from the request
    data = request.json
    print(f"{data},edit")
    # Update the sprint details
    sprint.sprint_name = data.get('title', sprint.title)
    startDate_str =  data.get('start_date')
    startDate_date = datetime.strptime(startDate_str, '%Y-%m-%d').date()
    sprint.start_date = startDate_date
    deadline_str = data.get('deadline')  
    deadline_date = datetime.strptime(deadline_str, '%Y-%m-%d').date()
    sprint.deadline = deadline_date
    
    sprint.updated_by = user.user_id

    # Commit the changes to the database
    db.session.commit()
    return jsonify(message="sprint updated successfully!"), 200


@sprint_route.route("/create_sprint/<int:project_id>", methods=["POST"])
@jwt_required()
@role_required('admin')
def create_sprint(project_id):
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    sprint_name = data.get('title')
    start_date = data.get('start_date')
    end_date = data.get('end_date')

    start_date_parsed = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date_parsed = datetime.strptime(end_date, '%Y-%m-%d').date()


    max_end_date = start_date_parsed + timedelta(weeks=2)
    if end_date_parsed > max_end_date:
        return jsonify(message="End date must not exceed 2 weeks from the start date"), 400

    new_sprint = Sprint(
        sprint_name=sprint_name,
        start_date=start_date_parsed,
        end_date=end_date_parsed,
        created_by=current_user_id,
        project_id=project_id
    )

    db.session.add(new_sprint)
    db.session.commit()
    
    return jsonify({'sprint_id': new_sprint.sprint_id,'project_id':new_sprint.project_id}), 201

@sprint_route.route("/current_sprint/<int:project_id>", methods=["GET"])
@jwt_required()
def get_current_sprint(project_id):
    current_date = datetime.now().date()
    print(current_date)
    
    current_sprint = (
        Sprint.query.filter(
            Sprint.project_id == project_id,
            Sprint.start_date <= current_date,
            Sprint.end_date >= current_date,
            Sprint.delete_yn == False
        )
        .order_by(Sprint.start_date.desc())
        .first()
    )
    # print(current_sprint)
    
    if not current_sprint:
        return jsonify(message="No current sprint found"), 404
    
    return jsonify(current_sprint.to_dict()), 200

@sprint_route.route('/delete_sprint/<int:sprint_id>',methods=['DELETE'])
@jwt_required()
def delete_sprint(sprint_id):
    sprint_delete = Sprint.query.filter_by(sprint_id=sprint_id,delete_yn=False).first()
    if not sprint_delete:
        return jsonify(message="There is no sprint in this id!!"), 400
    sprint_delete.delete_yn = True
    db.session.commit()
    return jsonify(message="Sprint is deleted!!!")


@sprint_route.route('/delete_sprint_permanent/<int:sprint_id>',methods=['DELETE'])
def delete(sprint_id):
    data = Sprint.query.get(sprint_id)
    db.session.delete(data)
    db.session.commit()
    return "commited!!"