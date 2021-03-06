from datetime import datetime, timedelta

from flask import render_template, redirect, url_for, flash, request, jsonify, abort, current_app, session, \
    make_response
from flask_login import current_user, login_required
from flask_sqlalchemy import Pagination, get_debug_queries
from sqlalchemy import not_, and_
from sqlalchemy_continuum import version_class, versioning_manager

from app.main.forms import *
from . import main
from .. import cache, utils, db, models, tree
from ..decorators import admin_required, permission_required


@main.before_app_request
def check_if_blocked():
    if current_user.is_authenticated and current_app.config['BLOCKING_USERS'] and current_user.blocked:
        abort(403)


@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config["SLOW_DB_QUERY_TIME"]:
            current_app.logger.warning(
                "Slow query: {}\n\tParameters: {}\n\tDuration: {}\n\tContext: {}\n".format(
                    query.statement,
                    query.parameters,
                    query.duration,
                    query.context)
            )
    return response


def make_cache_key(*args, **kwargs):
    path = request.path
    args = str(hash(frozenset(request.args.items())))
    return path + args


def anonymous_warning():
    if not current_user.is_authenticated:
        flash(
            "You are currently not logged in. Any edits you make will publicly display your IP address. \
            Log in or sign up to hide it.",
            "danger")


@main.route("/")
def index():
    pages_to_show = current_app.config["POPULAR_PAGE_COUNT"]
    tools = models.Tool.query \
        .order_by(models.Tool.id.desc()) \
        .limit(pages_to_show)
    return render_template("index.html",
                           tools=tools)


@main.route("/explore")
@cache.cached(key_prefix=make_cache_key)
def browse_categories():
    category_id = request.args.get("id")
    if category_id:
        category = models.Category.query.get_or_404(category_id)
    else:
        category = None
        category_id = None
    # Comma-separated envs
    environments = request.args.get("envs")
    environments_html = ""
    if environments:
        environments_html = utils.parse_environments_html(environments)
    return render_template("explore.html",
                           id=category_id,
                           category=category,
                           environments=environments,
                           environments_html=environments_html)


@main.route("/filter_nodes")
@cache.cached(key_prefix=make_cache_key)
def filter_nodes():
    ceiling = request.args.get("node", type=int) or request.args.get("ceiling", type=int) or 0
    params = {
        "query": request.args.get("q"),
        "environments": request.args.get("envs"),
        "ceiling": ceiling
    }

    bool_args = [
        "show_root",
        "show_links",
        "only_categories"
    ]
    for arg in bool_args:
        value = request.args.get(arg)
        if value:
            value = (value == "True") or (value == "true")
            params[arg] = value

    t = tree.Tree(**params)
    return jsonify(t.to_json())


@main.route("/about")
@cache.cached()
def get_about():
    return render_template("about.html")


@main.route("/roles")
@cache.cached()
def get_roles():
    return render_template("roles.html")


@main.route("/categories/<int:category_id>", defaults={'category_name': ""})
@main.route("/categories/<int:category_id>/", defaults={'category_name': ""})
@main.route("/categories/<int:category_id>/<category_name>")
@cache.cached(key_prefix=make_cache_key)
def fetch_category_page(category_id, category_name):
    category = models.Category.query.get_or_404(category_id)
    if category_name != category.slug:
        return redirect(url_for('.fetch_category_page', category_id=category_id, category_name=category.slug))

    ALTS_PER_LIST = current_app.config["ALTS_PER_LIST"]
    subcategories = category.children.limit(ALTS_PER_LIST).all()
    subtools = category.tools.limit(ALTS_PER_LIST).all()
    category_tree = utils.build_bottom_up_tree(category)

    what = utils.process_mentions(category.what)
    why = utils.process_mentions(category.why)
    where = utils.process_mentions(category.where)

    return render_template("category.html",
                           category=category,
                           subcategories=subcategories,
                           subtools=subtools,
                           breadcrumbs=category_tree,
                           ALTS_PER_LIST=ALTS_PER_LIST,
                           what=what,
                           why=why,
                           where=where)


