#!/usr/bin/env python

from unittest import TestCase, main

import yaml

from common.hierarchy import *

class NodeTests(TestCase):
    """Test Hierarchy Node Class"""
    
    def setUp(self):
        self.node = Node(1, 'Test')

    def test_init(self):
        pass
        
    def test_label(self):
        """Valid creation of a node"""
        n = Node(1)
        self.assertEqual('%s' % n, '1')
        n = Node(1, 'Test')
        self.assertEqual('%s' % n, 'Test')
        n.label = 'Changed'
        self.assertEqual('%s' % n, 'Changed')
        
    def test_family_references(self):
        """Test root references"""
        p = Node(1, 'Parent')
        c1 = Node(2, 'Child 1')
        c2 = Node(3, 'Child 2')
        c3 = Node(4, 'Child 3')
        c4 = Node(5, 'Child 4')
        c5 = Node(6, 'Child 5')
        p.add_node(c1)
        p.add_node(c2)
        p.add_node(c3)
        p.add_node(c4)
        c4.add_node(c5)
        
        # Test previous_sibling
        self.assertEqual(c1.previous_sibling, None)
        self.assertEqual(c2.previous_sibling, c1)
        
        # Test next_sibling
        self.assertEqual(c3.next_sibling, c4)
        self.assertEqual(c4.next_sibling, None)
        
        # Test path
        self.assertEqual(c5.path, 'parent.child_4.child_5')

        # Test depth
        self.assertEqual(p.depth, 0)
        self.assertEqual(c4.depth, 1)
        self.assertEqual(c5.depth, 2)

        # Test len
        self.assertEqual(len(p), 4)

        # Test width
        self.assertEqual(p.width, 4)
        self.assertEqual(c3.width, 1)
        self.assertEqual(c4.width, 1)
        self.assertEqual(c5.width, 1)

        # Test local_index
        self.assertEqual(c3.local_index, 2)
        
        # Test global_index
        self.assertEqual(p.global_index, 0)
        self.assertEqual(c3.global_index, 2)
        self.assertEqual(c4.global_index, 3)
        self.assertEqual(c5.global_index, 3)
        
        # Test global_extents        
        self.assertEqual(p.global_extents, (0,4))
        self.assertEqual(c3.global_extents, (2,3))
        self.assertEqual(c4.global_extents, (3,4))
        self.assertEqual(c5.global_extents, (3,4))

        # Test root identity
        self.assertEqual(p.root.id, 1)
        self.assertEqual(c1.root.id, 1)
        self.assertEqual(c4.root.id, 1)
        
        # Test is_root
        self.assertEqual(p.is_root, True)
        self.assertEqual(c1.is_root, False)
        self.assertEqual(c4.is_root, False)

        # Test is_parent
        self.assertEqual(p.is_parent, True)
        self.assertEqual(c1.is_parent, False)
        self.assertEqual(c5.is_parent, False)
        
        # Test is_first
        self.assertEqual(p.is_first, True)
        self.assertEqual(c1.is_first, True)
        self.assertEqual(c2.is_last, False)
        self.assertEqual(c4.is_root, False)
        
        # Test is_last
        self.assertEqual(p.is_last, True)
        self.assertEqual(c1.is_last, False)
        self.assertEqual(c2.is_last, False)
        self.assertEqual(c4.is_last, True)

    
    def test_add_node(self):
        """Tests adding a node to another node"""
        p = Node(1, 'Parent')
        c1 = Node(2, 'Child 1')
        c2 = Node(3, 'Child 2')
        c3 = Node(4, 'Child 3')
        c4 = Node(5, 'Child 4')
        
        p.add_node(c1)
        self.assertEqual(len(p.children), 1)
        self.assertEqual(p.children[0].id, 2)

        p.add_node(c2)
        self.assertEqual(len(p.children), 2)
        self.assertEqual(p.children[1].id, 3)      
        

    def test_disallow_children(self):
        """Tests adding a node to another node"""
        p = Node(1, 'Parent', allows_children = False)
        c1 = Node(2, 'Child 1')       
        
        self.assertEqual(p.allows_children, False)   
        self.assertEqual(p.children, None)        
        self.assertRaises(AttributeError, p.add_node, c1)

    def test_delete_nodes(self):
        p = Node(1, 'Parent')
        c1 = Node(2, 'Child 1')
        c2 = Node(3, 'Child 2')
        c3 = Node(4, 'Child')
        c4 = Node(5, 'Child') # Tests multiple matches
        c5 = Node(6, 'Child 4')
        p.add_node(c1)
        p.add_node(c2)        
        p.add_node(c3)
        p.add_node(c4)
        p.add_node(c5)
        
        p.delete_child(c2)
        results = [c.id for c in p.children]
        self.assertEqual(results, [2,4,5,6])       

        # Test delete_children_with
        p.delete_children_with('label', 'Child')
        results = [c.id for c in p.children]
        self.assertEqual(results, [2,6])
        
        # Test delete_child_at_index
        p.delete_child_at_index(1)
        results = [c.id for c in p.children]
        self.assertEqual(results, [2])

    def test_child_searching(self):
        """Test parents methods of searching for children"""
        p = Node(1, 'Parent')
        c1 = Node(2, 'Child 1')
        c2 = Node(3, 'Child 2')
        c3 = Node(4, 'Child')
        c4 = Node(5, 'Child') # Tests multiple matches
        c5 = Node(6, 'Child 4')
        p.add_node(c1)
        p.add_node(c2)        
        p.add_node(c3)
        p.add_node(c4)
        p.add_node(c5)
        
        self.assertEqual(p.index_of_child_node(c3), 2)
        self.assertEqual(p.index_of_first_child_with('label', 'Child 2'), 1)
        
        expecting = [4,5]
        results = p.children_with('label', 'Child')
        for i,n in enumerate(results):
            self.assertEqual(n.id, expecting[i])

        # Test bracket lookup
        self.assertEqual(p.children[1].label, 'Child 2')
        self.assertEqual(p[1].label, 'Child 2')
        self.assertEqual(p['Child 2'].label, 'Child 2')

    def test_child_collection_immutability(self):
        """Test child collection immutability"""
        p = Node(1, 'Parent')
        c1 = Node(2, 'Child 1')
        c2 = Node(3, 'Child 2')
        p.add_node(c1)
        p.add_node(c2)
        
        try:
            p.children.append('xyz')
        except AttributeError:
            pass
        else:
            self.fail('AttributeError was not raised')

    def test_iterator(self):
        """Iterate over collections multiple times"""
        p = Node(1, 'Parent')
        c1 = Node(2, 'Child 1')
        c2 = Node(3, 'Child 2')
        c3 = Node(4, 'Child 3')
        c4 = Node(5, 'Child 4')
        c5 = Node(6, 'Child 5')
        p.add_node(c1)
        p.add_node(c2)        
        p.add_node(c3)
        p.add_node(c4)
        p.add_node(c5)
        
        # Normal Iteration
        iterable = p
        expecting = [c1, c2, c3, c4, c5]
        
        # Test first pass through
        index = 0
        for item in iterable:
            self.assertEqual(item, expecting[index])
            index += 1
        # Test second pass to ensure iterator is reusable
        index = 0
        for item in iterable:
            self.assertEqual(item, expecting[index])
            index += 1

        
        # previous_siblings Iteration
        iterable = c3
        expecting = [c1, c2]
        
        # Test first pass through
        index = 0
        for item in iterable.previous_siblings:
            self.assertEqual(item, expecting[index])
            index += 1
        # Test second pass to ensure iterator is reusable
        index = 0
        for item in iterable.previous_siblings:
            self.assertEqual(item, expecting[index])
            index += 1


        # previous_siblings Iteration
        iterable = c3
        expecting = [c4, c5]
        
        # Test first pass through
        index = 0
        for item in iterable.next_siblings:
            self.assertEqual(item, expecting[index])
            index += 1
        # Test second pass to ensure iterator is reusable
        index = 0
        for item in iterable.next_siblings:
            self.assertEqual(item, expecting[index])
            index += 1
            


    # Formatting --------------------------------------------

    def test_representation(self):
        """Node referenced as representation"""
        r = None
        exec('r = ' + repr(self.node))
        self.assertEqual(r['id'], 1)
        self.assertEqual(r['label'], 'Test')
        self.assertEqual(r['allows_children'], True)

    def test_reference_as_string(self):
        """Node referenced as string"""
        expecting = 'Test'
        self.assertEqual('%s' % self.node, expecting)

    def test_yaml_format(self):
        """Node YAML format"""
        # 'node:\n  allows_children: true\n  id: 1\n  label: Test\n'
        y = yaml.load(self.node.to_yaml())
        self.assertEqual(y['node']['id'], 1)
        self.assertEqual(y['node']['label'], 'Test')
        self.assertEqual(y['node']['allows_children'], True)

    def test_xml_format(self):
        """Node XML format"""
        xml = self.node.to_xml()
        self.assertEqual(xml.id.PCDATA, '1')
        self.assertEqual(xml.label.PCDATA, 'Test')
        self.assertEqual(xml.allows_children.PCDATA, 'True')


if __name__ == '__main__':
    main()    