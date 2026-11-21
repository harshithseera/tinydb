from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage


def _db(*docs):
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple(list(docs))
    return db


def test_ac1_lt_skips_mixed_type():
    db = _db({'item': 'pen', 'price': 2},
             {'item': 'lamp', 'price': 'TBD'},
             {'item': 'desk', 'price': 150})
    result = db.search(Query().price < 10)
    assert [d['item'] for d in result] == ['pen']


def test_ac2_other_orderings_skip_mixed_type():
    db = _db({'item': 'pen', 'price': 2},
             {'item': 'lamp', 'price': 'TBD'},
             {'item': 'desk', 'price': 150})
    q = Query()
    assert [d['item'] for d in db.search(q.price > 10)] == ['desk']
    assert [d['item'] for d in db.search(q.price >= 150)] == ['desk']
    assert [d['item'] for d in db.search(q.price <= 2)] == ['pen']


def test_ac3_missing_field_still_skipped():
    db = _db({'item': 'pen', 'price': 2},
             {'item': 'desk', 'price': 150},
             {'item': 'misc'})
    q = Query()
    assert [d['item'] for d in db.search(q.price < 10)] == ['pen']
    assert [d['item'] for d in db.search(q.price >= 150)] == ['desk']


def test_ac4_or_with_mixed_type():
    db = _db({'item': 'pen', 'price': 2},
             {'item': 'lamp', 'price': 'TBD'},
             {'item': 'desk', 'price': 150})
    q = Query()
    result = db.search((q.price < 10) | (q.item == 'lamp'))
    assert sorted(d['item'] for d in result) == ['lamp', 'pen']
