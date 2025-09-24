import json
from .net_search import search_pattern
from .net_archivation import SemanticNetArchiver
from .query import SemanticQuery
from .net_functions import is_graph_acyclic
from .script import parse_script


class Object:
    def __init__(self, id):
        self.id = id

    def __str__(self):
        return "(%s)" % (self.id)

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id


class Relation:
    def __init__(self, id, source_obj, target_obj):
        assert source_obj != target_obj
        self.id = id
        self.source_obj = source_obj
        self.target_obj = target_obj

    def __str__(self):
        return "(%s %s %s)" % (
            self.id,
            self.source_obj.id,
            self.target_obj.id,
        )

    def __hash__(self):
        return hash((self.id, self.source_obj.id, self.target_obj.id))

    def __eq__(self, other):
        return (self.id, self.source_obj.id, self.target_obj.id) == (
            other.id,
            other.source_obj.id,
            other.target_obj.id,
        )


class SemanticNetwork:
    def __init__(self, name="Default", strict_mode=True):
        self.name = name
        self.strict_mode = strict_mode

        self.objects_by_id = {}
        self.relation_by_triplet = {}

        self.relations_by_relation_id = {}
        self.relations_by_source_id = {}
        self.relations_by_target_id = {}

        self.counter = 1
        self.counter_for_element = {}

    def __str__(self):
        n = 100
        items = self.to_dict()["items"]
        limited = (
            items if len(items) < n else items[: n // 2] + ["..."] + items[-n // 2 :]
        )
        limited = ["|- %s" % item for item in limited]
        limited = ["-" * 40] + limited + ["-" * 40]
        return "\n".join(limited)

    @classmethod
    def from_script(cls, script, name="Default", strict_mode=False):
        items = parse_script(script)

        sn = cls(name, strict_mode=strict_mode)
        for ids in items:
            if len(ids) == 1:
                sn.create_object(ids[0])
            elif len(ids) == 3:
                o1, rel, o2 = ids[0], ids[1], ids[2]
                sn.create_relation(rel, o1, o2)

        return sn

    def append_script(self, script, strict_mode=False):
        if strict_mode is None:
            strict_mode = self.strict_mode

        items = parse_script(script)

        for ids in items:
            if strict_mode == True:
                if len(ids) == 1:
                    self.create_object(ids[0])
                elif len(ids) == 3:
                    o1, rel, o2 = ids[0], ids[1], ids[2]
                    self.create_relation(rel, o1, o2)
            else:
                if len(ids) == 1:
                    self.get_or_create_object(ids[0])
                elif len(ids) == 3:
                    o1, rel, o2 = ids[0], ids[1], ids[2]
                    self.get_or_create_object(o1)
                    self.get_or_create_object(o2)
                    self.get_or_create_relation(rel, o1, o2)

        return self

    def delete_script(self, script, auto_detach=False):
        items = parse_script(script)
        for ids in items:
            if len(ids) == 1:
                self.delete_object(ids[0], auto_detach=auto_detach)
            elif len(ids) == 3:
                o1, rel, o2 = ids[0], ids[1], ids[2]
                self.delete_relation(rel, o1, o2)

    def _update_counter(self, obj_or_rel):
        self.counter_for_element[obj_or_rel] = self.counter
        self.counter += 1

    def get_object_iterator(self):
        return iter(self.objects_by_id.values())

    def get_relation_iterator(self):
        return iter(self.relation_by_triplet.values())

    def object_exists(self, obj_id):
        return obj_id in self.objects_by_id

    def get_object(self, obj_id):
        return self.objects_by_id[obj_id]

    def create_object(self, obj_id):
        obj = Object(obj_id)
        assert obj.id not in self.objects_by_id
        assert obj not in self.relations_by_source_id
        assert obj not in self.relations_by_target_id
        self.objects_by_id[obj_id] = obj
        self._update_counter(obj)
        return obj

    def get_or_create_object(self, obj_id):
        if obj_id in self.objects_by_id:
            obj = self.objects_by_id[obj_id]
        else:
            obj = self.create_object(obj_id)
        return obj

    def delete_object(self, obj_id, auto_detach=False):
        assert obj_id in self.objects_by_id

        if auto_detach == False:
            assert len(self.relations_by_source_id.get(obj_id, set())) == 0
            self.relations_by_source_id.pop(obj_id, None)
            assert len(self.relations_by_target_id.get(obj_id, set())) == 0
            self.relations_by_target_id.pop(obj_id, None)
            obj = self.objects_by_id.pop(obj_id)
            self.counter_for_element.pop(obj)

        else:
            assert obj_id in self.objects_by_id
            in_relations = self.relations_by_target_id.get(obj_id, set())
            out_relations = self.relations_by_source_id.get(obj_id, set())
            relations = in_relations.union(out_relations)
            for r in relations:
                self.delete_relation(r.id, r.source_obj.id, r.target_obj.id)
            self.delete_object(obj_id)

    def relation_exists(self, id, source_obj_id, target_obj_id):
        return (id, source_obj_id, target_obj_id) in self.relation_by_triplet

    def get_relation(self, id, source_obj_id, target_obj_id):
        r = self.relation_by_triplet[(id, source_obj_id, target_obj_id)]
        return r

    def create_relation(self, id, source_obj_id, target_obj_id):
        if source_obj_id not in self.objects_by_id:
            if self.strict_mode == True:
                m = "Object %s is not found." % source_obj_id
                raise ValueError(m)
            else:
                self.create_object(source_obj_id)

        if target_obj_id not in self.objects_by_id:
            if self.strict_mode == True:
                m = "Object %s is not found." % target_obj_id
                raise ValueError(m)
            else:
                self.create_object(target_obj_id)

        triplet = (id, source_obj_id, target_obj_id)
        assert triplet not in self.relation_by_triplet, triplet
        source_obj = self.objects_by_id[source_obj_id]
        target_obj = self.objects_by_id[target_obj_id]
        new_relation = Relation(id, source_obj, target_obj)
        self.relation_by_triplet[triplet] = new_relation
        self.relations_by_relation_id.setdefault(id, set()).add(new_relation)
        self.relations_by_source_id.setdefault(source_obj_id, set()).add(new_relation)
        self.relations_by_target_id.setdefault(target_obj_id, set()).add(new_relation)
        self._update_counter(new_relation)
        return new_relation

    def get_or_create_relation(self, id, source_obj_id, target_obj_id):
        triplet = (id, source_obj_id, target_obj_id)
        if triplet in self.relation_by_triplet:
            relation = self.relation_by_triplet[triplet]
        else:
            relation = self.create_relation(id, source_obj_id, target_obj_id)
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
        rel = self.relation_by_triplet.pop(triplet)

        self.counter_for_element.pop(rel)

    def select_relations(self, relation_id, source_id, target_id):
        in_status = (
            relation_id is not None,
            source_id is not None,
            target_id is not None,
        )
        if in_status == (False, False, False):
            relations = self.relation_by_triplet.values()
        elif in_status == (True, False, False):
            relations = self.relations_by_relation_id.get(relation_id, set())
        elif in_status == (False, True, False):
            relations = self.relations_by_source_id.get(source_id, set())
        elif in_status == (False, False, True):
            relations = self.relations_by_target_id.get(target_id, set())
        elif in_status == (True, True, False):
            relations = self.relations_by_source_id.get(source_id, set())
            relations = (r for r in relations if r.id == relation_id)
        elif in_status == (True, False, True):
            relations = self.relations_by_target_id.get(target_id, set())
            relations = (r for r in relations if r.id == relation_id)
        elif in_status == (False, True, True):
            relations = self.relations_by_source_id.get(source_id, set())
            relations = (r for r in relations if r.target_obj.id == target_id)
        elif in_status == (True, True, True):
            relations = self.relations_by_source_id.get(source_id, set())
            relations = (r for r in relations if r.target_obj.id == target_id)
            relations = (r for r in relations if r.id == relation_id)

        result = list(relations)
        return result

    def select_objects(self):
        result = [o for o in self.get_object_iterator()]
        return result

    def get_matched_relation(self, q_rel_id, q_source_id, q_target_id, query_match):
        obj_map, rel_map = query_match.get_mapping()
        rel_id, source_id, target_id = (
            rel_map[q_rel_id],
            obj_map[q_source_id],
            obj_map[q_target_id],
        )
        return self.get_relation(rel_id, source_id, target_id)

    def get_matched_object(self, q_obj_id, query_match):
        obj_map, rel_map = query_match.get_mapping()
        obj_id = obj_map[q_obj_id]
        return self.get_object(obj_id)

    def search_pattern(self, sub_graph, required_obj_ids, required_rel_ids):
        matches = search_pattern(self, sub_graph, required_obj_ids, required_rel_ids)
        return (m.get_mapping() for m in matches)

    def query(self, query_script, strict_mode=False):
        return SemanticQuery(self, query_script, strict_mode=strict_mode)

    def is_acyclic(self, relation_ids):
        return is_graph_acyclic(self, relation_ids)

    def collect_relation_chains(self, relation_id):

        assert self.is_acyclic([relation_id])

        rels = self.relations_by_relation_id.get(relation_id, [])
        parents = set([r.target_obj for r in rels])
        children = set([r.source_obj for r in rels])

        only_children = children.difference(parents)

        def req(semantic_net, chain):
            obj = chain[-1]
            found_chains = []
            count = 0
            for r in semantic_net.select_relations(relation_id, obj.id, None):
                count += 1
                found_chains += req(semantic_net, chain + [r.target_obj])
            if count == 0:
                return [chain]
            return found_chains

        total_chains = []
        for inh in only_children:
            total_chains += req(self, [inh])

        return total_chains

    def describe(self):
        info = [
            "-----------------------------",
            "SemanticNetwork: %s" % self.name,
            "\tUnique objects %s" % len(self.objects_by_id),
            "\tUnique relations %s"
            % len(set([r[0] for r in self.relation_by_triplet.keys()])),
            "\tTotal relations %s" % len(list(self.relation_by_triplet.keys())),
            "-----------------------------",
        ]
        print("\n".join(info))

    def to_dict(self):
        archiver = SemanticNetArchiver()
        return archiver.dump(self)

    @classmethod
    def from_dict(cls, dict_data):
        archiver = SemanticNetArchiver()
        return archiver.load(cls, dict_data)

    def dump(self, path, variables):
        data = self.to_dict()
        data["variables"] = variables
        with open(path, "w") as f:
            f.write(json.dumps(data, indent=4))

    def copy(self):
        data = self.to_dict()
        sn = SemanticNetwork.from_dict(data)
        return sn

    @classmethod
    def load(cls, path):
        with open(path) as f:
            data = f.read()
        net = cls.from_dict(json.loads(data))
        return net

    def append_semantic_network(self, path):
        with open(path) as f:
            data = f.read()
        archiver = SemanticNetArchiver()
        archiver.push(self, json.loads(data))