@main.route("/tools/<int:tool_id>", defaults={"tool_name": ""})
@main.route("/tools/<int:tool_id>/", defaults={"tool_name": ""})
@main.route("/tools/<int:tool_id>/<tool_name>")
@cache.cached(key_prefix=make_cache_key)
def fetch_tool_page(tool_id, tool_name):
    tool = models.Tool.query.get_or_404(tool_id)
    if tool_name != tool.slug:
        return redirect(url_for('.fetch_tool_page', tool_id=tool_id, tool_name=tool.slug))

    ALTS_PER_LIST = current_app.config["ALTS_PER_LIST"]
    tool_envs = tool.environments
    alts_for_this_env = []
    if tool_envs:
        alts_for_this_env = models.Tool.query \
            .filter_by(parent_category_id=tool.parent_category_id) \
            .filter(models.Tool.environments.any()) \
            .filter(and_(models.Tool.environments.contains(e) for e in tool_envs)) \
            .filter(models.Tool.id != tool.id) \
            .limit(ALTS_PER_LIST) \
            .all()

    alts_for_other_envs = models.Tool.query \
        .filter_by(parent_category_id=tool.parent_category_id) \
        .filter(and_(not_(models.Tool.environments.contains(e)) for e in tool_envs)) \
        .filter(models.Tool.id != tool.id) \
        .limit(ALTS_PER_LIST) \
        .all()

    # Get four levels up in tree
    category_tree = utils.build_bottom_up_tree(tool.category)[-4:]

    if tool.link:
        project_link = utils.get_hostname(tool.link)
    else:
        project_link = None

    what = utils.process_mentions(tool.what)
    why = utils.process_mentions(tool.why)

    return render_template("tool.html",
                           tool=tool,
                           env_alts=alts_for_this_env,
                           other_alts=alts_for_other_envs,
                           tree=category_tree,
                           link=project_link,
                           ALTS_PER_LIST=ALTS_PER_LIST,
                           what=what,
                           why=why)


@main.route("/tip/<int:category_id>")
@cache.memoize()
def get_tooltip(category_id):
    columns = utils.get_model_attributes(models.Category, ["name", "what"])
    result = db.session.query(*columns).filter_by(id=category_id).first()
    if result:
        name, what = result
        what = utils.process_mentions(what, show_links=False)
        bold_name = "<b>" + utils.escape_html(name) + "</b>"
        return bold_name + "<br>" + what
    else:
        abort(404)


@main.route("/search")
@cache.cached(key_prefix=make_cache_key)
def search_tools():
    search_query = request.args.get("q")
    is_escaped = request.args.get("e")
    results = []
    queried_tools = models.Tool.query.whoosh_search(search_query, like=True).all()
    for tool in queried_tools:
        label = tool.name
        if is_escaped:
            label = utils.escape_html(label)
        results.append({"label": label, "type": "t", "id": tool.id})
    search_categories = models.Category.query.whoosh_search(search_query, like=True).all()
    for category in search_categories:
        label = category.name
        if is_escaped:
            label = utils.escape_html(label)
        results.append({"label": label, "type": "c", "id": category.id})

    if not results:
        results.append({"label": "No results found", "type": "0", "id": "-1"})

    return jsonify(results)


@main.route("/search-envs")
@cache.cached(key_prefix=make_cache_key)
def search_envs():
    search_query = request.args.get("q")
    results = []
    queried_envs = models.Environment.query.whoosh_search(search_query, like=True).all()
    for env in queried_envs:
        results.append({"label": env.name, "id": env.id})
    return jsonify(results)


# USER ROUTES


@main.route('/users/<int:user_id>')
def user(user_id):
    edits_to_show = current_app.config["USER_EDITS_SHOWN"]
    user = models.User.query.get_or_404(user_id)
    tool_edits = version_class(models.Tool).query \
        .filter_by(edit_author=user_id) \
        .order_by(version_class(models.Tool).transaction_id.desc()) \
        .limit(edits_to_show)
    category_edits = version_class(models.Category).query \
        .filter_by(edit_author=user_id) \
        .order_by(version_class(models.Category).transaction_id.desc()) \
        .limit(edits_to_show)

    return render_template('user.html',
                           user=user,
                           total_edits=user.edits,
                           tool_edits=tool_edits,
                           category_edits=category_edits)


