from model.db import db
from datetime import datetime, timezone


class Attachment(db.Model):
    attachment_id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.task_id', name='fk_attachment_task_id'))
    status = db.Column(db.Enum('Pending', 'Not Started', 'In Progress', 'Completed', name='fk_status_enum'))
    file_name = db.Column(db.String(120))
    img_hash = db.Column(db.Text)
    attachment = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    created_by = db.Column(db.Integer, db.ForeignKey('register.user_id'))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    updated_by = db.Column(db.Integer, db.ForeignKey('register.user_id'))
    delete_yn = db.Column(db.Boolean, default=False)

    task = db.relationship('Task', back_populates='attachments')

    def to_dict(self):
        return {
            "attachment_id" : self.attachment_id,
            "task_id" : self.task_id,
            "file_name": self.file_name,
            "status" : self.status,
            "attachment" : self.attachment,
            "image_hash" : self.img_hash
        }