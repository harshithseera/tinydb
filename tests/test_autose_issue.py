from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage


def _make_db():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'name': 'theme', 'value': 'light'})
    return db


def test_ac1_mutating_search_result_does_not_affect_next_search():
    db = _make_db()
    Setting = Query()
    result = db.search(Setting.name == 'theme')
    result[0]['value'] = 'dark'
    assert db.search(Setting.name == 'theme') == [
        {'name': 'theme', 'value': 'light'}
    ]


def test_ac2_mutating_search_result_does_not_affect_all():
    db = _make_db()
    Setting = Query()
    result = db.search(Setting.name == 'theme')
    result[0]['value'] = 'dark'
    assert db.all() == [{'name': 'theme', 'value': 'light'}]


def test_ac3_cached_results_are_distinct_copies():
    db = _make_db()
    Setting = Query()
    db.search(Setting.name == 'theme')
    second = db.search(Setting.name == 'theme')
    second[0]['value'] = 'dark'
    third = db.search(Setting.name == 'theme')
    assert third[0]['value'] == 'light'
    assert third[0] is not second[0]


def test_ac4_update_still_persists_after_local_mutation():
    db = _make_db()
    Setting = Query()
    result = db.search(Setting.name == 'theme')
    result[0]['value'] = 'dark'
    db.update({'value': 'dark'}, Setting.name == 'theme')
    assert db.search(Setting.name == 'theme')[0]['value'] == 'dark'
