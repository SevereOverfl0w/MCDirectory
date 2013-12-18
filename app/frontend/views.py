from flask import Blueprint, render_template, g, flash, request, url_for
from flask.ext.login import current_user
from ..directory.forms import SearchForm

frontend = Blueprint('frontend', __name__)

@frontend.route('/')
def index():
    return render_template('frontend/index.html', form=SearchForm())

@frontend.before_app_request
def globals():
    g.sitename = "MCDirectory"
    g.user = current_user

from datetime import datetime

@frontend.app_template_filter()
def timesince(dt, default="just now"):
    """
    Returns string representing "time since" e.g.
    3 days ago, 5 hours ago etc.
    """
    now = datetime.utcnow()
    diff = now - dt
    periods = (
                (diff.days / 365, "year", "years"),
                (diff.days / 30, "month", "months"),
                (diff.days / 7, "week", "weeks"),
                (diff.days, "day", "days"),
                (diff.seconds / 3600, "hour", "hours"),
                (diff.seconds / 60, "minute", "minutes"),
                (diff.seconds, "second", "seconds"),
              )
    for period, singular, plural in periods:
        if period:
            return "%d %s ago" % (period, singular if period == 1 else plural)
    return default


@frontend.app_context_processor
def injections():
    def url_for_page(page, param='p'):
        args = request.args.to_dict()
        args[param] = page
        return url_for(request.endpoint, **args)

    return dict(url_for_page=url_for_page)
