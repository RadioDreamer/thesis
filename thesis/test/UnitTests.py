import sys
import pytest

sys.path.append("/home/levi/ELTE/ELTE6/SZAKDOGA/thesis/thesis/model")
from MultiSet import (
    MultiSet,
    ObjectNotFoundException,
    NotEnoughObjectsException,
    InvalidOperationException
)

from MembraneStructure import (
    Node,
    MembraneStructure
)

from Region import Region

from Rule import (
    Rule,
    Direction,
    TransportationRuleType,
    BaseModelRule,
    DissolvingRule,
    PriorityRule,
    SymportRule,
    InvalidTypeException
)

from BaseModel import BaseModel


def test_multiset():
    m = MultiSet()
    assert len(m) == 0
    assert m.is_empty()

    m.add_object('a')
    assert len(m) == 1
    assert m.is_empty() is False

    m.add_object('b', mul=3)
    assert len(m) == 4

    m.remove_object('a')
    assert len(m) == 3

    m.remove_object('b', mul=2)
    assert len(m) == 1

    with pytest.raises(ObjectNotFoundException) as _:
        m.remove_object('a', mul=2)

    with pytest.raises(NotEnoughObjectsException) as _:
        m.remove_object('b', mul=2)

    m2 = MultiSet({'a': 2, 'b': 3})
    assert m2.has_subset(m)
    assert not m.has_subset(m2)
    m2 = m2 + m
    assert len(m2) == 6

    m2 += m
    assert len(m2) == 7

    m2 -= m
    assert len(m2) == 6

    m3 = MultiSet({'a': 2, 'c': 1})
    with pytest.raises(InvalidOperationException) as _:
        m2 -= m3

    assert 'a' in m3
    assert 'd' not in m3

    with pytest.raises(AssertionError) as _:
        m4 = MultiSet({'a': -1, 'b': 2})
    m4 = MultiSet({'a': 12, 'd': 10})
    m4['a'] = 5
    assert m4.multiplicity('a') == 5


def test_membrane_structure():
    n = Node()
    assert n.id == 0
    assert n.is_leaf()

    n.add_child(Node())
    n.add_child(Node())
    assert n.num_of_children() == 2
    assert not n.is_leaf()
    assert n.children[0].is_leaf()

    ms = MembraneStructure(n)
    assert ms.get_root_id() == 0
    assert ms.get_parent(ms.skin) is None
    ms.preorder(ms.skin, ms.get_parent, lambda x: x.id == 2)
    assert ms.result == n

    n.children[0].add_child(Node())
    ms.preorder(ms.skin, MembraneStructure.get_all_children,
                lambda x: x.id == 0)
    assert ms.result == n.children

    ms.preorder(ms.skin, ms.add_node, lambda x: x.id == 3)
    assert n.children[0].children[0].children[0].id == 4

    ms.preorder(ms.skin, ms.remove_node, lambda x: x.id == 1)
    assert n.num_of_children() == 2
    assert n.children[0].id == 2
    assert n.children[1].id == 3
    assert n.children[1].children[0].id == 4


def test_rule():
    ls = {'a': 2, 'b': 1}
    rs = {('a', Direction.HERE): 1}
    rule1 = BaseModelRule(ls, rs)
    assert rule1.weight() == 3
    assert isinstance(rule1, Rule)
    assert len(rule1.left_side) == 3
    assert len(rule1.right_side) == 1

    ls = {'a': 1, 'c': 2}
    rs = {'a': 3}
    rule2 = DissolvingRule(ls, rs)
    assert isinstance(rule2, BaseModelRule)

    ls = {'b': 2, 'd': 1}
    rs = {'d': 2}
    rule3 = BaseModelRule(ls, rs)
    rule4 = PriorityRule(rule1, rule3)
    assert isinstance(rule4, PriorityRule)
    assert isinstance(rule3, BaseModelRule)

    rule5 = PriorityRule(rule3, rule2)
    assert isinstance(rule5.weak_rule, DissolvingRule)
    with pytest.raises(InvalidTypeException) as _:
        rule6 = PriorityRule(rule4, rule2)

    imp = {'a': 2}
    exp = {'b': 1}
    rule7 = SymportRule(TransportationRuleType.ANTIPORT, imp, exp)
    assert rule7.weight() == 2

    imp = {'a': 3}
    rule8 = SymportRule(TransportationRuleType.SYMPORT_IN, imported_obj=imp)
    assert rule8.weight() == 3
    assert rule8.exported_obj is None

    exp = {'e': 2}
    rule9 = SymportRule(TransportationRuleType.SYMPORT_OUT, exported_obj=exp)
    assert rule9.weight() == 2
    assert rule9.imported_obj is None


