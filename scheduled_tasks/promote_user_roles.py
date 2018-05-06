import os
from datetime import datetime

from sqlalchemy_continuum import version_class

from app import db, models, create_app, utils


def check_promotion_eligibility(user_since_date, days_required, total_edits, edits_required):
    satisfies_date_requirement = utils.is_over_x_hours_ago(t=user_since_date, hours=days_required * 24)
    satisfies_edit_requirement = total_edits >= edits_required
    return satisfies_date_requirement and satisfies_edit_requirement


def promote_roles(before, after, days_required, edits_required):
    print("Promoting {} users to {} status after {} days and {} edits.".format(before, after, days_required,
                                                                               edits_required))
    before_role_id = models.Role.query.filter_by(name=before).first().id
    after_role_id = models.Role.query.filter_by(name=after).first().id
    users = models.User.query.filter_by(role_id=before_role_id)
    for u in users:
        tool_edits_count = version_class(models.Tool).query.filter_by(edit_author=u.id).count()
        category_edits_count = version_class(models.Category).query.filter_by(edit_author=u.id).count()
        total_edits = tool_edits_count + category_edits_count

        if check_promotion_eligibility(u.user_since, days_required, total_edits, edits_required):
            print("\tPromoting", u.username,
                  "(member for {} days with {} edits)".format((datetime.utcnow() - u.user_since).days, total_edits))
            u.role_id = after_role_id
            db.session.add(u)
            db.session.commit()


if __name__ == "__main__":
    config = os.getenv('FLASK_CONFIG') or "default"
    print("Config:", config)
    blueprint = create_app(config)
    ctx = blueprint.test_request_context()
    ctx.push()

    # Promoting user -> member only
    u2m_days = blueprint.config["USER_TO_MEMBER_DAYS"]
    u2m_edits = blueprint.config["USER_TO_MEMBER_EDITS"]
    promote_roles("User", "Member", u2m_days, u2m_edits)

    # Promoting member to time traveler only
    m2t_days = blueprint.config["MEMBER_TO_TIME_TRAVELER_DAYS"]
    m2t_edits = blueprint.config["MEMBER_TO_TIME_TRAVELER_EDITS"]
    promote_roles("Member", "Time Traveler", m2t_days, m2t_edits)
