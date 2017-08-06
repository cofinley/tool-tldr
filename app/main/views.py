import ipaddress
from flask import render_template, redirect, url_for, flash, request, jsonify, abort, current_app, session
from datetime import datetime

from . import main
from .. import models as models
from .. import cache, utils, db
from app.main.forms import *
from ..decorators import admin_required, permission_required
from flask_login import login_required, current_user
from sqlalchemy_continuum import version_class


def make_cache_key(*args, **kwargs):
	path = request.path
	args = str(hash(frozenset(request.args.items())))
	return path + args


@main.route("/")
@cache.cached(key_prefix=make_cache_key)
def index():
	categories = models.Category.query.filter_by(parent=None).all()
	show_more = False
	if len(categories) > 16:
		show_more = True
	return render_template("index.html",
						   categories=categories[:16],
						   show_more=show_more)


@main.route("/explore")
@cache.cached(key_prefix=make_cache_key)
def browse_categories():
	category_id = request.args.get("id")
	if category_id:
		category = models.Category.query.get_or_404(category_id)
	else:
		category = None
		category_id = None
	environment = request.args.get("env")
	return render_template("explore.html",
						   id=category_id,
						   category=category,
						   environment=environment)


@cache.cached(key_prefix=make_cache_key)
def load_children_tools(id, env):

	# Used for explore tree

	if env:
		child_tools = models.Tool.query.filter_by(parent_category_id=id, env=env).all()
	else:
		child_tools = models.Tool.query.filter_by(parent_category_id=id).all()
	cols = ["id", "name", "env"]
	results = [{col: getattr(child, col) for col in cols} for child in child_tools]

	for result in results:
		if env:
			label_link = "<a href='/tools/{}'>{}</a>".format(result["id"], result["name"])
		else:
			label_link = "<a href='/tools/{}'>{}</a> ({})".format(result["id"], result["name"],
																 result["env"].title())
		result.pop("name")
		result["label"] = label_link

	return results


@cache.memoize()
def load_children_categories(id, no_link):
	if id:
		children = models.Category.query.filter_by(parent_category_id=id).all()
	else:
		children = models.Category.query.filter_by(parent_category_id=None).all()

	cols = ["id", "name"]
	results = [{col: getattr(child, col) for col in cols} for child in children]
	cleaned_results = []
	for result in results:
		cleaned_result = {"id": result["id"], "load_on_demand": True}
		if not no_link:
			# anchor tags for '/explore' tree, regular text if on '/add-new-...' page tree
			label_link = "<a href='/categories/{}'>{}</a>".format(result["id"], result["name"])
			cleaned_result["label"] = label_link
		else:
			cleaned_result["name"] = result["name"]
		cleaned_results.append(cleaned_result)

	return cleaned_results


@main.route("/explore_nodes")
@cache.cached(key_prefix=make_cache_key)
def explore_nodes():
	node_id = request.args.get("node")
	manual_node_id = request.args.get("manual_node")
	# `manual_node` id passed in from tool alternatives
	# At first, it will just be manual id passed as param here
	# Once user expands a node, `node` will also be added as param
	# If just `manual_node`, use it as node_id
	# If both, default to `node`. This prevents infinite recursive loop
	if manual_node_id and not node_id:
		node_id = manual_node_id
	env = request.args.get("env")
	show_root = request.args.get("show-root")
	no_link = request.args.get("no-link", False, type=bool)

	results = load_children_categories(node_id, no_link)
	if not no_link:
		results += load_children_tools(node_id, env)

	if show_root and not node_id:
		# Only show root node if explicit param and jqTree has not added a node id param (will recursively repeat otherwise)
		root = [{"id": 0, "name": "/", "children": results}]
		return jsonify(root)

	return jsonify(results)


@main.route("/load_blurb")
@cache.cached(key_prefix=make_cache_key)
def load_blurb():
	id = request.args.get("id")
	tool = request.args.get("tool")
	if tool:
		blurb = ""
	else:
		blurb = models.Category.query.get_or_404(id).what
	result = {"blurb": blurb}

	return jsonify(result)


@main.route("/about")
@cache.cached()
def get_about():
	return render_template("about.html")


@main.route("/categories/<int:category_id>")
@cache.cached(key_prefix=make_cache_key)
def fetch_category_page(category_id):
	category = models.Category.query.get_or_404(category_id)
	subcategories = category.children
	subtools = category.tools.all()
	category_tree = utils.build_bottom_up_tree(category.id)

	return render_template("category.html",
						   category=category,
						   subcategories=subcategories,
						   subtools=subtools,
						   breadcrumbs=category_tree)


