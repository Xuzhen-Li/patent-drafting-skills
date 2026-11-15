---
name: patent-orchestrator
description: "Entry point for an invention-patent draft. Reads patent.yaml and LOG.md, reports the stage, routes to the next skill, enforces human gates, and switches between US and PCT. English drafts only. Triggers: \"start a US patent draft\", \"draft a PCT application\", \"where is the patent draft\", \"continue the patent\", \"switch to PCT\", \"switch to a US filing\". Do not use this skill to draft claims, the description, or office-action responses."
---

# Patent orchestrator

Drafting assistance, not legal advice. A registered patent
agent or patent attorney reviews the package before anyone files it.

This skill does not write claims, the description, or the abstract. It
decides which skill runs next and stops on a human gate. Jurisdiction
rules: `shared/jurisdictions.md`. Gate rules: `shared/gates.md`. Chinese-to-English
terms for inventors who write their notes in Chinese:
`shared/glossary_cn_en.md`. Those files live in the suite repository.
The operational rules below are enough after `install.sh`.

## When to use

- The user wants to start, resume, or re-route a patent draft.
- The user asks where the draft stands.
- The user switches jurisdiction (`US`, `PCT`).

Do not use it to search prior art, judge a single eligibility question in
depth, or edit claim language. Route those requests.

## Inputs (paths) / Preconditions

The user points at a project directory. If none exists, the next skill is
`patent-project-setup` and there is nothing to read yet.

When the project exists, read:

- `<project>/patent.yaml`
- `<project>/LOG.md`
- Presence of the stage files listed in the routing table (do not read every draft in full)

`patent.yaml` field `jurisdiction` is `US` or `PCT`. Anything else
is a stop: ask the user to pick one. Drafts are in English. A Chinese
invention patent (CNIPA) is out of scope for this suite; point the user
to the Chinese pack, https://github.com/Xuzhen-Li/patent-skills-private.

## Procedure (numbered steps)

1. State the disclaimer in one sentence, in the project's language.
2. If there is no project, ask for a directory path and hand off to
   `patent-project-setup`. Stop.
3. Read `patent.yaml`. Report jurisdiction, title, applicant, and each
   gate flag. A flag set `true` while its file is missing is an error:
   set that flag back to `false`, append `LOG.md`, and tell the user.
4. If `incoming/` exists, or the user pointed at old drafts, run
   `skills/patent-project-setup/scripts/intake_existing.py score`.
   Reset every gate named in `gates_inconsistent` to false and append
   `LOG.md`. A stage file counts as missing when the score says it is
   not real. A filename containing "complete" is not proof. Drawing
   images without a frozen parts master and a matching sheet checksum are
   not a finished drawing stage. `visual_look.json` is written by
   `consistency-checker` after those sheets exist. Do not skip a lock the
   files do not satisfy.
5. Walk the routing table from the top and select the first row that
   matches. Tell the user the skill name and why. Then follow that
   skill's `SKILL.md`. Do not skip ahead because a later file already
   exists. When `intake_score.json` exists, its `earliest_missing`
   should name the same skill. If it does not, follow the table and say
   why.
6. After the child skill returns, append `LOG.md` if that skill did not,
   and issue a fresh status report.
7. Never set a gate to `true` yourself. Record `true` only after an
   explicit approval quoted in the log (see `shared/gates.md`).

### The twelve skills

| # | Skill | Owns |
|---|-------|------|
| 0 | `patent-orchestrator` | Status, routing, gates, jurisdiction switch |
| 1 | `patent-project-setup` | `patent.yaml`, folders, blank disclosure form, read-only `incoming/` |
| 2 | `invention-disclosure-intake` | `00-disclosure/disclosure.md`, invention lock |
| 3 | `patentability-screen` | `01-eligibility/screen.md` |
| 4 | `prior-art-search` | `02-prior-art/search_log.md`, `feature_matrix.csv`, prior-art review |
| 5 | `inventive-point-finder` | `03-inventive-points/inventive_points.md`, inventive-point lock |
| 6 | `claims-drafter` | `04-claims/claims.md`, claim-set lock |
| 7 | `description-writer` | `05-description/description.md` |
| 8 | `abstract-writer` | `06-abstract/abstract.md` |
| 9 | `patent-drawings` | frozen parts master, figure list, checksummed sheets |
| 10 | `consistency-checker` | `08-consistency/report.md` |
| 11 | `patent-docx-export` | `09-package/*.docx`, final package |

