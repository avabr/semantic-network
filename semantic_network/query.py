from .script import parse_script


class SemanticQuery:
    def _split_required_query_items(self, query_items):

        new_items = []
        required_obj_ids = set()
        required_rel_ids = set()
        optional_obj_ids = set()
        optional_rel_ids = set()
        for elements in query_items:

            if len(elements) == 1:
                obj_id = elements[0]

                if obj_id[0] == "*":
                    obj_id = obj_id[1:]
                    optional_obj_ids.add(obj_id)
                else:
                    required_obj_ids.add(obj_id)
                new_items.append([obj_id])

            elif len(elements) == 3:
                source_obj_id, rel_id, target_obj_id = elements

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

                new_items.append([source_obj_id, rel_id, target_obj_id])

        assert len(required_obj_ids.intersection(optional_obj_ids)) == 0
        assert len(required_rel_ids.intersection(optional_rel_ids)) == 0

        return new_items, required_obj_ids, required_rel_ids

    def __init__(self, semantic_network, query_script, strict_mode):
        self.semantic_network = semantic_network
        self.query_script = query_script
        parsed_items = parse_script(query_script, query_script=True)
        splitted_items, required_obj_ids, required_rel_ids = (
            self._split_required_query_items(parsed_items)
        )

        q = semantic_network.__class__("Query", strict_mode=strict_mode)
        for ids in splitted_items:
            if len(ids) == 1:
                q.create_object(ids[0])
            elif len(ids) == 3:
                o1, rel, o2 = ids[0], ids[1], ids[2]
                q.create_relation(rel, o1, o2)

        self.q = q
        self.required_obj_ids = required_obj_ids
        self.required_rel_ids = required_rel_ids

    def __iter__(self):
        res = self.semantic_network.search_pattern(
            self.q, self.required_obj_ids, self.required_rel_ids
        )
        return iter(res)


def perform_query(semnet, query, exclude, strict_mode):
    if exclude is None:
        matches = list(SemanticQuery(semnet, query, strict_mode=strict_mode))
    else:
        full_script = query + exclude
        matches = list(SemanticQuery(semnet, query, strict_mode=strict_mode))
        if len(matches) > 0:
            obj_keys = list(matches[0][0].keys())
            rel_keys = list(matches[0][1].keys())
            matches_full = list(
                SemanticQuery(semnet, full_script, strict_mode=strict_mode)
            )
            keys = set()
            for objs, rels in matches_full:
                key = " ".join(
                    ["%s=%s" % (o, objs[o]) for o in obj_keys]
                    + ["%s=%s" % (o, rels[o]) for o in rel_keys]
                )
                keys.add(key)
            filtered = []
            for objs, rels in matches:
                key = " ".join(
                    ["%s=%s" % (o, objs[o]) for o in obj_keys]
                    + ["%s=%s" % (o, rels[o]) for o in rel_keys]
                )
                if key not in keys:
                    filtered.append((objs, rels))
            matches = filtered

    return matches
