# Spec: `Query.between(lower, upper)` (issue #3)

Source S1: issue text. Add `between` to `Query`, equivalent to `(field >= lower) & (field <= upper)`, inclusive on both ends, for any mutually comparable values; documents missing the field do not match; composes with `&`, `|`, `~`.

- FR-1 (CONFIRMED): `Query().field.between(a, b)` matches documents where `a <= value <= b`.
- FR-2 (CONFIRMED): Missing field -> no match, no exception.
- FR-3 (CONFIRMED): Works with numbers and strings (incl. ISO date strings).
- FR-4 (CONFIRMED): Combines with `&`, `|`, `~`.

## Acceptance criteria
AC-1: Given documents with age 17, 18, 25, 30 and 31, When searching with `Query().age.between(18, 30)`, Then exactly the documents with age 18, 25 and 30 are returned.
AC-2: Given documents with ISO date strings in field `d` ("2020-01-01", "2020-06-15", "2021-01-01") and a document without `d`, When searching with `Query().d.between("2020-01-01", "2020-12-31")`, Then only the first two dated documents match and the document without `d` does not match and no exception is raised.
AC-3: Given documents with age 10, 20 and 40, When searching with `Query().age.between(15, 30) | Query().age.between(35, 45)` and with `Query().age.between(15, 30) & (Query().age >= 20)`, Then the results are the age 20 and 40 documents and the age 20 document respectively.
AC-4: Given a document with age 20 and a document without `age`, When evaluating `~Query().age.between(18, 30)`, Then the age 20 document does not match and the document without `age` does match (consistent with `~` on other query methods).

## Assumptions
- Behaviour mirrors `(q >= lower) & (q <= upper)`, so incomparable types (e.g. string vs int) yield no match rather than raising, as with existing comparison operators.
- If lower > upper, nothing matches (no error, no argument swapping).
- Query is hashable/cacheable like other methods (hash includes path, lower, upper).
- Nested paths and `Query()['field']` forms work as for other methods.

## Blocking open questions
None
