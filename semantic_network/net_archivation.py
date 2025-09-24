class SemanticNetArchiver:
    def dump(self, semantic_net):

        _items = {}

        for o in semantic_net.get_object_iterator():
            order = semantic_net.counter_for_element[o]
            _items[order] = o.id

        for r in semantic_net.get_relation_iterator():
            order = semantic_net.counter_for_element[r]
            _items[order] = f"{r.source_obj.id} {r.id} {r.target_obj.id}"

        items = [_items[k] for k in sorted(list(_items.keys()))]

        dump = {
            "name": semantic_net.name,
            "items": items,
        }

        return dump

    def load(self, semantic_net_class, semantic_net_json):

        net = semantic_net_class(name=semantic_net_json["name"])

        for item in semantic_net_json["items"]:
            ids = item.split(" ")
            if len(ids) == 1:
                net.create_object(ids[0])
            elif len(ids) == 3:
                o1, rel, o2 = ids[0], ids[1], ids[2]
                net.create_relation(rel, o1, o2)

        return net

    def push(self, semantic_net, semantic_net_json):

        for item in semantic_net_json["items"]:
            ids = item.split(" ")
            if len(ids) == 1:
                semantic_net.create_object(ids[0])
            elif len(ids) == 3:
                o1, rel, o2 = ids[0], ids[1], ids[2]
                semantic_net.create_relation(rel, o1, o2)
