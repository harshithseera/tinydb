# Spec: ordering comparisons skip incomparable values (issue 2)

Source S1: issue text. Existing behaviour: `Query().field < v` (and `<=`, `>`, `>=`) raises TypeError when a document's value is not comparable with `v`; missing fields already yield no match.

- FR-1 (CONFIRMED, S1): `<`, `<=`, `>`, `>=` queries shall treat a document whose value cannot be compared with the operand as non-matching instead of raising.
- FR-2 (CONFIRMED, S1): Documents with comparable values shall be matched as before.

## Acceptance criteria
AC-1: Given a table with documents {'price': 2}, {'price': 'TBD'} and {'price': 150}, When searching with `Query().price < 10`, Then the result is exactly [{'price': 2}] and no exception is raised.
AC-2: Given the same table, When searching with `Query().price > 10`, Then the result is exactly [{'price': 150}] and no exception is raised.
AC-3: Given the same table, When searching with `Query().price <= 2` and with `Query().price >= 150`, Then the results are [{'price': 2}] and [{'price': 150}] respectively, with no exception.
AC-4: Given a table with a document with no `price` field and a document with `price` 'TBD', When searching with `Query().price < 10`, Then neither document is returned and no exception is raised.

## Assumptions
- Only the four ordering operators (`<`, `<=`, `>`, `>=`) are in scope; `==`/`!=` already do not raise.
- Any TypeError from the comparison is treated as "no match"; no warning or logging is required.
- Negation with `~` of such a query is not specified.

## Blocking open questions
None
