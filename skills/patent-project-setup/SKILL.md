---
name: patent-project-setup
description: "Creates a patent-draft project folder, patent.yaml, a blank invention disclosure (技术交底书), and LOG.md for CN, US, or PCT. Triggers: \"新建专利项目\", \"init a patent project\", \"建一个发明专利文件夹\", \"set up a US patent draft\", \"建立PCT案卷\". Do not use this skill to interview the inventor in depth or to write claims; hand a created project back to patent-orchestrator."
---

# Patent project setup

Create the project skeleton and capture who is filing where. Do not draft
the invention. The disclosure form you copy is blank on purpose.

Not legal advice. A 专利代理师 (patent agent) or patent attorney should
review the file before filing.

## When to use

- `patent-orchestrator` found no `patent.yaml`.
- The user asks to start a project: "我要写一个发明专利", "start a US
  patent draft", "起草一件PCT".

Do not use it to rewrite a disclosure that already exists. That is
`invention-disclosure-intake`. Do use the existing-draft steps below
when the inventor already has files.

## Inputs (paths) / Preconditions

- A project directory the user names. Create it only inside a path the
  user gave. Do not invent a path under a home directory they did not name.
- Jurisdiction if they already said `CN`, `US`, or `PCT`. If they did not,
  ask before writing files.

Read `shared/jurisdictions.md` in the suite repository when you need the
document-set or grace-period comparison. Templates in this skill's
`references/` are the copies you seed into the project.

## Procedure (numbered steps)

1. State, once: public disclosure before filing can destroy novelty.
   China (专利法 Art. 24) is not a general six-month grace for the
   inventor's own paper. The United States has a one-year inventor grace
   (35 U.S.C. § 102(b)(1)). PCT creates no grace of its own.
2. Ask only what this skill stores. Skip a question the user already
   answered.
   - Jurisdiction: `CN`, `US`, or `PCT`.
   - Working title (a technical name, not a slogan). If they have none,
     use `[INVENTOR TO CONFIRM]` or `【待发明人确认】`.
   - Applicant name and type: individual, company, university, or other.
     For a 职务发明 (service invention, 专利法 Art. 6), the applicant is
     often the employer. If the inventor is unsure, leave the applicant
     as `【待发明人确认】` and do not guess.
   - Inventor names and a one-line role. Do not copy national ID numbers
     into the project. Those belong only on the official form.
   - Technical field, one phrase.
   - Whether they already know of a public disclosure (yes / no / unsure)
     and, if yes, the date. Details wait for the intake interview.
   - CN only: they are starting an 发明专利. Note utility model
     (实用新型) as a later screen question, not a second project.
3. Create the directories and files listed under Outputs. Copy the blank
   disclosure form:
   - `CN`: `references/disclosure-form.zh-CN.md` → `00-disclosure/disclosure_form.md`
   - `US` or `PCT`: `references/disclosure-form.en.md` → `00-disclosure/disclosure_form.md`
4. Write `patent.yaml` from `references/patent.yaml.example`. Fill only
   answers you were given. Gates stay `false`. `drawings: pending`.
5. Write `LOG.md` from `references/log-template.md` with the jurisdiction
   choice and who made it.
6. If the inventor already has drafts, notes, or drawings, copy them
   before any interview:
   - Ask them to put the files in a folder they name, or to confirm the
     files are already in the project.
   - Copy into `<project>/incoming/` with
     `scripts/intake_existing.py copy`. The copy is read-only. A second
     copy does not overwrite. `.DS_Store`, `Thumbs.db`, and `desktop.ini`
     are ignored. Do not edit the incoming files.
   - Run `scripts/intake_existing.py score --project <project>` and save
     the JSON as `<project>/intake_score.json`.
   - The score says which stage files are real. A filename that contains
     "complete" is not proof. Drawing images are a finished drawing stage
     only when `parts_master.json` is frozen and `sheet_manifest.json`
     matches the PNG bytes. `visual_look.json` is written later by
     `consistency-checker`.
   - Do not set a gate to true because a file was copied. The orchestrator
     starts at `earliest_missing` and does not skip a lock the files do
     not satisfy.
7. Hand control back to `patent-orchestrator`. If there were no old
   drafts, the next skill is `invention-disclosure-intake`. If there
   were, the next skill is the score's `earliest_missing`.

Do not create claim, description, or abstract drafts "to save time".

## Human gate(s)

None. Setup does not lock the invention. Confirming the jurisdiction is
a setup choice, not the invention lock.

## Outputs (exact paths + formats)

```
<project>/
  patent.yaml
  LOG.md
  00-disclosure/disclosure_form.md
  01-eligibility/
  02-prior-art/
  03-inventive-points/
  04-claims/
  05-description/
  06-abstract/
  07-drawings/
  08-consistency/
  09-package/
  incoming/            # read-only copies of old drafts, when any
  intake_score.json    # present only after an existing-draft score
```

Empty stage directories may contain a one-line `.gitkeep` if the
environment cannot store empty folders. Do not put draft text in them.

`patent.yaml` keys: `title`, `jurisdiction`, `language` (`zh` for CN, `en`
for US and PCT), `applicant`, `inventors`, `field`, `public_disclosure`,
`drawings`, `gates`. See `references/patent.yaml.example`.

## Quality checklist

- [ ] Jurisdiction is exactly `CN`, `US`, or `PCT`.
- [ ] The disclosure form language matches the jurisdiction.
- [ ] All five gates are `false`.
- [ ] No national ID, passport number, or bank detail was written.
- [ ] No experimental result, claim, or prior-art citation was invented.
- [ ] `LOG.md` records the date, the skill name, and the jurisdiction.
- [ ] Old drafts, if any, are only in `incoming/` as read-only copies, and `intake_score.json` does not mark a gate closed.

## Guardrails

- Do not choose the applicant by guessing from an email domain or a lab affiliation.
- Do not tell the user a planned paper is compatible with filing. Record the date as unknown until they supply it.
- Do not file, pay a fee, or open an office account.
- Fee amounts change. Point to [cnipa.gov.cn](https://www.cnipa.gov.cn), [uspto.gov](https://www.uspto.gov), or [patentscope.wipo.int](https://patentscope.wipo.int). Do not quote a figure from memory.

## Next step

`invention-disclosure-intake`, via `patent-orchestrator`.
