---
name: patentability-screen
description: "Screens subject-matter eligibility and practical applicability before a prior-art search: CN Patent Law Arts. 2, 5, and 25, US 35 U.S.C. § 101 (Alice/Mayo), and a CN invention-versus-utility-model recommendation. Triggers: \"能不能申请专利\", \"专利客体筛查\", \"eligibility screen\", \"Alice check\", \"发明还是实用新型\". Do not use this skill as a novelty search or to draft claims."
---

# Patentability screen

A pre-search screen of subject matter and practical applicability
(实用性). It is not a novelty search, not an inventive-step conclusion,
and not legal advice. A 专利代理师 (patent agent) or patent attorney
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
  - `CN`: `references/eligibility-checklist.cn.md`
  - `US`: `references/eligibility-checklist.us.md`
  - `PCT`: `references/eligibility-checklist.pct.md`, plus the CN or US
    list for each national phase the inventor already cares about

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
   - **CN.** 专利法 Art. 2: is there a technical solution (technical
     problem, technical means, technical effect)? Art. 5: law, morality,
     public interest, genetic resources obtained or used illegally.
     Art. 25 exclusions, including scientific discoveries, rules and
     methods for mental activities, methods of diagnosis or treatment,
     animal and plant varieties, and nuclear transformation. Software:
     审查指南 Part II Chapter 9, not a blanket yes or no.
     Practical applicability: Art. 22, can it be made or used and does
     it produce a positive effect the inventor actually reported?
   - **US.** Statutory class under 35 U.S.C. § 101 (process, machine,
     manufacture, composition of matter). Then MPEP 2106: judicial
     exception, integration into a practical application, inventive
     concept. Utility: specific, substantial, credible (MPEP 2107).
     Do not apply 专利法 Art. 25 to a US file.
   - **PCT.** The International Searching Authority will look at novelty,
     inventive step, and industrial applicability (PCT Article 33).
     This screen does not predict the written opinion. Flag national-phase
     exclusions the inventor already named (China, United States, or both).
4. Novelty and inventive step at this stage are **admission risks only**:
   the inventor's own disclosure table, and nothing you "recall" about
   the field. If they listed a paper before the filing date, say that CN
   novelty is at risk and that US § 102(b)(1) might differ. Do not say
   "still novel".
5. CN only: recommend 发明专利, 实用新型, both as a same-day strategy
   for counsel (专利法 Art. 9), or neither. A utility model needs a
   product's shape, structure, or their combination (专利法 Art. 2), not
   a method, not a composition without structure, and not a pure
   algorithm. Term and examination differ (Art. 42; utility models are
   not substantively examined before grant). State that tradeoff in one
   sentence. Do not open a second project.
6. End with one recommendation: `proceed`, `proceed-narrowed` (name the
   feature to keep out), or `stop`. A `stop` binds the orchestrator
   until the inventor writes an override into `LOG.md`.
7. Do not set a gate flag. This skill has no lock. Append `LOG.md` with
   the recommendation.

## Human gate(s)

No gate flag. If the recommendation is `stop`, the inventor must either
change the subject or record an override in `LOG.md` before
`prior-art-search` runs. Quote that override. Do not draft it for them.

## Outputs (exact paths + formats)

- `<project>/01-eligibility/screen.md` — filled checklist, recommendation,
  and a "not a search" banner at the top.
- `<project>/LOG.md` — one appended entry: date, skill, recommendation.

Language of `screen.md`: Chinese for `CN`, English for `US` and `PCT`.

## Quality checklist

- [ ] Every checklist row is filled with pass, fail, risk, or unknown.
- [ ] No prior-art publication number appears unless it is in the disclosure.
- [ ] CN utility-model advice is omitted for US and PCT files.
- [ ] A missing positive effect is `unknown` or `risk`, not a fabricated effect.
- [ ] The recommendation is a single word from the allowed set, plus a reason.
- [ ] Alice/Mayo steps are not used as the CN test, and the 三步法 is not used as the US § 101 test.

## Guardrails

- Do not tell the inventor the invention is patentable.
- Do not "fix" an excluded method of treatment by silently rewriting it as a device. You may note that a device or a substance might be a different invention, and mark that as a new disclosure the inventor must confirm.
- Do not advise withholding a publication from the disclosure.
- Diagnostic and treatment methods excluded in China can still raise US § 101 and remedy issues (35 U.S.C. § 287(c) limits remedies for some medical activities). Flag both; do not clear either.

## Next step

`patent-orchestrator`. If the recommendation is `proceed` or
`proceed-narrowed`, the next skill is `prior-art-search`.
