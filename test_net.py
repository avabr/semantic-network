import pytest
from semantic_network.net import SemanticNetwork


def test_net_index_consistency():
    sn = SemanticNetwork()
    sn.create_object("proto@Circle", {})
    sn.create_object("proto@Circle.x", {})
    sn.create_object("proto@Circle.y", {})
    sn.create_relation("hasPart", "proto@Circle", "proto@Circle.x", {})
    sn.create_relation("hasPart", "proto@Circle", "proto@Circle.y", {})
    sn.create_object("Circle_1", {})
    sn.create_relation("fromProto", "Circle_1", "proto@Circle", {})

    r = sn.get_or_create_relation("hasPart", "proto@Circle", "proto@Circle.x")

    assert len(sn.relations_by_relation_id) == 2
    assert len(sn.relations_by_source_id) == 2
    assert len(sn.relations_by_target_id) == 3
    assert len(sn.objects_by_id) == 4
    assert len(set([r[0] for r in sn.relation_by_triplet.keys()])) == 2
    assert len(list(sn.relation_by_triplet.keys())) == 3

    sn.detach_delete_object("proto@Circle")

    assert len(sn.relations_by_relation_id) == 0
    assert len(sn.relations_by_source_id) == 0
    assert len(sn.relations_by_target_id) == 0
    assert len(sn.objects_by_id) == 3
    print(sn.relation_by_triplet)
    assert len(set([r[0] for r in sn.relation_by_triplet.keys()])) == 0
    assert len(list(sn.relation_by_triplet.keys())) == 0


if __name__ == "__main__":
    test_net_index_consistency()