@main.route("/users/<int:id>/edits/<page_type>")
def view_user_edits(id, page_type):
    user = models.User.query.get_or_404(id)

    if page_type == "categories":
        cls = models.Category
    elif page_type == "tools":
        cls = models.Tool
    else:
        abort(404)

    pagination = version_class(cls).query.filter_by(edit_author=id) \
        .order_by(version_class(cls).transaction_id.desc()) \
        .paginate(per_page=current_app.config['EDITS_PER_PAGE'], error_out=False)
    edits = list(reversed(pagination.items))

    return render_template("view_user_edits.html",
                           user=user,
                           type=page_type,
                           pagination=pagination,
                           edits=edits)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated.', 'success')
        return redirect(url_for('.user', user_id=current_user.id))
    form.name.data = current_user.name
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile-admin', methods=['GET', 'POST'])
@admin_required
@login_required
def edit_profile_admin():
    id = request.args.get("id")
    user = models.User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = models.Role.query.get_or_404(form.role.data)
        db.session.add(user)
        flash('The profile has been updated.', 'success')
        return redirect(url_for('.user', user_id=user.id))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    return render_template('edit_profile_admin.html', form=form, user=user)


# EDIT ROUTES


def render_edits(page_type, page_id):
    if page_type == "tools":
        cls = models.Tool
    elif page_type == "categories":
        cls = models.Category
    else:
        abort(404)

    # Check to make sure id exists first, otherwise 404
    versions = cls.query.get_or_404(page_id).versions
    total = versions.count()

    page = int(request.args.get('page', 1))
    per_page = current_app.config["EDITS_PER_PAGE"]
    items = utils.version_paginate(versions, page, per_page, total)
    pagination = Pagination(query=None, page=page, per_page=per_page, total=total, items=items)

    return render_template(
        "view_edits.html",
        id=page_id,
        type=page_type,
        pagination=pagination,
        latest_version_num=total,
        current_version=versions[-1],
        previous_versions=total > 1,
        versions=pagination.items
    )


@main.route("/tools/<int:id>/edits")
def view_tool_edits(id):
    return render_edits(page_type="tools", page_id=id)


@main.route("/categories/<int:id>/edits")
def view_category_edits(id):
    return render_edits(page_type="categories", page_id=id)


def create_temp_user():
    ip = utils.get_client_ip()
    existing_temp_user = models.User.query.filter_by(username=ip).first()
    if not existing_temp_user:
        new_temp_user = models.User(
            email="",
            username=ip,
            password="",
            role_id=models.Role.query.filter_by(name="Anonymous User").first().id)
        db.session.add(new_temp_user)
        db.session.commit()
        return new_temp_user
    else:
        return existing_temp_user


@main.route("/categories/<int:category_id>/edit", methods=["GET", "POST"])
def edit_category_page(category_id):
    anonymous_warning()
    category = models.Category.query.get_or_404(category_id)

    if current_user.is_member:
        form = EditCategoryPageFormMember(category.id)
    else:
        form = EditCategoryPageForm()

    if form.validate_on_submit():
        category.name = form.name.data
        if current_user.is_member:
            if form.move_parent.data:
                if int(form.parent_category_id.data) == 0 or form.parent_category.data == "/":
                    category.parent_category_id = None
                else:
                    category.parent_category_id = form.parent_category_id.data
        category.what = form.what.data
        category.why = form.why.data
        category.where = form.where.data
        category.edit_msg = form.edit_msg.data
        category.edit_time = datetime.utcnow()
        if not current_user.is_authenticated:
            edit_author = create_temp_user()
        else:
            edit_author = current_user
        category.edit_author = edit_author.id
        category.is_time_travel_edit = False
        db.session.add(category)

        utils.create_activity(verb="edit", object=category)

        edit_author.edits += 1
        db.session.add(edit_author)

        # Remove any trailing flash messages (usually IP warning)
        session.pop('_flashes', None)
        flash('This category has been updated.', 'success')
        cache.clear()
        return redirect(url_for('.fetch_category_page', category_id=category.id, category_name=category.slug))
    if not form.is_submitted():
        form.name.data = category.name
        if current_user.is_member:
            form.move_parent.data = False
            if category.parent:
                form.parent_category.data = category.parent.name
                form.parent_category_id.data = category.parent.id
            else:
                form.parent_category.data = "/"
                form.parent_category_id.data = 0
        form.what.data = category.what
        form.why.data = category.why
        form.where.data = category.where
        form.edit_msg.data = ""
    return render_template('edit_category.html',
                           form=form,
                           category=category,
                           is_member=current_user.is_member)


