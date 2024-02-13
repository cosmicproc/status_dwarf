from flask import Flask
from flask_migrate import Migrate
from werkzeug.exceptions import HTTPException

from status_dwarf.commands import commands_bp
from status_dwarf.models import db
from status_dwarf.monitor import scheduler, monitor_task
from status_dwarf.utils import _
from status_dwarf.views import views_bp, error_handler


def create_app(no_db=False, no_scheduler=False):
    app = Flask(__name__)
    app.config.from_pyfile("config.py")

    app.register_blueprint(views_bp)
    app.register_blueprint(commands_bp)

    app.register_error_handler(HTTPException, error_handler)

    app.jinja_env.globals.update(_=_)
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    if not no_db:
        db.init_app(app)

        with app.app_context():
            db.create_all()
        Migrate(app, db)

    if not no_scheduler:
        scheduler.init_app(app)
        scheduler.start()
        scheduler.add_job("1", monitor_task, trigger="interval",
                          seconds=app.config["INTERVAL_SECONDS"])

    return app
