from difflib import ndiff
from datetime import timedelta, datetime
from urllib.parse import urlsplit
from app import models


def build_top_down_list(category_id):
	"""Used for validating the moving of pages"""
	top_category = models.Category.query.get(category_id)
	l = [category_id]
	for child_category in top_category.children:
		l += build_top_down_list(child_category.id)
	return l


def is_at_or_below_category(chosen_id, current_id):
	"""
	Checks to see if the chosen_id is not the current_id or a child of current_id.
	This is used in page move validation. A category cannot be its own parent or child.
	Moving can only go up, not down. Otherwise circular dependencies.
	
	:param chosen_id: parent category id picked in form explore tree
	:param current_id: id of current category
	:return: bool if the chosen_id is the same or below the current_id
	"""
	return int(chosen_id) in build_top_down_list(int(current_id))


def build_bottom_up_tree(parent_category_id):
	"""Used for tool page"""
	parent_list = []

	while parent_category_id is not None:
		parent_category = models.Category.query.get(parent_category_id)
		parent_list.insert(0, parent_category)
		parent_category_id = parent_category.parent_category_id

	return parent_list


def get_hostname(url):
	name = urlsplit(url).netloc or urlsplit(url).hostname
	hostname = name.replace("www.", "")
	return hostname


def gen_diff_html(old_data, new_data):

	# Generate word-by-word diff if spaces, letter-by-letter if not
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
			diff1[index] = "<span class='diff-danger'>{}</span>".format(value.replace("- ", ""))
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
			diff2[index] = "<span class='diff-success'>{}</span>".format(value.replace("+ ", ""))
		elif value.startswith("?"):
			diff2[index] = ""
		else:
			diff2[index] = value.replace(" ", "")

	if has_spaces:
		right = " ".join(diff2)
	else:
		right = "".join(diff2)

	sides = {"left": left, "right": right}

	return sides


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
			diffs["What"] = ("what", old_what, new_what)
		if old_where != new_where:
			diffs["Where"] = ("where", old_where, new_where)
		if old_parent_category_name != new_parent_category_name:
			diffs["Parent Category"] = ("parent_category_name", old_parent_category_name, new_parent_category_name)

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
			diffs["Avatar URL"] = ("avatar_url", old_avatar_url, new_avatar_url)
		if old_env != new_env:
			diffs["Environment"] = ("env", old_env.title(), new_env.title())
		if old_created != new_created:
			diffs["Created Date"] = ("created", old_created, new_created)
		if old_project_version != new_project_version:
			diffs["Project Version"] = ("project_version", old_project_version, new_project_version)
		if old_link != new_link:
			diffs["Project URL"] = ("link", old_link, new_link)

		new_parent_category_name = new.category.name
		old_parent_category_name = old.category.name
		if old_parent_category_name != new_parent_category_name:
			diffs["Parent Category"] = ("parent_category_name", old_parent_category_name, new_parent_category_name)

	new_name = new.name
	new_why = new.why

	old_name = old.name
	old_why = old.why

	if old_name != new_name:
		diffs["Name"] = ("name", old_name, new_name)
	if old_why != new_why:
		diffs["Why"] = ("why", old_why, new_why)

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


def check_if_three_edits(user, versions):
	"""
	Look at all versions, check if provided user shows up three or more times in the past 24 hours.
	:param user: user id (ip address if anon, user id if registered)
	:param versions: sqlalchemy-continuum version table
	:return: bool if user shows up three or more times for a page
	"""
	version_in_last_24_hours = [v for v in versions if datetime.utcnow()-timedelta(hours=24) <=
													   v.edit_time <=
													   datetime.utcnow()]
	user_count = 0
	for version in version_in_last_24_hours:
		if user == version.edit_author:
			user_count += 1

	return user_count >= 3
