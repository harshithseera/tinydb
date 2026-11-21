import pytest

from tinydb import TinyDB
from tinydb.operations import toggle
from tinydb.storages import MemoryStorage


def make_db(*docs):
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple(list(docs))
    return db


def test_ac1_toggle_flips_bools():
    db = make_db({'done': False}, {'done': True})
    db.update(toggle('done'))
    assert [d['done'] for d in db.all()] == [True, False]


def test_ac2_toggle_missing_field_raises_keyerror():
    db = make_db({'other': 1})
    with pytest.raises(KeyError):
        db.update(toggle('done'))
    assert db.all() == [{'other': 1}]


def test_ac3_toggle_int_raises_typeerror():
    db = make_db({'done': 1})
    with pytest.raises(TypeError):
        db.update(toggle('done'))
    stored = db.all()[0]['done']
    assert stored == 1 and type(stored) is int


@pytest.mark.parametrize('value', ['yes', None])
def test_ac4_toggle_non_bool_raises_typeerror(value):
    db = make_db({'done': value})
    with pytest.raises(TypeError):
        db.update(toggle('done'))
    assert db.all() == [{'done': value}]
