# Spec: path support in tinydb.operations (issue 34)

Scope: `delete`, `add`, `subtract`, `set`, `increment`, `decrement` accept a field that is a str (top-level key, unchanged) or a tuple/list of keys (nested path).

## Acceptance criteria
AC-1: Given a document `{'address': {'city': 'X'}, 'stats': {'visits': 3}, 'a.b': 1}`, When `increment(['stats','visits'])`, `set(('address','city'),'Pune')` and `increment('a.b')` are applied via `db.update`, Then `stats.visits` is 4, `address.city` is 'Pune', and the top-level key `'a.b'` is 2 (a dotted string is a single top-level key).
AC-2: Given a document `{'a': {'b': 5}}`, When `delete(('a','b'))`, `add(('a','b'),2)`, `subtract(('a','b'),1)` or `decrement(('a','b'))` is applied (each on a fresh document), Then the nested value is respectively removed, 7, 4, 4, and sibling fields are untouched.
AC-3: Given a document `{}`, When `set(('x','y','z'), 1)` is applied, Then the document becomes `{'x': {'y': {'z': 1}}}`.
AC-4: Given a document `{'a': {}}`, When `increment`, `add`, `subtract`, `decrement` or `delete` is applied with path `('a','missing')` or `('nope','b')`, Then a `KeyError` is raised and the document is unchanged.
AC-5: Given a document `{'n': 5}`, When `set(('n','x'), 1)` or `increment(('n','x'))` is applied, Then a `TypeError` is raised and the document is still `{'n': 5}` (no partial change).

## Assumptions
- A path is any tuple or list of keys; a str is always a single top-level key, never split on dots.
- "Dict" means any MutableMapping; a non-mapping intermediate (int, list, str, None) raises TypeError.
- For `set`, a missing intermediate key is created as a dict; an existing non-dict intermediate raises TypeError before any mutation (validate before writing).
- An empty path is out of scope (behavior unspecified).
- Existing top-level behavior and error types are unchanged.

## Blocking open questions
None
