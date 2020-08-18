from flaskr import db
from datetime import datetime

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_address = db.Column(db.String(10), nullable=False)
    end_address = db.Column(db.String(10), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    numbers = db.Column(db.Integer, nullable=False)
    now_numbers = db.Column(db.Integer, default=1)
    female = db.Column(db.Integer, default=0)
    male = db.Column(db.Integer, default=0)
    contact = db.Column(db.Integer, nullable=False)
    remark = db.Column(db.String(25), default="快来加入我们吧！")
    create_time = db.Column(db.DateTime, default=datetime.now())
