# patent-drafting-skills — Design Spec (clean-room)

Author: Xuzhen Li. License: MIT.

This suite is an original work. It is written from public statutes and
official guidance only:

- China: 《中华人民共和国专利法》(2020 修正), 《专利法实施细则》(2023 修订, 国务院令第769号, 自2024年1月20日起施行),
  《专利审查指南》(2023 版), CNIPA 官方申请文件格式要求.
- United States: 35 U.S.C. §§ 101, 102, 103, 112; 37 CFR 1.71–1.84; MPEP
  chapters 600, 700, 2100.
- PCT: PCT Articles 5–7, Rules 5–11; WIPO PCT Applicant's Guide.
- Search sources: CNIPA patent search, Google Patents, Espacenet, The Lens,
  WIPO PATENTSCOPE, USPTO Patent Public Search.

No third-party commercial skill pack text may be consulted or reproduced.

## Goal

An agent-agnostic skill suite that helps an inventor (typically a researcher)
turn a technical idea into a filing-ready **invention patent** draft, with
explicit jurisdiction modes:

- `CN` — Chinese invention patent (发明专利), all outputs in Chinese.
- `US` — US utility non-provisional application, outputs in English.
- `PCT` — international application, English.

Language: **bilingual**. `SKILL.md` instructions are in English with the
Chinese legal term in parentheses at first use; every `SKILL.md` frontmatter
`description` contains both English and Chinese trigger phrases. CN output
templates are written in Chinese; US/PCT templates in English. `README.md`
(English) and `README.zh-CN.md` (Chinese) are full versions, not summaries.

Disclaimer (both languages, in README and orchestrator): this is drafting
assistance, not legal advice; a registered patent attorney/agent
(专利代理师) should review before filing.

## Core principles

1. Never invent experimental data, effects, or embodiments; anything the
   inventor has not supplied is marked `[INVENTOR TO CONFIRM]` / `【待发明人确认】`.
2. Every claim feature must be supported by the description (专利法第 26 条第 4 款; US §112(a)). CN claim form is 实施细则第 22–25 条.
3. Antecedent basis: every "the X / 所述X" must have an earlier "a X / 一种X".
4. Reference numerals in description and drawings must match one-to-one.
5. Prior-art search results must be real, retrievable publications with
   publication numbers and links; no fabricated documents.
6. Confidentiality: remind the user that public disclosure before filing can
   destroy novelty (CN 专利法第 22/24 条 grace period limits; US §102(b)(1)
   one-year grace).
7. Human gates: invention lock, prior-art review, inventive-point lock,
   claim-set lock, final package.

## Project layout (created by `patent-project-setup`)

```
<project>/
  patent.yaml        # title, jurisdiction, applicant, inventors, field, gates passed
  00-disclosure/     # 技术交底书 / invention disclosure
  01-eligibility/
  02-prior-art/
  03-inventive-points/
  04-claims/
  05-description/
  06-abstract/
  07-drawings/       # parts_master.json, then PNG sheets and sheet_manifest.json
  08-consistency/
  09-package/        # final .docx files, images embedded
  incoming/          # read-only copies of old drafts, when any
  LOG.md
```

## Skills (12)

| # | name | Purpose | Key outputs |
|---|------|---------|-------------|
| 0 | `patent-orchestrator` | Entry point; reads `patent.yaml` + LOG, reports stage, routes, enforces gates; jurisdiction switch. | status report |
| 1 | `patent-project-setup` | Create layout; choose jurisdiction; capture applicant/inventor info; set up the invention disclosure form (交底书) template. | `patent.yaml`, `00-disclosure/disclosure_form.md` |
| 2 | `invention-disclosure-intake` | Interview inventor: problem, existing solutions and their drawbacks, technical solution, key parameters, embodiments, effects with evidence, alternatives; produce a complete disclosure; gate: invention lock. | `00-disclosure/disclosure.md` |
| 3 | `patentability-screen` | Subject-matter eligibility (CN 专利法第 2、5、25 条; US §101 Alice/Mayo), industrial applicability, preliminary novelty/inventiveness risk, recommend invention vs utility model (CN). | `01-eligibility/screen.md` |
| 4 | `prior-art-search` | Build keyword + classification (IPC/CPC) queries, run on the listed databases, record top 10–20 documents with number, date, link, closest features; feature-comparison matrix. | `02-prior-art/search_log.md`, `feature_matrix.csv` |
| 5 | `inventive-point-finder` | Problem–solution approach (三步法 / closest prior art → distinguishing features → objective technical problem → obviousness), rank inventive points, fallback positions; gate: inventive-point lock. | `03-inventive-points/inventive_points.md` |
| 6 | `claims-drafter` | Independent claims (product / method / system / use as applicable), dependent-claim ladder from fallback positions, CN two-part form (前序部分 + 特征部分, "其特征在于") vs US style; antecedent check via script; gate: claim-set lock. | `04-claims/claims.md` |
| 7 | `description-writer` | CN five sections (技术领域、背景技术、发明内容、附图说明、具体实施方式) per 实施细则第 20 条; US sections per 37 CFR 1.77; enablement and support for every claim feature; embodiments and variants. | `05-description/description.md` |
| 8 | `abstract-writer` | CN 摘要 ≤300 characters with 摘要附图 selection; US abstract ≤150 words; validated by script. | `06-abstract/abstract.md` |
| 9 | `patent-drawings` | Freeze a parts master, then black-and-white sheets from an editable source, with a sha256 per sheet. | `07-drawings/parts_master.json`, `sheet_manifest.json`, images |
| 10 | `consistency-checker` | Cross-check claims, description, abstract, and opened sheets: numerals, support, black-on-white pixels, and which figure shows each relationship. | `08-consistency/report.md` |
| 11 | `patent-docx-export` | Build the Word set and embed the PNG sheets. The build fails if a sha256 no longer matches the manifest. | `09-package/*.docx` |

