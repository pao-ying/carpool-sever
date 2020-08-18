from flask import Flask
import click
from flask_sqlalchemy import SQLAlchemy
from flask.cli import with_appcontext

db = SQLAlchemy()



def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI='mysql+mysqlconnector://root:000712@localhost/carpool',
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )
    db.init_app(app)
    app.cli.add_command(init_db_command)

    from flaskr.blueprint import team, user
    app.register_blueprint(team)
    app.register_blueprint(user)

    @app.route('/')
    def hello():
        return 'hello world'

    return app


def init_db():
    db.drop_all()
    db.create_all()


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


app = create_app()
if __name__ == '__main__':
    app.run()