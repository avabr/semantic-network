from collections import Counter
from semantic_network.net import SemanticNetwork


def collapse_chain_set(chain_set):
    items = []
    for chain in chain_set:
        obj_mapping, rel_mapping = chain.get_mapping()
        for k, v in obj_mapping.items():
            items.append(("obj", k, v))
        for k, v in rel_mapping.items():
            items.append(("rel", k, v))
    cnt = dict(Counter(items))
    return cnt


def test_lang_pattern_3():

    sn_script = """
        (Circle)
        (Circle.radius)
        (Circle.center)
        (hasPart Circle Circle.radius)
        (hasPart Circle Circle.center)
        (c1) {"type": "some_object"}
        (fromProto c1 Circle)
        (c1.radius)
        (hasPart c1 c1.radius)
        (c2)
        (c2.radius)
        (c2.center)
        (fromProto c2 Circle)
        (hasPart c2 c2.radius)
        (hasPart c2 c2.center)
        (fromProto c2.radius Circle.radius)
    """

    sn = SemanticNetwork.from_script(sn_script)

    q = """
        (*Class)
        (*Class.part)
        (hasPart *Class *Class.part)
        (*Object)
        (fromProto *Object *Class)
        (*Object.part)
        (hasPart *Object *Object.part)
        (fromProto *Object.part *Class.part)
    """
    chains = sn.search_query_script(q)

    right_mapping_counter = {
        ("obj", "Object", "c2"): 1,
        ("obj", "Object.part", "c2.radius"): 1,
        ("obj", "Class.part", "Circle.radius"): 1,
        ("obj", "Class", "Circle"): 1,
        ("rel", "hasPart", "hasPart"): 1,
        ("rel", "fromProto", "fromProto"): 1,
    }
    assert collapse_chain_set(chains) == right_mapping_counter
