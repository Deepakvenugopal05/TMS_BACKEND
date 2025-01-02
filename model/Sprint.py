from model.db import db
from model.Register import Register
from model.Project import Project
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

class Sprint(db.Model):
    __tablename__ = 'sprint'
    sprint_id = db.Column(db.Integer, primary_key=True)
    sprint_name = db.Column(db.String(70))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    created_by = db.Column(db.Integer, db.ForeignKey('register.user_id'))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    updated_by = db.Column(db.Integer, db.ForeignKey('register.user_id'))
    delete_yn = db.Column(db.Boolean, default=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.project_id'))
    
    # Relationships
    tasks = relationship('Task', back_populates='sprint')
    project = relationship('Project', back_populates='sprints')

    def to_dict(self):
        created_user = Register.query.filter_by(user_id=self.created_by).first()
        project_name = Project.query.filter_by(project_id = self.project_id).first()


        return {
            'sprint_id': self.sprint_id,
            'sprint_name': self.sprint_name,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'delete_yn': self.delete_yn,
            'project_id': self.project_id,
            'project_name': self.project.title if project_name else None,
            'created_username' : created_user.username if created_user else None
        }