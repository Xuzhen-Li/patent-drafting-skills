---
name: description-writer
description: >-
  Write the patent description that enables and supports the locked claims.
  CN five-part description, US specification order under 37 CFR 1.77, PCT
  Rule 5. 撰写说明书、技术领域、背景技术、发明内容、附图说明、具体实施方式、
  支持权利要求、充分公开、enablement、written description。
---

# Description writer

Write `05-description/description.md` so a person skilled in the art can carry out the invention and so every claim feature has support. CN text is Chinese. US and PCT text is English.

Read [`../../shared/jurisdictions.md`](../../shared/jurisdictions.md), [`../../shared/glossary_cn_en.md`](../../shared/glossary_cn_en.md), and the locked `04-claims/claims.md`.

## When to use

- Claim-set lock is recorded.
- The user asks for the description (说明书), specification, embodiments (具体实施方式), or enablement support.

## Inputs

- `patent.yaml`, `00-disclosure/disclosure.md`, `02-prior-art/`, `03-inventive-points/inventive_points.md`, `04-claims/claims.md`, `04-claims/claim_map.md`.
- CN template: [`references/cn-description-template.md`](references/cn-description-template.md).
- US and PCT template: [`references/us-description-template.md`](references/us-description-template.md).
- Domain rows: [`references/domain-checklist.md`](references/domain-checklist.md). Biology reminder: [`references/biology-reminder.md`](references/biology-reminder.md).

## Procedure

1. Stop if claim-set lock is missing. Do not quietly widen or narrow the claims in this step. A missing claim feature goes back to `claims-drafter`.
2. Copy the jurisdiction template into `05-description/description.md`. Keep the section order.
3. Technical field (技术领域 / technical field): one paragraph. Name the field in the same words as the claim preamble.
4. Background (背景技术 / background): describe the problem and the closest real documents from `02-prior-art/`. Every citation needs a publication number and a link that came from the search log. No document is added from memory. Do not describe the invention's own solution as already known. "Well known" needs a source in the search log.
5. Summary (发明内容 / brief summary): restate the claim solutions in descriptive sentences. Cover each independent claim and the important fallbacks. This section is support, not a repetition of `其特征在于` as claim boilerplate.
6. Drawings (附图说明 / brief description of the drawings): one sentence per figure, in order. Draft reference numerals and `07-drawings/numerals.json` (`"10": "housing"` or `"10": "壳体"`). These numbers are provisional. `patent-drawings` freezes `parts_master.json` before any formal sheet and keeps one number per part. Do not invent a part here.
7. Detailed description (具体实施方式 / detailed description): walk through at least one full way of making and using the invention, tied to the figures. Then add the variants the inventor actually disclosed. For each claim feature, include a paragraph that uses the claim's noun and the arrangement or step.
8. Effects (有益效果): write only effects tied to inventor-supplied evidence. Otherwise write `【待发明人确认】` or `[INVENTOR TO CONFIRM]`.
9. Leave paragraph numbers `[0001]` to `patent-docx-export`. Do not type them into the markdown.
10. PCT: follow the US template's English prose and the Rule 5 headings noted in that template (technical field, background art, disclosure, drawings, a way of carrying out the invention, industrial applicability when it is not obvious).
11. Admission pass. Run `scripts/admission_scan.py` on `description.md`. Write `05-description/admission_review.md` with each flag. A sentence that treats the invention as already known blocks handoff until it is rewritten or the inventor shows it is about a cited document, not about this solution.
12. Domain checklist. Copy `references/domain-checklist.md` to `05-description/domain_review.md` for machines, circuits, software, processes, chemistry, biology, and any combination that applies. Missing data stays a request. Do not fill it with generic text. Software needs a technical setting, not a business result.
13. Biology, when that row applies. Follow `references/biology-reminder.md`. Remind counsel to confirm 遗传资源来源披露 (专利法 Art. 26, paragraph 5; 实施细则 Art. 29), a WIPO ST.26 sequence listing if sequences were disclosed, and a biological-material deposit when 实施细则 Art. 27 applies. Do not generate sequences, source countries, or accession numbers. Do not clear a diagnostic or treatment question by retitling.
14. Added matter. Run `scripts/added_matter.py` with the description and the locked disclosure. Write `05-description/added_matter.md`. Mark sentences that were not in the disclosure. Unsupported widening goes back to `claims-drafter` or to the inventor. A new pre-filing fact needs a dated confirmation. Do not delete the list to make the description look original.

## Human gate(s)

Claim-set lock is a precondition, not a new gate. Before consistency checking, the inventor confirms the embodiments, the numeral list, and every `【待发明人确认】` / `[INVENTOR TO CONFIRM]` item. Record that confirmation in `LOG.md`.

## Outputs

- `05-description/description.md`
- `07-drawings/numerals.json` — drawing manifest consumed by `consistency-checker`
- `05-description/support_matrix.md` — one row per claim feature: claim number, feature, description heading, status `supported` or `confirm`
- `05-description/admission_review.md` — background sentences that treat the invention as known
- `05-description/domain_review.md` — domain checklist, including the biology reminder when it applies
- `05-description/added_matter.md` — sentences not in the locked disclosure

## Quality checklist

- Section order matches the template for the jurisdiction.
- A skilled person could carry out the independent claims from the detailed description without adding a fact that is not in the file (专利法第26条第3款; 35 U.S.C. §112(a); PCT Rule 5).
- Every claim noun appears in the description with the same meaning.
- Numerals are one number per part name in `numerals.json`, written in the text as `housing 10` or `壳体10` / `壳体(10)`.
- Background citations are real records from `02-prior-art/`.
- No new experimental result, range, or commercial comparison.
- `admission_scan.py` has no open flag, or each flag is resolved in `admission_review.md`.
- `added_matter.md` exists. New technical sentences are confirmed or sent back.

## Guardrails

- The description may be broader than a preferred embodiment. It may not introduce subject matter the inventor did not supply.
- Do not draft a sequence, a spectrum, a deposit number, or a genetic-resource origin the inventor did not supply.
- Do not criticize named competitors. State technical drawbacks of the prior art that the search file supports.
- CN claims must remain supported by this file (专利法第26条第4款). US claims must remain enabled and described (35 U.S.C. §112(a)).
- Reference signs in the description and in the claims are the same integers.
- This file is confidential until filing. A pre-filing public disclosure can destroy novelty (专利法第24条; 35 U.S.C. §102(b)(1)).

## Next step

`abstract-writer` and `patent-drawings` can proceed in parallel. `consistency-checker` runs after both have outputs.
