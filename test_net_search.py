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


def test_search_pattern_1():

    sn = SemanticNetwork("Main")
    sn.create_object("C", {})
    sn.create_object("C.r", {})
    sn.create_object("C.c", {})
    sn.create_relation("hasPart", "C", "C.r", {})
    sn.create_relation("hasPart", "C", "C.c", {})
    sn.create_object("c1", {})
    sn.create_relation("fromProto", "c1", "C", {})
    sn.create_object("c1.c", {})
    sn.create_relation("hasPart", "c1", "c1.c", {})
    sn.create_object("c2", {})
    sn.create_relation("fromProto", "c2", "C", {})
    sn.create_object("c2.c", {})
    sn.create_relation("hasPart", "c2", "c2.c", {})
    sn.create_object("c3", {})
    sn.create_relation("fromProto", "c3", "C", {})
    sn.create_object("c3.c", {})
    sn.create_relation("hasPart", "c3", "c3.c", {})
    sn.create_object("ext_r", {})
    sn.create_relation("fromProto", "ext_r", "C.r", {})

    q = SemanticNetwork("Query")
    q.create_object("class", {})
    q.create_object("obj1", {})
    q.create_relation("fromProto", "obj1", "class", {})
    chains = sn.search_pattern(q, set(), set(["fromProto", "hasPart"]))

    right_mapping_counter = {
        ("obj", "obj1", "c3"): 1,
        ("obj", "obj1", "c1"): 1,
        ("obj", "obj1", "ext_r"): 1,
        ("obj", "class", "C.r"): 1,
        ("obj", "obj1", "c2"): 1,
        ("obj", "class", "C"): 3,
        ("rel", "fromProto", "fromProto"): 4,
    }
    assert collapse_chain_set(chains) == right_mapping_counter

    q = SemanticNetwork("Query")
    q.create_object("class", {})
    q.create_object("obj1", {})
    q.create_relation("fromProto", "obj1", "class", {})
    q.create_object("class.x", {})
    q.create_relation("hasPart", "class", "class.x", {})
    chains = sn.search_pattern(q, set(), set(["fromProto", "hasPart"]))

    right_mapping_counter = {
        ("obj", "obj1", "c3"): 2,
        ("obj", "class", "C"): 6,
        ("obj", "class.x", "C.c"): 3,
        ("rel", "fromProto", "fromProto"): 6,
        ("rel", "hasPart", "hasPart"): 6,
        ("obj", "class.x", "C.r"): 3,
        ("obj", "obj1", "c1"): 2,
        ("obj", "obj1", "c2"): 2,
    }
    assert collapse_chain_set(chains) == right_mapping_counter

    q = SemanticNetwork("Query")
    q.create_object("class", {})
    q.create_object("obj1", {})
    q.create_relation("fromProto", "obj1", "class", {})
    q.create_object("class.x", {})
    q.create_relation("hasPart", "class", "class.x", {})
    q.create_object("class.y", {})
    q.create_relation("hasPart", "class", "class.y", {})
    q.create_object("ext_r", {})
    q.create_relation("fromProto", "ext_r", "class.y", {})
    chains = sn.search_pattern(q, set([]), set(["fromProto", "hasPart"]))

    right_mapping_counter = {
        ("obj", "obj1", "c1"): 1,
        ("obj", "class", "C"): 3,
        ("obj", "class.y", "C.r"): 3,
        ("obj", "ext_r", "ext_r"): 3,
        ("obj", "class.x", "C.c"): 3,
        ("rel", "fromProto", "fromProto"): 3,
        ("rel", "hasPart", "hasPart"): 3,
        ("obj", "obj1", "c3"): 1,
        ("obj", "obj1", "c2"): 1,
    }
    assert collapse_chain_set(chains) == right_mapping_counter


