from datetime import datetime
from tinydb import TinyDB


def test_datetime_is_stored_as_iso_string(tmp_path):
    path = tmp_path / 'db.json'
    with TinyDB(path) as db:
        db.insert({'created': datetime(2024, 3, 15, 10, 30)})
    with TinyDB(path) as db:
        assert db.all()[0]['created'] == '2024-03-15T10:30:00'
