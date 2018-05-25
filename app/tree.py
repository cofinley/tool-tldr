from typing import List

from app import models, utils


class Node:
    def __init__(self, id, page_type: str, name, parent=None):
        self.id = id
        self.parent = parent
        self.page_type = page_type
        self.name = name
        self.children = set()

    def __repr__(self):
        return "<Node: {}{}>".format(self.page_type.upper(), self.id)


class Tree:
    def __init__(self, query: str, nodes=None, ceiling=0):
        self.query = query
        self.nodes = nodes or {}
        self.ceiling = ceiling
        self.results = None
        self.find_query_results()
        self.build_tree_from_results()

    def add_node(self, node: Node):
        if node.id not in self.nodes:
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
        if self.query:
            self.results = \
                models.Category.query.whoosh_search(self.query, like=True).all() \
                + models.Tool.query.whoosh_search(self.query, like=True).all()
        else:
            pass

    def build_tree_from_results(self):
        # New branch for every endpoint
        for endpoint in self.results:
            endpoint_type = endpoint.__tablename__
            prefix = endpoint_type[0]
            if endpoint_type == "categories":
                branch = utils.build_bottom_up_tree(endpoint.parent)
            else:
                branch = utils.build_bottom_up_tree(endpoint.category)
            prev = None
            if self.ceiling == 0:
                root = Node(0, "r", prev)
                self.nodes[0] = root
                prev = root
            branch = self.filter_for_ceiling(branch)
            for item in branch:
                curr = Node(id=item.id, page_type="c", name=item.name, parent=prev)
                self.add_node(curr)
                prev = curr
            endpoint_node = Node(endpoint.id, page_type=prefix, name=endpoint.name, parent=prev)
            self.add_node(endpoint_node)

    def filter_for_ceiling(self, branch: List[models.Category]) -> List[models.Category]:
        branch_ids = [c.id for c in branch]
        if self.ceiling in branch_ids:
            ceiling_idx = branch_ids.index(self.ceiling)
        else:
            ceiling_idx = 0
        return branch[ceiling_idx:]

    def pprint(self, parent=None, level=0):
        root = parent or [node for node in self.nodes.values() if node.parent is parent][0]
        print(("\t" * level) + str(root))
        if root.children:
            level += 1
            for child in root.children:
                self.pprint(parent=child, level=level)
