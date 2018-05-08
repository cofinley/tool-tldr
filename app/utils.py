import html
from datetime import timedelta, datetime
from difflib import ndiff
from typing import List
from urllib.parse import urlsplit

from sqlalchemy_continuum import version_class, versioning_manager

from app import models, db


def is_at_or_below_category(chosen_category_id, current_category_id):
    """
    Checks to see if the current_category_id is in the upward path of the chosen_category_id
    If so, chosen_category_id is below current_category_id and user trying to move page down (illegal)
    This is used in page move validation.
    Moving can only go up, not down. Otherwise circular dependencies.
    Chosen should be above current!

    :param chosen_category_id: parent category picked in form explore tree
    :param current_category_id: current category id of page
    :return: bool if the chosen_id is the same or below the current_id
    """

    current_category = models.Category.query.get(current_category_id)
    chosen_category = models.Category.query.get(chosen_category_id)
    return current_category in build_bottom_up_tree(chosen_category)


def build_bottom_up_tree(parent_category):
    """
    Used for tool page hierarchy tree.

    :param parent_category: end parent_category
    :return List of categories going up
    """
    parent_list = []

    while parent_category is not None:
        parent_list.insert(0, parent_category)
        parent_category = parent_category.parent

    return parent_list


def get_hostname(url):
    name = urlsplit(url).netloc or urlsplit(url).hostname
    hostname = name.replace("www.", "")
    return hostname


def gen_diff_html(old_data, new_data):
    # Generate word-by-word diff if spaces, letter-by-letter if not

    # Diff is shown with html rendered with 'safe' filter in jinja template
    # Make sure to escape the content beforehand
    old_data = escape_html(old_data)
    new_data = escape_html(new_data)
    has_spaces = " " in old_data and " " in new_data
    if has_spaces:
        diff1 = list(ndiff(old_data.split(" "), new_data.split(" ")))
    else:
        diff1 = list(ndiff(old_data, new_data))
    # Create copy for other side
    diff2 = diff1.copy()

    # On left side, hide new additions
    for index, value in enumerate(diff1):
        if value.startswith("-"):
            diff1[index] = "<span class='diff-danger'>{}</span>".format(escape_html(value.replace("- ", "")))
        elif value.startswith("+"):
            diff1[index] = ""
        elif value.startswith("?"):
            diff1[index] = ""
        else:
            diff1[index] = value.replace(" ", "")

    # Join back results differently for fields that contain spaces
    if has_spaces:
        left = " ".join(diff1)
    else:
        left = "".join(diff1)

    # On right side, hide removals
    for index, value in enumerate(diff2):
        if value.startswith("-"):
            diff2[index] = ""
        elif value.startswith("+"):
            diff2[index] = "<span class='diff-success'>{}</span>".format(escape_html(value.replace("+ ", "")))
        elif value.startswith("?"):
            diff2[index] = ""
        else:
            diff2[index] = value.replace(" ", "")

    if has_spaces:
        right = " ".join(diff2)
    else:
        right = "".join(diff2)

    return [left, right]


def find_diff(old, new, type):
    """
    Find difference in old model vs. new.
    If any fields are different, note them in a dictionary of tuples (db column, old text, new text).
    :param old: old version model
    :param new: new version model
    :param type: category or tool
    :return: dictionary of tuples (db column, old text, new text)
    """

    diffs = {}

    if type == "categories":
        new_what = new.what
        new_where = new.where
        if new.parent:
            new_parent_category_name = new.parent.name
        else:
            new_parent_category_name = ""

        old_what = old.what
        old_where = old.where
        if old.parent:
            old_parent_category_name = old.parent.name
        else:
            old_parent_category_name = ""

        if old_what != new_what:
            diffs["What"] = [old_what, new_what]
            diffs["What"] = [old_what, new_what]
        if old_where != new_where:
            diffs["Where"] = [old_where, new_where]
        if old_parent_category_name != new_parent_category_name:
            diffs["Parent Category"] = [old_parent_category_name, new_parent_category_name]

    else:
        # Tool
        new_avatar_url = new.avatar_url
        new_env = new.env
        new_created = new.created
        new_project_version = new.project_version
        new_link = new.link

        old_avatar_url = old.avatar_url
        old_env = old.env
        old_created = old.created
        old_project_version = old.project_version
        old_link = old.link

        if old_avatar_url != new_avatar_url:
            diffs["Avatar URL"] = [old_avatar_url, new_avatar_url]
        if old_env != new_env:
            diffs["Environment"] = [old_env, new_env]
        if old_created != new_created:
            diffs["Created Date"] = [old_created, new_created]
        if old_project_version != new_project_version:
            diffs["Project Version"] = [old_project_version, new_project_version]
        if old_link != new_link:
            diffs["Project URL"] = [old_link, new_link]

        new_parent_category_name = new.category.name
        old_parent_category_name = old.category.name
        if old_parent_category_name != new_parent_category_name:
            diffs["Parent Category"] = [old_parent_category_name, new_parent_category_name]

    new_name = new.name
    new_why = new.why

    old_name = old.name
    old_why = old.why

    if old_name != new_name:
        diffs["Name"] = [old_name, new_name]
    if old_why != new_why:
        diffs["Why"] = [old_why, new_why]

    return diffs


def overwrite(old, new, type):
    """
    Overwrite old (typically current) model with data from new (typically an older version).
    This is used for time travel.
    :param old: model to be overwritten
    :param new: model whose date will be used
    :param type: category or tool
    :return: old model with overwritten data supplied by new
    """

    if type == "categories":
        old.what = new.what
        old.where = new.where

    else:
        # Tool
        old.avatar_url = new.avatar_url
        old.env = new.env
        old.created = new.created
        old.project_version = new.project_version
        old.link = new.link

    old.name = new.name
    old.why = new.why
    old.parent_category_id = new.parent_category_id

    return old


def is_within_last_x_hours(t: datetime, hours: int) -> bool:
    return (datetime.utcnow() - timedelta(hours=hours)) <= t <= datetime.utcnow()


def is_over_x_hours_ago(t: datetime, hours: int) -> bool:
    return t < (datetime.utcnow() - timedelta(hours=hours))


def check_if_three_time_travels(edit_author_id: int, model_class, page_id: int) -> bool:
    """
    Look at all versions, check if provided user shows up three or more times in the past 24 hours.
    :param edit_author_id: user id
    :param model_class: categories or tools class
    :param page_id: id of the page
    :return: bool if user has made 3 or more time travels alraedy
    """

    versions = db.session.query(version_class(model_class)).filter_by(id=page_id,
                                                                      edit_author=edit_author_id,
                                                                      is_time_travel_edit=True).all()
    time_travels_in_last_24_hours = [v for v in versions if is_within_last_x_hours(v.edit_time, 24)]
    db.session.close()
    return len(time_travels_in_last_24_hours) >= 3


def escape_html(s):
    return html.escape(str(s))


def create_activity(verb=None, object=None, target=None):
    db.session.flush()
    Activity = versioning_manager.activity_cls
    activity = Activity(
        object=object,
        target=target,
        verb=verb
    )
    db.session.add(activity)
    return activity


def version_paginate(itr, page, per_page, total):
    page -= 1
    latest = range(total, 0, -per_page)[page]
    oldest = latest - per_page
    oldest = oldest if oldest > 0 else 0
    return itr[oldest:latest]


def get_model_attributes(model: db.Model, cols: List[str]) -> List:
    return [getattr(model, col) for col in cols]
