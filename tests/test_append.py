from tinydb import TinyDB, Query
from tinydb.operations import append
from tinydb.storages import MemoryStorage


def test_append_to_list():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'id': 1, 'tags': ['a']})
    db.update(append('tags', 'b'), Query().id == 1)
    assert db.all()[0]['tags'] == ['a', 'b']


def test_append_creates_field():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'id': 1})
    db.update(append('tags', 'b'), Query().id == 1)
    assert db.all()[0]['tags'] == ['b']
