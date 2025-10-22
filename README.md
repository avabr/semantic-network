# semantic_network Package
## SemanticNetwork

The class is designed for encoding graph structures using universal triplets:

    entity_1 relation entity_2
    entity_2 relation entity_3

- Triplet parts are separated by spaces
- First and third parts are objects
- Second part is a directed relationship between objects


#### 1. Creating and Extending the Graph:

    from semantic_network import SemanticNetwork

    script = """
        Circle hasPart Circle.radius
        Circle hasPart Circle.center
    """

    sn = SemanticNetwork.from_script(script)

    script_2 = """
        c1 fromProto Circle
        c1 hasPart c1.radius
        c2 fromProto Circle
        c2 hasPart c2.radius
        c2 hasPart c2.center
        c2.radius fromProto Circle.radius
    """

    sn.append_script(script_2)

This creates a graph with objects and relationships:

    print(sn)
    ----------------------------------------
    |- c1
    |- Circle
    |- c1 fromProto Circle
    |- c1.radius
    |- c1 hasPart c1.radius
    |- c2
    |- c2 fromProto Circle
    |- c2.radius
    |- c2 hasPart c2.radius
    |- c2.center
    |- c2 hasPart c2.center
    |- Circle.radius
    |- c2.radius fromProto Circle.radius
    ----------------------------------------


#### 2. Graph Search
Search queries are specified using a special query format.
Elements starting with * are treated as variables, while other elements are treated as constants.

    q = """
        *o1 hasPart *o2
        *o1 fromProto Circle
    """

    for objs, rels in sn.query(q):
        print(objs, rels)

Returns dictionaries with found graph fragments:

    {'o1': 'c2', 'Circle': 'Circle', 'o2': 'c2.radius'} {'fromProto': 'fromProto', 'hasPart': 'hasPart'}
    {'o1': 'c2', 'Circle': 'Circle', 'o2': 'c2.center'} {'fromProto': 'fromProto', 'hasPart': 'hasPart'}
    {'o1': 'c1', 'Circle': 'Circle', 'o2': 'c1.radius'} {'fromProto': 'fromProto', 'hasPart': 'hasPart'}

During search, the system also verifies that the query graph is connected and acyclic.


#### 3. Utility Methods

    # Extend the graph
    sn.append_script(new_script)

    # Print graph description (number of unique objects and relationships)
    sn.describe()
    
    # Create a copy
    sn.copy()

    # Serialization to dictionary and creation from dictionary
    sn.to_dict()
    sn = SemanticNetwork.from_dict(dict_data)

    # Write to file with additional custom variables dictionary, and read from file
    sm.dump(path, variables)
    sn = SemanticNetwork.load(path)
