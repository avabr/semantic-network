from semantic_network import SemanticNetwork


def test_acyclic():

    sn = SemanticNetwork("Main")
    sn.create_object("A")
    sn.create_object("B")
    sn.create_object("C")
    sn.create_object("D")

    sn.create_relation("rel1", "A", "B")
    sn.create_relation("rel1", "B", "C")
    sn.create_relation("rel1", "C", "D")
    sn.create_relation("rel1", "D", "A")

    sn.create_relation("rel2", "A", "B")
    sn.create_relation("rel2", "A", "C")
    sn.create_relation("rel2", "C", "D")
    sn.create_relation("rel2", "A", "D")

    sn.create_relation("rel3", "C", "A")

    assert sn.is_acyclic(relation_ids=["rel1"]) == False
    assert sn.is_acyclic(relation_ids=["rel2"]) == True
    assert sn.is_acyclic(relation_ids=["rel2", "rel3"]) == False