@main.route("/tools/<int:tool_id>")
@cache.cached(key_prefix=make_cache_key)
def fetch_tool_page(tool_id):
	tool = models.Tool.query.get_or_404(tool_id)

	alts_for_this_env = models.Tool.query\
		.filter_by(parent_category_id=tool.parent_category_id)\
		.filter_by(env=tool.env)\
		.filter(models.Tool.id != tool.id)\
		.all()[:current_app.config['ALTS_PER_LIST']]
	alts_for_other_envs = models.Tool.query\
		.filter(models.Tool.parent_category_id == tool.parent_category_id)\
		.filter(models.Tool.env != tool.env)\
		.all()[:current_app.config['ALTS_PER_LIST']]

	# Get four levels up in tree
	category_tree = utils.build_bottom_up_tree(tool.parent_category_id)[-4:]

	project_link = utils.get_hostname(tool.link)

	return render_template("tool.html",
						   tool=tool,
						   env_alts=alts_for_this_env,
						   other_alts=alts_for_other_envs,
						   tree=category_tree,
						   link=project_link)


@main.route("/search")
@cache.cached(key_prefix=make_cache_key)
def search_tools():
	search_query = request.args.get("q")
	results = []
	queried_tools = models.Tool.query.whoosh_search(search_query, like=True).all()
	for tool in queried_tools:
		results.append({"label": tool.name, "type": "t", "id": tool.id})
	search_categories = models.Category.query.whoosh_search(search_query, like=True).all()
	for category in search_categories:
		results.append({"label": category.name, "type": "c", "id": category.id})

	return jsonify(results)


# USER ROUTES


@main.route('/users/<int:user_id>')
def user(user_id):
	user = models.User.query.get_or_404(user_id)

	tool_edits = version_class(models.Tool).query.filter_by(edit_author=user_id).all()
	category_edits = version_class(models.Category).query.filter_by(edit_author=user_id).all()

	total_edits = len(tool_edits) + len(category_edits)

	return render_template('user.html',
						   user=user,
						   total_edits=total_edits,
						   tool_edits=tool_edits[-11:],
						   category_edits=category_edits[-11:])


@main.route("/users/<int:id>/edits/<page_type>", defaults={'page_number': 1})
@main.route("/users/<int:id>/edits/<page_type>/<int:page_number>")
def view_user_edits(id, page_type, page_number):

	user = models.User.query.get_or_404(id)

	if page_type == "categories":
		cls = models.Category
	elif page_type == "tools":
		cls = models.Tool
	else:
		abort(404)

	pagination = version_class(cls).query.filter_by(edit_author=id) \
		.order_by(version_class(cls).transaction_id.desc()) \
		.paginate(page_number, per_page=current_app.config['EDITS_PER_PAGE'], error_out=False)
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
@login_required
@admin_required
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


def render_edits(page_type, page_id, page_number):

	if page_type == "tools":
		cls = models.Tool
	elif page_type == "categories":
		cls = models.Category
	else:
		abort(404)

	# Check to make sure id exists first, otherwise 404
	cls.query.get_or_404(page_id)

	all = version_class(cls).query.filter_by(id=page_id).all()
	latest_version_id = all[-1].transaction_id
	first_version_id = all[0].transaction_id
	pagination = version_class(cls).query.filter_by(id=page_id) \
		.order_by(version_class(cls).transaction_id.desc()) \
		.paginate(page_number, per_page=current_app.config['EDITS_PER_PAGE'], error_out=False)
	versions = list(reversed(pagination.items))
	return render_template("view_edits.html",
						   id=page_id,
						   type=page_type,
						   pagination=pagination,
						   latest_version_id=latest_version_id,
						   first_version_id=first_version_id,
						   current_version=versions[-1],
						   previous_versions=versions[:-1])


@main.route("/tools/<int:id>/edits", defaults={'page_number': 1})
@main.route("/tools/<int:id>/edits/<int:page_number>")
def view_tool_edits(id, page_number):

	return render_edits(page_type="tools", page_id=id, page_number=page_number)


@main.route("/categories/<int:id>/edits", defaults={'page_number': 1})
@main.route("/categories/<int:id>/edits/<int:page_number>")
def view_category_edits(id, page_number):

	return render_edits(page_type="categories", page_id=id, page_number=page_number)


def create_temp_user():
	ip = request.remote_addr
	existing_temp_user = models.User.query.filter_by(username=ip).first()
	if not existing_temp_user:
		new_temp_user = models.User(email="",
								username=ip,
								password="",
								role_id=models.Role.query.filter_by(name="Anonymous").first().id)
		db.session.add(new_temp_user)
		db.session.commit()
		return new_temp_user
	else:
		return existing_temp_user


