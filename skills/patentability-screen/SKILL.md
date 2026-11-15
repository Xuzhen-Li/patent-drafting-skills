---
name: patentability-screen
description: "Screens subject-matter eligibility and practical applicability before a prior-art search: US 35 U.S.C. § 101 (Alice/Mayo) and PCT industrial applicability. Triggers: \"can this be patented\", \"eligibility screen\", \"Alice check\". Do not use this skill as a novelty search or to draft claims."
---

# Patentability screen

A pre-search screen of subject matter and practical applicability
(utility, or industrial applicability under PCT). It is not a novelty
search, not an inventive-step conclusion, and not legal advice. A
registered patent agent or patent attorney
decides whether to file.

## When to use

- `gates.invention_lock` is true and `01-eligibility/screen.md` is missing.
- The inventor asks whether the subject can be patented at all.

If the disclosure is still unlocked, send the user back to
`invention-disclosure-intake`. You may write a one-paragraph warning if
the subject is plainly excluded, and you must label it incomplete.

## Inputs (paths) / Preconditions

- `<project>/patent.yaml`
- `<project>/00-disclosure/disclosure.md`
- Checklists:
  - `US`: `references/eligibility-checklist.us.md`
  - `PCT`: `references/eligibility-checklist.pct.md`, plus the US
    list when the inventor already plans a US national phase

Do not open a patent database in this skill. Inventor-named publications
are risk flags, not search results.

## Procedure (numbered steps)

1. Read the disclosure gap list. If the technical solution (form § 5) is
   still a placeholder, stop and say the screen would be fiction.
2. Copy the jurisdiction checklist into `01-eligibility/screen.md` and
   fill every item `pass`, `fail`, `risk`, or `unknown`. Each `fail` or
   `risk` gets one sentence tied to a disclosure section. No sentence
   may add a technical fact the disclosure does not contain.
3. Apply only that jurisdiction's test.
   - **US.** Statutory class under 35 U.S.C. § 101 (process, machine,
     manufacture, composition of matter). Then MPEP 2106: judicial
     exception, integration into a practical application, inventive
     concept. Utility: specific, substantial, credible (MPEP 2107).
   - **PCT.** The International Searching Authority will look at novelty,
     inventive step, and industrial applicability (PCT Article 33).
     This screen does not predict the written opinion. Flag national-phase
     exclusions the inventor already named.
4. Novelty and inventive step at this stage are **admission risks only**:
   the inventor's own disclosure table, and nothing you "recall" about
   the field. If they listed a paper before the filing date, say that
   novelty is at risk, that US § 102(b)(1) might give a one-year grace,
   and that PCT adds no grace of its own. Do not say
   "still novel".
5. End with one recommendation: `proceed`, `proceed-narrowed` (name the
   feature to keep out), or `stop`. A `stop` binds the orchestrator
   until the inventor writes an override into `LOG.md`.
6. Do not set a gate flag. This skill has no lock. Append `LOG.md` with
   the recommendation.

## Human gate(s)

No gate flag. If the recommendation is `stop`, the inventor must either
change the subject or record an override in `LOG.md` before
`prior-art-search` runs. Quote that override. Do not draft it for them.

## Outputs (exact paths + formats)

- `<project>/01-eligibility/screen.md` — filled checklist, recommendation,
  and a "not a search" banner at the top.
- `<project>/LOG.md` — one appended entry: date, skill, recommendation.

Language of `screen.md`: English.

## Quality checklist

- [ ] Every checklist row is filled with pass, fail, risk, or unknown.
- [ ] No prior-art publication number appears unless it is in the disclosure.
- [ ] A missing positive effect is `unknown` or `risk`, not a fabricated effect.
- [ ] The recommendation is a single word from the allowed set, plus a reason.
- [ ] The US § 101 test follows MPEP 2106, not an inventive-step argument.

## Guardrails

- Do not tell the inventor the invention is patentable.
- Do not "fix" an excluded method of treatment by silently rewriting it as a device. You may note that a device or a substance might be a different invention, and mark that as a new disclosure the inventor must confirm.
- Do not advise withholding a publication from the disclosure.
- Diagnostic and treatment methods can raise US § 101 and remedy issues (35 U.S.C. § 287(c) limits remedies for some medical activities). Flag them; do not clear them.

## Next step

`patent-orchestrator`. If the recommendation is `proceed` or
`proceed-narrowed`, the next skill is `prior-art-search`.
