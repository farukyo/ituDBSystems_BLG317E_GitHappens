from flask import Blueprint
from admin import routes  # noqa: F401

admin_bp = Blueprint(
    "admin", __name__, url_prefix="/admin", template_folder="../templates/admin"
)
