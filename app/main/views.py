import urllib
from flask import render_template, redirect, url_for, flash, request, jsonify, abort
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from . import main
from .. import models, cache, utils, db
from app.main.forms import EditProfileForm, EditProfileAdminForm, EditCategoryPageForm, EditToolPageForm
from ..decorators import admin_required, permission_required
from flask_login import login_required, current_user
from sqlalchemy import func


@main.route("/")
@main.route("/index")
@cache.cached(timeout=50)
def index():
	categories = models.Category.query.filter_by(parent=None).all()
	show_more = False
	if len(categories) > 16:
		print("More than 16 cats")
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
	subcategories = models.Category.query.filter_by(parent_category_id=category.id).all()
	subtools = models.Tool.query.filter_by(parent_category_id=category.id).all()
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
	search_tools = models.Tool.query.whoosh_search(search_query, like=True).all()
	for tool in search_tools:
		results.append({"label": tool.name, "type": "tool"})
	search_categories = models.Category.query.whoosh_search(search_query, like=True).all()
	for category in search_categories:
		results.append({"label": category.name, "type": "category"})
	return jsonify(results)


# USER ROUTES


@main.route('/user/<username>')
def user(username):
	user = models.User.query.filter_by(username=username).first_or_404()
	return render_template('user.html', user=user)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	form = EditProfileForm()
	if form.validate_on_submit():
		current_user.name = form.name.data
		current_user.about_me = form.about_me.data
		db.session.add(current_user)
		flash('Your profile has been updated.', 'success')
		return redirect(url_for('.user', username=current_user.username))
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
		return redirect(url_for('.user', username=user.username))
	form.email.data = user.email
	form.username.data = user.username
	form.confirmed.data = user.confirmed
	form.role.data = user.role_id
	return render_template('edit_profile.html', form=form, user=user)


# EDIT ROUTES


@main.route("/view_edits")
def view_edits():
	type = request.args.get("type")
	id = request.args.get("id")
	if type == "category":
		cls = models.Category
		edits_cls = models.CategoryHistory()
	elif type == "tool":
		cls = models.Tool
		edits_cls = models.ToolHistory()
	else:
		abort(404)

	Session = sessionmaker(bind=db.engine)
	session = Session()
	current_version = cls.query.get(id)
	previous_versions = session.query(edits_cls.table).filter_by(id=current_version.id).all()
	session.close()
	return render_template("view_edits.html",
						   name=current_version.name,
						   id=id,
						   type=type,
						   current_version=current_version,
						   previous_versions=previous_versions)


@main.route("/edit-category", methods=["GET", "POST"])
def edit_category_page():
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
		edits_cls = models.CategoryHistory()
	elif type == "tool":
		cls = models.Tool
		edits_cls = models.ToolHistory()

	# newer could be in regular table
	newer_version = request.args.get("newer")

	# older will always be in _history table
	older_version = request.args.get("older")

	Session = sessionmaker(bind=db.engine)
	session = Session()

	if newer_version == "current":
		newer_data = cls.query.get(id)
	else:
		newer_data = session.query(edits_cls.table).filter_by(id=id, version=newer_version).first()
	older_data = session.query(edits_cls.table).filter_by(id=id, version=older_version).first()

	session.close()

	html_results = utils.build_diff(older_data, newer_data, type)

	return render_template("view_diff.html",
						   id=id,
						   type=type,
						   name=newer_data.name,
						   older_version=older_version,
						   newer_version=newer_data.version,
						   diffs=html_results)