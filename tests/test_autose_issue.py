from tinydb import TinyDB, where
from tinydb.storages import MemoryStorage


def _db():
    return TinyDB(storage=MemoryStorage)


def test_ac1_count_without_query_returns_all():
    db = _db()
    db.insert_multiple([{'a': 1}, {'a': 2}, {'a': 3}])
    assert db.table('_default').count() == 3


def test_ac2_count_without_query_on_empty_table():
    db = _db()
    assert db.table('_default').count() == 0


def test_ac3_count_with_query_counts_matches_only():
    db = _db()
    db.insert_multiple([{'a': 1}, {'a': 2}, {'a': 2}])
    assert db.table('_default').count(where('a') == 2) == 2


def test_ac4_count_without_query_equals_len():
    db = _db()
    table = db.table('t')
    table.insert_multiple([{'a': 1}, {'a': 2}])
    assert table.count() == len(table)
