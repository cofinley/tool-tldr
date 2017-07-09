import urllib
import ipaddress
from flask import render_template, redirect, url_for, flash, request, jsonify, abort, current_app
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from . import main
from .. import models as models
from .. import cache, utils, db
from app.main.forms import EditProfileForm, EditProfileAdminForm, EditCategoryPageForm, EditToolPageForm, TimeTravelForm
from ..decorators import admin_required, permission_required
from flask_login import login_required, current_user
from sqlalchemy_continuum import version_class





@main.route("/")
@main.route("/index")
@cache.cached(timeout=50)
def index():
	categories = models.Category.query.filter_by(parent=None).all()
	show_more = False
	if len(categories) > 16:
		show_more = True
	return render_template("index.html",
						   categories=categories[:16],
						   show_more=show_more)


@main.route("/explore")
def browse_categories():
	title = "Explore"
	return render_template("explore.html",
						   title=title)


@main.route("/explore_nodes/")
def explore_nodes():
	node_id = request.args.get("node")
	if node_id:
		children = models.Category.query.filter_by(parent_category_id=node_id).all()
	else:
		children = models.Category.query.filter_by(parent_category_id=None).all()

	cols = ['id', 'name']
	results = [{col: getattr(child, col) for col in cols} for child in children]

	# Rename 'name' key as 'label' for jqTree
	for result in results:
		label_link = "<a href='/categories?id={}'>{}</a>".format(result["id"], result["name"])
		result.pop("name")
		result["label"] = label_link
		result["load_on_demand"] = True

	return jsonify(results)


@main.route("/categories")
def fetch_category_page():
	id = request.args.get("id")
	category = models.Category.query.get_or_404(id)
	subcategories = category.children
	subtools = category.tools.all()
	category_tree = utils.build_bottom_up_tree(category.id)

	return render_template("category.html",
						   category=category,
						   subcategories=subcategories,
						   subtools=subtools,
						   breadcrumbs=category_tree)


@main.route("/tools")
def fetch_tool_page():
	id = request.args.get("id")
	tool = models.Tool.query.get_or_404(id)

	alts_for_this_env = models.Tool.query\
		.filter_by(parent_category_id=tool.parent_category_id)\
		.filter_by(env=tool.env)\
		.filter(models.Tool.id != tool.id)\
		.all()
	alts_for_other_envs = models.Tool.query\
		.filter(models.Tool.parent_category_id == tool.parent_category_id)\
		.filter(models.Tool.env != tool.env)\
		.all()

	category_tree = utils.build_bottom_up_tree(tool.parent_category_id)

	project_link = utils.get_hostname(tool.link)

	return render_template("tool.html",
						   tool=tool,
						   env_alts=alts_for_this_env,
						   other_alts=alts_for_other_envs,
						   tree=category_tree,
						   link=project_link)


@main.route("/search")
def search_tools():
	search_query = request.args.get("term")
	results = []
	queried_tools = models.Tool.query.whoosh_search(search_query, like=True).all()
	for tool in queried_tools:
		results.append({"label": tool.name, "type": "tool", "id": tool.id})
	search_categories = models.Category.query.whoosh_search(search_query, like=True).all()
	for category in search_categories:
		results.append({"label": category.name, "type": "category", "id": category.id})
	return jsonify(results)


# USER ROUTES


@main.route('/users')
def user():
	id = request.args.get("id")
	user = models.User.query.get(id)
	Session = sessionmaker(bind=db.engine)
	session = Session()
	tool_edits = session.query(version_class(models.Tool)).filter_by(edit_author=id).all()
	category_edits = session.query(version_class(models.Category)).filter_by(edit_author=id).all()
	return render_template('user.html',
						   user=user,
						   tool_edits=tool_edits,
						   category_edits=category_edits)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	form = EditProfileForm()
	if form.validate_on_submit():
		current_user.name = form.name.data
		current_user.about_me = form.about_me.data
		db.session.add(current_user)
		flash('Your profile has been updated.', 'success')
		return redirect(url_for('.user', id=current_user.id))
	form.name.data = current_user.name
	form.about_me.data = current_user.about_me
	return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
	user = models.User.query.get_or_404(id)
	form = EditProfileAdminForm(user=user)
	if form.validate_on_submit():
		user.email = form.email.data
		user.username = form.username.data
		user.confirmed = form.confirmed.data
		user.role = models.Role.query.get(form.role.data)
		db.session.add(user)
		flash('The profile has been updated.', 'success')
		return redirect(url_for('.user', id=user.id))
	form.email.data = user.email
	form.username.data = user.username
	form.confirmed.data = user.confirmed
	form.role.data = user.role_id
	return render_template('edit_profile.html', form=form, user=user)


# EDIT ROUTES


@main.route("/view_edits")
def view_edits():
	page = request.args.get("page", 1, type=int)
	type = request.args.get("type")
	id = request.args.get("id")
	if type == "category":
		cls = models.Category
	elif type == "tool":
		cls = models.Tool
	else:
		abort(404)

	all = version_class(cls).query.all()
	latest_version_id = all[-1].transaction_id
	first_version_id = all[0].transaction_id
	pagination = version_class(cls).query.filter_by(id=id)\
		.order_by(version_class(cls).transaction_id.desc())\
		.paginate(page, per_page=current_app.config['EDITS_PER_PAGE'], error_out=False)
	versions = list(reversed(pagination.items))
	return render_template("view_edits.html",
						   id=id,
						   type=type,
						   pagination=pagination,
						   latest_version_id=latest_version_id,
						   first_version_id=first_version_id,
						   current_version=versions[-1],
						   previous_versions=versions[:-1])


