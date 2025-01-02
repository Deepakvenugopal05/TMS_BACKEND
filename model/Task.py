from model.db import db
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

class Task(db.Model):
    __tablename__ = 'task'
    task_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    description = db.Column(db.Text)
    priority = db.Column(db.Enum('Low', 'Medium', 'High', name='priority_enum'))
    status = db.Column(db.Enum('Pending', 'Not Started', 'In Progress', 'Completed', name='status_enum'))
    start_date = db.Column(db.Date)
    deadline = db.Column(db.Date)
    duration = db.Column(db.Integer)
    estimated_hours = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    created_by = db.Column(db.Integer, db.ForeignKey('register.user_id'))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    updated_by = db.Column(db.Integer, db.ForeignKey('register.user_id'))
    delete_yn = db.Column(db.Boolean, default=False)
    attachment = db.Column(db.String(120))  # For proof Attachment
    assigned_to = db.Column(db.Integer, db.ForeignKey('register.user_id'))
    project_id = db.Column(db.Integer, db.ForeignKey('project.project_id'))
    sprint_id = db.Column(db.Integer, db.ForeignKey('sprint.sprint_id'))
    parent_id = db.Column(db.Integer, db.ForeignKey('task.task_id'))
    work_hours = db.Column(db.Float, default=0.0)
    
    # Relationships
    project = relationship('Project', back_populates='tasks')
    sprint = relationship('Sprint', back_populates='tasks')
    parent = relationship('Task', remote_side=[task_id], backref=db.backref('children', cascade="all, delete-orphan"))
    comments = relationship('Comments', back_populates='task')
    attachments = relationship('Attachment', back_populates='task')




    def calculate_work_hours(self):
        if self.start_date and self.deadline:
            duration = (self.deadline - self.start_date).total_seconds() / 3600
            self.work_hours = duration
        return self.work_hours

    def to_dict(self):
        duration = None
        if self.start_date and self.deadline:
            duration = (self.deadline - self.start_date).days

        return {
            
            'task_id': self.task_id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'status': self.status,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'deadline': self.deadline.isoformat(),
            'duration': duration,
            'estimated_hours' : self.estimated_hours,
            'working_hours':self.work_hours,
            'assigned_to': self.assigned_to,
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'parent_id': self.parent_id,
            'attachments': [attachment.to_dict() for attachment in self.attachments],
            'comments': [{'comment_id': comment.comment_id, 'content': comment.content} for comment in self.comments]
        }
