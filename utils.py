from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from model.Register import Register
from functools import wraps

def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            current_user = get_jwt_identity()
            user = Register.query.filter_by(user_id=current_user).first()
            if user.role not in allowed_roles:
                return jsonify({"message": "Access forbidden: insufficient permissions"}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator
