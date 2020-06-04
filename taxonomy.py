import re
from collections.abc import Collection

class Node(Collection):

    def __init__(self, index, name, synonyms, parent, children=None):
        self.index = index
        self.name = name
        self.parent = parent
        self.synonyms = synonyms

        if children is None:
            self.children = []
        else:
            self.children = children

        self.u = .0
        self.G = []
        self.L = []
        self.V = .0
        self.v = .0
        self.p = .0
        self.H = []

    def __contains__(self, item):
        return item in self.children

    def __iter__(self):
        for item in self.children:
            yield item

    def __len__(self):
        return len(self.children)

    def __setattr__(self, name, value):
        self.__dict__[name] = value

    def __getattr__(self, name):
        if name not in self.__dict__:
            return None
        return self.__dict__[name]

    @property
    def leaf_cluster(self):
        leaves = []

        def find_leaves(self):
            if self.is_internal:
                for child in self.children:
                    find_leaves(child)
            else:
                leaves.append(self)

        find_leaves(self)
        return leaves

    @property
    def is_leaf(self):
        return not self.children

    @property
    def is_internal(self):
        return bool(self.children)

    @property
    def is_root(self):
        return self.parent is None


class Taxonomy:

    def __init__(self, filename):
        self._root = self.get_taxonomy_tree(filename)
    @property
    def root(self):
        return self._root

    # @staticmethod
    # def get_index_and_name(node_repr):
    #     index_s, name_s = node_repr
    #     if (name_s.group(0)[-1].isalpha() or name_s.group(0)[-1] == "'"):
    #         return index_s.group(0)[:-1], name_s.group(0)[1:].lower().strip()
    #     return index_s.group(0)[:-1], name_s.group(0)[1:-1].lower().strip()

    def get_taxonomy_tree(self, filename):
        nodes = []
        with open(filename, 'r') as file_opened:
            for line in file_opened:
                match = re.search(r'(\d[\.\d]*),+([\w\s\-]+),+"?([\w\s,]+)?"?', line)
                if match:
                    index = match.group(1).rstrip('.')
                    name = match.group(2).strip()
                    synonyms = match.group(3).strip()
                    nodes.append([index, name, synonyms])

        root_found = True
        root_index = nodes[0][0]
        for index, _, _ in nodes[1:]:
            if not index.startswith(root_index):
                root_found = False
                break

        if root_found:
            index, name, synonyms = nodes[0]
            tree = Node(index, name, synonyms, None)
            nodes = nodes[1:]
        else:
            tree = Node("0", "root", "", None)
            for node in nodes:
                node[0] = tree.index + '.' + node[0]

        curr_parent = tree

        for node in nodes:
            index, name, synonyms = node
            # если текущий родитель - не родитель текущей вершины
            while not index.startswith(curr_parent.index):
                if curr_parent.parent is not None:
                    curr_parent = curr_parent.parent

            curr_node = Node(index, name, synonyms, curr_parent)
            curr_parent.children.append(curr_node)
            curr_parent = curr_node

        return tree
