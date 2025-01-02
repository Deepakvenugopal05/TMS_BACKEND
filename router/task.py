from flask import Blueprint, request, jsonify,send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime,timezone

from sqlalchemy import and_
from model.db import db
from model.Register import Register
from model.Project import Project
from model.Task import Task
from model.Sprint import Sprint
from utils import role_required
import os



task_route = Blueprint("task",__name__)

# Adding the task
@task_route.route('dashboard/form_data', methods=['POST'])
@jwt_required()
@role_required(['admin', 'manager'])
def dashboard_form_data():
    data = request.get_json()
    print(data)
    project_id = data.get('project_id')
    sprint_id = data.get('sprint_id')
    title = data.get('title')
    description = data.get('description')
    priority = data.get('priority')
    status = data.get('status')
    start_date = data.get('start_date')
    deadline = data.get('deadline')
    estimated_hours = data.get('estimated_hours')
    assigned_username = data.get('assigned_to')
    created_by = get_jwt_identity()

    if not all([title, description, priority, status, start_date, deadline, assigned_username]):
        print('error1')  
        return jsonify(message="Missing required fields"), 400

    try:
        start_date_alter = datetime.strptime(start_date,'%Y-%m-%d').date()
        deadline_date = datetime.strptime(deadline, '%Y-%m-%d').date()
    except ValueError:
        print('error2')
        return jsonify(message="Invalid date format. Use YYYY-MM-DD"), 400
    
    duration = (deadline_date - start_date_alter).days

    new_task = Task(
        title=title,
        description=description,
        priority=priority,
        status=status,
        start_date = start_date_alter,
        deadline=deadline_date,
        duration = duration,
        estimated_hours = estimated_hours,
        assigned_to=assigned_username,
        created_by=created_by,
        project_id = project_id,
        sprint_id = sprint_id
    )
    print(new_task.project_id)
    db.session.add(new_task)
    db.session.commit()

    return jsonify(message="Task added successfully"), 201


# Adding the task
@task_route.route('/form_data/<int:project_id>/<int:sprint_id>', methods=['POST'])
@jwt_required()
@role_required(['admin', 'manager'])
def form_data(project_id,sprint_id):
    data = request.get_json()
    print(f"{data},data:75")
    title = data.get('title')
    description = data.get('description')
    priority = data.get('priority')
    status = data.get('status')
    start_date = data.get('start_date')
    deadline = data.get('deadline')
    estimated_hours = data.get('estimated_hours')
    assigned_username = data.get('assigned_to')
    created_by = get_jwt_identity()

    print(f"{data},data:85")

    if not all([title, description, priority, status, start_date, deadline, assigned_username]):
        print('error1')  
        return jsonify(message="Missing required fields"), 400

    try:
        start_date_alter = datetime.strptime(start_date,'%Y-%m-%d').date()
        print(type(start_date_alter))
        deadline_date = datetime.strptime(deadline, '%Y-%m-%d').date()
    except ValueError:
        print('error2')
        return jsonify(message="Invalid date format. Use YYYY-MM-DD"), 400
    
    duration = (deadline_date - start_date_alter).days

    new_task = Task(
        title=title,
        description=description,
        priority=priority,
        status=status,
        start_date = start_date_alter,
        deadline=deadline_date,
        duration=duration,
        estimated_hours = estimated_hours,
        assigned_to=assigned_username,
        created_by=created_by,
        project_id = project_id,
        sprint_id = sprint_id
    )
    print('hello')
    db.session.add(new_task)
    db.session.commit()

    return jsonify(message="Task added successfully"), 201

@task_route.route('/forms_assigned', methods=['GET'])
@jwt_required()
def get_users_for_assigned():
    manager_id = get_jwt_identity()
    user = Register.query.filter_by(user_id=manager_id).first()

    if not user:
        return jsonify(message="User not found"), 404

    if user.role == 'manager':
        users = Register.query.filter_by(role='user').all()
        usernames = [u.username for u in users]
        return jsonify(usernames)

    elif user.role == 'admin':
        users_and_manager = Register.query.filter(
            (Register.role == 'user') | (Register.role == 'manager')
        ).all()
        usernames_and_managers = [u.username for u in users_and_manager]
        return jsonify(usernames_and_managers)

    return jsonify(message= "No users found"), 404
    

