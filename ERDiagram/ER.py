from graphviz import Digraph
from IPython.display import display
from urllib.parse import quote
import networkx as nx
from networkx.readwrite import json_graph
from erdiagram.NodeType import NodeType

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
            print(f">> adding edge: {fromNodeLabel} <---[{edgeLabel}]---> {toNodeLabel}")
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

        attrLabel = f'{parentLabel}.{attrLabel}'
        if self.debug: 
            print(f">> adding attribute: {attrLabel}")

        self.get_graph().add_node(attrLabel, 
            label = attrLabel,
            isPK = isPK,
            isMultiple = isMultiple,
            isWeak = isWeak,
            composedOf = str(composedOf),
            nodeType= str(NodeType.ATTRIBUTE)
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
        relationLabel = f"{fromNodeLabel}<->{label}<->{toNodeLabel}"
        if self.debug: 
            print(f">> adding relation: {label}")
        self.get_graph().add_node(relationLabel, 
            label = relationLabel,
            relation = f"{fromNodeLabel}<-[{fromEdgeLabel}]--[{toEdgeLabel}]->{toNodeLabel}",
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
            relation = f"{superClassLabel}->[{superLabel}]->[isA]->[{subLabel}]->{subClasses}",
        else:
            isALabel = f"{superClassLabel}.isA.{subClasses}"
            relation = f"{superClassLabel}<-[{superLabel}]<-[isA]<-[{subLabel}]<-{subClasses}",
        if self.debug: 
            print(f">> adding relation: {isALabel}")
        
        self.get_graph().add_node( isALabel,
            label = isALabel,
            relation = relation,
            superClassLabel = superClassLabel,
            superLabel = superLabel,
            subLabel = subLabel,
            isDisjunct = isDisjunct,
            subClasses = str(subClasses),
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

        # add new node to graphML graph
        self.__add_graphml_attr(nodeLabel, attrLabel, isPK, isMultiple, isWeak, composedOf)

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
                print(f">> >> adding sublabel {fullSubLabel} ")

            # add to graphML graph
            self.__add_graphml_attr(f'{nodeLabel}.{attrLabel}', subAttrLabel, isPK, isMultiple, isWeak)
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
            fromEdgeLabel(str): Label on the "from" edge
            toEdgeLabel(str): Label on the "to" edge
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

        self.__add_graphml_relation(relationLabel, fromNodeLabel, toNodeLabel, fromEdgeLabel, toEdgeLabel, isWeak)

        # TODO: refactor this to .render() function
        # Add a relation between two nodes - a red rhombus
        self.__add_graphviz_relation(relationLabel, fromNodeLabel, toNodeLabel, fromEdgeLabel, toEdgeLabel, isWeak)

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

    def compareNodes(self, otherGraph, label = "", node_type = NodeType.NOT_SPECIFIED, scores={}):
        dist = 0
        if self.debug:
            print(" ¶ calculating distances between graphs:    ")
        for n1 in self.get_obj(label, node_type = node_type):
            if self.debug:
                print(f" » testing {n1['label']}:")
            if not otherGraph.has_node(n1["label"]):
                if self.debug:
                    print(f"   ✗ {scores['missing_node']:+.2f}, node '{n1['label']}' doesn't exist in other graph")
                dist += scores['missing_node']
            else:
                # node exists, check equality
                n2 = otherGraph.get_obj(n1["label"], node_type)
                if n1 == n2:
                    if self.debug:
                        print(f"   ✓  {0:.2f}, match@{n1['label']}")
                        print(f"   =  {dist:.2f}")
                    continue
                distancePerProperty = scores['missing_property'][n1['nodeType']]

                for k, v in n1.items():
                    if v != n2[k]:
                        if self.debug:
                            print(f"   ✗ {distancePerProperty:+.2f}, mismatch@{k}: {v} != {n2[k]} ")
                        dist += distancePerProperty

            if self.debug:
                print(f"   =  {dist:.2f}")

        if self.debug:
            print(f" ---------------")
            print(f"   ∑  {dist:.2f}")        
        return dist

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
        return self.get_graph().has_node(label)

    def has_attr(self, label):
        return self.has_obj(label, NodeType.ATTRIBUTE)

    def has_rel(self, label):
        return self.has_obj(label, NodeType.RELATION)

    def has_isA(self, label):
        return self.has_obj(label, NodeType.ATTRIBUTE)

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
        obj_list = []
        for obj in list(self.get_graph().nodes(data=True)):
            if ( node_type == NodeType.NOT_SPECIFIED or obj[1]["nodeType"] == str(node_type) ):
                if ( label == ""): 
                    obj_list.append(obj[1]) # get all nodes of this type
                if ( obj[1]["label"] == label ):
                    return obj[1]
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

    def get_attr(self, label=""):
        return self.get_obj(label, NodeType.ATTRIBUTE)

    def get_isA(self, label=""):
        return self.get_obj(label, NodeType.IS_A)

    def get_node_count(self):
        return len(self.get_graph().nodes())
                    
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
