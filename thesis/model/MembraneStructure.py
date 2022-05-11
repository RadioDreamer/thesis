class Node:
    """
    A class for representing a node in the tree structure of a membrane
    system's regions

    Attributes
    ----------
    id : int
        the unique identifier of the node
    parent : Node
        the parent node
    children : list[Node]
        the list of nodes whose parent is `self`
    """

    uid = 0

    def __init__(self, parent=None):
        """
        A function used to initialize the `Node` instance

        Parameters
        ----------
        parent : Node, optional
            the parent of the node (default is None)
        """

        self.id = Node.uid
        Node.uid += 1
        self.parent = parent
        self.children = []

    def __getitem__(self, item):
        """
        A function used to get a child node at a given index

        `item` must be integer and in range [0, len(self.children)]

        Parameters
        ----------
        item : int
            the index of the children

        Returns
        -------
        Node
            the child node at the index `item`
        """

        assert isinstance(item, int)
        assert item < len(self.children)
        return self.children[item]

    def __str__(self):
        """
        A function used to generate the string representation of the node

        Returns
        -------
        str
            the string containing the node's information
        """

        return f"Node: {self.id=}"

    def __repr__(self):
        """
        A function used to generate the instance's representation

        Returns
        -------
        str
            the string containing the node's information
        """
        return self.__str__()

    def add_child(self, node=None):
        """
        A function used to add a node as child to another node

        if `node` is not given then we create a new node to add as child

        Parameters
        ----------
        node : Node, optional
            the node to be added as a child (default is None)
        """

        if node is None:
            self.children.append(Node())
        else:
            self.children.append(node)
        node.parent = self

    def is_leaf(self):
        """
        A function used to determine whether the node is a leaf

        A leaf has no children

        Returns
        -------
        bool
            True if the node is a leaf, False otherwise
        """

        return len(self.children) == 0

    def num_of_children(self):
        """
        A function used to calculate the number of children the node has

        Returns
        -------
        int
            the number of children
        """

        return len(self.children)

    def set_parent(self, new_parent):
        """
        A function used to modify the parent of the node

        Parameters
        ----------
        new_parent : Node
            the new parent of the node
        """

        self.parent = new_parent


class MembraneStructure:
    """
    A class for representing the tree structure of a membrane system

    Attributes
    ----------
    skin : Node
        the root node of the tree structure
    result : object
        the returned value of a preorder traversal
    """

    def __init__(self, root):
        """
        A functioned used to initialize a `MembraneStructure` instance

        Parameters
        ----------
        root : Node
            the root node of the tree structure
        """

        self.skin = root
        self.result = None

    def get_root_id(self):
        """
        A function to return the identifier of the root node

        Returns
        -------
        int
            the identifier of the root node
        """

        return self.skin.id

    def preorder(self, root, fn, cond):
        """
        A function used to traverse the tree in a preorder way

        If `cond` evaluates to True on a given node, then the result of applying
        `fn` to that node is put in the field `result`

        Parameters
        ----------
        root : Node
            the root node in the current (sub)tree
        fn
            the function to evaluate on the node fulfilling the condition
        cond
            the condition to check on the nodes
        """

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
        """
        A static function used to return the number of children of a node

        It is designed to be passed in to `preorder` function as `fn` parameter

        Parameters
        ----------
        node : Node
            the node whose children's number we want to return

        Returns
        -------
        int
            the number of children
        """

        return node.num_of_children()

    @staticmethod
    def get_parent(node):
        """
        A static function used to return the parent of the given node

        It is designed to be passed in to `preorder` function as `fn` parameter

        Parameters
        ----------
        node : Node
            the node whose parent we want to return

        Returns
        -------
        Node
            the parent node
        """

        return node.parent

    @staticmethod
    def get_all_children(node):
        """
        A static function used to return all the children of the given node

        It is designed to be passed in to `preorder` function as `fn`

        Parameters
        ----------
        node : Node
            the node whose children we want to return

        Returns
        -------
        list
            the list of child (None if `node` is a leaf)
        """

        if node.is_leaf():
            return None
        else:
            return node.children

    def remove_node(self, node):
        """
        A function used to remove a node from the membrane structure

        The removed node's children will be the children of its' parent node

        Parameters
        ----------
        node : Node
            the node we want to remove

        Returns
        -------
        Node
            the parent of the removed node (None if `node` is a leaf)
        """

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
        """
        A static function used to add a node as child to the given node

        It is designed to be passed in to `preorder` function as `fn`
        
        Parameters
        ----------
        node : Node
            the node we want to add the child to
        """

        node.add_child(Node())
