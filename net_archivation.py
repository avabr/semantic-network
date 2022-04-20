class SemanticNetArchiver:
    def dump(self, semantic_net):

        _items = {}

        for o in semantic_net.get_object_iterator():
            order = semantic_net.counter_for_element[o]
            _items[order] = [o.id]

        for r in semantic_net.get_relation_iterator():
            order = semantic_net.counter_for_element[r]
            _items[order] = [r.id, r.source_obj.id, r.target_obj.id]

        items = [_items[k] for k in sorted(list(_items.keys()))]

        dump = {
            "name": semantic_net.name,
            "items": items,
        }

        return dump

    def load(self, semantic_net_class, semantic_net_json):

        net = semantic_net_class(name=semantic_net_json["name"])

        for item in semantic_net_json["items"]:
            if len(item) == 1:
                net.create_object(item[0])
            elif len(item) == 3:
                net.create_relation(item[0], item[1], item[2])

        return net

    def push(self, semantic_net, semantic_net_json):

        for item in semantic_net_json["items"]:
            if len(item) == 1:
                semantic_net.create_object(item[0])
            elif len(item) == 3:
                semantic_net.create_relation(item[0], item[1], item[2])