@main.route("/categories/<int:category_id>/edit", methods=["GET", "POST"])
def edit_category_page(category_id):
	if not current_user.is_authenticated:
		flash("You are currently not logged in. Any edits you make will publicly display your IP address. Log in or sign up to hide it.", "danger")
	category = models.Category.query.get_or_404(category_id)

	if current_user.is_confirmed:
		form = EditCategoryPageFormConfirmed(category.id)
	else:
		form = EditCategoryPageForm()

	if form.validate_on_submit():
		category.name = form.name.data
		if current_user.is_confirmed:
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
			edit_author = create_temp_user().id
		else:
			edit_author = current_user.id
		category.edit_author = edit_author
		db.session.add(category)
		# Remove any trailing flash messages (usually IP warning)
		session.pop('_flashes', None)
		flash('This category has been updated.', 'success')
		cache.clear()
		return redirect(url_for('.fetch_category_page', category_id=category.id))
	form.name.data = category.name
	if current_user.is_confirmed:
		form.move_parent.data = False
		if category.parent:
			form.parent_category.data = category.parent.name
		else:
			form.parent_category.data = "/"
	form.what.data = category.what
	form.why.data = category.why
	form.where.data = category.where
	form.edit_msg.data = ""
	return render_template('edit_category.html',
						   form=form,
						   category=category,
						   is_confirmed=current_user.is_confirmed)


@main.route("/tools/<int:tool_id>/edit", methods=["GET", "POST"])
def edit_tool_page(tool_id):
	if not current_user.is_authenticated:
		flash("You are currently not logged in. Any edits you make will publicly display your IP address. Log in or sign up to hide it.", "danger")
	tool = models.Tool.query.get_or_404(tool_id)

	if current_user.is_confirmed:
		form = EditToolPageFormConfirmed()
	else:
		form = EditToolPageForm()

	if form.validate_on_submit():
		tool.name = form.name.data
		tool.avatar_url = form.avatar_url.data
		tool.link = form.link.data
		if current_user.is_authenticated:
			edit_author = current_user.id
			if current_user.is_confirmed:
				if form.move_parent.data:
					tool.parent_category_id = form.parent_category_id.data
		else:
			edit_author = create_temp_user().id
		tool.env = form.env.data.lower()
		tool.created = form.created.data
		tool.project_version = form.project_version.data
		tool.is_active = form.is_active.data
		tool.why = form.why.data
		tool.edit_msg = form.edit_msg.data
		tool.edit_time = datetime.utcnow()
		tool.edit_author = edit_author
		session.pop('_flashes', None)
		flash('This tool has been updated.', 'success')
		cache.clear()
		return redirect(url_for('.fetch_tool_page', tool_id=tool.id))
	form.name.data = tool.name
	form.env.data = tool.env.title()
	form.created.data = datetime.strftime(tool.created, "%Y-%m-%d")
	form.project_version.data = tool.project_version
	form.is_active.data = tool.is_active
	form.avatar_url.data = tool.avatar_url
	form.link.data = tool.link
	if current_user.is_confirmed:
		form.parent_category_id.data = tool.parent_category_id
		form.parent_category.data = tool.category.name
	form.why.data = tool.why
	form.edit_msg.data = ""
	return render_template('edit_tool.html',
						   form=form,
						   tool=tool,
						   is_confirmed=current_user.is_confirmed)


