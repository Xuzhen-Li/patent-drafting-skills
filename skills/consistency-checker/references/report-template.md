# Consistency report

Jurisdiction:
Files checked:
Status: blocked

## 1. Claim dependencies and antecedent basis

Command:

```bash
python3 skills/claims-drafter/scripts/check_antecedent.py 04-claims/claims.md --lang auto --format json
```

Exit code:

| Code | Claim | Detail |
| --- | --- | --- |
|  |  |  |

Heuristic limits that still need a human look:

- 

## 2. Abstract

Command:

```bash
python3 skills/abstract-writer/scripts/check_abstract.py 06-abstract/abstract.md --lang auto --format json
```

Exit code:
Count / limit:
Warnings:

## 3. Reference numerals

Command:

```bash
python3 skills/consistency-checker/scripts/check_numerals.py 05-description/description.md 07-drawings/numerals.json --format json
```

Exit code:

| Code | Numeral or name | Detail |
| --- | --- | --- |
|  |  |  |

## 4. Claim-feature support

| Claim | Feature | Description location | Status |
| --- | --- | --- | --- |
|  |  |  | supported / confirm |

## 5. Term consistency

| Concept | Claim term | Description term | Abstract | Drawing name | Match |
| --- | --- | --- | --- | --- | --- |
|  |  |  |  |  | yes / no |

## 6. Abstract new matter

Nouns in the abstract that are absent from the description:

## 7. Open items

| Item | Owner | Decision |
| --- | --- | --- |
|  | inventor / drafter |  |

Status becomes `pass` when sections 1–3 exit 0, section 4 has no `confirm`, and sections 5–6 have no unresolved rows.
