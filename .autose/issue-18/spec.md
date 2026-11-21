# Spec: Query().field.between(low, high)

## Overview
S1 (issue #18) requests `Query().age.between(18, 30)` as a shortcut for `(q.age >= 18) & (q.age <= 30)`, inclusive on both ends, usable with ISO date strings, and excluding documents lacking the field.

## Requirements
- FR-1 (CONFIRMED, S1): `Query().<field>.between(low, high)` matches documents whose field value v satisfies low <= v <= high.
- FR-2 (CONFIRMED, S1): Works for string values (e.g. '2024-03-15') using normal comparison.
- FR-3 (CONFIRMED, S1): Documents missing the field do not match.

## Acceptance criteria
AC-1: Given a table with documents whose age is 17, 18, 25, 30 and 31, When searching with `Query().age.between(18, 30)`, Then exactly the documents with age 18, 25 and 30 are returned (both bounds inclusive).
AC-2: Given documents with a `date` string field '2024-03-14', '2024-03-15', '2024-03-20' and '2024-04-01', When searching with `Query().date.between('2024-03-15', '2024-03-31')`, Then only the documents dated '2024-03-15' and '2024-03-20' are returned.
AC-3: Given documents where one has no `age` field, When searching with `Query().age.between(0, 100)`, Then the document without `age` is not returned and no exception is raised.
AC-4: Given a document whose age is the string 'x', When searching with `Query().age.between(18, 30)`, Then that document is not returned and no exception is raised.

## Assumptions
- ASM-1: Behaviour equals `(q >= low) & (q <= high)`, so incomparable types (TypeError) yield no match, as with existing comparisons.
- ASM-2: If low > high, nothing matches (no special handling or error).
- ASM-3: Result supports the usual query composition (&, |, ~) and caching like other queries.
- ASM-4: Only `between` is required; no exclusive-bound variants.

## Blocking open questions
None
