# Status report

Fill this in the chat. Do not create a second project status file.

```
Project: <path>
Title: <or [INVENTOR TO CONFIRM]>
Jurisdiction: CN | US | PCT
Language of drafts: zh | en
Screen: missing | proceed | proceed-narrowed | stop | stop-overridden

Gates
  invention_lock:        true | false
  prior_art_review:      true | false
  inventive_point_lock:  true | false
  claim_set_lock:        true | false
  final_package:         true | false

Stage files
  00 disclosure:     present | missing
  01 screen:         present | missing
  02 search log:     present | missing
  02 feature matrix: present | missing
  03 inventive pts:  present | missing
  04 claims:         present | missing
  05 description:    present | missing
  06 abstract:       present | missing
  07 drawings:       present | none-declared | missing
  08 consistency:    pass | fail | missing
  09 package:        present | missing

Next skill: <exact skill name>
Why: <one sentence>
Open items: <【待发明人确认】 / [INVENTOR TO CONFIRM] list, or "none">
Public disclosure admitted: yes (date) | no | unknown
```

The next skill is a name from the orchestrator table: `patent-project-setup`,
`invention-disclosure-intake`, `patentability-screen`, `prior-art-search`,
`inventive-point-finder`, `claims-drafter`, `description-writer`,
`abstract-writer`, `patent-drawings`, `consistency-checker`,
`patent-docx-export`. If counsel must take over, write `none — counsel review`.
