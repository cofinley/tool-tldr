from datetime import datetime

from . import main
from ..models import Permission


@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)


@main.app_template_filter("timesince")
def timesince(dt, default="Just now"):
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
        if period >= 1:
            return "%d %s ago" % (period, singular if int(period) == 1 else plural)

    return default