def render_diff(page_type, page_id, older, newer):

	if page_type == "tools":
		cls = models.Tool
	elif page_type == "categories":
		cls = models.Category
	else:
		abort(404)

	newer_data = version_class(cls).query.get_or_404((page_id, newer))
	older_data = version_class(cls).query.get_or_404((page_id, older))

	diffs = utils.find_diff(older_data, newer_data, page_type)
	for key in diffs:
		diffs[key] = utils.gen_diff_html(diffs[key][1], diffs[key][2])

	older_time = older_data.edit_time.strftime('%d %B %Y, %H:%M')
	newer_time = newer_data.edit_time.strftime('%d %B %Y, %H:%M')

	return render_template("view_diff.html",
						   id=page_id,
						   type=page_type,
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
		return_route = url_for('main.fetch_category_page', category_id=page_id)
		three_revision_route = "main.view_category_edits"
	elif page_type == "tools":
		cls = models.Tool
		return_route = url_for('main.fetch_tool_page', tool_id=page_id)
		three_revision_route = "main.view_tool_edits"
	else:
		abort(404)

	# Make sure user hasn't made more than three reverts within past 24 hours
	if not current_user.is_authenticated:
		edit_author = create_temp_user().id
	else:
		edit_author = current_user.id

	# Enforce three-revision rule
	if utils.check_if_three_time_travels(edit_author, cls, page_id):
		flash("You have already reverted this page three times within a 24 hour period. Try again later.", "warning")
		return redirect(url_for(three_revision_route, id=page_id))

	# Load whole states of current and destination
	destination_version = version_class(cls).query.get_or_404((page_id, target_version_id))
	current_version = cls.query.get_or_404(page_id)

	current_time = current_version.edit_time.strftime('%d %B %Y, %H:%M')
	destination_time = destination_version.edit_time.strftime('%d %B %Y, %H:%M')

	# Create diff
	diffs = utils.find_diff(current_version, destination_version, page_type)
	for key in diffs:
		diffs[key] = utils.gen_diff_html(diffs[key][1], diffs[key][2])

	if not current_user.is_authenticated:
		flash("You are currently not logged in. Any edits you make will publicly display your IP address. Log in or sign up to hide it.", "danger")

	form = TimeTravelForm()
	if form.validate_on_submit():
		# Overwrite entire current state with destination edit state
		current_version = utils.overwrite(current_version, destination_version, page_type)
		current_version.edit_msg = form.edit_msg.data
		current_version.edit_time = datetime.utcnow()
		current_version.edit_author = edit_author
		current_version.is_time_travel_edit = True
		db.session.commit()
		flash('This {} has been updated.'.format(page_type), 'success')
		return redirect(return_route)

	form.edit_msg.data = "Time travel back to {} from {}".format(current_time, destination_time)
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
def tool_time_travel(tool_id, target_version_id):

	return render_time_travel(page_type="tools", page_id=tool_id, target_version_id=target_version_id)


@main.route("/categories/<int:tool_id>/edit/time-travel/<int:target_version_id>", methods=["GET", "POST"])
def category_time_travel(tool_id, target_version_id):

	return render_time_travel(page_type="categories", page_id=tool_id, target_version_id=target_version_id)


# CREATE ROUTES


@main.route("/add-new-tool", methods=["GET", "POST"])
def add_new_tool():

	if not current_user.is_authenticated:
		flash(
			"You must log in or sign up to add new pages.")
		return redirect(url_for("auth.login"))
	if current_user.is_confirmed:
		form = AddNewToolFormConfirmed()
	else:
		form = AddNewToolForm()

	if form.is_submitted():
		if form.parent_category.data == "":
			flash("You must pick a parent category from the tree.", "danger")
	if form.validate_on_submit():
		if not current_user.is_authenticated:
			edit_author = create_temp_user().id
		else:
			edit_author = current_user.id
		tool = models.Tool(
			name=form.name.data,
			parent_category_id=form.parent_category_id.data,
			avatar_url=form.avatar_url.data,
			env=form.env.data.lower(),
			created=form.created.data,
			project_version=form.project_version.data,
			is_active=form.is_active.data,
			link=form.link.data,
			why=form.why.data,
			edit_author=edit_author,
			edit_time=datetime.utcnow()
		)
		db.session.add(tool)
		db.session.commit()
		session.pop('_flashes', None)
		flash('This tool has been added.', 'success')
		cache.clear()
		return redirect(url_for('.fetch_tool_page', tool_id=tool.id))
	return render_template('add_new_tool.html',
						   form=form,
						   is_confirmed=current_user.is_confirmed)


@main.route("/add-new-category", methods=["GET", "POST"])
def add_new_category():

	if not current_user.is_authenticated:
		flash(
			"You must log in or sign up to add new pages.")
		return redirect(url_for("auth.login"))
	form = AddNewCategoryForm()
	if form.validate_on_submit():
		if not current_user.is_authenticated:
			edit_author = create_temp_user().id
		else:
			edit_author = current_user.id
		if form.parent_category.data == "" or form.parent_category.data == "/" or int(form.parent_category_id.data) == 0:
			parent_category_id = None
		else:
			parent_category_id = form.parent_category_id.data
		category = models.Category(
			name=form.name.data,
			parent_category_id=parent_category_id,
			what=form.what.data,
			why=form.why.data,
			where=form.where.data,
			edit_author=edit_author,
			edit_time=datetime.utcnow()
		)
		db.session.add(category)
		db.session.commit()
		session.pop('_flashes', None)
		flash('This category has been added.', 'success')
		cache.clear()
		return redirect(url_for('.fetch_category_page', category_id=category.id))
	return render_template('add_new_category.html', form=form)
