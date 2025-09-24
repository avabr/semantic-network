from semantic_network import SemanticNetwork


def test_lang_pattern_3():

    sn_script = """
        Circle hasPart Circle.radius
        Circle hasPart Circle.center
    """

    sn = SemanticNetwork.from_script(sn_script, strict_mode=False)

    sn_script_2 = """
        c1 fromProto Circle
        c1 hasPart c1.radius
        c2 fromProto Circle
        c2 hasPart c2.radius
        c2 hasPart c2.center
        c2.radius fromProto Circle.radius
    """

    sn.append_script(sn_script_2)

    assert len(sn.objects_by_id) == 8