@main.route("/edit-category", methods=["GET", "POST"])
def edit_category_page():
	if not current_user.is_authenticated:
		flash("You are currently not logged in. Any edits you make will publicly display your IP address. Log in or sign up to hide it.", "danger")
	id = request.args.get("id")
	category = models.Category.query.get_or_404(id)
	form = EditCategoryPageForm()
	if form.validate_on_submit():
		category.name = form.name.data
		category.what = form.what.data
		category.why = form.why.data
		category.where = form.where.data
		category.edit_msg = form.edit_msg.data
		category.edit_time = datetime.utcnow()
		if not current_user.is_authenticated:
			edit_author = request.remote_addr
		else:
			edit_author = current_user.id
		category.edit_author = edit_author
		db.session.add(category)
		flash('This category has been updated.', 'success')
		return redirect(url_for('.fetch_category_page', id=category.id))
	form.name.data = category.name
	form.what.data = category.what
	form.why.data = category.why
	form.where.data = category.where
	form.edit_msg.data = ""
	return render_template('edit_category.html', form=form, category=category)


@main.route("/edit-tool", methods=["GET", "POST"])
def edit_tool_page():
	if not current_user.is_authenticated:
		flash("You are currently not logged in. Any edits you make will publicly display your IP address. Log in or sign up to hide it.", "danger")
	id = request.args.get("id")
	tool = models.Tool.query.get_or_404(id)
	form = EditToolPageForm()

	if form.validate_on_submit():
		tool.name = form.name.data
		tool.avatar_url = form.avatar_url.data
		tool.env = form.env.data.lower()
		tool.created = form.created.data
		tool.project_version = form.project_version.data
		tool.link = form.link.data
		tool.why = form.why.data
		tool.edit_msg = form.edit_msg.data
		tool.edit_time = datetime.utcnow()
		if not current_user.is_authenticated:
			edit_author = request.remote_addr
		else:
			edit_author = current_user.id
		tool.edit_author = edit_author
		flash('This tool has been updated.', 'success')
		return redirect(url_for('.fetch_tool_page', id=tool.id))
	form.name.data = tool.name
	form.avatar_url.data = tool.avatar_url
	form.env.data = tool.env.title()
	form.created.data = tool.created
	form.project_version.data = tool.project_version
	form.link.data = tool.link
	form.why.data = tool.why
	form.edit_msg.data = ""
	return render_template('edit_tool.html', form=form, tool=tool)


@main.route("/view-diff")
def view_diff():

	id = request.args.get("id")
	type = request.args.get("type")

	if type == "category":
		cls = models.Category
	elif type == "tool":
		cls = models.Tool
	else:
		abort(403)

	# Version numbers
	newer_version = int(request.args.get("newer"))
	older_version = int(request.args.get("older"))

	newer_data = version_class(cls).query.get((id, newer_version))
	older_data = version_class(cls).query.get((id, older_version))

	diffs = utils.find_diff(older_data, newer_data, type)
	for key in diffs:
		diffs[key] = utils.gen_diff_html(diffs[key][1], diffs[key][2])

	older_time = older_data.edit_time.strftime('%d %B %Y, %H:%M')
	newer_time = newer_data.edit_time.strftime('%d %B %Y, %H:%M')

	return render_template("view_diff.html",
						   id=id,
						   type=type,
						   name=newer_data.name,
						   older_time=older_time,
						   newer_time=newer_time,
						   diffs=diffs)


@main.route("/time-travel", methods=["GET", "POST"])
def undo():

	id = request.args.get("id")
	type = request.args.get("type")

	if type == "category":
		cls = models.Category
		return_route = '.fetch_category_page'
	elif type == "tool":
		cls = models.Tool
		return_route = '.fetch_tool_page'
	else:
		abort(403)

	# Make sure user hasn't made more than three reverts within past 24 hours
	if not current_user.is_authenticated:
		edit_author = request.remote_addr
	else:
		edit_author = current_user.id

	if utils.check_if_three_edits(edit_author, cls.query.get_or_404(id).versions):
		flash("You have already reverted this page three times within a 24 hour period. Try again later.", "warning")
		return redirect(url_for('main.view_edits', id=id, type=type))

	version = request.args.get("target_version")
	destination_version = version_class(cls).query.get_or_404((id, version))
	current_version = cls.query.get_or_404(id)

	current_time = current_version.edit_time.strftime('%d %B %Y, %H:%M')
	destination_time = destination_version.edit_time.strftime('%d %B %Y, %H:%M')

	diffs = utils.find_diff(current_version, destination_version, type)
	for key in diffs:
		diffs[key] = utils.gen_diff_html(diffs[key][1], diffs[key][2])

	if not current_user.is_authenticated:
		flash("You are currently not logged in. Any edits you make will publicly display your IP address. Log in or sign up to hide it.", "danger")

	form = TimeTravelForm()
	if form.validate_on_submit():
		# Overwrite entire current state with destination edit state
		current_version = utils.overwrite(current_version, destination_version, type)
		current_version.edit_msg = form.edit_msg.data
		current_version.edit_time = datetime.utcnow()
		current_version.edit_author = edit_author
		db.session.commit()
		flash('This {} has been updated.'.format(type), 'success')
		return redirect(url_for(return_route, id=id))

	form.edit_msg.data = "Time travel back to {} from {}".format(current_time, destination_time)
	return render_template("undo.html",
						   id=id,
						   type=type,
						   name=current_version.name,
						   form=form,
						   current_time=current_time,
						   destination_time=destination_time,
						   diffs=diffs,
						   current_version=current_version)


# JINJA FUNCTIONS

@main.context_processor
def utility_processor():
	# IP validator
	def is_ip(input):
		try:
			ipaddress.ip_address(str(input))
			return True
		except ValueError:
			return False
	return dict(is_ip=is_ip)
