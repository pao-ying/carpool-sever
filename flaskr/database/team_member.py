from flaskr import db
from .team import Team
from .user import User


class TeamMember(db.Model):
    team_id = db.Column(db.ForeignKey(Team.id), primary_key=True)
    user_id = db.Column(db.ForeignKey(User.id), primary_key=True)
    is_leader = db.Column(db.Boolean, nullable=False)
    team = db.relationship(Team, backref="team_member")
    user = db.relationship(User, backref="team_member")