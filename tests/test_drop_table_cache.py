from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage

Q = Query()


def _users():
    db = TinyDB(storage=MemoryStorage)
    users = db.table('users')
    users.insert({'name': 'ann'})
    users.search(Q.name == 'ann')
    return db, users


def test_drop_table_clears_cached_search():
    db, users = _users()
    db.drop_table('users')
    assert users.search(Q.name == 'ann') == []


def test_drop_tables_clears_cached_search():
    db, users = _users()
    db.drop_tables()
    assert users.search(Q.name == 'ann') == []


def test_repeated_drop_through_same_handle():
    db, users = _users()
    db.drop_table('users')
    users.insert({'name': 'bob'})
    users.search(Q.name == 'bob')
    db.drop_table('users')
    assert users.search(Q.name == 'bob') == []
    assert len(users) == 0


def test_ids_restart_after_drop():
    db, users = _users()
    db.drop_table('users')
    assert users.insert({'name': 'bob'}) == 1
