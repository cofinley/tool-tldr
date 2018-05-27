from typing import List

from slugify import slugify
from sqlalchemy import and_

from app import models, utils


class Node:
    def __init__(self, id, name, link, is_tool=False, parent=None):
        self.id = id
        self.parent = parent
        self.name = name
        self.link = link
        self.is_tool = is_tool
        self.children = set()

    def __repr__(self):
        return "<Node {}: {}>".format(self.id, self.name)


class Tree:
    def __init__(
            self,
            query: str,
            ceiling: int = 0,
            show_links=True,
            show_root=False,
            environments=None,
            only_categories=False):
        self.query = query
        self.nodes = {}
        self.ceiling = ceiling
        self.show_links = show_links
        self.show_root = show_root
        self.environments = environments or ""
        self.only_categories = only_categories
        if self.environments:
            self.environments = utils.parse_environments(self.environments)
        self.results = []
        if self.query:
            self.find_query_results()
            self.build_tree_from_bottom()
        else:
            self.find_children_results()
            self.build_tree_from_top()

    def add_node(self, node: Node):
        if node.is_tool or node.id not in self.nodes:
            self.nodes[node.id] = node
            if node.parent:
                # Set children based on parent
                # Make sure to set children of parent nodes in self.nodes,
                #  not the children of the parent of the input arg `node`
                #  AKA tracked
                tracked_parent = self.nodes[node.parent.id]
                tracked_current = self.nodes[node.id]
                tracked_parent.children.add(tracked_current)

    def find_query_results(self):
        self.results += models.Category.query \
            .whoosh_search(self.query, like=True) \
            .order_by(models.Category.name).all()
        if not self.only_categories:
            self.results += models.Tool.query \
                .whoosh_search(self.query, like=True) \
                .order_by(models.Tool.name).all()

    def find_children_results(self):
        # Start from root/ceiling
        # Load all children cats/tools at one level below ceiling
        if self.ceiling == 0:
            categories = models.Category.query.filter_by(parent_category_id=None).order_by(models.Category.name).all()
        else:
            categories = models.Category.query.filter_by(parent_category_id=self.ceiling).order_by(
                models.Category.name).all()

            if not self.only_categories:
                # Load tools if not at root level
                if self.environments:
                    tools = models.Tool.query \
                        .filter_by(parent_category_id=self.ceiling) \
                        .filter(and_(models.Tool.environments.contains(e) for e in self.environments)) \
                        .order_by(models.Tool.name).all()
                else:
                    tools = models.Tool.query \
                        .filter_by(parent_category_id=self.ceiling) \
                        .order_by(models.Tool.name).all()

                self.results += tools
        self.results += categories

    def build_tree_from_top(self):
        if self.ceiling == 0:
            root = Node(id=0, name="/", link="/", parent=None)
            self.add_node(root)
            parent_node = root
        else:
            parent_category = models.Category.query.get_or_404(self.ceiling)
            parent_node = Node(
                id=parent_category.id,
                name=parent_category.name,
                link=self.generate_node_html(parent_category))
        self.add_node(parent_node)

        for child in self.results:
            is_tool = child.__tablename__ == "tools"
            child_node = Node(
                id=child.id,
                name=child.name,
                link=self.generate_node_html(child),
                is_tool=is_tool,
                parent=parent_node)
            self.add_node(child_node)

    def build_tree_from_bottom(self):
        # New branch for every endpoint
        for endpoint in self.results:
            endpoint_type = endpoint.__tablename__
            if endpoint_type == "categories":
                branch = utils.build_bottom_up_tree(endpoint.parent)
            else:
                branch = utils.build_bottom_up_tree(endpoint.category)
            prev = None
            if self.ceiling == 0:
                if 0 not in self.nodes:
                    root = Node(id=0, name="/", link="/", parent=prev)
                    self.add_node(root)
                else:
                    root = self.nodes[0]
                prev = root
            branch = self.filter_for_ceiling(branch)
            for item in branch:
                if item.id not in self.nodes:
                    curr = Node(
                        id=item.id,
                        name=item.name,
                        link=self.generate_node_html(item),
                        parent=prev)
                    self.add_node(curr)
                else:
                    curr = self.nodes[item.id]
                prev = curr
            # Always add endpoint, don't check if not in self.nodes
            # Endpoint usually a tool, can't check tool.id against
            # category ids in self.nodes.keys()
            is_tool = endpoint_type == "tools"
            endpoint_node = Node(
                id=endpoint.id,
                name=endpoint.name,
                link=self.generate_node_html(endpoint),
                is_tool=is_tool,
                parent=prev)
            self.add_node(endpoint_node)

    def filter_for_ceiling(self, branch: List[models.Category]) -> List[models.Category]:
        branch_ids = [c.id for c in branch]
        if self.ceiling in branch_ids:
            ceiling_idx = branch_ids.index(self.ceiling)
        else:
            ceiling_idx = 0
        return branch[ceiling_idx:]

    @staticmethod
    def generate_node_html(model_node):
        link = "<a href='/{}/{}/{}'>{}</a>".format(
            utils.escape_html(model_node.__tablename__),
            utils.escape_html(model_node.id),
            utils.escape_html(slugify(model_node.name)),
            utils.escape_html(model_node.name)
        )
        if model_node.__tablename__ == "tools":
            if model_node.environments:
                link += "<div class='tool-environments ml-1'>"
                for e in model_node.environments:
                    link += e.html
                link += "</div>"
        return link

    def pprint(self, parent: Node = None, level=0):
        root = parent or self.nodes[self.ceiling]
        print(("\t" * level) + str(root))
        if root.children:
            level += 1
            for child in root.children:
                self.pprint(parent=child, level=level)

    def to_json(self):
        if not self.nodes:
            return [{"id": -1, "label": "No results found"}]
        if self.query:
            tree = self.tree_to_json()
        else:
            tree = self.children_to_json()
            if self.show_root:
                return [{"id": 0, "label": "/", "children": tree}]
        if not isinstance(tree, list):
            tree = [tree]
        return tree

    def tree_to_json(self, parent_node: Node = None):
        parent = parent_node or self.nodes[self.ceiling]

        if parent.id == 0 and not self.show_root:
            l = []
            for child in sorted(parent.children, key=lambda c: c.name):
                l.append(self.tree_to_json(child))
            return l

        label = parent.link if self.show_links else parent.name
        d = {"id": parent.id, "label": label}
        if parent.children:
            d["children"] = []
            for child in sorted(parent.children, key=lambda c: c.name):
                d["children"].append(self.tree_to_json(child))
        else:
            if not parent.is_tool:
                # Show folder icon for category endpoints
                d["load_on_demand"] = True
        return d

    def children_to_json(self, parent_node: Node = None):
        parent = parent_node or self.nodes[self.ceiling]

        l = []
        for child in sorted(parent.children, key=lambda c: c.name):
            label = child.link if self.show_links else child.name
            c = {"id": child.id, "label": label}
            if not child.is_tool:
                c["load_on_demand"] = True
            l.append(c)
        return l
