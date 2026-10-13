# Search query builder

Build the queries. Then run them. A query string is not a search result.

## 1. Concept table

From the locked disclosure, make one row per essential feature and one row
for the technical effect (only if the inventor reported it).

| Concept | Inventor's words | Synonyms and spellings | Broader class | Narrower class |
|---------|------------------|------------------------|---------------|----------------|
| C1 | | | | |

Rules:

- Keep the inventor's term, then add synonyms a patent might use
  (function, structure, trade name, Latin name, old name).
- Do not add a synonym that changes the invention.
- Chinese and English both belong in the table when the jurisdiction is
  `CN` or when Chinese publications matter. Search the original script,
  not only a translation.

## 2. IPC and CPC

IPC (International Patent Classification) runs Section (A–H) → class →
subclass → group → subgroup. CPC (Cooperative Patent Classification) is
finer and is what Espacenet and USPTO search well. CNIPA search can take
IPC; use CPC as well when the database offers it.

How to choose a symbol, in this order:

1. Open a document the inventor already identified and copy its IPC and CPC.
2. If you have no such document, use the classification browser inside
   [Espacenet](https://worldwide.espacenet.com),
   [PATENTSCOPE](https://patentscope.wipo.int), or
   [USPTO Patent Public Search](https://ppubs.uspto.gov/pubwebapp/).
   Record the symbol and the official title you saw.
3. Search once at subclass or main-group breadth combined with a keyword,
   then narrow. A subgroup search alone will miss neighboring groups.

Do not assign a symbol from memory of the schedule. An illustrative
pattern, not a classification opinion and not a real query to file:

```
keyword on the problem  AND  subclass you just looked up
```

Delete any illustrative symbol before the query goes into `search_log.md`.

## 3. What to run

For each concept group, prepare:

- a keyword query (title/abstract, then claims if the first set is noisy);
- a classification query (IPC or CPC plus one anchor keyword);
- a name query only for assignees or authors the inventor named.

Also search the inventor's own admitted papers by title, outside the
patent databases if you must, and say so. Do not skip them because they
are not patents.

## 4. Database syntax

If a query returns a syntax error, open that site's help and fix it.
Do not invent hits while "fixing" the query.

### CNIPA patent search

Site: https://pss-system.cponline.cnipa.gov.cn

Use the advanced-search form. Fields that matter: 发明名称, 摘要,
权利要求, 说明书, 申请号, 公开（公告）号, 申请日, 公开（公告）日,
IPC 分类号, 申请人, 发明人. Combine them with the form's AND/OR/NOT.
Copy the 检索式 string the system displays into the log. Do not type
undocumented field codes.

### Google Patents

Site: https://patents.google.com

Operators you may use, and should drop if the page rejects them:

- phrases in quotes; `OR`; parentheses
- `assignee:` and `inventor:`
- `CPC=` and a classification symbol
- `country:CN` (or US, WO, EP, …)
- `before:filing:YYYYMMDD`, `after:publication:YYYYMMDD`,
  `before:priority:YYYYMMDD`

Example pattern (replace the words; this is not a search you should cite):

```
("soil moisture" OR "water content") (sensor OR probe) CPC=G01N country:CN
```

### Espacenet

Site: https://worldwide.espacenet.com

Prefer Advanced search or Smart search, then copy the query Espacenet
shows. Field names that the smart-search help documents include title
(`ti`), abstract (`ab`), title or abstract (`ta`), inventor (`in`),
applicant (`pa`), IPC (`ipc`), CPC (`cpc`), publication date (`pd`),
publication number (`pn`).

Example pattern to verify against the on-page help before you trust a
zero-hit result:

```
ta all "solid electrolyte" AND cpc = H01M
```

### The Lens

Site: https://www.lens.org

Use the structured search (jurisdiction, dates, IPC/CPC, inventor,
applicant). Save the result URL. Do not invent a Lens query language.
If biological sequences are relevant, use the site's sequence search
only on sequences the inventor supplied.

### PATENTSCOPE

Site: https://patentscope.wipo.int

Fielded search commonly accepts `EN_TI`, `EN_AB`, `IC`, `CPC`, `PA`,
`IN`, and a publication-date range `DP:[YYYY TO YYYY]`. Confirm the
codes on the PATENTSCOPE field list if a query fails.

Example pattern:

```
EN_AB:(sensor AND moisture) AND IC:(G01N) AND DP:[2018 TO 2026]
```

### USPTO Patent Public Search

Site: https://ppubs.uspto.gov/pubwebapp/

Build the query with the index picker (title, abstract, claims, CPC,
IPC, inventor, applicant) and copy the string the tool displays.
The old PatFT/AppFT suffixes are retired. Do not use them as if they
were current syntax.

## 5. Log each run

One block per query in `search_log.md`:

```
database:
date:
query (as run):
hits shown:
filters (country, date, family dedup):
kept publication numbers:
why the others were dropped (one line, not a fake relevance score):
```

Family duplicates: keep the earliest publication that actually discloses
the feature, and note the family. Do not count ten family members as ten
documents toward the 10–20.

## 6. Relevance labels

These mimic international-search categories so the matrix is readable.
They are not an official search report.

| Label | Use only when |
|-------|----------------|
| X | One document, read by you, appears to disclose every essential feature under test |
| Y | The document discloses some essential features and is useful in combination |
| A | Background; not the closest |
| inventor-known | Named in the disclosure; contents unverified until you open them |

X is not a rejection. It is a flag for `inventive-point-finder`.