@main.route("/tools/<int:tool_id>/edit", methods=["GET", "POST"])
def edit_tool_page(tool_id):
    anonymous_warning()
    tool = models.Tool.query.get_or_404(tool_id)

    if current_user.is_member:
        form = EditToolPageFormMember()
    else:
        form = EditToolPageForm()

    if form.validate_on_submit():
        tool.name = form.name.data
        tool.logo_url = form.logo_url.data or None
        tool.link = form.link.data or None
        if current_user.is_authenticated:
            edit_author = current_user
            if current_user.is_member:
                if form.move_parent.data:
                    tool.parent_category_id = form.parent_category_id.data
        else:
            edit_author = create_temp_user()
        environments = utils.parse_environments(form.environments.data)
        tool.environments = environments or []
        tool.environments_dumped = utils.dump_environments(environments)
        tool.created = form.created.data or None
        tool.project_version = form.project_version.data or None
        tool.is_active = form.is_active.data or None
        tool.what = form.what.data
        tool.why = form.why.data
        tool.edit_msg = form.edit_msg.data
        tool.edit_time = datetime.utcnow()
        tool.edit_author = edit_author.id
        tool.is_time_travel_edit = False
        db.session.add(tool)

        utils.create_activity(verb="edit", object=tool)

        edit_author.edits += 1
        db.session.add(edit_author)

        session.pop('_flashes', None)
        flash('This tool has been updated.', 'success')
        cache.clear()
        return redirect(url_for('.fetch_tool_page', tool_id=tool.id))
    if not form.is_submitted():
        form.name.data = tool.name
        form.environments.data = utils.dump_environments(tool.environments)
        form.created.data = tool.created
        form.project_version.data = tool.project_version
        form.is_active.data = tool.is_active
        form.logo_url.data = tool.logo_url
        form.link.data = tool.link
        if current_user.is_member:
            form.parent_category_id.data = tool.parent_category_id
            form.parent_category.data = tool.category.name
        form.what.data = tool.what
        form.why.data = tool.why
        form.edit_msg.data = ""
    return render_template('edit_tool.html',
                           form=form,
                           tool=tool,
                           is_member=current_user.is_member)


def render_diff(page_type, page_id, older, newer):
    if page_type == "tools":
        cls = models.Tool
    elif page_type == "categories":
        cls = models.Category
    else:
        abort(404)

    page = cls.query.get_or_404(page_id)
    newer_data = page.versions[newer - 1]
    older_data = page.versions[older - 1]
    # TODO: input validation on version index

    diffs = utils.find_diff(older_data, newer_data, page_type)
    for key in diffs:
        before, after = diffs[key]
        if key == "Environment(s)":
            diffs[key] = utils.gen_environment_diff_html(before, after)
        else:
            diffs[key] = utils.gen_diff_html(before, after)

    older_time = older_data.edit_time.strftime('%d %B %Y, %H:%M')
    newer_time = newer_data.edit_time.strftime('%d %B %Y, %H:%M')

    return render_template("view_diff.html",
                           id=page_id,
                           type=page_type,
                           page_name=page.name,
                           older_data=older_data,
                           newer_data=newer_data,
                           older_time=older_time,
                           newer_time=newer_time,
                           diffs=diffs)


