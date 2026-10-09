# Abstract rules

The checker implements these rules. It does not replace a reading of the official text.

## Chinese invention patent

- The abstract briefly states the technical points of the invention (专利法第26条第3款).
- 《专利审查指南》要求摘要文字部分（包括标点符号）不得超过300个字，并且不得使用商业性宣传用语。
- Counting rule used by `check_abstract.py`: count every character, including punctuation; exclude whitespace (space, tab, newline, and fullwidth space U+3000). A string `甲，乙` counts as 3. A string `甲 乙` counts as 2.
- State the subject, the technical problem, the point of the solution, and the principal use.
- Choose one 摘要附图 that best characterizes the invention. Record the file name in `patent.yaml` as `abstract_figure`.
- The abstract text does not use a title (审查指南: 摘要文字部分不得使用标题). A reference sign in the abstract, if any, is placed in parentheses.
- Do not write 其特征在于 or 其特征是. Those belong in claims, not in the abstract.
- Advertising phrases the script warns on include: 最佳, 最好, 完美, 独特, 领先, 革命性, 卓越, 无与伦比, 国际领先, 填补空白, 世界第一, 唯一.

## United States

- 37 CFR 1.72(b): the abstract must commence on a separate sheet and be as concise as the disclosure permits, preferably not exceeding 150 words. MPEP 608.01(b) generally limits it to a single paragraph of 50 to 150 words. `check_abstract.py` fails a draft longer than 150 words.
- Word count used here: one whitespace-separated token is one word. `state-of-the-art` is one word. The script does not apply a special USPTO hyphen or numeral table beyond that.
- Do not use `characterized in that` or `characterised in that`.
- Advertising words the script warns on include: best, perfect, unique, superior, revolutionary, unparalleled, world-leading, cutting-edge, first-class.
- The abstract is not a claim and is not a marketing blurb.

## PCT

- PCT Rule 8: the abstract summarizes the disclosure. Where the abstract is in English, the length is preferably 50 to 150 words. This suite checks the 150-word ceiling with the English counter.
- Draft the PCT abstract in English, in `06-abstract/abstract.md`.

## Exit codes

| Code | Meaning |
| --- | --- |
| 0 | Within limit, no warnings |
| 1 | Over 300 characters (zh) or 150 words (en) |
| 2 | Within limit, with claim-language or advertising warnings; also used when the file path is missing |

```bash
python3 skills/abstract-writer/scripts/check_abstract.py 06-abstract/abstract.md --lang auto
python3 skills/abstract-writer/scripts/check_abstract.py 06-abstract/abstract.md --lang zh --format json
```

`--format text|json|both`. `both` prints the text report, a `===JSON===` line, then JSON.
