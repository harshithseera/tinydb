import subprocess
import sys

import pytest

from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage
from tinydb.operations import append


def _db():
    return TinyDB(storage=MemoryStorage)


def test_ac1_append_to_existing_list():
    db = _db()
    db.insert({'id': 3, 'tags': ['a']})
    db.update(append('tags', 'urgent'), Query().id == 3)
    assert db.get(Query().id == 3)['tags'] == ['a', 'urgent']


def test_ac2_append_creates_missing_field():
    db = _db()
    db.insert({'id': 3})
    db.update(append('tags', 'urgent'), Query().id == 3)
    assert db.get(Query().id == 3)['tags'] == ['urgent']


def test_ac3_append_non_list_raises_typeerror():
    db = _db()
    db.insert({'id': 3, 'tags': 'abc'})
    with pytest.raises(TypeError):
        db.update(append('tags', 'urgent'), Query().id == 3)
    assert db.get(Query().id == 3)['tags'] == 'abc'


def test_ac4_existing_operations_still_work():
    from tinydb.operations import add, increment, set as set_op
    db = _db()
    db.insert({'id': 1, 'n': 1, 's': 'x'})
    db.update(add('n', 2), Query().id == 1)
    db.update(increment('n'), Query().id == 1)
    db.update(set_op('s', 'y'), Query().id == 1)
    doc = db.get(Query().id == 1)
    assert doc['n'] == 4 and doc['s'] == 'y'
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', '-p', 'no:cacheprovider', '-q',
         '--no-cov', 'tests/test_operations.py'],
        capture_output=True, text=True)
    assert result.returncode == 0, result.stdout
