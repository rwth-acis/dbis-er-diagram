'''
Created on 2022-01-12

@author: wf, ms
'''
from tests.basetest import Basetest
from erdiagram.ER import ER
from erdiagram.NodeType import NodeType
import json
class TestGraphER(Basetest):
    '''
      test graph handling for ER Diagrams
    '''

    def setUp(self, debug=False, profile=True):
        self.nodeLabel = "Tester_Node"
        self.nodeLabel2 = "Tester_2_Node"
        self.otherNodeLabel = "Testee_Node"
        self.attributeLabel = "Test_Attribute"
        self.attribute2Label = "Test_Attribute_2"
        self.compose1 = "Composed 1"
        self.compose2 = "Composed 2"
        self.composedList = [self.compose1, self.compose2]
        self.isA1 = "isA 1"
        self.isA2 = "isA 2"
        self.isAList = [self.isA1, self.isA2]
        self.attributeLabel_full = f"{self.nodeLabel}.{self.attributeLabel}"
        self.relationLabel = "tests"
        self.fromEdgeLabel = "(1,1)"
        self.toEdgeLabel = "(1,n)"
        self.relationLabel_full = f"{self.nodeLabel}-->{self.relationLabel}<--{self.otherNodeLabel}"
        self.otherNodeLabelList = [self.otherNodeLabel]
        self.isARelationLabel = f"{self.nodeLabel}.isA.{self.otherNodeLabelList}"
        self.isAComposedRelationLabel = f"{self.nodeLabel}.isA.{self.isAList}"
        self.subLabel = 'subLabel / t'
        self.superLabel = 'superLabel / p'

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

    def testAddNodeEmptyName(self):
        debug = self.debug
        debug = True
        g = ER()

        g.add_node(self.nodeLabel)
        g.add_node(self.otherNodeLabel)
        g.add_relation(self.nodeLabel, self.relationLabel, self.otherNodeLabel, self.fromEdgeLabel, self.toEdgeLabel)
        g.add_attribute("", self.attributeLabel)

        g.add_relation('', self.relationLabel, self.nodeLabel2, '', self.toEdgeLabel)

        self.assertEqual(3, g.get_obj_count(NodeType.NODE))


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
        self.assertFalse(g.has_attr(self.attributeLabel))
        self.assertTrue(g.has_attr(self.attributeLabel_full))
 
    def testAddAttributeUnknownNode(self):
        g = ER()
        g.add_attribute(self.nodeLabel, self.attributeLabel)
        self.assertEqual( 2, g.get_node_count() )
        self.assertFalse(g.has_attr(self.attributeLabel))
        self.assertTrue(g.has_attr(self.attributeLabel_full))  

    def testAddAttributeCheckParameters(self):
        g = ER()
        g.add_node(self.nodeLabel)
        g.add_attribute(self.nodeLabel, self.attributeLabel, isPK=True, isMultiple=True, isWeak=True)
        self.assertEqual( 2, g.get_node_count() )
        self.assertFalse(g.has_attr(self.attributeLabel))
        self.assertTrue(g.has_attr(self.attributeLabel_full))
        
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
        debug = self.debug
        #debug = True
        g = ER()
        g.add_node(self.nodeLabel)
        g.add_attribute(self.nodeLabel, self.attributeLabel, composedOf=[self.compose1, self.compose2])
        
        self.assertEqual( 4, g.get_node_count() ) # parent, attribute and two composed.

        if debug: g.print_graphml()

        self.assertTrue(g.has_attr(self.attributeLabel_full))
        
        added_attr = g.get_attr(self.attributeLabel_full)
        self.assertTrue( self.compose1 in added_attr["composedOf"] )
        self.assertTrue( self.compose2 in added_attr["composedOf"] )

        self.assertTrue( g.has_comp_attr(f"{self.attributeLabel_full}.{self.compose1}") )
        self.assertTrue( g.has_comp_attr(f"{self.attributeLabel_full}.{self.compose2}") )

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

    def testRelationCompare(self):
        g = ER(debug=True)
        #g.add_relation(self.nodeLabel, self.relationLabel, self.otherNodeLabel, self.fromEdgeLabel, self.toEdgeLabel)

        g.add_node('S')
        g.add_node('Bewertung')
        g.add_relation('S', 'hat', 'Bewertung', '1', 'n')

        h = ER(debug=True)
        #h.add_relation(self.nodeLabel, "Schwachsinn", self.otherNodeLabel, self.fromEdgeLabel, self.toEdgeLabel)
        h.add_node('S')
        h.add_node('Bewertung')
        h.add_relation('S', 'fsdfsdfsdfsdf', 'Bewertung', '1', 'n')

        score = h.compareGraphs(g, debug = True)
        self.assertEqual(0, score)
        #self.assertFalse(True)


    def testAddIsA(self):
        g = ER()
        g.add_is_a(self.nodeLabel, self.otherNodeLabel, self.superLabel, self.subLabel, isDisjunct = True)
        added_isA = g.get_isA(self.isARelationLabel)
        self.assertTrue(g.has_isA(self.isARelationLabel))
        debug=self.debug
        #debug=True
        if debug:
            print(added_isA)
        self.assertEqual(self.nodeLabel, added_isA["superClassLabel"])
        self.assertEqual(self.superLabel, added_isA["superLabel"])
        self.assertEqual(self.subLabel, added_isA["subLabel"])
        self.assertEqual(True, added_isA["isDisjunct"])
        self.assertEqual(json.dumps(self.otherNodeLabelList), added_isA["subClasses"]) # graph translates params to string


    def testAddIsAComposed(self):
        g = ER()
        g.add_is_a(self.nodeLabel, self.isAList, self.superLabel, self.subLabel, isDisjunct = True)
        added_isA = g.get_isA(self.isAComposedRelationLabel)
        self.assertTrue(g.has_isA(self.isAComposedRelationLabel))
        debug=self.debug
        #debug=True
        if debug:
            print(added_isA)
        self.assertEqual(self.nodeLabel, added_isA["superClassLabel"])
        self.assertEqual(self.superLabel, added_isA["superLabel"])
        self.assertEqual(self.subLabel, added_isA["subLabel"])
        self.assertEqual(True, added_isA["isDisjunct"])
        self.assertEqual(json.dumps(self.isAList), added_isA["subClasses"]) # graph translates params to string

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


    def testExcScoreComparison(self): 
        '''
            test ER graph comparison. calculates distance, i.e. points to be deducted
        '''
        debug=self.debug
        #debug=True
        solution = ER(debug=debug)

        solution.add_node('Hersteller')
        solution.add_attribute('Hersteller', 'Name', isPK = True)
        solution.add_attribute('Hersteller', 'Sitz') # 0.25 missing attribute
        solution.add_node('Käse') # 1p missing node

        compare = ER()

        compare.add_node('Hersteller', isWeak=True) # 0.25 Weak
        compare.add_attribute('Hersteller', 'Name', isPK = False) # 0.25 PK

        # keep this outside for two reasons:
        # - security
        # - reusability, maybe in some tasks we want to grade things differently
        scores = {
            'missing_object': 1,
            'missing_property': {
                str(NodeType.NODE): 0.5,
                str(NodeType.ATTRIBUTE): 0.25,
                str(NodeType.RELATION): 0.5,
                str(NodeType.IS_A): 0.25
            }
        }

        self.assertEqual(2.0, solution.compareGraphs(compare, scores=scores, debug=False))                

    def testAddNodeCopy(self):
        debug = self.debug
        #debug = True

        g = ER(debug=debug)

        h = ER(debug=debug)
        h.add_node(
            self.nodeLabel, 
            isWeak=True, 
            isMultiple=True
        )
        h.add_attribute(
            self.nodeLabel, 
            self.attributeLabel, 
            isPK=True, 
            isMultiple=True, 
            isWeak=True
        )
        h.add_attribute(
            self.nodeLabel, 
            self.attribute2Label, 
            isPK=False, 
            isMultiple=True, 
            isWeak=True, 
            composedOf=self.composedList           
        )
        h.add_is_a(
            self.nodeLabel, 
            self.isAList, 
            self.superLabel, 
            self.subLabel, 
            isDisjunct = True
        )
        h.add_relation(
            self.nodeLabel, 
            self.relationLabel, 
            self.otherNodeLabel, 
            self.fromEdgeLabel, 
            self.toEdgeLabel,
            isWeak=True
        )
        
        g.mergeGraphsWith(h)

        self.assertEqual(True, g.has_node(self.nodeLabel))
        if debug:
            print(g.asGraphvizPlaygroundUrl())
        
        self.assertEqual(True, g.has_attr(self.attributeLabel_full))

        difference_score = g.compareGraphs(h, scores = g.get_default_scores(), debug=True)

        self.assertEqual(0, difference_score)













    def testEXCa(self):
        g = ER()

        g.add_node('A')

        ### BEGIN SOLUTION

        g.add_attribute('A', 'A_ID', isPK=True)
        g.add_attribute('A', 'B')
        g.add_attribute('A', 'C')
        g.add_attribute('A', 'D', isMultiple=True)

        h = ER() # test empty solution
        h.add_node('A')

        scores = {
            'missing_object': 1,
            'missing_property': {
                str(NodeType.NODE): 0.5,
                str(NodeType.ATTRIBUTE): 0.5,
                str(NodeType.RELATION): 0.5,
                str(NodeType.COMPOSED_ATTRIBUTE): 0.125,
                str(NodeType.IS_A): 0.25
            }
        }
        score_compare  = g.compareGraphs(h, scores=scores, debug = False)
        #print(score_compare)
        self.assertEqual(2, score_compare)

    def testEXCb(self):

        g = ER()

        g.add_node('E')
        g.add_node('F')

        ### BEGIN SOLUTION

        g.add_attribute('F', 'F_ID', isPK=True)
        g.add_attribute('F', 'G')
        g.add_attribute('F', 'H')
        g.add_attribute('F', 'I')

        g.add_relation('E', 'hat', 'F', '1', 'n')


        h = ER() # test empty solution
        h.add_node('E')
        h.add_node('F')

        #h.add_relation('E', 'hat', 'F', '1', 'm') # n or m doesn't matter.
        score_compare  = g.compareGraphs(h, debug = True)
        #print(score_compare)
        self.assertEqual(2, score_compare)

    def testEXCc(self):
        g = ER()

        g.add_node('U')
        g.add_node('V')
        g.add_node('W')

        ### BEGIN SOLUTION
        g.add_attribute('W', 'W_ID', isPK = True)
        g.add_attribute('W', 'A')
        g.add_attribute('W', 'B')
        g.add_attribute('W', 'C')
        g.add_relation('U', 'y', 'W', '1', 'n')
        g.add_relation('V', 'x', 'U', 'n', 'm')
        ### END SOLUTION

        h = ER() # test empty solution

        h.add_node('U')
        h.add_node('V')
        h.add_node('W')

        #h.add_relation('E', 'hat', 'F', '1', 'm')

        score_compare  = g.compareGraphs(h, debug = True)
        #print(score_compare)
        self.assertEqual(3, score_compare)
    
    def testEXCd(self):
        g = ER()

        g.add_node('I')
        g.add_node('J')

        ### BEGIN SOLUTION

        g.add_node('K', isWeak = True)
        
        g.add_attribute('K', 'K_ID', isPK = True)
        g.add_attribute('K', 'K2')
        #g.add_attribute('K', 'K3')

        g.add_attribute('J', 'J1', isPK = True)
        g.add_attribute('J', 'JC', composedOf = ['JC1', 'JC2'])

        g.add_relation('J', 'sss', 'K', '1', 'n')
        g.add_relation('J', 'sss', 'I', '1', 'n')
        g.add_relation('K', 'AA', 'K', '1', 'n')
        g.add_relation('I', 'eee', 'K', '1', 'n', isWeak = True)


        h = ER() # test empty solution

        h.add_node('I')
        h.add_node('J')

        #h.add_relation('E', 'hat', 'F', '1', 'm')

        score_compare  = g.compareGraphs(h, debug = True)
        #print(score_compare)
        self.assertEqual(6, score_compare)


    def testEXCe(self):
        g = ER()

        g.add_node('S')

        ### BEGIN SOLUTION

        g.add_relation('S', 'hat', 'G', '1', 'n')
        g.add_attribute('G', 'G_ID', isPK = True)
        g.add_is_a('G', ['A', 'B', 'C', 'D'], superLabel = 'p', isDisjunct = False)

        h = ER() # test empty solution
        h.add_node('S')

        scores = {
            'missing_object': 0.5, # less points for IS-As
            'missing_property': {
                str(NodeType.NODE): 0.5,
                str(NodeType.ATTRIBUTE): 0.5,
                str(NodeType.RELATION): 0.25,
                str(NodeType.COMPOSED_ATTRIBUTE): 0.125,
                str(NodeType.IS_A): 0.25
            }
        }
        score_compare  = g.compareGraphs(h, scores = scores, debug = True)
        #print(score_compare)
        self.assertEqual(4, score_compare)

    def testXX(self):
        g = ER(debug=True)
        g.add_node('S')
        g.add_node('B')
        g.add_node('E')

        g.add_relation('S', 'b','E','1', 'n')
        g.add_attribute('E','E_ID', isPK=True)
        g.add_attribute('E','t')
        g.add_attribute('E','d')
        g.add_attribute('E','k')

        g.add_relation('E','s','B','  m  ','  n  ') # Test spaces in cardinalities

        h = ER(debug=True) # test empty solution
        h.add_node('S')
        h.add_node('B')
        h.add_node('E')
        h.add_attribute('E', 'E_ID', isPK = True)
        h.add_attribute('E', 't')
        h.add_attribute('E', 'd')
        h.add_attribute('E', 'k')
        h.add_relation('S', 'b', 'E', '1', 'n')
        h.add_relation('B', 'sfsdf', 'E', 'n', 'm')

        score_compare  = h.compareGraphs(g, debug = True)
        maxPoints = 3

        score = min( maxPoints, max( 0, round( maxPoints - score_compare, 2 ) ) )
        print("------------------")
        print(f"score: {3} - {score_compare} = {score}")

        self.assertEqual(3, score)

    def testIsAGrading(self):
        g = ER(debug=True)
        g.add_is_a("A", ["B", "C", "D"], "t", True)
        h = ER(debug=True)
        h.add_is_a("A", ["C", "D", "B"], "t", True)
        self.assertEqual(0, h.compareGraphs(g, debug = True))
        