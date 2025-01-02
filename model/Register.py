from model.db import db
from datetime import datetime, timezone

# created_on = Column(DateTime, default=lambda: datetime.now(timezone.utc))  # Correct approach

class Register(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    profile_img = db.Column(db.Text)
    password = db.Column(db.Text)
    role = db.Column(db.String(30))
    manager_id = db.Column(db.Integer, db.ForeignKey('register.user_id'))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    delete_yn = db.Column(db.Boolean, default=False)