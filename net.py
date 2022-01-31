from re import search
from numpy import tri
from net_search import search_pattern


class Object:
    def __init__(self, id, props):
        self.id = id
        self.props = props

    def __str__(self):
        return "(%s %s)" % (self.id, self.props)

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id


class Relation:
    def __init__(self, id, source_obj, target_obj, props):
        assert source_obj != target_obj
        self.id = id
        self.source_obj = source_obj
        self.target_obj = target_obj
        self.props = props

    def __str__(self):
        return "[(%s) - %s -> (%s) %s]" % (self.source_obj.id, self.id, self.target_obj.id, self.props)

    def __hash__(self):
        return hash((self.id, self.source_obj.id, self.target_obj.id))

    def __eq__(self, other):
        return (self.id, self.source_obj.id, self.target_obj.id) == (other.id, other.source_obj.id, other.target_obj.id)


class SemanticNetwork:
    def __init__(self, name="Default"):
        self.name = name
        self.objects_by_id = {}
        self.relation_by_triplet = {}

        self.relations_by_relation_id = {}
        self.relations_by_source_id = {}
        self.relations_by_target_id = {}

    def get_object_iterator(self):
        return iter(self.objects_by_id.values())

    def get_relation_iterator(self):
        return iter(self.relation_by_triplet.values())

    def object_exists(self, obj_id):
        return obj_id in self.objects_by_id

    def get_object(self, obj_id):
        return self.objects_by_id[obj_id]

    def create_object(self, obj_id, props):
        obj = Object(obj_id, props)
        assert obj.id not in self.objects_by_id
        assert obj not in self.relations_by_source_id
        assert obj not in self.relations_by_target_id
        self.objects_by_id[obj_id] = obj
        return obj

    def update_object(self, obj, props):
        obj.props = props
        return obj

    def get_or_create_object(self, obj_id, props=None):
        if obj_id in self.objects_by_id:
            obj = self.objects_by_id[obj_id]
            if props is not None:
                self.update_object(obj, props)
        else:
            obj = self.create_object(obj_id, props)
        return obj

    def delete_object(self, obj_id):
        assert obj_id in self.objects_by_id
        assert len(self.relations_by_source_id.get(obj_id, set())) == 0
        self.relations_by_source_id.pop(obj_id, None)
        assert len(self.relations_by_target_id.get(obj_id, set())) == 0
        self.relations_by_target_id.pop(obj_id, None)
        self.objects_by_id.pop(obj_id)

    def detach_delete_object(self, obj_id):
        assert obj_id in self.objects_by_id
        in_relations = self.relations_by_target_id.get(obj_id, set())
        out_relations = self.relations_by_source_id.get(obj_id, set())
        relations = in_relations.union(out_relations)
        for r in relations:
            self.delete_relation(r.id, r.source_obj.id, r.target_obj.id)
        self.delete_object(obj_id)

    def relation_exists(self, id, source_obj_id, target_obj_id):
        return (id, source_obj_id, target_obj_id) in self.self.relation_by_triplet

    def get_relation(self, id, source_obj_id, target_obj_id):
        r = self.relation_by_triplet[(id, source_obj_id, target_obj_id)]
        return r

    def create_relation(self, id, source_obj_id, target_obj_id, props):
        assert source_obj_id in self.objects_by_id
        assert target_obj_id in self.objects_by_id
        triplet = (id, source_obj_id, target_obj_id)
        assert triplet not in self.relation_by_triplet
        source_obj = self.objects_by_id[source_obj_id]
        target_obj = self.objects_by_id[target_obj_id]
        new_relation = Relation(id, source_obj, target_obj, props)
        self.relation_by_triplet[triplet] = new_relation
        self.relations_by_relation_id.setdefault(id, set()).add(new_relation)
        self.relations_by_source_id.setdefault(source_obj_id, set()).add(new_relation)
        self.relations_by_target_id.setdefault(target_obj_id, set()).add(new_relation)
        return new_relation

    def update_relation(self, id, source_obj_id, target_obj_id, props):
        triplet = (id, source_obj_id, target_obj_id)
        relation = self.relation_by_triplet[triplet]
        relation.props = props
        return relation

    def get_or_create_relation(self, id, source_obj_id, target_obj_id, props=None):
        triplet = (id, source_obj_id, target_obj_id)
        if triplet in self.relation_by_triplet:
            relation = self.relation_by_triplet[triplet]
            if props is not None:
                relation.props = props
        else:
            relation = self.create_relation(id, source_obj_id, target_obj_id, props)
        return relation

    def delete_relation(self, id, source_obj_id, target_obj_id):
        triplet = (id, source_obj_id, target_obj_id)
        assert triplet in self.relation_by_triplet
        relation = self.relation_by_triplet[triplet]

        self.relations_by_relation_id.get(id, set()).remove(relation)
        if len(self.relations_by_relation_id.get(id, set())) == 0:
            self.relations_by_relation_id.pop(id, None)
        self.relations_by_source_id.get(source_obj_id, set()).remove(relation)
        if len(self.relations_by_source_id.get(source_obj_id, set())) == 0:
            self.relations_by_source_id.pop(source_obj_id, None)
        self.relations_by_target_id.get(target_obj_id, set()).remove(relation)
        if len(self.relations_by_target_id.get(target_obj_id, set())) == 0:
            self.relations_by_target_id.pop(target_obj_id, None)
        self.relation_by_triplet.pop(triplet)

    def select_relations(self, relation_id, source_id, target_id):
        in_status = (relation_id is not None, source_id is not None, target_id is not None)
        if in_status == (False, False, False):
            relations = list(self.relation_by_triplet.values())
        elif in_status == (True, False, False):
            relations = self.relations_by_relation_id.get(relation_id, set())
        elif in_status == (False, True, False):
            relations = self.relations_by_source_id.get(source_id, set())
        elif in_status == (False, False, True):
            relations = self.relations_by_target_id.get(target_id, set())
        elif in_status == (True, True, False):
            relations = self.relations_by_source_id.get(source_id, set())
            relations = [r for r in relations if r.id == relation_id]
        elif in_status == (True, False, True):
            relations = self.relations_by_target_id.get(target_id, set())
            relations = [r for r in relations if r.id == relation_id]
        elif in_status == (False, True, True):
            relations = self.relations_by_source_id.get(source_id, set())
            relations = [r for r in relations if r.target_obj.id == target_id]
        elif in_status == (True, True, True):
            relations = self.relations_by_source_id.get(source_id, set())
            relations = [r for r in relations if r.target_obj.id == target_id]
            relations = [r for r in relations if r.id == relation_id]
        return list(relations)

    def search_pattern(self, sub_graph, required_obj_ids, required_rel_ids):
        return search_pattern(self, sub_graph, required_obj_ids, required_rel_ids)

    def describe(self):
        info = [
            "-----------------------------",
            "SemanticNetwork: %s" % self.name,
            "\tUnique objects %s" % len(self.objects_by_id),
            "\tUnique relations %s" % len(set([r[0] for r in self.relation_by_triplet.keys()])),
            "\tTotal relations %s" % len(list(self.relation_by_triplet.keys())),
            "-----------------------------",
        ]
        print("\n".join(info))


