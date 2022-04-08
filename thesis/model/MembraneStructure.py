# This Python file uses the following encoding: utf-8

class Node:
    uid = 0

    def __getitem__(self, item):
        assert isinstance(item, int)
        assert item < len(self.children)
        return self.children[item]

    def __str__(self):
        return f"Node: {self.id=}"

    def __repr__(self):
        return self.__str__()

    def __init__(self, parent=None):
        self.id = Node.uid
        Node.uid += 1
        self.parent = parent
        self.children = []

    def add_child(self, node=None):
        if node is None:
            self.children.append(Node())
        else:
            self.children.append(node)
        node.parent = self

    def is_leaf(self):
        return len(self.children) == 0

    def num_of_children(self):
        return len(self.children)

    def set_parent(self, new_parent):
        self.parent = new_parent


class MembraneStructure:
    def __init__(self, root):
        self.skin = root
        self.result = None

    def get_root_id(self):
        return self.skin.id

    def preorder(self, root, fn, cond):
        if root is None:
            return
        if cond(root):
            self.result = fn(root)
        else:
            iter_count = root.num_of_children()
            for i in range(iter_count):
                self.preorder(root.children[i], fn, cond)

    @staticmethod
    def get_num_of_children(node):
        return node.num_of_children()

    @staticmethod
    def get_parent(node):
        return node.parent

    @staticmethod
    def get_all_children(node):
        if node.is_leaf():
            return None
        else:
            return node.children

    def remove_node(self, node):
        if node.id == self.get_root_id():
            return None
        parent = node.parent
        for child in node.children:
            child.parent = parent
        parent.children.extend(node.children)
        parent.children.remove(node)
        return parent

    @staticmethod
    def add_node(node):
        node.add_child(Node())
