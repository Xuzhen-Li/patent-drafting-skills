# Changelog

All notable changes to this suite are documented in this file.

## 0.2.0 — 2026-10-09

- Unity check before claims: separate inventions that do not share one special technical feature (专利法 Art. 31; 实施细则 Art. 39; 35 U.S.C. § 121; PCT Rule 13). One claim set waits for `one-invention` or a documented combination.
- Drawings freeze a parts-and-steps master, accept only editable sources, and store a sha256 per sheet. Image-model bitmaps, traced art, invented spectra, and invented structures are rejected.
- Consistency opens each PNG, checks black-on-white pixels, and requires every claimed relationship to name a figure. Failures return to `patent-drawings`.
- Word export embeds those images and exits 1 if a checksum no longer matches.
- Description adds a domain checklist, a background admission pass, an added-matter list, and a biology reminder for genetic-resource source disclosure, WIPO ST.26, and deposits. Sequences and data are not generated.
- Disclosure facts carry an origin tag and an evidence grade. Unverified effects are ignored. Search logs state whether one document shows every essential feature, and that in-force claims were not reviewed.
- Claims start with a dependency sketch. Excess-claim fees are a warning with a link to the current office fee page, not a fixed ceiling.
- Existing drafts can be copied into a read-only folder and scored. The score does not close a gate or skip a lock.

## 0.1.0 — 2026-10-09

Initial clean-room release.

- Repository documents: English and Chinese READMEs, MIT license, `install.sh`, and `shared/` (jurisdictions, human gates, Chinese–English glossary).
- Skills 0–5: `patent-orchestrator`, `patent-project-setup`, `invention-disclosure-intake`, `patentability-screen`, `prior-art-search`, `inventive-point-finder`, with disclosure forms, eligibility checklists, a search-query builder, a feature-matrix template, and a bilingual problem–solution worksheet.
- Skills 6–11: `claims-drafter`, `description-writer`, `abstract-writer`, `patent-drawings`, `consistency-checker`, and `patent-docx-export`, with claim and description templates, length and numeral checks, and Word export.

Legal sources named in the skills are public statutes and office guidance only. This suite does not provide legal advice.
