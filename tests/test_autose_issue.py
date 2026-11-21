import pytest

from tinydb import TinyDB, Query
from tinydb.middlewares import CachingMiddleware
from tinydb.storages import MemoryStorage


class CountingStorage(MemoryStorage):
    writes = 0

    def write(self, data):
        type(self).writes += 1
        super().write(data)


def _snapshot(db):
    return {
        'default': sorted(d['a'] for d in db.all()),
        'logs': sorted(d['id'] for d in db.table('logs').all()),
    }


def test_ac1_single_write_for_batch():
    CountingStorage.writes = 0
    db = TinyDB(storage=CountingStorage)
    logs = db.table('logs')
    logs.insert({'id': 3, 'seen': False})
    CountingStorage.writes = 0

    with db.batch():
        db.insert({'a': 1})
        db.insert({'a': 2})
        db.update({'a': 5}, Query().a == 1)
        db.table('logs').update({'seen': True}, Query().id == 3)
        db.table('logs').insert({'id': 4})
        assert CountingStorage.writes == 0

    assert CountingStorage.writes == 1
    assert sorted(d['a'] for d in db.all()) == [2, 5]
    assert db.table('logs').get(Query().id == 3)['seen'] is True
    assert len(db.table('logs')) == 2


def test_ac2_reads_see_changes_in_batch():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'a': 1})
    db.insert({'a': 2})
    with db.batch():
        new_id = db.insert({'a': 3})
        db.update({'a': 10}, Query().a == 1)
        assert db.count(Query().a == 3) == 1
        assert db.count(Query().a == 10) == 1
        assert db.count(Query().a == 1) == 0
        assert len(db.search(Query().a > 1)) == 3
        assert db.get(doc_id=new_id)['a'] == 3
        assert db.get(Query().a == 10) is not None


def test_ac3_exception_rolls_back():
    CountingStorage.writes = 0
    db = TinyDB(storage=CountingStorage)
    db.insert({'a': 1})
    db.table('logs').insert({'id': 1})
    CountingStorage.writes = 0
    before = _snapshot(db)
    raw_before = repr(db.storage.read())

    with pytest.raises(ValueError):
        with db.batch():
            db.insert({'a': 2})
            db.update({'a': 9}, Query().a == 1)
            db.table('logs').insert({'id': 2})
            db.table('logs').remove(Query().id == 1)
            raise ValueError('boom')

    assert CountingStorage.writes == 0
    assert repr(db.storage.read()) == raw_before
    assert _snapshot(db) == before
    assert db.insert({'a': 100}) == 2
    assert db.table('logs').insert({'id': 100}) == 2


def test_ac4_nested_and_empty_batches():
    CountingStorage.writes = 0
    db = TinyDB(storage=CountingStorage)
    db.insert({'a': 0})
    CountingStorage.writes = 0

    with db.batch():
        db.insert({'a': 1})
        with db.batch():
            db.insert({'a': 2})
        assert CountingStorage.writes == 0
        db.insert({'a': 3})
    assert CountingStorage.writes == 1
    assert len(db) == 4

    CountingStorage.writes = 0
    with db.batch():
        db.all()
        db.search(Query().a == 1)
    with db.batch():
        with db.batch():
            pass
    assert CountingStorage.writes == 0


def test_ac5_caching_middleware():
    storage = CachingMiddleware(MemoryStorage)
    db = TinyDB(storage=storage)
    db.insert({'a': 1})

    with db.batch():
        db.insert({'a': 2})
        db.table('logs').insert({'id': 1})
    assert len(db) == 2
    assert len(db.table('logs')) == 1

    with pytest.raises(RuntimeError):
        with db.batch():
            db.insert({'a': 3})
            db.update({'a': 50}, Query().a == 1)
            raise RuntimeError('x')
    assert sorted(d['a'] for d in db.all()) == [1, 2]
    assert db.insert({'a': 4}) == 3
