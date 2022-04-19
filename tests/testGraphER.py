'''
Created on 2022-01-12

@author: wf, ms
'''
from tests.basetest import Basetest
from ERDiagram.ER import ER
from ERDiagram.NodeType import NodeType

class TestGraphER(Basetest):
    '''
      test graph handling for ER Diagrams
    '''

    def setUp(self, debug=False, profile=True):
        self.nodeLabel = "Tester Node"
        self.otherNodeLabel = "Testee Node"
        self.attributeLabel = "Test Attribute"
        self.compose1 = "Composed 1"
        self.compose2 = "Composed 2"
        self.composedList = [self.compose1, self.compose2]
        self.attributeLabel_full = f"{self.nodeLabel}.{self.attributeLabel}"
        self.relationLabel = "tests"
        self.fromEdgeLabel = "(1,1)"
        self.toEdgeLabel = "(1,n)"
        self.relationLabel_full = f"{self.nodeLabel}<->{self.relationLabel}<->{self.otherNodeLabel}"
        self.otherNodeLabelList = [self.otherNodeLabel]
        self.isARelationLabel = f"{self.nodeLabel}.isA.{self.otherNodeLabelList}"
        self.isAComposedRelationLabel = f"{self.nodeLabel}.isA.{self.composedList}"
        self.subLabel = 't'
        self.superLabel = 'p'

        return super().setUp(debug, profile)

    def testAddNode(self):
        debug=self.debug
        #debug=True
        g = ER()
        g.add_node(self.nodeLabel)
        
        # check one node added
        self.assertEqual( 1, g.get_node_count() )
        
        # check node params
        added_node = g.get_node(self.nodeLabel)
        if debug:
            print(["added node", added_node])
        
        #self.assertEqual( f'{NodeType.NODE}_0', added_node["id"] )
        self.assertEqual( str(NodeType.NODE), added_node["nodeType"]) 
        self.assertEqual( self.nodeLabel, added_node["label"] )
        self.assertEqual( False, added_node["isWeak"] ) 
        self.assertEqual( False, added_node["isMultiple"] )

    def testAddNodeExists(self):
        debug=self.debug
        #debug=True
        g = ER()

        self.assertFalse(g.has_node(self.nodeLabel))
        g.add_node(self.nodeLabel)
        self.assertTrue(g.has_node(self.nodeLabel))

    def testAddNodeWeak(self):
        g = ER()
        g.add_node(self.nodeLabel, isWeak=True)
        added_node = g.get_node(self.nodeLabel)
        self.assertEqual( self.nodeLabel, added_node["label"] )
        self.assertTrue( added_node["isWeak"] )
        self.assertFalse( added_node["isMultiple"] )
        self.assertEqual( 1, g.get_node_count() )
  
    def testAddNodeMultiple(self):
        g = ER()
        g.add_node(self.nodeLabel, isMultiple=True)
        added_node = g.get_node(self.nodeLabel)
        self.assertTrue( added_node["isMultiple"] )
        self.assertFalse( added_node["isWeak"] )
        self.assertEqual( 1, g.get_node_count() )      

    def testAddAttribute(self):
        g = ER()
        g.add_node(self.nodeLabel)
        g.add_attribute(self.nodeLabel, self.attributeLabel)
        self.assertEqual( 2, g.get_node_count() )
        # the attribute should be called nodeLabel.nodeAttribute
        self.assertFalse(g.has_node(self.attributeLabel))
        self.assertTrue(g.has_node(self.attributeLabel_full))
 
    def testAddAttributeUnknownNode(self):
        g = ER()
        g.add_attribute(self.nodeLabel, self.attributeLabel)
        self.assertEqual( 2, g.get_node_count() )
        self.assertFalse(g.has_node(self.attributeLabel))
        self.assertTrue(g.has_node(self.attributeLabel_full))  

    def testAddAttributeCheckParameters(self):
        g = ER()
        g.add_node(self.nodeLabel)
        g.add_attribute(self.nodeLabel, self.attributeLabel, isPK=True, isMultiple=True, isWeak=True)
        self.assertEqual( 2, g.get_node_count() )
        self.assertFalse(g.has_node(self.attributeLabel))
        self.assertTrue(g.has_node(self.attributeLabel_full))
        
        added_attr = g.get_attr(self.attributeLabel_full)
        debug=self.debug
        #debug=True
        if debug:
            g.print_nodes()
            print(added_attr)
        self.assertEqual( self.attributeLabel_full, added_attr["label"] )
        self.assertEqual( True, added_attr["isPK"] )
        self.assertEqual( True, added_attr["isWeak"] )
        self.assertEqual( True, added_attr["isMultiple"] )

    def testAddAttributeComposedOf(self):
        g = ER()
        g.add_node(self.nodeLabel)
        g.add_attribute(self.nodeLabel, self.attributeLabel, composedOf=[self.compose1, self.compose2])
        
        self.assertEqual( 4, g.get_node_count() )
        
        added_attr = g.get_attr(self.attributeLabel_full)
        self.assertTrue( self.compose1 in added_attr["composedOf"] )
        self.assertTrue( self.compose2 in added_attr["composedOf"] )

        self.assertTrue( g.has_node(f"{self.attributeLabel_full}.{self.compose1}") )
        self.assertTrue( g.has_node(f"{self.attributeLabel_full}.{self.compose2}") )

    def testAddRelation(self):
        g = ER()
        g.add_relation(self.nodeLabel, self.relationLabel, self.otherNodeLabel, self.fromEdgeLabel, self.toEdgeLabel)

        added_rel = g.get_rel(self.relationLabel_full)
        debug=self.debug
        #debug=True
        if debug:
            print(added_rel)
        self.assertEqual(self.nodeLabel, added_rel["relationFrom"])
        self.assertEqual(self.otherNodeLabel, added_rel["relationTo"])
        self.assertEqual(self.fromEdgeLabel, added_rel["fromEdgeLabel"])
        self.assertEqual(self.toEdgeLabel, added_rel["toEdgeLabel"])

    def testAddIsA(self):
        g = ER()
        g.add_is_a(self.nodeLabel, self.otherNodeLabel, self.superLabel, self.subLabel, isDisjunct = True)
        added_isA = g.get_isA(self.isARelationLabel)
        self.assertTrue(g.has_node(self.isARelationLabel))
        debug=self.debug
        #debug=True
        if debug:
            print(added_isA)
        self.assertEqual(self.nodeLabel, added_isA["superClassLabel"])
        self.assertEqual(self.superLabel, added_isA["superLabel"])
        self.assertEqual(self.subLabel, added_isA["subLabel"])
        self.assertEqual(True, added_isA["isDisjunct"])
        self.assertEqual(str(self.otherNodeLabelList), added_isA["subClasses"]) # graph translates params to string


    def testAddIsAComposed(self):
        g = ER()
        g.add_is_a(self.nodeLabel, [self.compose1, self.compose2], self.superLabel, self.subLabel, isDisjunct = True)
        added_isA = g.get_isA(self.isAComposedRelationLabel)
        self.assertTrue(g.has_node(self.isAComposedRelationLabel))
        debug=self.debug
        #debug=True
        if debug:
            print(added_isA)
        self.assertEqual(self.nodeLabel, added_isA["superClassLabel"])
        self.assertEqual(self.superLabel, added_isA["superLabel"])
        self.assertEqual(self.subLabel, added_isA["subLabel"])
        self.assertEqual(True, added_isA["isDisjunct"])
        self.assertEqual(str(self.composedList), added_isA["subClasses"]) # graph translates params to string

    def testAddTernaryRelation(self):
        g = ER()

        g.add_relation("Bier", "trinkt ", "Person", "1", "n")
        g.add_relation("Bier", "trinkt ", "Ort", "1", "m")

        debug=self.debug
        #debug=True
        if debug:
            g.print_nodes()
            g.print_edges()
            print(g.asGraphvizPlaygroundUrl())

    def testGraphML(self):
        g = ER()

        g.add_node(self.nodeLabel)
        g.add_attribute(self.nodeLabel, self.attributeLabel, isPK=True, isMultiple=True, isWeak=True, composedOf=["Test1", "Test2"])
        
        debug=self.debug
        #debug=True
        if debug:
            g.print_graphml()       

    def testGraphViz(self):

        debug=self.debug
        #debug=True
        g = ER()
        g.add_node('Hersteller')
        g.add_attribute('Hersteller', 'Name', isPK = True)
        g.add_attribute('Hersteller', 'Sitz')
        g.add_relation('Hersteller', 'entwickelt', 'Modell', '1', 'n')
        g.add_is_a('Modell', ['3D', '2D'], superLabel = 'p', isDisjunct = False) 
        expectedNodes=["Hersteller","Modell","3D","2D"]
        for node in g.graph.nodes():
            if debug:
                print (node)
        if debug:
            print(g.graphViz)
            #webbrowser.open(g.asGraphvizPlaygroundUrl())
            print(g.asGraphvizPlaygroundUrl())
            
            
        #self.assertEqual(1,g.get_node_count() 
        
    def testAbstracExample(self):
        
        nodes=["Hersteller","Modell"]
        edges=[
            {"Hersteller": ["Modell"] }
        ]

    def testGetDFSTree(self):
        debug=self.debug
        #debug=True
        g = ER()
        g.add_node('Hersteller')
        g.add_attribute('Hersteller', 'Name', isPK = True)
        g.add_attribute('Hersteller', 'Sitz')
        g.add_relation('Hersteller', 'entwickelt', 'Modell', '1', 'n')
        g.add_is_a('Modell', ['3D', '2D'], superLabel = 'p', isDisjunct = False)

        g.add_node('Produzent')
        g.add_node('Käse')
        g.add_attribute('Käse', 'Marke', isPK = True)
        g.add_is_a('Käse', ['Gouda', 'Emmentaler'], superLabel = 'p', isDisjunct = True)
        g.add_relation('Produzent', 'produziert', 'Käse', '1', 'n')

        x = g.get_subtree("Hersteller")
        y = g.get_subtree("Produzent")

        self.assertTrue("Hersteller" in x)
        self.assertTrue("Modell" in x)
        self.assertTrue("Käse" not in x)

        self.assertTrue("Produzent" in y)
        self.assertTrue("Modell" not in y)
        self.assertTrue("Käse" in y)

        if debug:
            # sadly, it seems that the attributes of each node and edge are gone on creation of the subtree
            # so you need to query the original graph for the attributes :/ 
            print ("> Hersteller subtree: ")
            for n in x.nodes(data=True):
                print([n, g.get_obj(n[0])])
            
            print ("> Produzent subtree: ")
            for n in y.nodes(data=True):
                print([n, g.get_obj(n[0])])
