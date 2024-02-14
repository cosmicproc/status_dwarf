import json
from pathlib import Path

from flask import Flask
from flask_migrate import Migrate  # type: ignore[import-untyped]

from status_dwarf.commands import commands
from status_dwarf.models import db
from status_dwarf.monitor import scheduler, monitor_task
from status_dwarf.utils import _
from status_dwarf.views import views

BASE_DIR = Path(__file__).resolve().parent


def create_app(no_db=False, no_scheduler=False):
    app = Flask(__name__)
    config_file = "config/config.json" if (BASE_DIR / Path(
        "config/config.json")).is_file() else "config/config_base.json"
    app.config.from_file(config_file, load=json.load)

    app.register_blueprint(views)
    app.register_blueprint(commands)

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
