from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage


def _db():
    return TinyDB(storage=MemoryStorage)


def test_ac1_between_numbers_inclusive():
    db = _db()
    db.insert_multiple([{'age': a} for a in (17, 18, 25, 30, 31)])
    res = db.search(Query().age.between(18, 30))
    assert sorted(d['age'] for d in res) == [18, 25, 30]


def test_ac2_between_date_strings():
    db = _db()
    dates = ['2024-03-14', '2024-03-15', '2024-03-20', '2024-04-01']
    db.insert_multiple([{'date': d} for d in dates])
    res = db.search(Query().date.between('2024-03-15', '2024-03-31'))
    assert sorted(d['date'] for d in res) == ['2024-03-15', '2024-03-20']


def test_ac3_between_missing_field_not_returned():
    db = _db()
    db.insert_multiple([{'age': 20}, {'name': 'noage'}])
    res = db.search(Query().age.between(0, 100))
    assert res == [{'age': 20}]


def test_ac4_between_incomparable_type_not_returned():
    db = _db()
    db.insert_multiple([{'age': 'x'}, {'age': 20}])
    res = db.search(Query().age.between(18, 30))
    assert res == [{'age': 20}]
