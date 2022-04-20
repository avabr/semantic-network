import re
import json


def parse_script(script, query_script=False):

    items = []

    id_re = r"^[\w\-\.@]+$"
    if query_script:
        id_re = r"^\*{0,1}[\w\-\.@]+$"

    for line in script.strip().split("\n"):

        if len(line) == 0:
            continue

        ids = line.strip().split(" ")
        assert None not in [re.search(id_re, i) for i in ids], (
            "%s line of Semantic script is not correct" % line
        )
        assert len(ids) in [1, 3], "%s line of Semantic script is not correct" % line

        items.append(ids)

    return items
