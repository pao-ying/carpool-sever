from flaskr import db
from ..database import User, Notice, Team
from flask import request, Blueprint


notice = Blueprint('notice', __name__, url_prefix='/notice')


# @notice.route('')