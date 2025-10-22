import re


def clean_script(script: str):
    """
    Clean script: remove empty lines and comments:
    - remove line if l.scrip() == ''
    - remove line if l.scrip()[:2] == '--'
    """
    lines = []
    for line in script.strip().split("\n"):
        if (line.strip() != "") and (line.strip()[:2] != "--"):
            lines.append(line)
    return "\n".join(lines)


def decompose_multiline_script(script):

    new_lines = []
    existed_lines = set()

    for line in script.strip().split("\n"):
        line = line.strip()
        items = line.strip().split(" ")
        assert len(items) % 2 == 1, "%s line of Semantic script is not correct" % line
        if len(line) <= 3:
            if line not in existed_lines:
                new_lines.append(line)
            existed_lines.add(line)
        else:
            ls = []
            for i in range(0, len(items) - 1, 2):
                new_line = " ".join(items[i : i + 3])
                if new_line not in existed_lines:
                    ls.append(new_line)
                existed_lines.add(new_line)
            new_lines = new_lines + ls[::-1]
    result = "\n".join(new_lines)

    return result


def parse_script(script, query_script=False):

    script = clean_script(script)

    if type(script) in (list, tuple):
        script = "\n".join(script)

    items = []

    id_re = r"^[\w\-\.@^#$:\(\),\[\]|/=]+$"
    if query_script:
        script = decompose_multiline_script(script)
        id_re = r"^\*{0,1}[\w\-\.@^#$:\(\),\[\]|/=]+$"

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
