import re
import json


class SemanticQuery:
    def _parse_query_script(self, query_script):

        items = []

        base_re = "^\((.+)\) *(\{.*\})$"
        ids_re = "^\*{0,1}\S+$|^\*{0,1}\S+ \*{0,1}\S+ \*{0,1}\S+$"
        for line in query_script.split("\n"):
            res = re.search(base_re, line.strip())
            if res:
                ids = re.search(ids_re, res.groups()[0])
                props = res.groups()[1]
                assert ids is not None
                ids = ids.string.split(" ")
                props = json.loads(props)
                items.append((ids, props))

        return items

    def _split_required_query_items(self, query_items):

        new_items = []
        required_obj_ids = set()
        required_rel_ids = set()
        optional_obj_ids = set()
        optional_rel_ids = set()
        for elements, props in query_items:

            if len(elements) == 1:
                obj_id = elements[0]

                if obj_id[0] == "*":
                    obj_id = obj_id[1:]
                    optional_obj_ids.add(obj_id)
                else:
                    required_obj_ids.add(obj_id)
                new_items.append(([obj_id], props))

            elif len(elements) == 3:
                rel_id, source_obj_id, target_obj_id = elements

                if rel_id[0] == "*":
                    rel_id = rel_id[1:]
                    optional_rel_ids.add(rel_id)
                else:
                    required_rel_ids.add(rel_id)
                if source_obj_id[0] == "*":
                    source_obj_id = source_obj_id[1:]
                    optional_obj_ids.add(source_obj_id)
                else:
                    required_obj_ids.add(source_obj_id)
                if target_obj_id[0] == "*":
                    target_obj_id = target_obj_id[1:]
                    optional_obj_ids.add(target_obj_id)
                else:
                    required_obj_ids.add(target_obj_id)

                new_items.append(([rel_id, source_obj_id, target_obj_id], props))

        assert len(required_obj_ids.intersection(optional_obj_ids)) == 0
        assert len(required_rel_ids.intersection(optional_rel_ids)) == 0

        return new_items, required_obj_ids, required_rel_ids

    def __init__(self, semantic_network, query_script):
        self.semantic_network = semantic_network
        self.query_script = query_script
        parsed_items = self._parse_query_script(query_script)
        splitted_items, required_obj_ids, required_rel_ids = self._split_required_query_items(
            parsed_items
        )

        q = semantic_network.__class__("Query")
        for ids, props in splitted_items:
            if len(ids) == 1:
                q.create_object(ids[0], props)
            elif len(ids) == 3:
                q.create_relation(ids[0], ids[1], ids[2], props)

        self.q = q
        self.required_obj_ids = required_obj_ids
        self.required_rel_ids = required_rel_ids

    def __iter__(self):
        res = self.semantic_network.search_pattern(
            self.q, self.required_obj_ids, self.required_rel_ids
        )
        return iter(res)
