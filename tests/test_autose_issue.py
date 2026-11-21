import datetime
import json

from tinydb import TinyDB, Query

DT = datetime.datetime(2024, 5, 17, 13, 45, 12, 123456)
D = datetime.date(2024, 5, 17)


def test_ac1_insert_dates_writes_file(tmp_path):
    path = tmp_path / 'db.json'
    db = TinyDB(str(path))
    db.insert({'created': DT, 'due': D})
    db.close()

    assert path.exists()
    assert path.stat().st_size > 0
    with open(path) as f:
        json.load(f)


def test_ac2_roundtrip_preserves_types(tmp_path):
    path = str(tmp_path / 'db.json')
    db = TinyDB(path)
    db.insert({'created': DT, 'due': D})
    db.close()

    db = TinyDB(path)
    doc = db.all()[0]
    db.close()

    assert doc['created'] == DT
    assert type(doc['created']) is datetime.datetime
    assert doc['due'] == D
    assert type(doc['due']) is datetime.date


def test_ac3_query_on_datetime_after_reopen(tmp_path):
    path = str(tmp_path / 'db.json')
    db = TinyDB(path)
    db.insert({'name': 'a', 'created': DT})
    db.insert({'name': 'b', 'created': DT + datetime.timedelta(days=1)})
    db.close()

    db = TinyDB(path)
    res = db.search(Query().created == DT)
    db.close()

    assert len(res) == 1
    assert res[0]['name'] == 'a'


def test_ac4_plain_values_unchanged(tmp_path):
    path = str(tmp_path / 'db.json')
    doc = {
        's': '2024-05-17',
        't': '2024-05-17T13:45:12',
        'i': 3,
        'l': [1, 'x', {'a': 'b'}],
        'd': {'k': 'v'},
    }
    db = TinyDB(path)
    db.insert(doc)
    db.close()

    db = TinyDB(path)
    got = db.all()[0]
    db.close()

    assert got == doc
    assert type(got['s']) is str
    assert type(got['t']) is str
