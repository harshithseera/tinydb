from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage


def _setup():
    db = TinyDB(storage=MemoryStorage)
    users = db.table('users')
    users.insert({'name': 'ann'})
    assert users.search(Query().name == 'ann') == [{'name': 'ann'}]
    return db, users


def test_ac1_drop_table_clears_held_handle_cache():
    db, users = _setup()
    db.drop_table('users')
    assert users.search(Query().name == 'ann') == []


def test_ac2_drop_tables_clears_held_handle_cache():
    db, users = _setup()
    db.drop_tables()
    assert users.search(Query().name == 'ann') == []


def test_ac3_insert_after_drop_via_held_handle():
    db, users = _setup()
    db.drop_table('users')
    users.insert({'name': 'bob'})
    assert users.search(Query().name == 'ann') == []
    assert users.search(Query().name == 'bob') == [{'name': 'bob'}]
