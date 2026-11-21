import pytest

from tinydb import TinyDB, where
from tinydb.operations import toggle
from tinydb.storages import MemoryStorage


def make_db():
    return TinyDB(storage=MemoryStorage)


def test_ac1_toggle_flips_bool_back_and_forth():
    db = make_db()
    db.insert({'done': False})

    db.update(toggle('done'))
    assert db.all()[0]['done'] is True

    db.update(toggle('done'))
    assert db.all()[0]['done'] is False


def test_ac2_toggle_only_affects_matching_documents():
    db = make_db()
    db.insert_multiple([
        {'name': 'a', 'done': False},
        {'name': 'b', 'done': False},
        {'name': 'c', 'done': True},
    ])

    db.update(toggle('done'), where('name') == 'a')

    assert db.get(where('name') == 'a')['done'] is True
    assert db.get(where('name') == 'b')['done'] is False
    assert db.get(where('name') == 'c')['done'] is True


def test_ac3_toggle_missing_field_raises_and_leaves_doc_unchanged():
    db = make_db()
    db.insert({'name': 'a'})

    with pytest.raises(Exception):
        db.update(toggle('done'))

    assert db.all() == [{'name': 'a'}]


@pytest.mark.parametrize('value', [1, 0, 'yes', None])
def test_ac4_toggle_non_bool_raises_and_leaves_value_unchanged(value):
    db = make_db()
    db.insert({'done': value})

    with pytest.raises(Exception):
        db.update(toggle('done'))

    stored = db.all()[0]['done']
    assert stored == value
    assert type(stored) is type(value)
