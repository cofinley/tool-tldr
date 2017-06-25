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
