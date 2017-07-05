from difflib import Differ, SequenceMatcher, ndiff
from urllib.parse import urlsplit
from app import models


def build_top_down_tree():
	"""Used for explore page"""
	cat_dict = {}
	categories = models.Category.query.all()
	for category in categories:
		if category.parent is None:
			cat_dict[category.name] = {}
		else:
			# parent = [cat.name for cat in categories if category.parent_category_id == cat.id][0]
			parent = models.Category.query.filter_by(id=category.parent_category_id).first().name
			cat_dict[parent][category.name] = {}

	return cat_dict


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


def build_diff(old, new, type):

	diffs = {}

	if type == "category":
		new_what = new.what
		new_where = new.where

		old_what = old.what
		old_where = old.where

		if old_what != new_what:
			diffs["What"] = gen_diff_html(old_what, new_what)
		if old_where != new_where:
			diffs["Where"] = gen_diff_html(old_where, new_where)

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
			diffs["Avatar URL"] = gen_diff_html(old_avatar_url, new_avatar_url)
		if old_env != new_env:
			diffs["Environment"] = gen_diff_html(old_env.title(), new_env.title())
		if old_created != new_created:
			diffs["Created Date"] = gen_diff_html(old_created, new_created)
		if old_project_version != new_project_version:
			diffs["Project Version"] = gen_diff_html(old_project_version, new_project_version)
		if old_link != new_link:
			diffs["Project URL"] = gen_diff_html(old_link, new_link)

	new_name = new.name
	new_why = new.why

	old_name = old.name
	old_why = old.why

	if old_name != new_name:
		diffs["Name"] = gen_diff_html(old_name, new_name)
	if old_why != new_why:
		diffs["Why"] = gen_diff_html(old_why, new_why)

	return diffs