def test_search_pattern_2():

    sn = SemanticNetwork("Main")
    sn.create_object("C", {})
    sn.create_object("C.r", {})
    sn.create_object("C.c", {})
    sn.create_relation("hasPart", "C", "C.r", {})
    sn.create_relation("hasPart", "C", "C.c", {})
    sn.create_object("c1", {})
    sn.create_relation("fromProto", "c1", "C", {})
    sn.create_object("c1.c", {})
    sn.create_relation("hasPart", "c1", "c1.c", {})
    sn.create_object("c2", {})
    sn.create_relation("fromProto", "c2", "C", {})
    sn.create_object("c2.c", {})
    sn.create_relation("hasPart", "c2", "c2.c", {})
    sn.create_object("c3", {})
    sn.create_relation("fromProto", "c3", "C", {})
    sn.create_object("c3.c", {})
    sn.create_relation("hasPart", "c3", "c3.c", {})
    sn.create_object("c4", {})
    sn.create_relation("fromProto", "c4", "C", {})
    sn.create_object("ext_r", {})
    sn.create_relation("fromProto", "ext_r", "C.r", {})

    q = SemanticNetwork("Query")
    q.create_object("C", {})
    q.create_object("obj1", {})
    q.create_relation("someRelation", "C", "obj1", {})
    q.create_object("obj1.obj", {})
    q.create_relation("someRelation2", "obj1.obj", "obj1", {})
    chains = sn.search_pattern(q, set(["C"]), set([]))

    right_mapping_counter = {
        ("obj", "obj1.obj", "ext_r"): 1,
        ("obj", "obj1", "C.r"): 1,
        ("obj", "C", "C"): 1,
        ("rel", "someRelation2", "fromProto"): 1,
        ("rel", "someRelation", "hasPart"): 1,
    }
    assert collapse_chain_set(chains) == right_mapping_counter

    q = SemanticNetwork("Query")
    q.create_object("A", {})
    q.create_object("B", {})
    q.create_relation("someRelation1", "A", "B", {})
    q.create_object("C", {})
    q.create_relation("someRelation2", "A", "C", {})
    chains = sn.search_pattern(q, set([]), set([]))

    right_mapping_counter = {
        ("obj", "A", "c1"): 2,
        ("obj", "C", "C"): 3,
        ("obj", "B", "c1.c"): 1,
        ("rel", "someRelation2", "fromProto"): 3,
        ("rel", "someRelation1", "hasPart"): 3,
        ("obj", "C", "c1.c"): 1,
        ("obj", "B", "C"): 3,
        ("rel", "someRelation2", "hasPart"): 3,
        ("rel", "someRelation1", "fromProto"): 3,
        ("obj", "A", "c2"): 2,
        ("obj", "B", "c2.c"): 1,
        ("obj", "C", "c2.c"): 1,
        ("obj", "A", "c3"): 2,
        ("obj", "B", "c3.c"): 1,
        ("obj", "C", "c3.c"): 1,
    }
    assert collapse_chain_set(chains) == right_mapping_counter


def test_search_pattern_3():

    sn = SemanticNetwork("Main")
    sn.create_object("Circle", {})
    sn.create_object("Circle.radius", {})
    sn.create_object("Circle.center", {})
    sn.create_relation("hasPart", "Circle", "Circle.radius", {})
    sn.create_relation("hasPart", "Circle", "Circle.center", {})

    sn.create_object("c1", {"type": "some_object"})
    sn.create_relation("fromProto", "c1", "Circle", {})
    sn.create_object("c1.radius", {})
    sn.create_relation("hasPart", "c1", "c1.radius", {})

    sn.create_object("c2", {})
    sn.create_object("c2.radius", {})
    sn.create_object("c2.center", {})
    sn.create_relation("fromProto", "c2", "Circle", {})
    sn.create_relation("hasPart", "c2", "c2.radius", {})
    sn.create_relation("hasPart", "c2", "c2.center", {})
    sn.create_relation("fromProto", "c2.radius", "Circle.radius", {})

    q = SemanticNetwork("Query")
    q.create_object("Class", {})
    q.create_object("Class.part", {})
    q.create_relation("hasPart", "Class", "Class.part", {})

    q.create_object("Object", {})
    q.create_relation("fromProto", "Object", "Class", {})
    q.create_object("Object.part", {})
    q.create_relation("hasPart", "Object", "Object.part", {})
    q.create_relation("fromProto", "Object.part", "Class.part", {})

    chains = sn.search_pattern(q, set([]), set(["fromProto", "hasPart"]))

    right_mapping_counter = {
        ("obj", "Object", "c2"): 1,
        ("obj", "Object.part", "c2.radius"): 1,
        ("obj", "Class.part", "Circle.radius"): 1,
        ("obj", "Class", "Circle"): 1,
        ("rel", "hasPart", "hasPart"): 1,
        ("rel", "fromProto", "fromProto"): 1,
    }
    assert collapse_chain_set(chains) == right_mapping_counter


