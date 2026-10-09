# Human gates

The agent drafts. The inventor decides. A gate is open only after the
inventor, or their 专利代理师 (patent agent) / patent attorney, explicitly
says so in the conversation. The agent then records the decision in
`patent.yaml` and appends `LOG.md`. Silence, a polite "looks fine", or the
agent's own confidence does not close a gate.

This suite is not legal advice. Closing the final gate means the draft
package is internally complete. It does not authorize filing.

## Where the decision is stored

`patent.yaml`:

```yaml
gates:
  invention_lock: false
  prior_art_review: false
  inventive_point_lock: false
  claim_set_lock: false
  final_package: false
```

`LOG.md` is append-only. Each closure adds a dated entry: skill name, gate
name, who approved it, and one sentence naming what was approved. Do not
rewrite older entries.

Suggested phrases, so the record is unambiguous:

- Invention lock: `发明人确认锁定交底` or `I confirm the invention lock`
- Prior-art review: `发明人确认检索结果` or `I confirm the prior-art review`
- Inventive-point lock: `发明人确认发明点` or `I confirm the inventive-point lock`
- Claim-set lock: `发明人确认权利要求` or `I confirm the claim-set lock`
- Final package: `发明人确认文本包` or `I confirm the final package`

Any clear equivalent is enough if the log quotes it. Do not treat a
discussion of one paragraph as approval of the whole document.

## G1 — Invention lock

| | |
|---|---|
| Skill | `invention-disclosure-intake` |
| Flag | `gates.invention_lock` |
| File | `00-disclosure/disclosure.md` |
| Blocks until true | `prior-art-search` as a completed search, `inventive-point-finder`, and every later drafting skill. `patentability-screen` may run on a clearly incomplete disclosure only to warn that the subject matter looks excluded; it must not pretend the facts are complete |

Exit criteria:

- Technical problem, existing solutions and their real drawbacks, the solution, and which features are essential versus optional are written in the inventor's facts.
- Every feature in `00-disclosure/fact_ledger.md` has an origin tag (`user-confirmed`, `copied-from-file`, `summarized`, `suggested`, or `open`). A `suggested` feature is not an essential feature.
- Every effect has an evidence grade (`measured`, `experienced`, `directly-inferable`, or `unverified`) and a source, or it stays `unverified`.
- Public disclosures are listed with dates, or the inventor states there are none.
- Applicant and inventors are identified, or the employment question is explicitly open.
- No fabricated examples, numbers, or figures.

Reopen the gate if the inventor later changes the technical solution, the
essential features, or the disclosure history.

## G2 — Prior-art review

| | |
|---|---|
| Skill | `prior-art-search` |
| Flag | `gates.prior_art_review` |
| Files | `02-prior-art/search_log.md`, `02-prior-art/feature_matrix.csv` |
| Blocks until true | `inventive-point-finder` and later claim drafting |

Exit criteria:

- The log lists the databases, the queries actually run, the date, and the hit counts.
- Every retained document has a publication number and a link the inventor or the agent opened. Nothing is cited from memory alone.
- The matrix covers the candidate essential features. Empty cells that were not checked are `unknown`, not `no`.
- Fewer than 10 relevant documents is acceptable. Padding is not.
- The log says whether any single opened document shows every essential feature, and says that in-force claims were not reviewed.
- The inventor has looked at the closest items and agrees the comparison is fair.

A new search that adds a closer reference reopens this gate and G3.

## G3 — Inventive-point lock

| | |
|---|---|
| Skill | `inventive-point-finder` |
| Flag | `gates.inventive_point_lock` |
| File | `03-inventive-points/inventive_points.md` |
| Blocks until true | `claims-drafter` |

Exit criteria:

- Closest prior art is one real document (or an identified combination), not a composite the agent invented.
- Distinguishing features are features, not slogans.
- Effects used in the argument are graded `measured`, `experienced`, or `directly-inferable` in the fact ledger. `unverified` effects are ignored.
- Fallback positions are ordered from broader to narrower.
- `unity_decision` is `one-invention` or `documented-combination`. `split-pending` does not close this gate. The note names the special technical feature (特定技术特征) when more than one candidate invention stays in the file. CN: 专利法 Art. 31 and 实施细则 (2023) Art. 39. US: 35 U.S.C. § 121. PCT: Rule 13.
- For `US`, the write-up applies obviousness under 35 U.S.C. § 103. For `CN`, it applies the 三步法. For `PCT`, it keeps the two separate enough that national phase counsel can reuse the facts.

## G4 — Claim-set lock

| | |
|---|---|
| Skill | `claims-drafter` |
| Flag | `gates.claim_set_lock` |
| File | `04-claims/claims.md` |
| Blocks until true | Treating the description, abstract, or export as aligned to a final claim set |

Exit criteria are owned by `claims-drafter`: the inventor has looked at
`04-claims/dependency_sketch.md` before the claim sentences, unity is
`one-invention` or `documented-combination`, antecedent basis, support in
the disclosure, dependency rules, and jurisdiction form. `fee_note.md` may
warn that the count can add an official fee. It does not delete claims to
hit a number. If claims change after this gate, reopen G4 and rerun
consistency.

## G5 — Final package

| | |
|---|---|
| Skill | `patent-docx-export` |
| Flag | `gates.final_package` |
| Files | `09-package/*.docx` plus a passing `08-consistency/report.md` |
| Blocks until true | Calling the package ready for counsel |

Exit criteria:

- Consistency report has no open failures. When drawings exist, each PNG was opened and its sha256 still matches `sheet_manifest.json`.
- The Word package embeds those same images. A checksum mismatch means this gate is not closed.
- Abstract length and drawing rules for the jurisdiction have been checked.
- The inventor knows a registered patent agent or patent attorney still needs to review the file before it is filed.
- The agent has not submitted anything to an office.

## What the orchestrator does with a closed gate

`patent-orchestrator` reads the flags and the files. A flag set to `true`
while the file is missing is an error: reset the flag to `false` and say why.
The agent never sets a flag to `true` to "get past" a step.

Order of work:

1. Project layout exists.
2. G1 invention lock.
3. Eligibility screen written (no separate flag; a "do not proceed" recommendation stops the pipeline until the inventor overrides it in the log).
4. G2 prior-art review.
5. G3 inventive-point lock.
6. G4 claim-set lock.
7. Description, abstract, drawings (or an explicit `drawings: none`). Drawings start from a frozen parts master. Formal sheets come from an editable source and a sha256 manifest.
8. Consistency report clean, including an opened-sheet check when figures exist. A drawing failure returns to `patent-drawings` before export.
9. G5 final package. Export embeds the sheets and stops if a checksum changed.

An existing-draft score does not close any gate. Copied files in `incoming/` stay read-only. The orchestrator starts at the earliest stage whose lock or file is not satisfied.

## Jurisdiction switch

If `jurisdiction` changes after G1, reopen every gate that is already true,
keep the disclosure facts, and rewrite the legal analysis in the new mode.
Do not leave a Chinese claim set marked locked inside a US project.
