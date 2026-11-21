from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage


def _db(docs):
    db = TinyDB(storage=MemoryStorage)
    for d in docs:
        db.insert(d)
    return db


PRICES = [{'price': 2}, {'price': 'TBD'}, {'price': 150}]


def test_ac1_less_than_skips_incomparable():
    db = _db(PRICES)
    assert db.search(Query().price < 10) == [{'price': 2}]


def test_ac2_greater_than_skips_incomparable():
    db = _db(PRICES)
    assert db.search(Query().price > 10) == [{'price': 150}]


def test_ac3_le_and_ge_skip_incomparable():
    db = _db(PRICES)
    assert db.search(Query().price <= 2) == [{'price': 2}]
    assert db.search(Query().price >= 150) == [{'price': 150}]


def test_ac4_missing_and_incomparable_not_returned():
    db = _db([{'name': 'x'}, {'price': 'TBD'}])
    assert db.search(Query().price < 10) == []
