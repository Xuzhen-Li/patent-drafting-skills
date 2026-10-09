---
name: inventive-point-finder
description: "Ranks inventive points with the CN three-step approach (三步法) or US obviousness under 35 U.S.C. § 103, and records fallback positions for a later claim ladder. Triggers: \"找发明点\", \"三步法\", \"inventive step\", \"obviousness analysis\", \"区别技术特征\", \"fallback positions\". Do not use this skill to draft the claim set or to invent a technical effect."
---

# Inventive-point finder

Compare the locked disclosure with the closest real prior art. Rank what
is actually distinctive. Leave fallback positions for `claims-drafter`.
Not legal advice. A 专利代理师 (patent agent) or patent attorney decides
whether the argument is one they will sign.

## When to use

- `gates.prior_art_review` is true.
- `gates.inventive_point_lock` is not true.

Do not use it when the feature matrix still has `unknown` on an essential
feature of the document you want to call "closest". Go back to
`prior-art-search` and read it, or pick a different closest document.

## Inputs (paths) / Preconditions

- `<project>/00-disclosure/disclosure.md`
- `<project>/02-prior-art/search_log.md` and `feature_matrix.csv`
- `<project>/patent.yaml` jurisdiction
- Worksheet: `references/problem-solution-worksheet.md`

You may not add a document that is not in the search log. If you think
one is missing, reopen search. Do not cite it from memory.

## Procedure (numbered steps)

1. Copy the worksheet into `03-inventive-points/inventive_points.md`.
   Fill it in Chinese for `CN`, English for `US`. For `PCT`, fill the
   English problem–solution section and the US column only if the United
   States is a named national phase; otherwise leave that column
   `not requested`.
2. Choose one closest prior art (最接近的现有技术). Prefer a document
   that shares the same purpose and the most essential features. Say why
   the runner-up lost. Do not stitch two documents into a fictional
   single reference. A combination is allowed only as a combination:
   name both documents and the feature each one actually has.
3. List distinguishing technical features (区别技术特征): features in
   the candidate invention that the closest document does not disclose.
   Use the matrix. A cell of `unknown` cannot support a distinction.
4. Attach effects. Use only effects written in the disclosure with a
   source. If the inventor hopes for an effect, it is not an effect in
   this worksheet. Write "no supported effect" and lower the rank.
5. Apply the legal test that matches the file. Do not mix them into one
   conclusion.
   - **CN — 三步法** (审查指南 Part II Chapter 4). (1) Closest prior art.
     (2) Distinguishing features and the technical problem they actually
     solve (实际解决的技术问题), stated without sneaking the solution
     into the problem. (3) Would the skilled person (本领域技术人员)
     have reached the invention from that problem and the prior art?
     "Common general knowledge" needs a source in the log or the
     disclosure. Otherwise mark it unproven.
   - **US — 35 U.S.C. § 103.** Differences, level of ordinary skill on
     the facts you have, and a reason to combine (MPEP 2141, 2143).
     Secondary considerations (unexpected results, failure of others)
     count only when the disclosure contains them. The Chinese
     objective-problem sentence is a fact organizer here, not the US test.
   - **PCT.** Inventive step under PCT Article 33 is the international
     standard (not obvious to the skilled person). Keep national
     differences visible for later phases. Do not call the invention
     "patentable in the PCT countries".
6. Rank inventive points. For each: the feature, the evidence, the risk
   (X document, missing data, narrow workaround), and whether it can
   carry an independent claim concept. A claim concept is one sentence
   naming features. It is not claim language and must not use
   其特征在于 or "comprising" as if it were a filed claim.
7. Fallback positions, broadest first: which feature moves into the
   independent concept, which stays dependent, which is only an
   embodiment. Every fallback feature must already be in the disclosure.
8. Lock only on `发明人确认发明点` or `I confirm the inventive-point lock`.
   Set `gates.inventive_point_lock` to `true` and quote the approval in
   `LOG.md`. If the closest document is still disputed, do not lock.

## Human gate(s)

Inventive-point lock (G3). See `shared/gates.md`. The inventor is locking
the ranking and the fallback order, not a claim set. Claim-set lock is
G4 and belongs to `claims-drafter`.

## Outputs (exact paths + formats)

- `<project>/03-inventive-points/inventive_points.md` — completed worksheet.
- `<project>/patent.yaml` — `gates.inventive_point_lock` after approval.
- `<project>/LOG.md` — appended approval or a note that the closest reference is disputed.

Do not create `04-claims/claims.md`.

## Quality checklist

- [ ] The closest prior art is one row in the search log, with a URL.
- [ ] Every distinguishing feature is a matrix cell of `no` or `partial`, not `unknown`.
- [ ] The objective technical problem does not recite the solution.
- [ ] No effect appears that the disclosure does not support.
- [ ] CN files use the 三步法; US files use § 103; a US file does not end on "therefore inventive step".
- [ ] Fallbacks are ordered and each one points at a disclosure section.
- [ ] The lock quote is in `LOG.md` if the flag is true.

## Guardrails

- Do not upgrade `partial` to `no` to manufacture a distinction.
- Do not argue "no teaching, suggestion, or motivation" unless you read the references you are talking about.
- Do not invent a comparative example or an unexpected result.
- Do not tell the inventor to delete a close reference from the log.
- A utility-model recommendation from the screen does not lower the invention standard inside this worksheet. If both were discussed, say which standard you applied.

## Next step

`patent-orchestrator`, which routes to `claims-drafter` after G3.
If you cannot name a closest document, the next step is `prior-art-search`, not claims.
