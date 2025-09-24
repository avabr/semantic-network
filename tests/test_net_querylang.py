from collections import Counter
from semantic_network import SemanticNetwork


def collapse_chain_set(chain_set):
    items = []
    for obj_mapping, rel_mapping in chain_set:
        for k, v in obj_mapping.items():
            items.append(("obj", k, v))
        for k, v in rel_mapping.items():
            items.append(("rel", k, v))
    cnt = dict(Counter(items))
    return cnt


def test_lang_pattern_3():

    sn_script = """
        Circle
        Circle.radius
        Circle.center
        Circle hasPart Circle.radius
        Circle hasPart Circle.center
        c1
        c1 fromProto Circle
        c1.radius
        c1 hasPart c1.radius
        c2
        c2.radius
        c2.center
        c2 fromProto Circle
        c2 hasPart c2.radius
        c2 hasPart c2.center
        c2.radius fromProto Circle.radius
    """

    sn = SemanticNetwork.from_script(sn_script)

    q = """
        *Class
        *Class.part
        *Class hasPart *Class.part
        *Object
        *Object fromProto *Class
        *Object.part
        *Object hasPart *Object.part
        *Object.part fromProto *Class.part
    """
    matches = sn.query(q)

    right_mapping_counter = {
        ("obj", "Object", "c2"): 1,
        ("obj", "Object.part", "c2.radius"): 1,
        ("obj", "Class.part", "Circle.radius"): 1,
        ("obj", "Class", "Circle"): 1,
        ("rel", "hasPart", "hasPart"): 1,
        ("rel", "fromProto", "fromProto"): 1,
    }
    assert collapse_chain_set(matches) == right_mapping_counter

    q = """
        *Class hasPart *Class.part
        *Object fromProto *Class
        *Object hasPart *Object.part
        *Object.part fromProto *Class.part
    """

    for obj_mapping, rel_mapping in sn.query(q, strict_mode=False):
        for k, v in obj_mapping.items():
            print("obj", k, v)
        for k, v in rel_mapping.items():
            print("rel", k, v)


def test_lang_pattern_4():

    sn_script = """
        ^a1 instanceOf Point
        ^a2 instanceOf Point
        ^a3 instanceOf Point
        ^c1 instanceOf Circle
        ^c2 instanceOf Circle
        ^a1 isCenterOf ^c1
    """

    sn = SemanticNetwork.from_script(sn_script)

    q = """
        *point instanceOf Point
        *circle instanceOf Circle
        *point isCenterOf *circle
    """

    for obj_mapping, rel_mapping in sn.query(q, strict_mode=False):
        for k, v in obj_mapping.items():
            print("obj", k, v)
        for k, v in rel_mapping.items():
            print("rel", k, v)