def test_search_pattern_4():

    sn = SemanticNetwork("Main")
    sn.create_object("Circle", {"type": "ENTITY"})
    sn.create_object("Circle.radius", {"type": "ENTITY"})
    sn.create_object("Circle.center", {"type": "ENTITY"})
    sn.create_relation("hasPart", "Circle", "Circle.radius", {})
    sn.create_relation("hasPart", "Circle", "Circle.center", {})

    sn.create_object("c1", {"type": "ENTITY"})
    sn.create_relation("fromProto", "c1", "Circle", {})
    sn.create_object("c1.radius", {"type": "ENTITY"})
    sn.create_relation("hasPart", "c1", "c1.radius", {})

    sn.create_object("c2", {})
    sn.create_object("c2.radius", {})
    sn.create_object("c2.center", {})
    sn.create_relation("fromProto", "c2", "Circle", {})
    sn.create_relation("hasPart", "c2", "c2.radius", {})
    sn.create_relation("hasPart", "c2", "c2.center", {})
    sn.create_relation("fromProto", "c2.radius", "Circle.radius", {})

    q = SemanticNetwork("Query")
    q.create_object("Circle", {"type": "ENTITY"})
    q.create_object("obj", {"type": "ENTITY"})
    q.create_relation("fromProto", "obj", "Circle", {})
    chains = sn.search_pattern(q, set(["Circle"]), set(["fromProto"]))

    right_mapping_counter = {
        ("obj", "obj", "c1"): 1,
        ("obj", "Circle", "Circle"): 1,
        ("rel", "fromProto", "fromProto"): 1,
    }
    assert collapse_chain_set(chains) == right_mapping_counter

    # for i, ch in enumerate(chains):
    #     obj_mapping, rel_mapping = ch.get_mapping()
    #     print("\tchain %s\t%s, %s" % (i + 1, obj_mapping, rel_mapping))
    # print(collapse_chain_set(chains))


def test_search_pattern_5():

    sn = SemanticNetwork("Main")
    sn.create_object("Circle", {"type": "ENTITY"})
    sn.create_object("Circle.radius", {"type": "ENTITY"})
    sn.create_object("Circle.center", {"type": "ENTITY"})
    sn.create_relation("hasPart", "Circle", "Circle.radius", {})
    sn.create_relation("hasPart", "Circle", "Circle.center", {})

    sn.create_object("c1", {"type": "ENTITY"})
    sn.create_relation("fromProto", "c1", "Circle", {"type": "RELATION"})
    sn.create_object("c1.radius", {"type": "ENTITY"})
    sn.create_relation("hasPart", "c1", "c1.radius", {})

    sn.create_object("c2", {})
    sn.create_object("c2.radius", {})
    sn.create_object("c2.center", {})
    sn.create_relation("fromProto", "c2", "Circle", {})
    sn.create_relation("hasPart", "c2", "c2.radius", {"type": "RELATION"})
    sn.create_relation("hasPart", "c2", "c2.center", {})
    sn.create_relation("fromProto", "c2.radius", "Circle.radius", {})

    assert len(sn.select_objects({"type": "ENTITY"})) == 5
    assert len(sn.select_objects({"someKey": "someValue"})) == 0
    assert len(sn.select_objects({})) == 8

    assert len(sn.select_relations(None, None, None, {"type": "RELATION"})) == 2
    assert len(sn.select_relations(None, None, None, {})) == 8
    assert len(sn.select_relations("fromProto", None, None, {"type": "RELATION"})) == 1


if __name__ == "__main__":
    test_search_pattern_1()
    test_search_pattern_2()
    test_search_pattern_3()
    test_search_pattern_4()
    test_search_pattern_5()
