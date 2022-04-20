from collections import Counter
from semantic_network.net import SemanticNetwork


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

    assert sn.is_acyclic(relation_id="rel1") == False
    assert sn.is_acyclic(relation_id="rel2") == True
