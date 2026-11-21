import pytest

from tinydb import TinyDB
from tinydb.operations import add, decrement, delete, increment, set, subtract
from tinydb.storages import MemoryStorage


def _db(doc):
    db = TinyDB(storage=MemoryStorage)
    db.insert(doc)
    return db


def test_ac1_nested_paths_and_dotted_key():
    db = _db({'address': {'city': 'X'}, 'stats': {'visits': 3}, 'a.b': 1})
    db.update(increment(['stats', 'visits']))
    db.update(set(('address', 'city'), 'Pune'))
    db.update(increment('a.b'))
    assert db.all()[0] == {
        'address': {'city': 'Pune'}, 'stats': {'visits': 4}, 'a.b': 2}


def test_ac2_nested_operations():
    ops = [
        (delete(('a', 'b')), {'a': {'c': 1}}),
        (add(('a', 'b'), 2), {'a': {'b': 7, 'c': 1}}),
        (subtract(('a', 'b'), 1), {'a': {'b': 4, 'c': 1}}),
        (decrement(('a', 'b')), {'a': {'b': 4, 'c': 1}}),
    ]
    for op, expected in ops:
        db = _db({'a': {'b': 5, 'c': 1}})
        db.update(op)
        assert db.all()[0] == expected


def test_ac3_set_creates_missing_dicts():
    db = _db({})
    db.update(set(('x', 'y', 'z'), 1))
    assert db.all()[0] == {'x': {'y': {'z': 1}}}


def test_ac4_missing_path_raises_keyerror():
    for path in [('a', 'missing'), ('nope', 'b')]:
        for op in [increment(path), add(path, 1), subtract(path, 1),
                   decrement(path), delete(path)]:
            db = _db({'a': {}})
            with pytest.raises(KeyError):
                db.update(op)
            assert db.all()[0] == {'a': {}}


def test_ac5_non_dict_intermediate_raises_typeerror():
    for op in [set(('n', 'x'), 1), increment(('n', 'x'))]:
        db = _db({'n': 5})
        with pytest.raises(TypeError):
            db.update(op)
        assert db.all()[0] == {'n': 5}
