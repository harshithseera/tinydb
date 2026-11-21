from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage


def _users():
    db = TinyDB(storage=MemoryStorage)
    users = db.table('users')
    users.insert({'name': 'ann'})
    users.search(Query().name == 'ann')
    return db, users


def test_drop_table_clears_cached_search():
    db, users = _users()
    db.drop_table('users')
    assert users.search(Query().name == 'ann') == []


def test_drop_tables_clears_cached_search():
    db, users = _users()
    db.drop_tables()
    assert users.search(Query().name == 'ann') == []
