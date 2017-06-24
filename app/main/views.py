from flask import render_template, redirect, url_for, abort, flash, request, jsonify, current_app
from . import main
from .. import models, cache, utils, db
from app.main.forms import EditProfileForm, EditProfileAdminForm
from app.auth.forms import LoginForm, RegistrationForm
from ..decorators import admin_required, permission_required
from flask_login import login_required, current_user


# timestamp=datetime.datetime.utcnow()


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


@main.route("/explore", defaults={"category": ""})
@main.route("/explore/<path:category>")
def browse_categories(category):
	queried_env = request.args.get("env")
	if category:
		main_category = models.Category.query.filter_by(name=category).first()
		title = main_category.name
		children_categories = [category for category in models.Category.query.filter_by(parent_id=main_category.id).all()]
		if queried_env:
			children_tools = [tool for tool in models.Tool.query
				.filter_by(parent_category_id=main_category.id)
				.filter_by(env=queried_env)
				.all()]
		else:
			children_tools = [tool for tool in models.Tool.query.filter_by(parent_category_id=main_category.id).all()]
		tree = {}
		for i in (children_categories + children_tools):
			tree[i] = {}
	else:
		title = "Explore"
		categories = [category for category in models.Category.query.filter_by(parent_id=None)]
		# tree = utils.build_top_down_tree()
		tree = {}
		for i in categories:
			tree[i] = {}

	return render_template("explore.html",
						   title=title,
						   tree=tree)


@main.route("/tools/<path:tool_name>")
def fetch_tool_page(tool_name):
	tool = models.Tool.query.filter_by(name_lower=tool_name.lower()).first()

	# KEEP THESE B/C USERS MAY WANT TO SPECIFY ALTERNATIVES THEMSELVES RATHER THAN
	#   RELYING ON AGREED-UPON PARENT CATEGORIES
	# this_env = tool.env
	# alts_for_this_env = tool.dest_alts.filter_by(env=this_env).all()
	# alts_for_other_envs = tool.dest_alts.filter(models.Tool.env != this_env).all()

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
						   content=tool,
						   env_alts=alts_for_this_env,
						   other_alts=alts_for_other_envs,
						   tree=category_tree,
						   link=project_link)


@main.route("/search")
def search_tools():
	tool_name_query = request.args.get("term")
	results = []
	search = models.Tool.query.whoosh_search(tool_name_query, like=True).all()
	for result in search:
		results.append(result.name)
	return jsonify(results)


@main.route('/user/<username>')
def user(username):
	user = models.User.query.filter_by(username=username).first_or_404()
	return render_template('user.html', user=user)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	form = EditProfileForm()
	if form.validate_on_submit():
		current_user.username = form.username.data
		db.session.add(current_user)
		flash('Your profile has been updated.')
		return redirect(url_for('.user', username=current_user.username))
	form.username.data = current_user.username
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
		flash('The profile has been updated.')
		return redirect(url_for('.user', username=user.username))
	form.email.data = user.email
	form.username.data = user.username
	form.confirmed.data = user.confirmed
	form.role.data = user.role_id
	return render_template('edit_profile.html', form=form, user=user)


@main.route("/view_all_edits/<tool_name>")
def view_edits(tool_name):
	current_version = models.Tool.query.filter_by(name=tool_name).first()
	session = models.load_tool_history_session()
	previous_versions = session.query(models.ToolHistory).filter(models.ToolHistory.id == current_version.id).all()
	return render_template("view_edits.html",
					tool_name=tool_name,
					current_version=current_version,
					previous_versions=previous_versions)