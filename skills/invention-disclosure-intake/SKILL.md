---
name: invention-disclosure-intake
description: "Interviews the inventor and writes a complete invention disclosure (技术交底书) from their answers only, then stops for the invention lock (发明锁定). Triggers: \"写技术交底书\", \"填写交底\", \"interview the inventor\", \"complete the invention disclosure\", \"锁定技术方案\". Do not use this skill to search prior art, judge patentability, or draft claims."
---

# Invention disclosure intake

Turn the inventor's answers into `00-disclosure/disclosure.md`. Every
sentence comes from the inventor or from a document they handed you.
Missing facts stay `【待发明人确认】` (CN) or `[INVENTOR TO CONFIRM]`
(US, PCT).

Not legal advice. A 专利代理师 (patent agent) or patent attorney reviews
the file before filing.

## When to use

- The project exists and `gates.invention_lock` is not true.
- The inventor wants to fill or correct the 技术交底书 (invention disclosure).

Do not use it after the lock unless the inventor reopens the lock by
changing the solution, the essential features, or the disclosure history.

## Inputs (paths) / Preconditions

- `<project>/patent.yaml` with `jurisdiction` set to `CN`, `US`, or `PCT`.
- `<project>/00-disclosure/disclosure_form.md` (seeded by `patent-project-setup`).
- If the form is missing, copy it from `../patent-project-setup/references/disclosure-form.zh-CN.md` (CN) or `../patent-project-setup/references/disclosure-form.en.md` (US, PCT). Those paths are relative to this skill directory.
- Interview questions: `references/interview-checklist.md`.

Read `patent.yaml` `public_disclosure` before the interview so you do not
ask the inventor to repeat a date they already gave. Still confirm it.

## Procedure (numbered steps)

1. Remind the inventor, in the project language: do not include secrets
   they are not willing to file, and a public disclosure before filing can
   destroy novelty. Point at the grace-period box already printed on the form.
2. Work in three passes. Accept partial answers and mark the rest.
   Do not "complete" a pass from general knowledge of the field.
   - Pass A — problem and known approaches (form §§ 1–4).
   - Pass B — solution, parameters, effects, embodiments, alternatives,
     drawings (form §§ 5–10).
   - Pass C — disclosures, applicant, inventors, genetic resources,
     sequences (form §§ 11–13).
3. Write `00-disclosure/disclosure.md` in Chinese for `CN`, English for
   `US` and `PCT`. Keep the form's section order. Under each effect, name
   the control and the source, or write that the effect is unquantified.
4. Build a gap list at the top of the file: every `【待发明人确认】` or
   `[INVENTOR TO CONFIRM]`, one line each.
5. Show the draft. Ask whether the essential-feature column is right.
   Do not proceed to prior-art search inside this skill.
6. Invention lock, only if the inventor explicitly says `发明人确认锁定交底`
   or `I confirm the invention lock` (or a clear equivalent you quote):
   - Set `gates.invention_lock` to `true` in `patent.yaml`.
   - Append `LOG.md` with the date, this skill's name, the quoted approval,
     and the disclosure filename.
   - If essential sections 4, 5, or 11 are still entirely blank, do not
     lock. Say which section is empty.
7. If the inventor wants changes, edit and leave the gate `false` until
   they lock again.

Unknown patent numbers the inventor "thinks they have seen" go under
background as unverified notes. They are not citations.

## Human gate(s)

Invention lock (G1). The agent records it only after explicit approval.
See `shared/gates.md`.

What the inventor is locking: the technical facts in `disclosure.md`,
including the statement of what is not yet known. They are not locking
patentability.

## Outputs (exact paths + formats)

- `<project>/00-disclosure/disclosure.md` — filled disclosure, same headings
  as the blank form, gap list at the top.
- `<project>/patent.yaml` — `gates.invention_lock: true` only after approval.
  Also update `public_disclosure` if the interview established it.
- `<project>/LOG.md` — append one entry on lock or on a refusal to lock.

Do not write `01-eligibility/`, `02-prior-art/`, or `04-claims/`.

## Quality checklist

- [ ] No number, effect, or embodiment appears that the inventor did not supply.
- [ ] Essential and optional features are separated.
- [ ] Each claimed effect has a control and a source, or is marked unconfirmed.
- [ ] Disclosure history is a filled table, not "N/A" by assumption.
- [ ] Inventorship is tied to conception of a feature, not to author order.
- [ ] Language matches `patent.yaml` `language`.
- [ ] The lock, if set, quotes the inventor's approval in `LOG.md`.

## Guardrails

- Do not embellish "positive results" to satisfy 实用性 (practical applicability). If no positive result is known, say so.
- Do not drop a failed experiment to make the invention look cleaner.
- Do not advise the inventor to hide a publication. Record it.
- Do not store national ID numbers.
- Do not draft claim sentences. A feature table is not a claim set.
- Medical methods, animal or plant varieties, and pure algorithms stay in the disclosure as facts. Eligibility is the next skill's job, not a rewrite of the science.

## Next step

`patent-orchestrator`, which will route to `patentability-screen` after the lock.
If the lock was refused, stay on this skill until the empty sections are filled or the inventor postpones.
