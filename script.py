import re
import json


def parse_script(script, query_script=False):

    items = []

    allowed_symbols = "\w\-.@"

    base_re = "^\((.+)\) *(\{.*\})$"

    if query_script == True:
        ids_re = "^\*{0,1}[$asyms]+$|^\*{0,1}[$asyms]+ \*{0,1}[$asyms]+ \*{0,1}[$asyms]+$".replace(
            "$asyms", allowed_symbols
        )
    else:
        ids_re = "^[$asyms]+$|^[$asyms]+ [$asyms]+ [$asyms]+$".replace("$asyms", allowed_symbols)

    for line in script.split("\n"):
        res = re.search(base_re, line.strip())
        if res:
            props = res.groups()[1]
            props = json.loads(props)

            ids = re.search(ids_re, res.groups()[0])
            assert ids is not None, '"%s" is not good with regex "%s"' % (res.groups()[0], ids_re)
            ids = ids.string.split(" ")
            assert len(ids) in [1, 3]
            items.append((ids, props))

    return items
