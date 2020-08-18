from flaskr import db
from .team import Team
from datetime import datetime

class Notice(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    team_id = db.Column(db.ForeignKey(Team.id), primary_key=True, nullable=False)
    # 修改 0 时间， 1 地址， 2 需求人数， 3 联系群号， 4 备注， 5 加入， 6 退出
    type = db.Column(db.Integer, nullable=False)
    # 有关对象的微信头像
    img_url = db.Column(db.String(256), nullable=False)
    team = db.relationship(Team, backref="notices")
    create_time = db.Column(db.DateTime, default=datetime.now())