---
name: prior-art-search
description: "Builds IPC/CPC and keyword queries, searches real patent databases, and writes a search log plus a feature-comparison matrix. Triggers: \"检索现有技术\", \"查专利\", \"prior art search\", \"search Espacenet\", \"找最接近的对比文件\". Do not use this skill to declare the invention novel or to draft claims."
---

# Prior-art search

Find real documents. Record what you opened. Compare features. Stop for
the inventor to review. Not legal advice, and not a patentability opinion.

A 专利代理师 (patent agent) or patent attorney should review the matrix
before it drives claim scope.

## When to use

- Invention lock is true, `01-eligibility/screen.md` exists, and its
  recommendation is not `stop` (unless `LOG.md` quotes an override).
- `gates.prior_art_review` is not true.

Do not use it to invent citations from memory of "famous patents".

## Inputs (paths) / Preconditions

- `<project>/00-disclosure/disclosure.md` — feature table and disclosure history.
- `<project>/01-eligibility/screen.md` — especially a `proceed-narrowed` note.
- `<project>/patent.yaml` — jurisdiction.
- Method: `references/search-query-builder.md`.
- Blank matrix: `references/feature-matrix.csv`.
- Blank log: `references/search-log-template.md`.

Databases, official sites only:

- CNIPA patent search: https://pss-system.cponline.cnipa.gov.cn
- Google Patents: https://patents.google.com
- Espacenet: https://worldwide.espacenet.com
- The Lens: https://www.lens.org
- PATENTSCOPE: https://patentscope.wipo.int
- USPTO Patent Public Search: https://ppubs.uspto.gov

## Procedure (numbered steps)

1. Freeze the feature list from the disclosure (F1, F2, …). If a feature
   is still `【待发明人确认】` / `[INVENTOR TO CONFIRM]`, you may search
   the confirmed features and you must say which features were not searched.
2. Build queries with `references/search-query-builder.md`: synonyms,
   IPC and CPC, one keyword query and one classification query at minimum.
   Do not pick a classification symbol because it "sounds right". Take it
   from a document you opened, or browse the classification inside
   Espacenet, PATENTSCOPE, or USPTO Patent Public Search and record the
   symbol you actually selected.
3. Run the queries. If you cannot open a database, write `not searched`
   and the reason. Do not fill the gap from memory.
   - `CN`: at least one source that retrieves Chinese publications
     (CNIPA, Google Patents, Espacenet, or PATENTSCOPE) and one second source.
   - `US`: USPTO Patent Public Search or Google Patents, plus Espacenet or PATENTSCOPE.
   - `PCT`: Espacenet or PATENTSCOPE, plus one other source.
4. Keep 10 to 20 documents that are actually relevant. If fewer than 10
   are relevant, keep the smaller set and write "only N relevant hits".
   Never pad.
5. For each kept document, the log must include publication number,
   publication date, title, database, retrieval date, and a URL on one of
   the hosts above. Open the page in this session (or accept a page the
   inventor opened and pasted). If the number cannot be opened, it does
   not enter the matrix; put it under "unverified leads".
6. Copy closest features with a location (paragraph, claim, or figure).
   If you did not read that location, write `unknown`, not a paraphrase
   from the abstract's vibe.
7. Fill `feature_matrix.csv`. Rows are the disclosure features. Columns
   after `ours` are publication numbers. Cell values are only `yes`,
   `partial`, `no`, or `unknown`. `no` means you looked and the feature
   was not there. Unread text is `unknown`.
8. Single-document novelty line, in the search log. Say whether any one
   opened document shows every essential feature. Novelty, on this
   screen, fails only in that case. If a cell on an essential feature is
   still `unknown`, the answer is `unknown`, not `no`. Do not analyze a
   combination here. That stays in `inventive-point-finder`. Add one
   sentence: in-force claims were not reviewed. This is not a
   freedom-to-operate opinion and not an allowance opinion.
9. Ask the inventor to review. Prior-art review (G2) closes only on
   `发明人确认检索结果` or `I confirm the prior-art review`. Then set
   `gates.prior_art_review` to `true` and quote the approval in `LOG.md`.
10. Hand the closest one or two documents to the next skill by naming them
    in the log. Do not run the 三步法 here.

## Human gate(s)

Prior-art review (G2). See `shared/gates.md`. The inventor is confirming
that the documents exist and that the matrix is a fair reading, not that
the invention is patentable.

Reopen the gate if a later document is closer than the one you marked closest.

## Outputs (exact paths + formats)

- `<project>/02-prior-art/search_log.md` — queries, dates, counts, document register, unverified leads.
- `<project>/02-prior-art/feature_matrix.csv` — UTF-8 CSV, header as in the template, no example row left in place.
- `<project>/patent.yaml` — gate only after approval.
- `<project>/LOG.md` — append on approval or on "search blocked, databases unreachable".

Non-patent literature the inventor named stays in the log as inventor-supplied
and is verified only if you opened it. Do not invent a DOI.

## Quality checklist

- [ ] Every matrix column header except `feature_id`, `feature_text`, and `ours` is a publication number that appears in the log with a URL.
- [ ] No cell is `no` unless the relevant part was actually read.
- [ ] Queries are copied as run, including the database name and the date.
- [ ] Hit counts are the counts the database showed, not estimates.
- [ ] IPC/CPC symbols are traced to a page you opened or a symbol copied from a retrieved document.
- [ ] The log says whether any single opened document shows every essential feature.
- [ ] The log says in-force claims were not reviewed.
- [ ] The inventor's own admitted papers are in the log even if they are not patents.
- [ ] Language of the log narrative matches the project. Publication titles stay in the original language.

## Guardrails

- Do not fabricate publication numbers, dates, assignees, or quotations.
- Do not cite a patent because you remember it. Verify it on an official page first.
- Do not conclude "novel" or "inventive".
- Do not omit the closest reference because it is inconvenient (37 CFR 1.56; 专利法 Art. 20).
- Do not download or redistribute full PDFs into a public place. Store links and the notes you wrote.
- Search syntax that errors is fixed from that database's own help, not by inventing a field code.

## Next step

`patent-orchestrator`, which routes to `inventive-point-finder` after G2.
