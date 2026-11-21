from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage


def _db():
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple([{'item': 'pen', 'price': 2}, {'item': 'lamp', 'price': 'TBD'},
                        {'item': 'desk', 'price': 150}])
    return db


def test_lt_with_mixed_types():
    assert _db().search(Query().price < 10) == [{'item': 'pen', 'price': 2}]


def test_gt_with_mixed_types():
    assert _db().search(Query().price > 100) == [{'item': 'desk', 'price': 150}]
