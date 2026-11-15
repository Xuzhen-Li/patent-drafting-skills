# Abstract rules

The checker implements these rules. It does not replace a reading of the official text.

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
| 1 | Over 150 words |
| 2 | Within limit, with claim-language or advertising warnings; also used when the file path is missing |

```bash
python3 skills/abstract-writer/scripts/check_abstract.py 06-abstract/abstract.md --lang en
python3 skills/abstract-writer/scripts/check_abstract.py 06-abstract/abstract.md --lang en --format json
```

The script also has a Chinese mode (`--lang zh`, 300 characters) left from an older version; this suite does not use it. `--format text|json|both`. `both` prints the text report, a `===JSON===` line, then JSON.
