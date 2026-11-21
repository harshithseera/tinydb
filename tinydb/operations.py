"""
A collection of update operations for TinyDB.

They are used for updates like this:

>>> db.update(delete('foo'), where('foo') == 2)

This would delete the ``foo`` field from all documents where ``foo`` equals 2.

A field may be a string (a top-level key, never split on dots) or a tuple/list
of keys describing a path into nested documents:

>>> db.update(increment(('stats', 'visits')))
"""


from collections.abc import Callable, MutableMapping, Sequence
from typing import Any, Union

Field = Union[str, Sequence]


def _split_path(field: Field):
    # A str is always a single top-level key (no splitting on dots)
    if isinstance(field, str):
        return [], field

    keys = list(field)
    return keys[:-1], keys[-1]


def _get_parent(doc: MutableMapping, field: Field):
    """
    Resolve the mapping holding the last key of ``field``.

    Raises ``KeyError`` for a missing key and ``TypeError`` if an intermediate
    value is not a mapping.
    """
    parent_keys, last = _split_path(field)
    parent = doc
    for key in parent_keys:
        parent = parent[key]
        if not isinstance(parent, MutableMapping):
            raise TypeError(f'Cannot descend into non-mapping at {key!r}')

    return parent, last


def _ensure_parent(doc: MutableMapping, field: Field):
    """
    Like :func:`_get_parent` but creates missing intermediate dicts.

    Existing intermediates are validated before anything is created, so a
    ``TypeError`` leaves the document untouched.
    """
    parent_keys, last = _split_path(field)

    current = doc
    for key in parent_keys:
        if key not in current:
            break
        current = current[key]
        if not isinstance(current, MutableMapping):
            raise TypeError(f'Cannot descend into non-mapping at {key!r}')

    parent = doc
    for key in parent_keys:
        if key not in parent:
            parent[key] = {}
        parent = parent[key]

    return parent, last


def delete(field: Field) -> Callable[[MutableMapping], None]:
    """
    Delete a given field from the document.
    """
    def transform(doc: MutableMapping):
        parent, last = _get_parent(doc, field)
        del parent[last]

    return transform


def add(field: Field, n: Union[int, float, str]) -> Callable[[MutableMapping], None]:
    """
    Add ``n`` to a given field in the document.

    Also works for strings (concatenation), matching the documented behavior.
    """
    def transform(doc: MutableMapping):
        parent, last = _get_parent(doc, field)
        parent[last] += n

    return transform


def subtract(field: Field, n: Union[int, float]) -> Callable[[MutableMapping], None]:
    """
    Subtract ``n`` to a given field in the document.
    """
    def transform(doc: MutableMapping):
        parent, last = _get_parent(doc, field)
        parent[last] -= n

    return transform


def set(field: Field, val: Any) -> Callable[[MutableMapping], None]:
    """
    Set a given field to ``val``.
    """
    def transform(doc: MutableMapping):
        parent, last = _ensure_parent(doc, field)
        parent[last] = val

    return transform


def increment(field: Field) -> Callable[[MutableMapping], None]:
    """
    Increment a given field in the document by 1.
    """
    def transform(doc: MutableMapping):
        parent, last = _get_parent(doc, field)
        parent[last] += 1

    return transform


def decrement(field: Field) -> Callable[[MutableMapping], None]:
    """
    Decrement a given field in the document by 1.
    """
    def transform(doc: MutableMapping):
        parent, last = _get_parent(doc, field)
        parent[last] -= 1

    return transform