@task_route.route('/edit_status/<int:task_id>', methods=['PATCH'])
@jwt_required()
def update_task_status(task_id):
    current_user_id = get_jwt_identity()
    data = request.get_json()
    task = Task.query.filter_by(task_id=task_id).first()
    
    if not task:
        return jsonify(message= "Task not found"), 404
    
    # Check if the current user is allowed to update the task
    if task.created_by != current_user_id and task.assigned_to != current_user_id:
        return jsonify(message= "You do not have permission to update this task."), 403
    
    new_status = data.get("status")
    task.status = new_status

    if new_status == "Completed":
        task.calculate_work_hours()

    db.session.commit()
    return jsonify(message="Task updated successfully"), 200

@task_route.route('/edit_work_hours/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task_work_hours(task_id):
    current_user_id = get_jwt_identity()
    data = request.get_json()
    print(data)
    task = Task.query.filter_by(task_id=task_id).first()
    
    if not task:
        return jsonify(message= "Task not found"), 404
    
    # Check if the current user is allowed to update the task
    if task.created_by != current_user_id and task.assigned_to != current_user_id:
        return jsonify(message= "You do not have permission to update this task."), 403
    
    new_work_hours = data.get("work_hours")
    task.work_hours = new_work_hours

    db.session.commit()
    return jsonify(message="Task updated successfully"), 200

@task_route.route('/edit_task/<int:task_id>', methods=['PUT'])
@jwt_required()
def edit_task(task_id):

    current_user_id = get_jwt_identity()
    user = Register.query.filter_by(user_id=current_user_id).first()

    if not user:
        return jsonify(message="User not found!"), 404

    # Fetch the task by task_id
    task = Task.query.filter_by(task_id=task_id, delete_yn=False).first()

    if not task:
        return jsonify(message="Task not found!"), 404

    # Check if the user is the creator or an admin
    if task.created_by != user.user_id and user.role != 'admin':
        return jsonify(message="You are not authorized to edit this task!"), 403

    # Get the updated task data from the request
    data = request.json
    print(f"{data},edit")
    # Update the task details
    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.priority = data.get('priority', task.priority)
    task.status = data.get('status', task.status)
    startDate_str =  data.get('start_date')
    startDate_date = datetime.strptime(startDate_str, '%Y-%m-%d').date()
    task.start_date = startDate_date
    deadline_str = data.get('deadline')  
    deadline_date = datetime.strptime(deadline_str, '%Y-%m-%d').date()
    task.deadline = deadline_date
    task.estimated_hours = data.get('estimated_hours',task.estimated_hours)
    task.assigned_to = data.get('Assigned_to', task.assigned_to)
    task.updated_by = user.user_id

    # Commit the changes to the database
    db.session.commit()
    return jsonify(message="Task updated successfully!"), 200

@task_route.route('/delete_task/<int:task_id>',methods=['DELETE'])
@jwt_required()
@role_required(['admin','manager'])
def delete_task(task_id):
    task_delete = Task.query.filter_by(task_id=task_id,delete_yn=False).first()
    task_delete.delete_yn = True
    db.session.commit()
    return jsonify(message="task is deleted!!!"),200

# This is not going to use in frontend
@task_route.route('/change/<int:task_id>',methods=['POST'])
def change(task_id):
    data = Task.query.filter_by(task_id=task_id,delete_yn=False).first()
    if data:
        data.delete_yn = False
        db.session.commit()
        return "commited!!"

# This is not going to use in frontend
@task_route.route('/delete/<int:task_id>',methods=['DELETE'])
def delete(task_id):
    data = Task.query.get(task_id)
    db.session.delete(data)
    db.session.commit()
    return "commited!!"

@task_route.route('/search', methods=['GET'])
@jwt_required()
def search_tasks():
    current_user_id = get_jwt_identity()
    query = request.args.get('title')
    if not query:
        return jsonify(message="Query parameter 'title' is missing"), 400
    
    search_results = Task.query.filter(Task.title.ilike(f"%{query}%"), Task.delete_yn == False, Task.assigned_to or Task.created_by == current_user_id).all()
    
    if not search_results:
        return jsonify(message= "No tasks found matching the query"), 404
    
    results = [task.to_dict() for task in search_results]    
    return jsonify(results), 200

@task_route.route('/get_all_tasks', methods=['GET'])
@jwt_required()
def get_all_tasks():
    current_user_id = get_jwt_identity()
    
    assigned_to_user = db.aliased(Register, name='assigned_to_user')
    created_by_user = db.aliased(Register, name='created_by_user')
    
    tasks = (
        db.session.query(
            Task,
            assigned_to_user.username.label('assigned_to_username'), 
            created_by_user.username.label('created_by_username'),
            Sprint.sprint_name.label('sprint_name'),
            Project.title.label('project_title'),
            Project.project_id.label('project_id'),
            Sprint.sprint_id.label('sprint_id')
        )
        .join(assigned_to_user, Task.assigned_to == assigned_to_user.user_id)
        .join(created_by_user, Task.created_by == created_by_user.user_id)
        .outerjoin(Sprint, Task.sprint_id == Sprint.sprint_id)
        .outerjoin(Project, Task.project_id == Project.project_id)
        .filter((Task.assigned_to == current_user_id) | (Task.created_by == current_user_id), Task.delete_yn == False)
        .all()
    )

    if not tasks:
        return jsonify(message="Task not found!")

    response = {
        "tasks": [
            {
                **task.to_dict(),
                "project_name": project_title,
                "project_id": project_id,
                "sprint_name": sprint_name,
                "sprint_id": sprint_id,
                "assigned_to_username": assigned_to_username,
                "created_username": created_by_username
            } for task, assigned_to_username, created_by_username, sprint_name, project_title, project_id, sprint_id in tasks
        ]
    }
    
    return jsonify(response), 200
  

@task_route.route('/get_tasks', methods=['GET'])
@jwt_required()
def tasks():
    current_user_id = get_jwt_identity()
    user = Register.query.filter_by(user_id=current_user_id).first()
    if not user:
        return jsonify(message="No users found!"), 400
    
    # Get created tasks and join with Register, Project and Sprint table to get the username for created_by, assigned_to, project title, and sprint name
    created_tasks = (
        db.session.query(
            Task, 
            Register.username.label('created_by_username'), 
            Sprint.sprint_name.label('sprint_name'),
            Project.title.label('project_title'),
            Project.project_id.label('project_id'),
            Sprint.sprint_id.label('sprint_id')
        )
        .join(Register, Task.assigned_to == Register.user_id)
        .outerjoin(Sprint, Task.sprint_id == Sprint.sprint_id)
        .outerjoin(Project, Task.project_id == Project.project_id)
        .filter(Task.created_by == current_user_id, Task.delete_yn == False, Task.parent_id == None)
        .all()
    )
    
    # Get assigned tasks and join with Register and Project table to get the username of the creator and project title
    assigned_tasks = (
        db.session.query(
            Task, 
            Register.username.label('created_by_username'),
            Sprint.sprint_name.label('sprint_name'),
            Project.title.label('project_title'),
            Project.project_id.label('project_id'),
            Sprint.sprint_id.label('sprint_id')
        )
        .join(Register, Task.created_by == Register.user_id)
        .outerjoin(Sprint, Task.sprint_id == Sprint.sprint_id)
        .outerjoin(Project, Task.project_id == Project.project_id)
        .filter(and_(Task.assigned_to == current_user_id, Task.delete_yn == False, Task.parent_id == None))
        .all()
    )
    print(f"{created_tasks},created_tasks")
    print(f"{assigned_tasks},assigned_tasks")

    if not created_tasks and not assigned_tasks:
        return jsonify(message="No Task Found!!"), 400
    
    response = {
        "created_tasks": [
            {
                **task.to_dict(),
                "project_name": project_title,
                "project_id": project_id,
                "sprint_name": sprint_name,
                "sprint_id": sprint_id,
                "assigned_to_username": created_by_username,
                "created_username": user.username
            } for task, created_by_username, sprint_name, project_title, project_id, sprint_id in created_tasks
        ],
        "assigned_tasks": [
            {
                **task.to_dict(),
                "created_by_username": created_by_username,
                "assigned_username": user.username,
                "project_name": project_title,
                "project_id": project_id,
                "sprint_name": sprint_name,
                "sprint_id": sprint_id
            } for task, created_by_username, sprint_name, project_title, project_id, sprint_id in assigned_tasks
        ],
    }
    return jsonify(response), 200

@task_route.route('/task_specific/<int:task_id>', methods=['GET'])
@jwt_required()
def task_specific(task_id):
    ParentTask = db.aliased(Task)
    
    specific_task = (
        db.session.query(
            Task, 
            ParentTask.title.label('parent_title'),
            Sprint.sprint_name.label('sprint_name'),
            Register.username.label('assigned_to_username')
        )
        .outerjoin(ParentTask, Task.parent_id == ParentTask.task_id)
        .outerjoin(Sprint, Task.sprint_id == Sprint.sprint_id)
        .outerjoin(Register, Task.assigned_to == Register.user_id)
        .filter(Task.task_id == task_id, Task.delete_yn == False)
        .first()
    )
    
    if not specific_task:
        return jsonify(message="Task not found"), 404

    task, parent_title, sprint_name, assigned_to_username = specific_task
    task_dict = task.to_dict()
    task_dict['parent_title'] = parent_title
    task_dict['sprint_name'] = sprint_name
    task_dict['assigned_to_username'] = assigned_to_username

    return jsonify(task_dict), 200


# Adding attachement file in the tasks
@task_route.route('/attach_file', methods=['POST'])
@jwt_required()
def attach_file():
    print(request.form)
    print(request.files)
    if 'task_id' not in request.form or 'file' not in request.files:
        return jsonify(message="Task ID and file are required"), 400

    task_id = request.form['task_id']
    file = request.files['file']

    task = Task.query.filter_by(task_id=task_id).first()
    if not task:
        return jsonify(message="Task not found"), 404

    upload_directory = os.path.join('static','uploads', 'files')

    file_path = os.path.join(upload_directory, file.filename)
    file.save(file_path)

    task.attachment = file_path.replace('\\', '/')
    
    db.session.commit()

    return jsonify(message="File attached successfully"), 200


@task_route.route('/download/<int:task_id>', methods=['GET'])
@jwt_required()
def download_attachment(task_id):
    current_user_id = get_jwt_identity()

    task = Task.query.filter_by(task_id=task_id).first()
    
    if task:
        if task.created_by == current_user_id or task.assigned_to == current_user_id:
            file_path = os.path.join('uploads/files', task.attachment)
            if os.path.exists(file_path):
                return send_file(file_path, as_attachment=True)
            else:
                return jsonify(message="File not found"), 404
        else:
            return jsonify(message="Unauthorized"), 403
    else:
        return jsonify(message="Task not found"), 404

# SubTasks for tasks
@task_route.route('/create_subtask', methods=['POST'])
@jwt_required()
def create_subtask():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    print(data)

    parent_task_id = data.get('parent_task_id')
    title = data.get('title')
    description = data.get('description')
    priority = data.get('priority')
    status = data.get('status')
    startDate_str =  data.get('start_date')
    startDate_date = datetime.strptime(startDate_str, '%Y-%m-%d').date()
    start_date = startDate_date
    deadline_str = data.get('deadline')  
    deadline_date = datetime.strptime(deadline_str, '%Y-%m-%d').date()
    deadline = deadline_date
    estimated_hours = data.get('estimated_hours')
    assigned_username = data.get('assigned_to')

    duration = (deadline_date - startDate_date).days

    parent_task = Task.query.filter_by(task_id=parent_task_id, created_by=current_user_id, delete_yn=False).first()
    
    if not parent_task:
        return jsonify(message="Parent task not found or you don't have permission to create a subtask"), 404
    project_id = parent_task.project_id
    print(project_id)
    sprint_id = parent_task.sprint_id
    print(sprint_id)

    subtask = Task(
        title=title,
        description=description,
        priority=priority,
        status=status,
        start_date=start_date,
        deadline=deadline,
        duration = duration,
        estimated_hours = estimated_hours,
        created_at = datetime.now(timezone.utc),
        created_by=current_user_id,
        assigned_to=assigned_username,
        parent_id=parent_task_id,
        project_id = project_id,
        sprint_id = sprint_id
    )

    print(f"SUBTASK : {subtask}")

    db.session.add(subtask)
    db.session.commit()

    return jsonify(message="Subtask created successfully"),200

# GET the subtasks
@task_route.route('/tasks/<int:task_id>/subtasks', methods=['GET'])
@jwt_required()
def get_subtasks(task_id):
    current_user_id = get_jwt_identity()
    
    parent_task = Task.query.filter(
        (Task.task_id == task_id) & 
        (Task.delete_yn == False) & 
        ((Task.created_by == current_user_id) | (Task.assigned_to == current_user_id))
    ).first()
    
    if not parent_task:
        return jsonify(message="Parent task not found or you don't have permission to view its subtasks"), 404
    
    subtasks = Task.query.filter_by(parent_id=task_id, delete_yn=False).all()
    subtasks_dict = []
    
    for subtask in subtasks:
        assigned_user = Register.query.filter_by(user_id=subtask.assigned_to).first()
        created_user = Register.query.filter_by(user_id=subtask.created_by).first()
        parent_id = Task.query.filter_by(parent_id=subtask.parent_id).first()
        subtask_dict = subtask.to_dict()
        subtask_dict["parent_title"] = parent_id.title if parent_id else None
        subtask_dict["assigned_username"] = assigned_user.username if assigned_user else None
        subtask_dict["created_username"] = created_user.username if created_user else None
        
        # Calculate duration
        if subtask.start_date and subtask.deadline:
            duration = (subtask.deadline - subtask.start_date).days
        else:
            duration = None
        subtask_dict["duration"] = duration
        
        subtasks_dict.append(subtask_dict)
    
    print(subtasks_dict)
    return jsonify(subtasks_dict), 200