if __name__ == "__main__":

    sn = SemanticNetwork("Main")
    sn.create_object("Circle", {"type": "ENTITY"})
    sn.create_object("Circle.radius", {"type": "ENTITY"})
    sn.create_object("Circle.center", {"type": "ENTITY"})
    sn.create_relation("hasPart", "Circle", "Circle.radius", {})
    sn.create_relation("hasPart", "Circle", "Circle.center", {})

    sn.create_object("c1", {"type": "ENTITY"})
    sn.create_relation("fromProto", "c1", "Circle", {})
    sn.create_object("c1.radius", {"type": "ENTITY"})
    sn.create_relation("hasPart", "c1", "c1.radius", {})

    sn.create_object("c2", {})
    sn.create_object("c2.radius", {})
    sn.create_object("c2.center", {})
    sn.create_relation("fromProto", "c2", "Circle", {})
    sn.create_relation("hasPart", "c2", "c2.radius", {})
    sn.create_relation("hasPart", "c2", "c2.center", {})
    sn.create_relation("fromProto", "c2.radius", "Circle.radius", {})

    q = SemanticNetwork("Query")
    q.create_object("Circle", {"type": "ENTITY"})
    q.create_object("obj", {"type": "ENTITY"})
    q.create_relation("fromProto", "obj", "Circle", {})
    chains = search_pattern(sn, q, set(["Circle"]), set(["fromProto"]))

    for i, ch in enumerate(chains):
        obj_mapping, rel_mapping = ch.get_mapping()
        print("\tchain %s\t" % i, obj_mapping, rel_mapping)
