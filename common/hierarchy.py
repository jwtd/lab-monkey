#!/usr/bin/env python

from common.base import *

class Node(AppBase):
    """
    Node represents a single point within a Hierarchy. Nodes can may or may not contain child nodes.
    """

    entity_name = 'node'
    entity_atts = ['id', 'label', 'allows_children']

    def __init__(self, id = None, label = None, allows_children = True, parent = None):
        # Prepare Parent
        super(Node, self).__init__()

        # Identity references
        self.id    = id  # Unique id
        self.label = label if label else id
        
        # Hierarchy references
        self.parent = parent
        self._allows_children = allows_children       
        self._children = []  # Ordered stack of children


    def __str__(self):
        """Returns the label of the node."""
        return str(self.label)

    def __len__(self):
        """Returns the number of child nodes."""
        return len(self._children)

    def __getitem__(self, label_or_index):
        """Returns a reference to the node with the index or label specified."""
        try:
            n = self._children[int(label_or_index)]
        except ValueError:
            i = self.index_of_first_child_with('label', label_or_index)
            if i != None:
                n = self._children[i]
            else:
                raise LookupError('Could not find node %s' % label_or_index)
        except:
            raise LookupError('Could not find node %s' % label_or_index)
        return n
    
    # Family References --------------------------------------------

    @property
    def root(self):
        """Returns a reference to the root node."""
        node = self
        while node.parent != None:
            node = node.parent
        return node

    @property
    def is_root(self):
        """Returns True or False reflecting whether this node is a root node."""
        if self.parent == None:
            return True
        else:
            return False

    @property
    def is_parent(self):
        """Returns True or False reflecting whether this node has children."""
        if self._children:
            return True
        else:
            return False

    @property
    def allows_children(self):
        """Returns True or False reflecting whether or not this node can have child nodes."""
        return self._allows_children

    @property
    def children(self):
        """Returns a list of the node instances child nodes."""
        if self._allows_children:
            return tuple(self._children)
        else:
            return None

    @property
    def local_index(self):
        """The index this node is located at within its parents child colleciton."""
        if self.is_root:
            return 0
        else:
            return self.parent.index_of_child_node(self)

    @property
    def global_index(self):
        """The index this node is located at relative to the root."""
        if self.is_root:
            return 0
        else:
            s = self.previous_sibling
            if s != None:
                return s.global_index + s.width
            else:
                return self.parent.global_index

    @property
    def width(self):
        """The number of end points bellow the node instance."""
        if self.is_parent:
            w = 0
            for c in self._children:
                if c.is_parent:
                    w += c.width                    
                else:
                    w += 1
        else:
            w = 1
        return w
    
    @property
    def global_extents(self):
        """
        Returns a tuple containing the node instance's left and right global indexes.
            left  = global index 
            right = lobal index + width
        """
        return (self.global_index, self.global_index + self.width)
    
    @property
    def is_first(self):
        """Returns True or False reflecting whether this node is the first child in it's parent's children colleciton."""
        if self.local_index == 0:
            return True
        else:
            return False

    @property
    def is_last(self):
        """Returns True or False reflecting whether this node is the last child in it's parent's children colleciton."""
        if self.parent == None or self.local_index == len(self.parent.children)-1:
            return True
        else:
            return False

    @property
    def previous_sibling(self):
        """Returns a reference to the node that comes immediately before the node instance in it's parents children collection."""
        if self.is_first:
            return None
        else:
            return self.parent[self.local_index-1]

    @property
    def next_sibling(self):
        """Returns a reference to the node that comes immediately after the node instance in it's parents children collection."""
        if self.is_last:
            return None
        else:
            return self.parent[self.local_index+1]

    @property
    def path(self):
        """Returns a normalized path to the node instance from the root."""
        if self.is_root:
            return methodize_label(self.label)
        else:
            return '%s.%s' % (self.parent.path, methodize_label(self.label))

    @property
    def depth(self):
        """Returns the number of levels deep the target node is from the root as base 0."""
        if self.is_root:
            return 0
        else:
            return self.parent.depth + 1

        
    # Family Manipulation --------------------------------------------


    # Collection modifier
    def add_node(self, node, index = None):
        """
        Adds a node to this node's children. The node will be added to the 
        end by default, or alternatively at the index specified.
        """
        if not self._allows_children:
            raise AttributeError('This node cannot accept children')
        node.parent = self
        if index == None:
            self._children.append(node)
        else:
            self._children.insert(index, node)
        # Metaprogram reference to children
        #append_reference(self, node.label, node)
        return node

    def delete_child_at_index(self, index):
        """Removes the node instance's child node which exists at the index provided."""
        del self._children[index]
        # Remmove metaprogrammed reference

    def delete_child(self, node):
        """Removes the provided child node from it's parents collection."""
        for i,c in enumerate(self._children):
            if c.id == node.id:
                del self._children[i]
        # Remmove metaprogrammed reference

    def delete_children_with(self, property, value):
        """Removes child nodes from the node instance, which have the value provided for the property specified."""
        matches = []
        for i,c in enumerate(self._children):
            if getattr(c, property) == value:
                matches.append(i)
        matches.reverse()
        for i in matches:
            del self._children[i]
        
        
    # Child Collection Searching --------------------------------------------


    # Collection searching
    def index_of_child_node(self, node):
        """Returns the index of the node provided or -1 if the node is not found."""
        for i,c in enumerate(self._children):
            if c == node:
                return i
        return -1

    def index_of_first_child_with(self, property, value):
        """Returns the index of the child node whose property matches the value or -1 if the ID is not found."""
        for i,c in enumerate(self._children):
            if getattr(c, property) == value:
                return i
        return None

    def children_with(self, property, value):
        """Returns a list of child node references which have the value for the property."""
        matches = []
        for c in self._children:
            if getattr(c, property) == value:
                matches.append(c)
        return matches

       
    # Child Iteration --------------------------------------------


    def __iter__(self):
        """Iteratation returns sucsesive references to this nodes child nodes."""
        return NodeIterator(self)

    @property
    def previous_siblings(self):
        """Returns sucsesive references to the nodes that came before this node in it's parent's child collection."""
        return NodeIterator(self.parent, stop = self.local_index)

    @property
    def next_siblings(self):
        """Returns sucsesive references to the nodes that come after this node in it's parent's child collection."""
        return NodeIterator(self.parent, start = self.local_index)
        


class NodeIterator(object):
    """Node itterator."""
    
    def __init__(self, target, start = -1, stop = None):
        self.target  = target
        self.current = start
        if stop == None: 
            self.stop = len(target)
        else:
            self.stop = stop            

    def __iter__(self):
        return self

    def next(self):
        current = self.current + 1
        self.current = current
        if current >= self.stop:
            raise StopIteration
        return self.target[current]



if __name__ == '__main__':
    pass