from datetime import timezone, datetime

import werkzeug
from flask import Blueprint, render_template, abort, Response
from flask import current_app

from status_dwarf.models import Target, session, Status
from status_dwarf.utils import div_ceil, _

views = Blueprint("views", __name__)


@views.route("/", defaults={"page": 1})
@views.route("/<int:page>")
def index(page: int) -> str:
    all_targets = session.query(Target).all()
    page_size = current_app.config["PAGE_SIZE"]
    page_count = div_ceil(len(all_targets), page_size)
    if page > page_count and page != 1:
        return abort(404)
    context = {
        "targets": all_targets[(page - 1) * page_size: page * page_size],
        "next_page": page + 1 if page_count > page else None,
        "prev_page": page - 1 if page > 1 else None,
        "show_positive_message": not Target.any_target_down(),
        "Status": Status,
    }
    return render_template("index.html", **context)


@views.route("/atom")
@views.route("/atom.xml")
def atom() -> Response:
    if not current_app.config["ATOM_ENABLED"]:
        return abort(404)
    return Response(render_template("atom.xml", targets=session.query(Target).all(),
                                    now=datetime.now(timezone.utc).isoformat()),
                    mimetype='text/xml')


@views.errorhandler(404)
@views.errorhandler(500)
def error_handler(e: werkzeug.exceptions.NotFound) -> tuple[str, int]:
    error_descriptions = {
        500: _("An error has occurred. Please try again later."),
        404: _("The requested URL was not found on the server.")
    }
    e.description = error_descriptions.get(e.code, e.description)
    return render_template("error.html", exception=e), e.code