### Routing

| Condition | Next skill |
|-----------|------------|
| No `patent.yaml` or missing stage folders | `patent-project-setup` |
| Old drafts were offered and `incoming/` has not been scored | `patent-project-setup` |
| `gates.invention_lock` is not true, `00-disclosure/disclosure.md` is missing, or that file is not a real disclosure | `invention-disclosure-intake` |
| `01-eligibility/screen.md` is missing | `patentability-screen` |
| The screen says stop, and the log has no inventor override | Stop. Do not search or draft |
| `gates.prior_art_review` is not true, or `02-prior-art/feature_matrix.csv` is missing | `prior-art-search` |
| `gates.inventive_point_lock` is not true, or `unity_decision` is missing or `split-pending` | `inventive-point-finder` |
| `gates.claim_set_lock` is not true, or `04-claims/claims.md` is missing | `claims-drafter` |
| `05-description/description.md` is missing | `description-writer` |
| `06-abstract/abstract.md` is missing | `abstract-writer` |
| Drawings are not `none`, and the frozen `parts_master.json` or `sheet_manifest.json` is missing, or a sheet checksum does not match | `patent-drawings` |
| `08-consistency/report.md` records an open drawing failure (checksum, unopened image, forbidden source, or a relationship without a figure) | `patent-drawings` |
| `08-consistency/report.md` is missing or still has other failures | `consistency-checker` |
| `gates.final_package` is not true, or `09-package/` has no `.docx` | `patent-docx-export` |
| All of the above are satisfied | Stop. Counsel review. Do not file |

`drawings: none` is allowed only when the inventor says figures are not
needed to understand the invention (PCT Article 7; US 35 U.S.C. § 113).
Record that sentence in the log.

### Jurisdiction switch

When the user changes `US` / `PCT`:

1. Explain what must be redone: claim form and fees, the grace period
   (35 U.S.C. § 102(b)(1) for US; PCT adds no grace of its own), and the
   inventive-step write-up (§ 103 versus the PCT problem-solution style).
2. Wait for an explicit yes.
3. Update `jurisdiction`. Set every gate that is already true back to
   `false`. Keep `00-disclosure/disclosure.md` as facts, but mark legal
   conclusions inside it as stale.
4. Append `LOG.md`. Route to the first skill whose output is now stale.
   Do not machine-translate a locked claim set.

### Status report

Use `references/status-report.md`. Include open items marked
`[INVENTOR TO CONFIRM]`, and any public disclosure
the inventor has admitted.

## Human gate(s)

This skill enforces gates; it does not close them. If the user asks to
"just mark it locked", refuse and name the missing approval.

## Outputs (exact paths + formats)

- A status report in the chat, and, when the project exists, an appended
  entry in `<project>/LOG.md` for any routing or jurisdiction change.
- Updated `patent.yaml` only for a confirmed jurisdiction switch or for
  resetting an inconsistent gate. Do not invent applicant or inventor data.

## Quality checklist

- [ ] The next skill is the first matching row, not a later one the user happened to mention.
- [ ] Jurisdiction is `US` or `PCT`, and the output is in English.
- [ ] No gate was set to `true` in this turn without a quoted approval.
- [ ] A "do not proceed" screen is honored unless the log contains an override.
- [ ] The report names file paths, not a vague "almost done".

## Guardrails

- Do not fabricate data, effects, prior-art documents, or dates.
- Do not tell the user that a paper is "safe" under a grace period. State the rule and mark the facts unconfirmed until dates are in the disclosure.
- Do not submit anything to the USPTO or a receiving Office.
- Do not hide a close reference. US duty of disclosure: 37 CFR 1.56.
- Unpublished technical content may be confidential. Warn once, at the start of a new project, that a public disclosure before filing can destroy novelty.

## Next step

The skill named in the status report. When the table's last row matches,
the next step is human counsel, not another skill.
