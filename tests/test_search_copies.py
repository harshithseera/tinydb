from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage


def test_mutating_search_result_does_not_affect_cache():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'name': 'theme', 'value': 'light'})
    db.search(Query().name == 'theme')[0]['value'] = 'dark'
    assert db.search(Query().name == 'theme')[0]['value'] == 'light'


def test_mutating_nested_value_does_not_affect_cache():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'name': 'x', 'tags': ['a']})
    db.search(Query().name == 'x')
    db.search(Query().name == 'x')[0]['tags'].append('b')
    assert db.search(Query().name == 'x')[0]['tags'] == ['a']


def test_doc_id_preserved_on_cached_result():
    db = TinyDB(storage=MemoryStorage)
    doc_id = db.insert({'name': 'x'})
    db.search(Query().name == 'x')
    assert db.search(Query().name == 'x')[0].doc_id == doc_id
