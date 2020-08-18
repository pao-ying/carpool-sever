from flaskr import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), nullable=False)
    sex = db.Column(db.String(1), nullable=False)
    is_notice = db.Column(db.Boolean, default=False)
    img_url = db.Column(db.String(256), nullable=True)