@main.route("/tools/<int:tool_id>/edits/diff/<int:older>/<int:newer>")
@cache.cached(key_prefix=make_cache_key)
def view_tool_diff(tool_id, newer, older):
    return render_diff(page_type="tools", page_id=tool_id, older=older, newer=newer)


@main.route("/categories/<int:category_id>/edits/diff/<int:older>/<int:newer>")
@cache.cached(key_prefix=make_cache_key)
def view_category_diff(category_id, newer, older):
    return render_diff(page_type="categories", page_id=category_id, older=older, newer=newer)


def render_time_travel(page_type, page_id, target_version_id):
    if page_type == "categories":
        cls = models.Category
        three_revision_route = "main.view_category_edits"
    elif page_type == "tools":
        cls = models.Tool
        three_revision_route = "main.view_tool_edits"
    else:
        abort(404)

    # Make sure user hasn't made more than three reverts within past 24 hours
    if not current_user.is_authenticated:
        edit_author = create_temp_user()
    else:
        edit_author = current_user

    # Enforce three-revision rule
    if utils.check_if_three_time_travels(edit_author.id, cls, page_id):
        flash("You have already reverted this page three times within a 24 hour period. Try again later.", "warning")
        return redirect(url_for(three_revision_route, id=page_id))

    # Load whole states of current and destination
    page = cls.query.get_or_404(page_id)
    current_version = page.versions[-1]
    destination_version = page.versions[target_version_id - 1]

    current_time = current_version.edit_time.strftime('%d %B %Y, %H:%M')
    destination_time = destination_version.edit_time.strftime('%d %B %Y, %H:%M')

    # Create diff
    diffs = utils.find_diff(current_version, destination_version, page_type)
    for key in diffs:
        before, after = diffs[key]
        if key == "Environment(s)":
            diffs[key] = utils.gen_environment_diff_html(before, after)
        else:
            diffs[key] = utils.gen_diff_html(before, after)

    anonymous_warning()

    form = TimeTravelForm()
    if form.validate_on_submit():
        # Overwrite entire current state with destination edit state
        page = utils.overwrite(page, destination_version, page_type)
        page.edit_msg = form.edit_msg.data
        page.edit_time = datetime.utcnow()
        page.edit_author = edit_author.id
        page.is_time_travel_edit = True
        db.session.add(page)

        utils.create_activity(verb="time_travel", object=page)

        edit_author.edits += 1
        db.session.add(edit_author)

        cache.clear()
        flash('This page has been updated.', 'success')
        destination_slug = destination_version.slug
        if page_type == "categories":
            return_route = url_for('main.fetch_category_page', category_id=page_id, category_name=destination_slug)
        else:
            return_route = url_for('main.fetch_tool_page', tool_id=page_id, tool_name=destination_slug)
        return redirect(return_route)

    form.edit_msg.data = "Time travel back to {} from {}".format(destination_time, current_time)
    return render_template("time_travel.html",
                           id=page_id,
                           type=page_type,
                           name=current_version.name,
                           form=form,
                           current_time=current_time,
                           destination_time=destination_time,
                           diffs=diffs,
                           current_version=current_version)


@main.route("/tools/<int:tool_id>/edit/time-travel/<int:target_version_id>", methods=["GET", "POST"])
@permission_required(models.Permission.TIME_TRAVEL)
@login_required
def tool_time_travel(tool_id, target_version_id):
    return render_time_travel(page_type="tools", page_id=tool_id, target_version_id=target_version_id)


@main.route("/categories/<int:category_id>/edit/time-travel/<int:target_version_id>", methods=["GET", "POST"])
@permission_required(models.Permission.TIME_TRAVEL)
@login_required
def category_time_travel(category_id, target_version_id):
    return render_time_travel(page_type="categories", page_id=category_id, target_version_id=target_version_id)


# CREATE ROUTES


