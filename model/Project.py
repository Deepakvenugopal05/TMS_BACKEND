from model.db import db
from model.Register import Register
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

class Project(db.Model):
    project_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    description = db.Column(db.Text)
    status = db.Column(db.Enum('Pending', 'Not Started', 'In Progress', 'Completed', name='status_enum'))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    created_by = db.Column(db.Integer, db.ForeignKey('register.user_id'))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    updated_by = db.Column(db.Integer, db.ForeignKey('register.user_id'))
    delete_yn = db.Column(db.Boolean, default=False)

    # Relationships
    sprints = relationship('Sprint', back_populates='project')
    tasks = relationship('Task', back_populates='project')
    comments = relationship('ProjectComments', back_populates='project')

    def to_dict(self):
        duration = None
        if self.start_date and self.end_date:
            duration = (self.end_date - self.start_date).days

        created_user = Register.query.filter_by(user_id=self.created_by).first()
        updated_user = Register.query.filter_by(user_id=self.updated_by).first()

        total_tasks = len(self.tasks)
        completed_tasks = len([task for task in self.tasks if task.status == 'Completed'])

        return {
            'project_id': self.project_id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat(),
            'duration': duration,
            'created_by': created_user.username if created_user else None,
            'updated_by': updated_user.username if updated_user else None,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'comments': [{'comment_id': comment.project_comment_id, 'content': comment.content} for comment in self.comments]
        }
