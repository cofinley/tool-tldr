import os
from datetime import datetime

from sqlalchemy_continuum import version_class

from app import db, models, create_app, utils


def check_promotion_eligibility(member_since_date, days_required, total_edits, edits_required):
    satisfies_date_requirement = utils.is_over_x_hours_ago(t=member_since_date, hours=days_required * 24)
    satisfies_edit_requirement = total_edits >= edits_required
    return satisfies_date_requirement and satisfies_edit_requirement


def promote_roles(before, after, days_required, edits_required):
    print("Promoting {} users to {} status after {} days and {} edits.".format(before, after, days_required,
                                                                               edits_required))
    before_role_id = models.Role.query.filter_by(name=before).first().id
    after_role_id = models.Role.query.filter_by(name=after).first().id
    registered_users = models.User.query.filter_by(role_id=before_role_id)
    for u in registered_users:
        tool_edits_count = version_class(models.Tool).query.filter_by(edit_author=u.id).count()
        category_edits_count = version_class(models.Category).query.filter_by(edit_author=u.id).count()
        total_edits = tool_edits_count + category_edits_count

        if check_promotion_eligibility(u.member_since, days_required, total_edits, edits_required):
            print("\tPromoting", u.username,
                  "(member for {} days with {} edits)".format((datetime.utcnow() - u.member_since).days, total_edits))
            u.role_id = after_role_id
            db.session.add(u)
            db.session.commit()


if __name__ == "__main__":
    config = os.getenv('FLASK_CONFIG') or "default"
    print("Config:", config)
    blueprint = create_app(config)
    ctx = blueprint.test_request_context()
    ctx.push()

    # Promoting registered -> confirmed only
    r2c_days = blueprint.config["REGISTERED_TO_CONFIRMED_DAYS"]
    r2c_edits = blueprint.config["REGISTERED_TO_CONFIRMED_EDITS"]
    promote_roles("Registered", "Confirmed", r2c_days, r2c_edits)

    # Promoting confirmed to time traveler only
    c2t_days = blueprint.config["CONFIRMED_TO_TIME_TRAVELER_DAYS"]
    c2t_edits = blueprint.config["CONFIRMED_TO_TIME_TRAVELER_EDITS"]
    promote_roles("Confirmed", "Time Traveler", c2t_days, c2t_edits)
