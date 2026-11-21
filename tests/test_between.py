from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage


def test_between_matches_value_in_range():
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple([{'age': 10}, {'age': 25}, {'age': 40}])
    assert db.search(Query().age.between(18, 30)) == [{'age': 25}]


def test_between_missing_field():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'name': 'x'})
    assert db.search(Query().age.between(18, 30)) == []
