from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage


def _db(docs):
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple(docs)
    return db


def test_ac1_between_inclusive_numbers():
    db = _db([{'age': a} for a in (17, 18, 25, 30, 31)])
    res = db.search(Query().age.between(18, 30))
    assert sorted(d['age'] for d in res) == [18, 25, 30]


def test_ac2_between_iso_dates_missing_field():
    db = _db([{'d': '2020-01-01'}, {'d': '2020-06-15'},
              {'d': '2021-01-01'}, {'x': 1}])
    res = db.search(Query().d.between('2020-01-01', '2020-12-31'))
    assert [d['d'] for d in res] == ['2020-01-01', '2020-06-15']


def test_ac3_between_combines_with_or_and():
    db = _db([{'age': 10}, {'age': 20}, {'age': 40}])
    res = db.search(Query().age.between(15, 30) | Query().age.between(35, 45))
    assert sorted(d['age'] for d in res) == [20, 40]
    res = db.search(Query().age.between(15, 30) & (Query().age >= 20))
    assert [d['age'] for d in res] == [20]


def test_ac4_not_between():
    db = _db([{'age': 20}, {'other': 1}])
    res = db.search(~Query().age.between(18, 30))
    assert res == [{'other': 1}]
