class SemanticNetArchiver:
    def dump(self, semantic_net):

        items = []
        for o in semantic_net.get_object_iterator():
            items.append(
                {
                    "type": "Object",
                    "id": o.id,
                    "props": o.props,
                }
            )

        for r in semantic_net.get_relation_iterator():
            items.append(
                {
                    "type": "Relation",
                    "id": r.id,
                    "source_id": r.source_obj.id,
                    "target_id": r.target_obj.id,
                    "props": r.props,
                }
            )

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
            if item["type"] == "Object":
                net.create_object(item["id"], item["props"])
            elif item["type"] == "Relation":
                net.create_relation(item["id"], item["source_id"], item["target_id"], item["props"])

        return net
