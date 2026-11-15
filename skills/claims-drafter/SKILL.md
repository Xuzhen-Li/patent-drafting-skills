---
name: claims-drafter
description: >-
  Draft US and PCT invention claims in English and check antecedent basis
  and dependencies. Use for an independent claim, dependent claim, claim
  ladder, multiple dependent claims, or claim-set review.
---

# Claims drafter

Draft a claim set for one jurisdiction, then run `scripts/check_antecedent.py`. This is drafting assistance. A registered patent attorney or patent agent reviews the set before filing.

Read [`../../shared/jurisdictions.md`](../../shared/jurisdictions.md), [`../../shared/gates.md`](../../shared/gates.md), and [`../../shared/glossary_cn_en.md`](../../shared/glossary_cn_en.md) before drafting.

## When to use

- The invention disclosure and inventive points are locked.
- The user asks for product, method, system, or use claims.
- An existing `04-claims/claims.md` fails a dependency or antecedent check.

## Inputs

- `patent.yaml` `jurisdiction`: `US` or `PCT`.
- `00-disclosure/disclosure.md` and `03-inventive-points/inventive_points.md`.
- Template: [`references/us-claims-template.md`](references/us-claims-template.md). PCT uses the same template and PCT Rule 6.
- Optional prior-art matrix in `02-prior-art/` so the preamble can name features shared with the closest prior art.

## Procedure

1. Read `unity_decision` in `03-inventive-points/inventive_points.md`.
   If it is missing or `split-pending`, stop. Do not write one claim set
   for groups that do not share a special technical feature.
   Ask the inventor to pick one group (`one-invention`) or to accept a
   documented combination (`documented-combination`) in that file and in
   `LOG.md`. The combination must name the shared feature. US: 35 U.S.C. § 121
   restriction. PCT: Rule 13.
2. Write `04-claims/dependency_sketch.md` before any claim sentence.
   Include the unity decision, each independent category, and the parent
   of every dependent concept. Show it to the user. Continue only after
   `I have looked at the dependency sketch` (or a clear
   equivalent you quote in `LOG.md`). Do not write `claims.md` in the
   same turn as the first sketch unless that quote is already in the
   conversation.
3. Confirm jurisdiction (`US` or `PCT`). Claims are in English. One claim is one sentence.
4. Choose only categories the disclosure supports. A use claim needs a use the inventor actually described. Stay inside the group the inventor selected.
5. Write each independent claim so it states the technical solution as a whole, including the essential technical features that solve the stated problem.
   - US: preamble, transition, body. Prefer `comprising` unless the inventor requires a closed claim (`consisting of`).
6. Build the dependent-claim ladder from the fallback positions. One added feature per dependent claim where that stays readable. Each dependent claim refers only to an earlier claim.
7. Give every element an antecedent. First mention is `a`/`an`. Later mention is `the`/`said`. Along each alternative parent, the ancestor chain must contain that introduction.
8. Multiple-dependent claims refer to earlier claims in the alternative only: `or` or `any one of`. A multiple-dependent claim must not be the basis of another multiple-dependent claim. A single dependent claim may depend on a multiple-dependent claim.
9. Run, from the skill repo:

```bash
python3 skills/claims-drafter/scripts/check_antecedent.py <project>/04-claims/claims.md --lang en
```

`--lang en` (the script also accepts `zh` and `auto`; this suite uses `en`). Default output is a text report, then `===JSON===`. Exit 0 means no errors. Exit 1 means fix the file and run again. Exit 2 means the file was missing.

10. Map each dependent claim to the fallback it preserves. Store that map in `04-claims/claim_map.md`.
11. Write `04-claims/fee_note.md`. Count the claims. Open the current fee page and say whether that count may add an excess-claim fee. If it may, list optional fallbacks the inventor could leave for a divisional or omit. Do not delete them, and do not add claims to reach a number. If the page will not open, say the warning is unverified. Do not type a currency amount.
    - US: [USPTO fee schedule](https://www.uspto.gov/learning-and-resources/fees-and-payment/uspto-fee-schedule) and 37 CFR 1.16.
    - PCT: [WIPO PCT fees](https://www.wipo.int/en/web/pct-system/fees).

## Human gate(s)

Claim-set lock. Stop after a clean script run and show the inventor the independent claims, the ladder, and any `[INVENTOR TO CONFIRM]` marks. Record the lock in `patent.yaml` and `LOG.md` using the fields in [`../../shared/gates.md`](../../shared/gates.md). Description drafting waits for this lock.

## Outputs

- `04-claims/dependency_sketch.md` — categories and parents, written before the sentences.
- `04-claims/claims.md` — numbered claims (`1.`), only after the sketch has been looked at and unity is `one-invention` or `documented-combination`.
- `04-claims/claim_map.md` — claim number, category, parent, fallback covered.
- `04-claims/fee_note.md` — fee-page warning and optional fallbacks. Not a claim ceiling.
- Script JSON when a machine-readable report is useful.

## Quality checklist

- Each independent claim can stand alone and matches one technical problem from the disclosure.
- Every `the` / `said` noun was introduced earlier on every branch the script checks.
- No forward reference and no citation of a missing claim number.
- Multiple dependencies are alternative, and none of those parents is itself multiple-dependent.
- Reference numerals, if used, sit in parentheses and repeat the description's names. They do not add a limitation by themselves.
- No measured effect, percentage, or example appears unless the inventor supplied it.
- The dependency sketch was shown before `claims.md`.
- `fee_note.md` does not delete or pad claims.

## Guardrails

- Leave gaps as `[INVENTOR TO CONFIRM]`. Do not invent embodiments, data, or advantages.
- Support for every feature is required later by the description (35 U.S.C. §112(a); PCT Article 6). Do not put a feature in a claim that the disclosure cannot enable.
- Avoid means-plus-function wording (`means for`, `step for`, and bare nonce words such as `module for`) unless the inventor accepts 35 U.S.C. §112(f) and the description names the corresponding structure. See the US template.
- Remind the user that a public disclosure before filing can destroy novelty (35 U.S.C. §102(b)(1) one-year grace in the US; PCT adds no grace of its own). Do not publish the draft.
- The script is a heuristic. Read `limitations` in its JSON. A clean run is not a legal opinion.
- Do not copy claims from a retrieved patent. Use the closest prior art only to decide which features belong in the preamble.

## Next step

After claim-set lock, run `description-writer` for `05-description/description.md`. Abstract and drawings come after the description.
