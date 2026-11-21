from datetime import datetime

from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage

DT = datetime(2024, 1, 2, 3, 4, 5)


def test_ac1_insert_datetime_no_error(tmp_path):
    with TinyDB(str(tmp_path / 'db.json')) as db:
        db.insert({'title': 'hello', 'created': DT})


def test_ac2_read_back_datetime(tmp_path):
    with TinyDB(str(tmp_path / 'db.json')) as db:
        db.insert({'title': 'hello', 'created': DT})
        for doc in (db.all()[0], db.get(Query().title == 'hello')):
            assert doc['created'] == DT
            assert isinstance(doc['created'], datetime)


def test_ac3_datetime_survives_reopen(tmp_path):
    path = str(tmp_path / 'db.json')
    with TinyDB(path) as db:
        db.insert({'title': 'hello', 'created': DT})
    with TinyDB(path) as db:
        doc = db.all()[0]
        assert doc['created'] == DT
        assert isinstance(doc['created'], datetime)


def test_ac4_search_by_datetime(tmp_path):
    with TinyDB(str(tmp_path / 'db.json')) as db:
        db.insert({'title': 'a', 'created': DT})
        db.insert({'title': 'b', 'created': datetime(2025, 5, 5)})
        res = db.search(Query().created == DT)
        assert len(res) == 1
        assert res[0]['title'] == 'a'


def test_ac5_native_values_unchanged(tmp_path):
    path = str(tmp_path / 'db.json')
    docs = [{'s': '2024-01-02T03:04:05', 'i': 3, 'l': [1, 'x', {'a': 2}],
             'n': {'k': {'z': 'v'}}}]
    with TinyDB(path) as db:
        db.insert_multiple(docs)
    with TinyDB(path) as db:
        assert [dict(d) for d in db.all()] == docs
