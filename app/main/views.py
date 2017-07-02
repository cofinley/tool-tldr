import urllib
from flask import render_template, redirect, url_for, flash, request, jsonify
from sqlalchemy.orm import sessionmaker

from . import main
from .. import models, cache, utils, db
from app.main.forms import EditProfileForm, EditProfileAdminForm
from ..decorators import admin_required, permission_required
from flask_login import login_required, current_user
from sqlalchemy import func


@main.route("/")
@main.route("/index")
@cache.cached(timeout=50)
def index():
	categories = [category.name for category in models.Category.query.filter_by(parent=None)]
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
		label_link = "<a href='/categories/{}'>{}</a>".format(urllib.parse.quote(result["name"]), result["name"])
		result.pop("name")
		result["label"] = label_link
		result["load_on_demand"] = True

	return jsonify(results)


@main.route("/categories/<path:category_name>")
def fetch_category_page(category_name):
	category = models.Category.query.filter(func.lower(models.Category.name) == func.lower(category_name)).first()
	subcategories = models.Category.query.filter_by(parent_category_id=category.id).all()
	subtools = models.Tool.query.filter_by(parent_category_id=category.id).all()
	category_tree = utils.build_bottom_up_tree(category.id)

	return render_template("category.html",
						   category=category,
						   subcategories=subcategories,
						   subtools=subtools,
						   breadcrumbs=category_tree)


@main.route("/tools/<path:tool_name>")
def fetch_tool_page(tool_name):
	tool = models.Tool.query.filter(func.lower(models.Tool.name) == func.lower(tool_name)).first()

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
	name = request.args.get("name")
	if type == "categories":
		cls = models.Category
		edits_cls = models.CategoryHistory()
	if type == "tools":
		cls = models.Tool
		edits_cls = models.ToolHistory()

	Session = sessionmaker(bind=db.engine)
	session = Session()
	current_version = cls.query.filter_by(name=name).first()
	previous_versions = session.query(edits_cls.table).filter_by(id=current_version.id).all()
	session.close()
	return render_template("view_edits.html",
						   name=name,
						   current_version=current_version,
						   previous_versions=previous_versions)