@main.route("/categories/<int:parent_category_id>/add-new-tool", methods=["GET", "POST"])
@main.route("/add-new-tool", methods=["GET", "POST"])
@login_required
def add_new_tool(parent_category_id=None):
    if not current_user.is_authenticated:
        flash("You must log in or sign up to add new pages.")
        return redirect(url_for("auth.login"))
    if current_user.is_member:
        form = AddNewToolFormMember()
    else:
        form = AddNewToolForm()

    if form.validate_on_submit():
        if not current_user.is_authenticated:
            edit_author = create_temp_user()
        else:
            edit_author = current_user

        environments = utils.parse_environments(form.environments.data)
        tool = models.Tool(
            name=form.name.data,
            parent_category_id=form.parent_category_id.data,
            logo_url=form.logo_url.data or None,
            environments=environments or [],
            environments_dumped=utils.dump_environments(environments),
            created=form.created.data or None,
            project_version=form.project_version.data or None,
            is_active=form.is_active.data or None,
            link=form.link.data or None,
            what=form.what.data,
            why=form.why.data,
            edit_author=edit_author.id,
            edit_time=datetime.utcnow()
        )
        db.session.add(tool)

        utils.create_activity(verb="add", object=tool)

        edit_author.edits += 1
        db.session.add(edit_author)

        # Leave this commit, need record created now so it can be used on the redirect
        db.session.commit()
        session.pop('_flashes', None)
        flash('This tool has been added.', 'success')
        cache.clear()
        return redirect(url_for('.fetch_tool_page', tool_id=tool.id))

    if parent_category_id:
        # Tool added from category page
        form.parent_category_id.data = parent_category_id
        parent_category = models.Category.query.get_or_404(parent_category_id)
        form.parent_category.data = parent_category.name

    return render_template('add_new_tool.html',
                           form=form,
                           is_member=current_user.is_member)


@main.route("/categories/<int:parent_category_id>/add-new-category", methods=["GET", "POST"])
@main.route("/add-new-category", methods=["GET", "POST"])
@login_required
def add_new_category(parent_category_id=None):
    form = AddNewCategoryForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            edit_author = create_temp_user()
        else:
            edit_author = current_user
        if form.parent_category.data == "/" or int(form.parent_category_id.data) == 0:
            # User must specify parent category, even if root
            parent_category_id = None
        else:
            parent_category_id = form.parent_category_id.data
        category = models.Category(
            name=form.name.data,
            parent_category_id=parent_category_id,
            what=form.what.data,
            why=form.why.data,
            where=form.where.data,
            edit_author=edit_author.id,
            edit_time=datetime.utcnow()
        )
        db.session.add(category)

        utils.create_activity(verb="add", object=category)

        edit_author.edits += 1
        db.session.add(edit_author)

        # Leave this commit, need record created now so it can be used on the redirect
        db.session.commit()
        session.pop('_flashes', None)
        flash('This category has been added.', 'success')
        cache.clear()
        return redirect(url_for('.fetch_category_page', category_id=category.id))

    if parent_category_id:
        # Subcategory added from category page
        form.parent_category_id.data = parent_category_id
        parent_category = models.Category.query.get_or_404(parent_category_id)
        form.parent_category.data = parent_category.name

    return render_template('add_new_category.html', form=form)


# SITE LOG


@main.route("/sitelog")
def sitelog():
    page_number = 1
    if request.args.get("page"):
        page_number = int(request.args.get("page"))
    Activity = versioning_manager.activity_cls
    pagination = Activity.query \
        .order_by(Activity.id.desc()) \
        .paginate(page_number, per_page=current_app.config['EDITS_PER_PAGE'], error_out=False)

    return render_template("sitelog.html",
                           pagination=pagination)


# OTHER


@main.route('/sitemap.xml', methods=['GET'])
def sitemap():
    """Generate sitemap.xml. Makes a list of urls and date modified."""
    pages = []
    ten_days_ago = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
    # static pages
    for rule in current_app.url_map.iter_rules():
        if "GET" in rule.methods and len(rule.arguments) == 0 and "admin" not in rule.rule:
            pages.append(
                [rule.rule, ten_days_ago]
            )

    sitemap_xml = render_template('sitemap.xml', pages=pages)
    response = make_response(sitemap_xml)
    response.headers["Content-Type"] = "application/xml"

    return response


@main.route("/changelog")
def changelog():
    return render_template("changelog.html")
