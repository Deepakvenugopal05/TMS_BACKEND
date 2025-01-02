from model.db import db
from datetime import datetime, timezone

class Comments(db.Model):
    comment_id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    task_id = db.Column(db.Integer, db.ForeignKey('task.task_id', name='fk_comments_task_id'))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    created_by = db.Column(db.Integer, db.ForeignKey('register.user_id'))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    updated_by = db.Column(db.Integer, db.ForeignKey('register.user_id'))
    delete_yn = db.Column(db.Boolean, default=False)
    
    task = db.relationship('Task', back_populates='comments')