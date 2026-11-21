from tinydb import TinyDB, where
from tinydb.storages import MemoryStorage


class CountingStorage(MemoryStorage):
    def __init__(self):
        super().__init__()
        self.reads = 0
        self.writes = 0

    def read(self):
        self.reads += 1
        return super().read()

    def write(self, data):
        self.writes += 1
        super().write(data)


def _db(n=1000):
    db = TinyDB(storage=CountingStorage)
    db.insert_multiple({'n': i} for i in range(n))
    return db


def test_ac1_update_single_write():
    db = _db()
    s = db.storage
    s.writes = 0
    db.update({'x': 1}, where('n') > 10)
    assert s.writes == 1
    for doc in db.all():
        if doc['n'] > 10:
            assert doc['x'] == 1


def test_ac2_repeated_search_uses_cache():
    db = _db()
    s = db.storage
    first = db.search(where('n') == 5)
    s.reads = 0
    second = db.search(where('n') == 5)
    assert s.reads == 0
    assert first == second


def test_ac3_insert_multiple_single_write():
    db = _db(10)
    s = db.storage
    s.writes = 0
    db.insert_multiple({'n': i} for i in range(500))
    assert s.writes == 1
    assert len(db) == 510


def test_ac4_cache_not_stale():
    db = _db(20)
    q = where('n') == 5
    assert len(db.search(q)) == 1
    db.update({'n': 100}, q)
    assert db.search(q) == []
    assert len(db.search(where('n') == 100)) == 1
    db.remove(where('n') == 100)
    assert db.search(where('n') == 100) == []
