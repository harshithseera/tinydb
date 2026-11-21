import pytest

from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage
from tinydb.operations import append


def make_db():
    return TinyDB(storage=MemoryStorage)


def test_ac1_append_to_existing_list():
    db = make_db()
    db.insert({'id': 3, 'tags': ['a']})
    db.update(append('tags', 'urgent'), Query().id == 3)
    assert db.get(Query().id == 3)['tags'] == ['a', 'urgent']


def test_ac2_append_creates_missing_field():
    db = make_db()
    db.insert({'id': 3})
    db.update(append('tags', 'urgent'), Query().id == 3)
    assert db.get(Query().id == 3)['tags'] == ['urgent']


def test_ac3_append_non_list_raises_typeerror():
    db = make_db()
    db.insert({'id': 3, 'tags': 'x'})
    with pytest.raises(TypeError):
        db.update(append('tags', 'urgent'), Query().id == 3)
    assert db.get(Query().id == 3)['tags'] == 'x'


def test_ac4_append_only_matching_document():
    db = make_db()
    db.insert({'id': 3, 'tags': ['a']})
    db.insert({'id': 4, 'tags': ['b']})
    db.update(append('tags', 'urgent'), Query().id == 3)
    assert db.get(Query().id == 3)['tags'] == ['a', 'urgent']
    assert db.get(Query().id == 4)['tags'] == ['b']
