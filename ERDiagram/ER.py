from erdiagram.NodeType import NodeType
from graphviz import Digraph
from IPython.display import display
from networkx.readwrite import json_graph
from urllib.parse import quote
import json
import networkx as nx

class ER:
    '''
        Entity Relationship Diagram Wrapper for graphviz.
        Michal Slupczynski RWTH DBIS 2021-2022
    '''

    def __init__(self, engine='dot', edge_len=1.5, debug=False, graph_attr={}):
        '''
        constructor
        
        Args:
            engine(str): the graphviz engine to use
            edge_len(float): the length of edeges
            debug(bool): if true switch on debugging
            graph_attr(dict): the graph attributes to use 
            
        '''
        # start counting at 0!
        self.__id = -1
        
        # default values
        self.debug = debug
        self.edge_len = edge_len

        # The semantic true graph - graphViz is only the representation
        self.graph = nx.DiGraph()
        # @TODO -do this lazily we don't need the visualization while creating the graph
        self.graphViz = Digraph('ER', engine=engine, graph_attr=graph_attr)

        # helper lists and dicts
        self.isAs = list()
        self.nodes = dict()
        self.nodesInfoDict = dict()
        self.relations = list()

        self.__default_scores = {
            'missing_object': 1,
            'missing_property': {
                str(NodeType.NODE): 0.5,
                str(NodeType.ATTRIBUTE): 0.25,
                str(NodeType.RELATION): 0.5,
                str(NodeType.COMPOSED_ATTRIBUTE): 0.125,
                str(NodeType.IS_A): 0.25
            }
        }
        
    @classmethod
    def copyfrom(cls, diagram, engine='dot', edge_len=1.5, debug=False, graph_attr={}):
        # TODO
        new_diagram = cls(engine, edge_len, debug, graph_attr)
        # Copy nodes & attributes
        for node in diagram.nodes:
            n = diagram.nodes[node]
            new_diagram.add_node(n['name'], n['isMultiple'], n['isWeak'])
            for attr in n["attributes"]:
                new_diagram.add_attribute(n['name'], attr['attr_name'], attr['isPK'], attr['isMultiple'], attr['isWeak'], attr['composedOf'])
        # Copy relations
        for rel in diagram.relations:
            new_diagram.add_relation(rel['from_edge'], rel['relation_label'], rel['to_edge'], rel['from_label'], rel['to_label'], rel['isWeak'])
        # Copy isAs
        for isA in diagram.isAs:
            new_diagram.add_is_a(isA['superclass'], isA['subclass'], isA['super_label'], isA['sub_label'], isA['is_disjunct'])
        return new_diagram

    def __nextID(self):
        # TODO: figure out if this is necessary
        self.__id += 1
        return self.__id

    def __add_graphml_node(self, label, isMultiple=False, isWeak=False):
        '''
        add node to graphML graph
        Args:
            label(str): label of this node
            isMultiple(bool): is cardinality of node multiple or singular?
            isWeak(bool): is this a weak node? 
        '''
        if self.debug: 
            print(f">> adding node: {label}")
        self.get_graph().add_node(label, 
            label = label,
            isMultiple = isMultiple,
            isWeak = isWeak,
            nodeType = str(NodeType.NODE)
        )
        
        '''
            # TODO
            def __add_graphml_attr_parent(self,
                parentLabel,
                attrLabel, 
                isPK=False, 
                isMultiple=False, 
                isWeak=False, 
                composedOf=[],
                fromLabel="",
                toLabel=""
            ):
                self.get_graph().add_node(attrLabel, 
                    label = f'{parentLabel}.{attrLabel}',
                    isPK = isPK,
                    isMultiple = isMultiple,
                    isWeak = isWeak,
                    composedOf = composedOf,
                    nodeType= str(NodeType.ATTRIBUTE)
                )

                self.__add_graphml_edge(parentLabel, attrLabel, fromLabel, toLabel)
        '''

    # TODO: figure out directed edges
    # https://networkx.org/documentation/stable/auto_examples/drawing/plot_selfloops.html#sphx-glr-auto-examples-drawing-plot-selfloops-py
    def __add_graphml_edge(self, fromNodeLabel, toNodeLabel, edgeLabel="", directed=False, inverseDirection=False):
        '''
        add edge to graphML graph
        Args:
            fromNodeLabel(str): label of the node on "from" end
            toNodeLabel(str): label of the node on "to" end
            edgeLabel(str): label of the edge
            directed(bool): draw an arrow at the "to" end of the edge?
            inverseDirection(bool): if "directed" and "inverseDirection" are both true, the arrow is drawn at the "from" end
        '''
        if self.debug: 
            print(f"   >> adding edge: {fromNodeLabel} <---[{edgeLabel}]---> {toNodeLabel}")
        if self.get_graph().has_edge(fromNodeLabel, toNodeLabel) or self.get_graph().has_edge(toNodeLabel, fromNodeLabel) :
            if self.debug:
                print(f">> trying to add existing edge, nothing to be done.")
            return
        self.get_graph().add_edge(fromNodeLabel, toNodeLabel, 
            edgeLabel=edgeLabel, directed=directed, inverseDirection=inverseDirection)

    def __add_graphml_attr(self, 
        parentLabel, 
        attrLabel, 
        isPK=False, 
        isMultiple=False, 
        isWeak=False, 
        isComposed=False,
        composedOf=[]):
        '''
        add attribute to graphML graph
        Args:
            parentLabel(str): label of parent node
            attrLabel(str): label of attribute
            isPK(bool): is this attribute the primary key?
            isMultiple(bool): is cardinality of node multiple or singular?
            isWeak(bool): is this a weak node?
            composedOf(list): list of attributes this attribute is built of
        '''

        directLabel = f'{parentLabel}.{attrLabel}'
        if self.debug: 
            print(f">> adding attribute: {attrLabel}")
        if not isComposed:
            nodeType = str(NodeType.ATTRIBUTE)
        else:
            nodeType = str(NodeType.COMPOSED_ATTRIBUTE)

        self.get_graph().add_node(directLabel, 
            label = directLabel,
            attrLabel = attrLabel,
            parentLabel = parentLabel,
            isPK = isPK,
            isMultiple = isMultiple,
            isWeak = isWeak,
            composedOf = json.dumps(composedOf),
            nodeType = nodeType
        )

    def __add_graphml_relation(self, label, fromNodeLabel, toNodeLabel, fromEdgeLabel, toEdgeLabel, isWeak=False):
        '''
        add relation to graphML graph
        Args:
            label(str): label of the relation
            fromNodeLabel(str): label of the node from which the relation starts
            toNodeLabel(str): label of the node at which the relation ends
            fromEdgeLabel(str): label on edge at the "from" side
            toEdgeLabel(str): label on edge at the "to" side
            isWeak(bool): is this a weak relation?
        '''
        relationLabel = f"{fromNodeLabel}-->{label}<--{toNodeLabel}"
        if self.debug: 
            print(f">> adding relation: {label}")
        self.get_graph().add_node(relationLabel, 
            label = relationLabel,
            relation = f"{fromNodeLabel}<-[{fromEdgeLabel}]--[{toEdgeLabel}]->{toNodeLabel}",
            relationLabel = label,
            relationFrom = fromNodeLabel,
            relationTo = toNodeLabel,
            fromEdgeLabel = fromEdgeLabel,
            toEdgeLabel = toEdgeLabel,
            isWeak = isWeak,
            nodeType = str(NodeType.RELATION)
        )

        self.__add_graphml_edge(fromNodeLabel, relationLabel, fromEdgeLabel)
        self.__add_graphml_edge(relationLabel, toNodeLabel, toEdgeLabel)

    def __add_graphml_is_a(self, superClassLabel, superLabel, subLabel, isDisjunct=False, subClasses=[]):
        if isDisjunct:
            isALabel = f"{superClassLabel}.isA.{subClasses}"
            relation = f"{superClassLabel}->[{superLabel}]->[isA]->[{subLabel}]->{subClasses}"
        else:
            isALabel = f"{superClassLabel}.isA.{subClasses}"
            relation = f"{superClassLabel}<-[{superLabel}]<-[isA]<-[{subLabel}]<-{subClasses}"
        if self.debug: 
            print(f">> adding relation: {isALabel}")
        
        self.get_graph().add_node( isALabel,
            label = isALabel,
            relation = relation,
            superClassLabel = superClassLabel,
            superLabel = superLabel,
            subLabel = subLabel,
            isDisjunct = isDisjunct,
            subClasses = json.dumps(subClasses),
            nodeType = str(NodeType.IS_A)
        )

        self.__add_graphml_edge(superClassLabel, isALabel, superLabel, directed=True, inverseDirection=isDisjunct)
        for i, subclass in enumerate(subClasses):
            self.__add_graphml_edge(isALabel, subclass, subLabel, directed=True, inverseDirection=isDisjunct)

    def __add_graphviz_node(self, label, isMultiple=False, isWeak=False):
        '''
        add node to rendering
        Args:
            label(str): node label
            isMultiple(bool): is cardinality of node multiple or singular?
            isWeak(bool): is this a weak node?
        '''
        # Add Node for rendering - a Blue box
        if isMultiple or isWeak:
            self.graphViz.attr('node', shape='box', style='filled',
                            fillcolor='#CCCCFF', color='#0000FF', peripheries='2')
        else:
            self.graphViz.attr('node', shape='box', style='filled',
                            fillcolor='#CCCCFF', color='#0000FF', peripheries='1')
        self.graphViz.node(label)



    def __add_graphviz_attr(self, parentLabel, attrLabel, fullAttrLabel, isMultiple):
        '''
        add attribute to rendering
        Args:
            parentLabel(str): label of parent node
            attrLabel(str): label of attribute
            fullAttrLabel(str): label of form {parentLabel}.{attrLabel} with underlined formatting
            isMultiple(bool): is cardinality of node multiple or singular?
            isWeak(bool): is this a weak node?
        '''
        if isMultiple:
            # Can be Multiple, then it has a double outline
            self.graphViz.attr('node', shape='ellipse', style='filled',
                            fillcolor='#FFFBD6', color='#656354', peripheries='2')
        else:
            self.graphViz.attr('node', shape='ellipse', style='filled',
                            fillcolor='#FFFBD6', color='#656354', peripheries='1')

        self.graphViz.node(fullAttrLabel, label=attrLabel)

        self.graphViz.edge(parentLabel, fullAttrLabel, arrowhead='none')   

    def __add_graphviz_relation(self, relationLabel, fromNodeLabel, toNodeLabel, fromEdgeLabel, toEdgeLabel, isWeak):
        edge_color = 'black:invis:black' if isWeak else 'black'

        if isWeak:
            self.graphViz.attr('node', shape='diamond', style='filled',
                            fillcolor='#FFCCCC', color='#BA2128', peripheries='2')
        else:
            self.graphViz.attr('node', shape='diamond', style='filled',
                            fillcolor='#FFCCCC', color='#BA2128', peripheries='1')

        self.graphViz.node(relationLabel)

        if fromNodeLabel != '':
            self.graphViz.edge(fromNodeLabel, relationLabel, label=fromEdgeLabel, len=str(
                self.edge_len), arrowhead='none')

        self.graphViz.edge(relationLabel, toNodeLabel, label=toEdgeLabel,
                        len=str(self.edge_len), arrowhead='none', color=edge_color)

    def __add_graphviz_is_a(self, superClassLabel, super_label, sub_label, is_disjunct, subClasses):
        self.graphViz.attr('node', shape='invtriangle', style='filled',
                        fillcolor='#CCFFCC', color='#506550', peripheries='1')

        isA_ID = self.__nextID() # is this necessary??

        self.graphViz.node('is_A' + str(isA_ID), 'isA')

        self.graphViz.edge(superClassLabel, 'is_A' + str(isA_ID),
                        label=super_label, len=str(self.edge_len), arrowhead='none')

        if not is_disjunct:
            for i, subclass in enumerate(subClasses):
                self.graphViz.edge('is_A' + str(isA_ID), subclass, label=sub_label, len=str(
                    self.edge_len), arrowhead='normal', dir='back')
        else:
            for i, subclass in enumerate(subClasses):
                self.graphViz.edge('is_A' + str(isA_ID),
                                subclass, label=sub_label, len=str(self.edge_len), arrowhead='normal')





    def add_node(self, label, isMultiple=False, isWeak=False):
        '''
        Add an entity to the graph
        Args:
            label(str): node label
            isMultiple(bool): is cardinality of node multiple or singular?
            isWeak(bool): is this a weak node?
        '''
        # add new node to graphML graph
        self.__add_graphml_node(label, isMultiple, isWeak)

        # add new node to graphViz graph - a blue rectangle
        # TODO: refactor this to .render() function
        self.__add_graphviz_node(label, isMultiple, isWeak)

    def add_attribute(self, nodeLabel, attrLabel, isPK=False, isMultiple=False, isWeak=False, composedOf=[]):
        '''
        Add an attribute to an entity in the graph
        Args:
            nodeLabel(str): parent node label
            attrLabel(str): attribute label
            isPK(bool): is this attribute the primary key?
            isMultiple(bool): is cardinality of node multiple or singular?
            isWeak(bool): is this a weak attribute?
            composedOf(list): list of attributes this attribute is built of
        '''
        fullAttrLabel = f'{nodeLabel}.{attrLabel}'

        # label can be PrimaryKey (isPK), then it's underlined.
        graphVizAttrLabel = self.__format_label(attrLabel, isWeak, isPK)

        # if parent node doesn't exist, create it
        if not self.has_node(nodeLabel):
            if self.debug:
                print(f">> node not found, adding {nodeLabel}")
            self.add_node(nodeLabel)

        if isinstance(composedOf, str):
            composedOf = json.loads(composedOf)

        # add new node to graphML graph
        self.__add_graphml_attr(nodeLabel, attrLabel, isPK, isMultiple = isMultiple, isWeak = isWeak, composedOf = composedOf, isComposed=False)

        # add new edge to graphML graph connecting the parent node to this new attribute
        self.__add_graphml_edge(nodeLabel, fullAttrLabel)

        # add new attribute to graphViz graph - a yellow circle
        # TODO: refactor this to .render() function
        self.__add_graphviz_attr(nodeLabel, graphVizAttrLabel, fullAttrLabel, isMultiple)

        if self.debug and len(composedOf) > 0:
            print(f">- -> {len(composedOf)} sublabels found")

        for subAttrLabel in composedOf:
            graphVizSubLabel = self.__format_label(subAttrLabel, isWeak, isPK)
            
            fullSubLabel = f'{nodeLabel}.{attrLabel}.{subAttrLabel}'
            
            if self.debug:
                print(f"   >> >> adding sublabel {fullSubLabel} ")

            # add to graphML graph
            self.__add_graphml_attr(f'{nodeLabel}.{attrLabel}', subAttrLabel, isPK, isMultiple, isWeak, isComposed=True)
            self.__add_graphml_edge(f'{nodeLabel}.{attrLabel}', fullSubLabel)

            # add to graphViz graph
            self.__add_graphviz_attr(f'{nodeLabel}.{attrLabel}', graphVizSubLabel, fullSubLabel, isMultiple)

    def add_relation(self, fromNodeLabel, relationLabel, toNodeLabel, fromEdgeLabel, toEdgeLabel, isWeak=False):
        '''
        Add a relation with two labelled edges
        Args:
            fromNodeLabel(str): Label of the "from" node
            relationLabel(str): Label of the relation
            toNodeLabel(str): Label of the "to" node
            fromEdgeLabel(str): Label/cardinality on the "from" edge
            toEdgeLabel(str): Label/cardinality on the "to" edge
            isWeak(bool): is this a weak relation?
        '''
        if fromNodeLabel != '' and not self.has_node(fromNodeLabel):
            if self.debug:
                print(f">> fromNode missing, adding {fromNodeLabel}")
            self.add_node(fromNodeLabel)
        if not self.has_node(toNodeLabel):
            if self.debug:
                print(f">> toNode missing, adding {toNodeLabel}")
            self.add_node(toNodeLabel, isWeak=isWeak)

        self.__add_graphml_relation(relationLabel, fromNodeLabel, toNodeLabel, fromEdgeLabel.replace(" ", ""), toEdgeLabel.replace(" ", ""), isWeak)

        # TODO: refactor this to .render() function
        # Add a relation between two nodes - a red rhombus
        self.__add_graphviz_relation(relationLabel, fromNodeLabel, toNodeLabel, fromEdgeLabel.replace(" ", ""), toEdgeLabel.replace(" ", ""), isWeak)

    def add_is_a(self, superClassLabel, subclassParam, superLabel='', subLabel='', isDisjunct=True):
        '''
        Add an "is-A" (Generalization / Specialization) to the graph
        Args:
            superClassLabel(str): Label of the superclass node 
            subclassParam(str or list of str): Label of the subclass node(s)
            superLabel(str): Is the relation partial or total? ("p" or "t" - written on the edge to the super class)
            subLabel(str): Is the relation partial or total? ("p" or "t" - written on the edge to the sub class)
            isDisjunct(bool): Are the elements of this relation disjunct?
        '''
        # Add "X is a Y" relation - a green inverted triangle from a superclass to multiple subclasses
        if not isinstance(subclassParam, list):
            subClasses = [subclassParam]
        else:
            subClasses = subclassParam

        if subClasses is not None:
            subClasses.sort()

        if not self.has_node(superClassLabel):
            self.add_node(superClassLabel)
        for i, subClassLabel in enumerate(subClasses):
            if not self.has_node(subClassLabel):
                self.add_node(subClassLabel)

        self.__add_graphml_is_a(superClassLabel, superLabel, subLabel, isDisjunct, subClasses)

        # TODO: refactor this to .render() function
        self.__add_graphviz_is_a(superClassLabel, superLabel, subLabel, isDisjunct, subClasses)


    def getNodeByLabel(self, label):
        if ( label in self.nodes.keys() ):
            return self.nodes[label]
        else:
            return None

    def display(self):
        self.draw()
        
    def draw(self):
        display(self.graphViz)

    def asSolution(self, format="json"):
        if format == "json":
            return json_graph.node_link_data(self.get_graph())

        return "please pick data format"

    def get_graph(self):
        return self.graph

    def get_default_scores(self):
        return self.__default_scores        

    def _add_obj_node(self, obj):
        self.add_node(obj.get('label', ''), isMultiple = obj['isMultiple'], isWeak = obj['isWeak'])
        if self.debug:
            print(f"    ✓  added node {obj.get('label', '')}:")
            print(f"       isMultiple = {obj['isMultiple']}, isWeak = {obj['isWeak']}")
    
    def _add_obj_attr(self, obj):
        self.add_attribute(
            obj['parentLabel'], obj['attrLabel'], 
            isPK = obj['isPK'], isMultiple = obj['isMultiple'], isWeak = obj['isWeak'], 
            composedOf = obj['composedOf']
        )
        if self.debug:
            print(f"    ✓  added attribute {obj['attrLabel']} to node {obj['parentLabel']}:")
            print(f"       isPK = obj['isPK'], isMultiple = {obj['isMultiple']}, isWeak = {obj['isWeak']}, composedOf = {obj['composedOf']}")

    def _add_obj_is_a(self, obj):
        self.add_is_a(
            superClassLabel = obj['superClassLabel'], subclassParam = json.loads(obj['subClasses']),
            superLabel = obj['superLabel'], subLabel = obj['subLabel'], isDisjunct = obj['isDisjunct']
        )
        if self.debug:
            print(f"    ✓  added isA {json.loads(obj['subClasses'])} to super class {obj['superClassLabel']}:")
            print(f"       superLabel = {obj['superLabel']}, subLabel = {obj['subLabel']}, isDisjunct = {obj['isDisjunct']}")

    def _add_obj_rel(self, obj):
        self.add_relation(
            fromNodeLabel=obj['relationFrom'], 
            relationLabel=obj['relationLabel'], 
            toNodeLabel=obj['relationTo'], 
            fromEdgeLabel=obj['fromEdgeLabel'], 
            toEdgeLabel=obj['toEdgeLabel'], 
            isWeak=obj['isWeak']
        )
        if self.debug:
            print(f"    ✓  added relation {obj['relationLabel']} between {obj['relationFrom']} and {obj['relationTo']}:")
            print(f"       fromEdgeLabel = {obj['fromEdgeLabel']}, toEdgeLabel = {obj['toEdgeLabel']}, isWeak = {obj['isWeak']}")

    def __add_obj_copy(self, argument):
        if self.has_obj(argument.get('label', '')):
            if self.debug:
                print(f" ! trying to add object {argument.get('label', '')} of type {argument.get('nodeType', NodeType.NOT_SPECIFIED)}, but already exists")
            return
        switcher = {
            str(NodeType.NODE): "_add_obj_node",
            str(NodeType.ATTRIBUTE): "_add_obj_attr",
            str(NodeType.IS_A): "_add_obj_is_a",
            str(NodeType.RELATION): "_add_obj_rel"
        }
        function_name = switcher.get(argument.get('nodeType', NodeType.NOT_SPECIFIED), "not found")
        if function_name == "not found":
            raise Exception(f"  no adequate function found to add object copy for type {argument.get('nodeType', NodeType.NOT_SPECIFIED)}")
        #if self.debug:
        #    print(f"    calling function {function_name}() to add object copy of type {argument.get('nodeType', NodeType.NOT_SPECIFIED)}")
        func = getattr(self, function_name, lambda: "Invalid node type")(argument)
        return func

    def mergeGraphsWith(self, otherGraph):
        if self.debug:
            print(" ")
            print("|-> merging graphs")
        for n1 in otherGraph.get_obj():
            if self.has_obj(n1.get("label", "")):
                continue
            else:
                if self.debug:
                    print(f" >  object '{n1.get('label', '')}' doesn't exist in this graph")
            if (n1.get('nodeType', NodeType.NOT_SPECIFIED) == str(NodeType.COMPOSED_ATTRIBUTE)):
                if self.debug:
                    print(f" -> object copy of {NodeType.COMPOSED_ATTRIBUTE}s not supported directly, copy via parent object instead")
                continue
            
            if self.debug:
                print(f" » checking object '{n1.get('label', '')}' of type {n1.get('nodeType', NodeType.NOT_SPECIFIED)}")
            self.__add_obj_copy(n1)
            if self.debug: print(" ")

    def compareGraphs(self, otherGraph, label = "", node_type = NodeType.NOT_SPECIFIED, scores={}, debug=False):
        if debug: debugging = True
        else: debugging = self.debug
        dist = 0
        if debugging:
            print(" ¶ calculating distances between graphs:    ")
        if scores == {}:
            if debugging:
                print("  no scores provided, fallback to default.")
            scores = self.get_default_scores()


        for n1 in self.get_obj(label, node_type = node_type):
            # ignore attributes, will be checked as part of NodeType.NODE
            thisNodeType = n1.get("nodeType", NodeType.NOT_SPECIFIED)
            if thisNodeType == str(NodeType.ATTRIBUTE) or thisNodeType == str(NodeType.COMPOSED_ATTRIBUTE):
                continue

            if debugging:
                print(f" » testing {n1.get('label', '')}:")

            distancePerProperty = scores['missing_property'][n1.get('nodeType', NodeType.NOT_SPECIFIED)]

            otherGraphHasObjectBool = otherGraph.has_obj(n1["label"], thisNodeType)
            if thisNodeType == str(NodeType.RELATION):
                otherGraphHasObjectBool = otherGraph.has_rel_adv(n1)

            # check (by label) if object exists in other graph
            if not otherGraphHasObjectBool:
                # not found.
                if debugging:
                    print(f"   ✗ {scores['missing_object']:+.2f}, {n1.get('nodeType', NodeType.NOT_SPECIFIED)} '{n1.get('label', '')}' doesn't exist in other graph")
                dist += scores['missing_object']

                # additionally substract points for missing node attributes
                if thisNodeType == str(NodeType.NODE):
                    # get all attributes
                    x = self.get_attr_and_comp(f"{n1.get('label', '')}.*")
                    for y in x:
                        distancePerProperty = scores['missing_property'][str(NodeType.ATTRIBUTE)]
                        if debugging:
                            print(f"   ✗ {distancePerProperty:+.2f}, missing {NodeType.ATTRIBUTE} '{y.get('label', '')}' ")
                        dist += distancePerProperty
            else:
                # node exists, check equality and compare
                if debugging: 
                    print(f"   ✓        exists")
                    #print(["test", n1, n1["nodeType"]])
                    
                if thisNodeType == str(NodeType.RELATION):
                    #if debugging: print(f"   checking relation for comparison")
                    
                    n2 = otherGraph.get_rel_adv(n1)
                    #if debugging: print(f"   found {n2['label']}")
                    if n2 == False:
                        if debugging: print(f" cannot get relation {n1['label']} for comparison ")
                        dist += scores['missing_object']
                        continue
                else:
                    n2 = otherGraph.get_obj(n1["label"], n1["nodeType"])

                localDist = self.__compare_two_nodes(n1, n2, 
                    scores, otherGraph, debugging)

                dist += localDist

                if debugging:
                    print(f"   =  {dist:.2f}")

        if debugging:
            print(f" ---------------")
            print(f"   ∑  {dist:.2f}")        
        return dist

    def __compare_node_properties(self, thisNode, otherNode, key, debugging):
        #if debugging: 
        #    print(f"comparing property[{thisNode.get('label', '')}.{key}]: {thisNode[key]} vs {otherNode[key]}")
        thisValue = thisNode.get(key, "")
        otherValue = otherNode.get(key, "")
        
        # RELATION: don't check "relation" and "relationLabel" strings
        if thisNode.get('nodeType', NodeType.NOT_SPECIFIED) == str(NodeType.RELATION): 
            if key == "relation":
                return True
            if key == "relationLabel":
                return True
        
            # RELATION: don't differentiate between letters
            if  (key == "fromEdgeLabel" or key == "toEdgeLabel") and (otherValue.isalpha() and thisValue.isalpha()):
                #if debugging: 
                #    print(f"   // ignoring literal mismatch in edge label {thisValue} vs {otherValue}")
                return True
            
            if thisValue != otherValue:
                #if debugging: print(f"direct property match {key} fail {thisValue} vs {otherValue}")
                check = False
                if key == "relationFrom":
                    check = (thisNode.get("relationFrom", "") == otherNode.get("relationTo", ""))
                    #if debugging: print(f'({thisNode.get("relationFrom", "")} == {otherNode.get("relationTo", "")})?')
                if key == "relationTo":
                    check = (thisNode.get("relationTo", "") == otherNode.get("relationFrom", ""))
                    #if debugging: print(f'({thisNode.get("relationTo", "")} == {otherNode.get("relationFrom", "")})?')
                if key == "fromEdgeLabel":
                    check = (thisNode.get("fromEdgeLabel", "") == otherNode.get("toEdgeLabel", ""))
                    #if debugging: print(f'({thisNode.get("fromEdgeLabel", "")} == {otherNode.get("toEdgeLabel", "")})?')
                if key == "toEdgeLabel":
                    check = (thisNode.get("toEdgeLabel", "") == otherNode.get("fromEdgeLabel", ""))
                    #if debugging: print(f'({thisNode.get("toEdgeLabel", "")} == {otherNode.get("fromEdgeLabel", "")})?')
                if key == "subClasses":
                    thisSubClasses = thisNode.get("subClasses", [])
                    otherSubClasses = otherNode.get("subClasses", [])
                    if isinstance(thisSubClasses, list): thisSubClasses = thisSubClasses.sort()
                    if isinstance(otherSubClasses, list): otherSubClasses = otherSubClasses.sort()
                    check = (thisSubClasses == otherSubClasses)
                    if debugging: print(f'({thisNode.get("subClasses", "")} == {otherNode.get("subClasses", "")})?')
                if not check:
                    #if debugging: print(f"inverse property compare {key} fail {thisValue} vs {otherValue}")
                    return False
                else:
                    return True

            
        if thisValue != otherValue:
            if debugging: 
                print(f"property compare {key} fail {thisValue} vs {otherValue}")
            return False
        return True

    def __compare_two_nodes(self, thisNode, otherNode, 
                        scores, otherGraph, debugging):
        #if thisNode.get('label', '') != otherNode.get('label', ''):
        #    if self.debug: print(f"node compare label fail {thisNode.get('label', '')} vs {otherNode.get('label', '')}")
        #    return False

        # TODO: refactor these items into separate classes with helper functions

        localDist = 0

        if thisNode["nodeType"] == str(NodeType.NODE):
            # SPECIAL CASE: NodeType.NODE - compare node attributes
            nodeAttributes = self.get_attr(f"{thisNode.get('label', '')}.*")
            for localAttr in nodeAttributes:
                distancePerProperty = scores['missing_property'][str(NodeType.ATTRIBUTE)]

                # is attribute missing?
                if not otherGraph.has_attr(localAttr.get('label', '')):
                    if debugging:
                        print(f"   ✗ {distancePerProperty:+.2f}, missing {NodeType.ATTRIBUTE} '{localAttr.get('label', '')}' ")
                    localDist += distancePerProperty
                else:
                    # exists but check params (isWeak etc.)
                    otherAttr = otherGraph.get_attr(localAttr.get('label', ''))
                    for key, value in localAttr.items():
                        if value != otherAttr[key]:
                            if debugging:
                                print(f"   ✗ {distancePerProperty:+.2f}, mismatch@{key}: {value} != {otherAttr[key]} ")
                            localDist += distancePerProperty

        # compare node properties (isWeak etc.)

        # comparison property keys:
        _nodeType = thisNode.get('nodeType', NodeType.NOT_SPECIFIED)
        if _nodeType == str(NodeType.NODE):
            propertyKeys = ['isMultiple', 'isWeak']
        if _nodeType == str(NodeType.ATTRIBUTE) or _nodeType == str(NodeType.COMPOSED_ATTRIBUTE):
            propertyKeys = ['attrLabel', 'parentLabel', 'isPK', 'isMultiple', 'isWeak', 'composedOf']
        if _nodeType == str(NodeType.IS_A):
            propertyKeys = ['relation', 'superClassLabel', 'superLabel', 'subLabel', 'isDisjunct', 'subClasses']
        if _nodeType == str(NodeType.RELATION):
            propertyKeys = ['relationFrom', 'relationTo', 'fromEdgeLabel', 'toEdgeLabel', 'isWeak']
        distancePerProperty = scores['missing_property'][_nodeType]
        for k in propertyKeys:
            #if debugging: print([thisNode, otherNode])
            if not self.__compare_node_properties(thisNode, otherNode, k, debugging):
                if debugging:
                    print(f"   ✗ {distancePerProperty:+.2f}, property mismatch")
                localDist += distancePerProperty
            else:
                continue
        
        return localDist

    def print_nodes(self):
        if self.debug:
            print("-> printing nodes")
        for n in self.get_graph().nodes(data=True):
            print(n)
    def print_edges(self):
        if self.debug:
            print("-> printing edges")
        for e in self.get_graph().edges(data=True):
            print(e)

    def has_node(self, label):
        return self.has_obj(label, NodeType.NODE)#self.get_graph().has_node(label)

    def has_attr(self, label):
        return self.has_obj(label, NodeType.ATTRIBUTE)

    def has_comp_attr(self, label):
        return self.has_obj(label, NodeType.COMPOSED_ATTRIBUTE)

    def has_attr_or_comp(self, label):
        return self.has_attr(label) or self.has_comp_attr(label)

    def has_rel(self, label):
        return self.has_obj(label, NodeType.RELATION)

    def has_rel_adv(self, thisNode):
        propertyKeys = ['relationFrom', 'relationTo', 'fromEdgeLabel', 'toEdgeLabel', 'isWeak']
        x = self.get_obj("", NodeType.RELATION)
        #if self.debug: print(["testing with ", thisNode])
        for otherNode in self.get_obj("", NodeType.RELATION):
            #if self.debug: print(["testing for ", otherNode])
            for k in propertyKeys:
                if self.__compare_node_properties(thisNode, otherNode, k, self.debug):
                    return True
                else:
                    continue
        return False

    def has_isA(self, label):
        return self.has_obj(label, NodeType.IS_A)

    def has_obj(self, label, node_type=NodeType.NOT_SPECIFIED):
        """"
            Checks existence of object of node_type. 
            If label is empty, checks for all objects of this type.
            If node_type is NodeType.NOT_SPECIFIED, counts all objects in graph.
        """
        return len(self.get_obj(label, node_type)) > 0

    def get_obj(self, label="", node_type=NodeType.NOT_SPECIFIED):
        """"
            Gets object of node_type. 
            If label is empty, gets all objects of this type.
            If node_type is NodeType.NOT_SPECIFIED, gets all objects in graph.
        """
        if label.endswith(".*"):
            label = label.partition("*")[0]
        obj_list = []

        for obj in list(self.get_graph().nodes(data=True)):
            potentialNode = obj[1]
            potentialNodeType = potentialNode.get("nodeType", NodeType.NOT_SPECIFIED)
            if ( node_type == NodeType.NOT_SPECIFIED or potentialNodeType == str(node_type) ):
                #if self.debug: print([f"label={label}  | nodeType={potentialNodeType}", "considering", potentialNode])
                obj_label = potentialNode.get("label", "")
                if label == "": 
                    #if self.debug: print([f"label={label}", "found", potentialNode])
                    obj_list.append(potentialNode) # get all nodes of this type
                    continue
                if label.endswith("."):
                    #if self.debug: print("wildcard search" + label + "*")
                    if obj_label.startswith(label):
                        obj_list.append(potentialNode)
                    continue
                if potentialNodeType == str(NodeType.RELATION):
                    # hackaround: replace the relationLabel away
                    left, bracket, rest = label.partition("-->")
                    block, bracket, right = rest.partition("<--")
                    new_label = left + right

                    left, bracket, rest = obj_label.partition("-->")
                    block, bracket, right = rest.partition("<--")
                    new_obj_label = left + right
                    #if self.debug: print(["checking", new_label, new_obj_label])
                    if new_label == new_obj_label:
                        return potentialNode

                if obj_label == label:
                    return potentialNode
        return obj_list

    def get_subtree(self, rootNode):
        """
            Returns DFS subtree of object graph, starting at rootNode
            WARNING: In the returned DFS tree, there are no object attributes. 
                     Query the original graph for them.
        """
        if not self.has_obj(rootNode): 
            raise KeyError(f"There is no item named '{rootNode}' in the graph")
        
        return nx.dfs_tree(self.get_graph(), rootNode)

    def get_node(self, label=""):
        return self.get_obj(label, NodeType.NODE)

    def get_rel(self, label=""):
        return self.get_obj(label, NodeType.RELATION)

    def get_rel_adv(self, thisNode):
        propertyKeys = ['relationFrom', 'relationTo', 'fromEdgeLabel', 'toEdgeLabel', 'isWeak']
        #if self.debug: print([f"testing relation (found {len(self.get_obj("", NodeType.RELATION))} others), this: ", thisNode])
        for otherNode in self.get_obj("", NodeType.RELATION):
            #if self.debug: print(["testing relation, other: ", otherNode])
            propertyTestCount = 0
            for k in propertyKeys:
                propertyTest = self.__compare_node_properties(thisNode, otherNode, k, self.debug)
                #if self.debug: print(f"testing property {k}, mismatch? {propertyTest}")
                if propertyTest:
                    propertyTestCount += 1
                else:
                    continue
            if propertyTestCount == len(propertyKeys):
                return otherNode
        return False        

    def get_attr(self, label=""):
        return self.get_obj(label, NodeType.ATTRIBUTE)

    def get_comp_attr(self, label=""):
        return self.get_obj(label, NodeType.COMPOSED_ATTRIBUTE)

    def get_attr_and_comp(self, label=""):
        ret_list = []
        attrs = self.get_obj(label, NodeType.ATTRIBUTE) 
        comps = self.get_obj(label, NodeType.COMPOSED_ATTRIBUTE)
        for i in attrs:
            ret_list.append(i)
        for i in comps:
            ret_list.append(i)
        return ret_list

    def get_isA(self, label=""):
        return self.get_obj(label, NodeType.IS_A)

    def get_node_count(self):
        return len(self.get_graph().nodes())

    def get_obj_count(self, nodeType = NodeType.NOT_SPECIFIED):
        return len(self.get_obj("", nodeType))
                    
    def get_graphViz(self):
        return self.graphViz

    def print_graphml(self):
        for line in nx.generate_graphml(self.get_graph()):
            print(line)

    def write_graphml(self, fname):
        nx.write_graphml_lxml(self.get_graph(), fname)
    
    def asGraphvizPlaygroundUrl(self):
        '''
        Returns:
            str(graphviz playground URL)
        '''
        graphVizCode=str(self.graphViz)
        encoded=quote(graphVizCode.encode('utf8'))
        url=f"http://magjac.com/graphviz-visual-editor/?{self.graphViz.engine}={encoded}"
        return url
    
    def __format_label(self, label, isWeak=False, isPK=False):
        if isWeak and isPK:
            # https://stackoverflow.com/a/57950193/665159
            i = 0 
            tempLabel = ''
            for c in label:
                i += 1
                if i % 2:
                    tempLabel += '<u>' + c + '</u>'
                else:
                    tempLabel += c
            return '<' + tempLabel + '>'
        elif isPK:
            return f'<<U>{label}</U>>'
        else:
            return label