def test_base_model():
    n = Node()
    ms = MembraneStructure(n)

    rule_0 = BaseModelRule({'a': 1, 'b': 1}, {('c', Direction.HERE): 2})
    rule_00 = BaseModelRule({'a': 1}, {('d', Direction.OUT): 2})
    obj_0 = {'a': 2, 'b': 1}
    region_0 = Region(n.id, None, objects=obj_0, rules=[rule_0, rule_00])

    regions = {0: region_0}
    model = BaseModel(tree=ms, regions=regions)
    assert model.is_dissolving is False
    assert model.any_rule_applicable() is True

    model.apply(rule_0, region_0)
    assert region_0.new_objects.multiplicity('c') == 2
    assert region_0.objects.multiplicity('a') == 1
    print(region_0.objects)
    with pytest.raises(ObjectNotFoundException) as _:
        region_0.objects.multiplicity('b')

    region_0.new_objects = None
    region_0.objects = MultiSet({'a': 2, 'b': 1})

    print(model.tree.get_root_id())
    model.apply(rule_00, region_0)
    assert len(region_0.objects) == 2
    assert region_0.objects.multiplicity('a') == 1
    assert model.any_rule_applicable()
    model.apply(rule_00, region_0)
    assert len(region_0.objects) == 1
    with pytest.raises(ObjectNotFoundException) as _:
        region_0.objects.multiplicity('a')
    assert model.any_rule_applicable() is False

    rule_000 = BaseModelRule({'a': 1}, {('f', Direction.IN): 2})
    region_0.rules.append(rule_000)
    assert model.is_applicable(rule_000, region_0) is False
    assert model.any_rule_applicable() is False

    n1 = Node()
    n1.add_child(Node())
    n1.children[0].add_child(Node())
    ms1 = MembraneStructure(n1)

    rule_a = BaseModelRule({'a': 1},
                           {('b', Direction.HERE): 1, ('a', Direction.HERE): 1})
    rule_b = DissolvingRule({'a': 1},
                            {('b', Direction.HERE): 1})
    rule_c = BaseModelRule({'c': 1},
                           {('c', Direction.HERE): 2})
    inner_rules = [rule_a, rule_b, rule_c]
    inner_objects = {'a': 1, 'c': 1}

    strong_rule = BaseModelRule({'c': 2}, {('c', Direction.HERE): 1})
    weak_rule = DissolvingRule({'c': 2}, {})
    rule_d = PriorityRule(strong_rule, weak_rule)

    rule_e = BaseModelRule({'b': 1}, {('d', Direction.HERE): 1})
    rule_f = BaseModelRule({'d': 1},
                           {('d', Direction.HERE): 1, ('e', Direction.HERE): 1})

    middle_rules = [rule_d, rule_e, rule_f]

    outer_id = n1.id
    middle_id = n1.children[0].id
    inner_id = n1.children[0].children[0].id

    region_inner = Region(inner_id, middle_id,
                          objects=inner_objects, rules=inner_rules
                          )
    region_middle = Region(middle_id, outer_id, None, middle_rules)

    outer_rule = [BaseModelRule({'e': 1}, {('e', Direction.OUT): 1})]
    region_outer = Region(outer_id, None, None, outer_rule)
    regions = {outer_id: region_outer, middle_id: region_middle,
               inner_id: region_inner}

    model = BaseModel(tree=ms1, regions=regions)
    print("SIMULATE")
    print(model.regions)    
    model.simulate_step()
    print(model.regions)

    model.simulate_step()
    print(model.regions)
test_base_model()