## Scripts (Python 3.9+, each with pytest tests)

- `claims-drafter/scripts/check_antecedent.py` — parse claims (CN and EN), flag "所述X/the X/said X" without prior introduction in the same claim chain; validate dependency references (no forward refs, no missing claims, CN multiple-dependent rules).
- `abstract-writer/scripts/check_abstract.py` — CN char count (≤300, excluding punctuation? follow 审查指南: count all characters incl. punctuation — document the rule used), EN word count (≤150).
- `consistency-checker/scripts/check_numerals.py` — extract "name + numeral" pairs from description and a drawing manifest (JSON), report mismatches, unused numerals, one numeral with two names.
- `patent-docx-export/scripts/build_docx.py` — markdown sections → .docx per jurisdiction. Embeds PNG sheets. Exit 1 when a sha256 no longer matches `sheet_manifest.json`.
- `patent-drawings/scripts/sheet_checksums.py` — hash formal PNGs from an editable source after `parts_master.json` is frozen. Rejects image-model bitmaps, traced art, invented spectra, and invented structures.
- `consistency-checker/scripts/check_sheets.py` — opens each PNG, checks black-on-white pixels, checksums, and that each claimed relationship names a figure.
- `description-writer/scripts/admission_scan.py` — flags background sentences that treat the invention as already known.
- `description-writer/scripts/added_matter.py` — lists description sentences that are not in the locked disclosure.
- `patent-project-setup/scripts/intake_existing.py` — copies old drafts into a read-only `incoming/` folder and scores the earliest real stage. It does not close a gate.

## v0.2 additions

Unity (单一性) is decided in `inventive-point-finder` before claims.
CN uses 专利法 Art. 31 and 实施细则 (2023) Art. 39 (特定技术特征). US
restriction practice is 35 U.S.C. § 121. PCT unity is Rule 13. A single
claim set waits until the inventor picks one invention or accepts a
documented combination.

Drawings freeze `07-drawings/parts_master.json` first. Formal sheets come
only from Graphviz, Mermaid, draw.io, SVG, or a matplotlib script. The
consistency checker opens each image. Export embeds the images and fails
if any checksum differs.

Description adds a domain checklist (machine, circuit, software, process,
chemistry, biology), a background admission pass, and an added-matter
list. Biology reminds counsel about 遗传资源来源披露 (专利法 Art. 26,
paragraph 5), WIPO ST.26, and deposits under 实施细则 Art. 27. The skills
do not generate sequences or data.

Other additions: origin tags and evidence grades on disclosure facts
(`unverified` effects are ignored); a single-document novelty line in the
search log, with a statement that in-force claims were not reviewed; a
dependency sketch before claim sentences; an excess-fee warning that does
not impose a claim ceiling; existing-draft intake that cannot skip a lock.

## Per-skill contract and SKILL.md structure

Same as literature-review-skills: `SKILL.md` frontmatter (`name`, `description`),
sections: When to use / Inputs / Procedure / Human gate(s) / Outputs /
Quality checklist / Guardrails / Next step. Keep under ~250 lines; long
templates go to `references/` (e.g. `references/cn-claims-template.md`,
`references/us-claims-template.md`).

## Repo-level files

`README.md`, `README.zh-CN.md`, `LICENSE` (MIT, Copyright (c) 2026 Xuzhen Li),
`install.sh` (same behavior as the review suite), `shared/` (`jurisdictions.md`,
`gates.md`, `glossary_cn_en.md` — CN↔EN patent term glossary), `CHANGELOG.md`.
