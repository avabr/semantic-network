from collections import Counter
from semantic_network import SemanticNetwork


def test_query_exclude():

    sn_script = """
        
        -- Define a circle and it's parts
        Circle
        Circle.radius
        Circle.center
        Circle hasPart Circle.radius
        Circle hasPart Circle.center
        
        -- Define the first object (c1 does not have any parts)
        c1 fromProto Circle
        
        -- Define another object
        c2.radius
        c2.center
        c2 fromProto Circle
        c2 hasPart c2.radius
        c2 hasPart c2.center
        c2.radius fromProto Circle.radius
    """

    sn = SemanticNetwork.from_script(sn_script)

    query = """
        *obj fromProto Circle
    """

    exclude = """
        *obj hasPart *part
    """

    matches = sn.query(query, exclude=exclude)
    assert len(matches) == 1
