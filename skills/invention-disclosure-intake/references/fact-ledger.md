# Fact ledger / 事实分层

Copy to `00-disclosure/fact_ledger.md`. One row per feature or effect.
The disclosure prose can summarize. This table is what later skills read.

Origin (来源), one value:

| Token | Meaning |
| --- | --- |
| `user-confirmed` | The inventor stated it in this interview |
| `copied-from-file` | Copied from a file the inventor supplied, with the filename |
| `summarized` | Shortened from the inventor's material, not a new fact |
| `suggested` | An agent proposal. It stays out of claims until the inventor changes the tag to `user-confirmed` |
| `open` | Still unknown |

Evidence grade (证据等级), for effects. Features that are not effects use `n/a`.

| Token | Meaning |
| --- | --- |
| `measured` | A measurement, with the notebook, file, or figure the inventor named |
| `experienced` | The inventor observed it and said how |
| `directly-inferable` | Follows from a stated mechanism without a new number |
| `unverified` | Hoped for, or no source. `inventive-point-finder` does not use it |

```text
| ID | Statement | Kind (feature/effect) | Origin | Evidence grade | Source |
|----|-----------|------------------------|--------|----------------|--------|
| F1 |           | feature                |        | n/a            |        |
| E1 |           | effect                 |        |                |        |
```

Do not upgrade `suggested` or `open` while writing the table. Do not
upgrade `unverified` because the effect would help the argument.
