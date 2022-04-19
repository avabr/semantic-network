class SemanticNetArchiver:
    def dump(self, semantic_net):

        _items = {}

        for o in semantic_net.get_object_iterator():
            order = semantic_net.counter_for_element(o)
            _items[order] = {
                "type": "Object",
                "id": o.id,
                "props": o.props,
            }

        for r in semantic_net.get_relation_iterator():
            order = semantic_net.counter_for_element(o)
            _items[order] = {
                "type": "Relation",
                "id": r.id,
                "source_id": r.source_obj.id,
                "target_id": r.target_obj.id,
                "props": r.props,
            }

        items = [_items[k] for k in sorted(list(_items.keys()))]

        dump = {
            "name": semantic_net.name,
            "obj_props_schema": semantic_net.obj_props_schema,
            "rel_props_schema": semantic_net.rel_props_schema,
            "items": items,
        }

        return dump

    def load(self, semantic_net_class, semantic_net_json):

        net = semantic_net_class(
            name=semantic_net_json["name"],
            obj_props_schema=semantic_net_json["obj_props_schema"],
            rel_props_schema=semantic_net_json["rel_props_schema"],
        )

        for item in semantic_net_json["items"]:
            props = item.get("props", {})
            if item["type"] == "Object":
                net.create_object(item["id"], props)
            elif item["type"] == "Relation":
                net.create_relation(item["id"], item["source_id"], item["target_id"], props)

        return net

    def push(self, semantic_net, semantic_net_json):

        for item in semantic_net_json["items"]:
            props = item.get("props", {})
            if item["type"] == "Object":
                semantic_net.create_object(item["id"], props)
            elif item["type"] == "Relation":
                semantic_net.create_relation(
                    item["id"], item["source_id"], item["target_id"], props
                )
