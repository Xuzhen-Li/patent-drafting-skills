# Jurisdictions — CN, US, and PCT

This file is the suite's comparison of a Chinese invention patent (发明专利),
a US utility non-provisional, and a PCT international application (国际申请).
It is drafting orientation, not legal advice. Confirm every fee, form, and
time limit on the office site before you rely on it.

Choose one mode in `patent.yaml` and keep it until a human switches it.
`CN` outputs are Chinese. `US` and `PCT` outputs are English.

Statutes named below are ones this suite treats as settled public law.
Where a procedural deadline lives only in the Implementing Regulations
(专利法实施细则, 2023 revision) and the article number is easy to mis-cite
after that revision, the skill says "see the Implementing Regulations and
审查指南" instead of guessing a number.

## 1. What each mode is

| | CN | US | PCT |
|---|----|----|-----|
| Right you are drafting | Invention patent (发明专利) | Utility patent, non-provisional | International application |
| Office | CNIPA | USPTO | Receiving Office, then an International Searching Authority; patents are granted only in the national/regional phase |
| Language of this suite | Chinese | English | English |
| Term | 20 years from the filing date (专利法 Art. 42), subject to any term compensation the office actually applies | 20 years under 35 U.S.C. § 154, generally from the earliest related non-provisional filing date, plus any patent term adjustment the Office applies | No international grant. National terms follow each office |
| Publication | 18 months from the filing date unless early publication is requested (专利法 Art. 34) | 18 months from the earliest filing date, with exceptions | International publication, normally 18 months from the priority date |

Utility models (实用新型) and design patents (外观设计) are not this suite's
default product. A CN screen may recommend a utility model as an alternative.
US design patents and plant patents are out of scope.

## 2. Document set

### CN invention

Separate filing pieces the later export skill produces:

- 请求书 (request) — filled on the CNIPA system, not generated as a fake form here
- 权利要求书 (claims)
- 说明书 (description)
- 说明书附图 (drawings), when the invention needs figures
- 说明书摘要 (abstract)
- 摘要附图 (figure accompanying the abstract), one figure, when drawings exist

Also expect, when they apply, and do not invent their contents:

- 实质审查请求 (request for substantive examination), within three years from the filing date (专利法 Art. 35)
- Power of attorney if a 专利代理师 files
- Genetic-resource source disclosure (遗传资源来源披露) when the invention relies on genetic resources (专利法 Art. 26)
- A sequence listing in WIPO ST.26 form when the office requires one
- Priority documents when priority is claimed (专利法 Art. 29: 12 months for inventions)

Same-day invention and utility model: 专利法 Art. 9 allows the same applicant
to file both on the same day for the same creation, with a declaration. That
is a filing strategy for counsel, not a second draft this suite writes unasked.

### US utility non-provisional

Typical contents (37 CFR 1.51 and the arrangement in 37 CFR 1.77):

- Specification: title, background, brief summary, brief description of the drawings, detailed description
- Claims
- Abstract
- Drawings when required to understand the invention (35 U.S.C. § 113)
- Application Data Sheet
- Inventor oath or declaration (35 U.S.C. § 115)
- Fees

This suite's export target is the specification, claims, and abstract as
editable documents. The inventor still files the ADS, declaration, and fees
in Patent Center. A provisional application is only a priority placeholder;
this suite drafts the non-provisional.

### PCT

International application contents follow PCT Articles 5–7 and Rules 5–11:

- Request
- Description (Rule 5), including the technical field, background art, disclosure of the invention, brief description of drawings, and the best mode contemplated by the applicant
- Claims (Article 6, Rule 6)
- Drawings when necessary (Article 7, Rule 11)
- Abstract (Rule 8)

National phase entry is a later, country-by-country act. The usual time limit
is 30 months from the priority date, and some offices differ. Read the current
national chapter; do not memorize a single number for every office. PCT
search and written opinion are not a grant.

## 3. Claim form

| | CN | US | PCT |
|---|----|----|-----|
| Independent claim shape | Two-part form when it fits: 前序部分 (preamble: title plus features shared with the closest prior art) + 特征部分 (characterizing portion) introduced by 其特征在于 (characterized in that) | Open-ended claim, usually "comprising". A Jepson (two-part) claim is optional, not the default (37 CFR 1.75(e)) | Two-part form where appropriate (Rule 6.3); otherwise a one-part claim |
| Dependent claims | Further technical features (附加技术特征) referring to a preceding claim | Further limitations; proper antecedent basis | Rule 6 |
| Multiple dependent claims | Refer to earlier claims in the alternative only, and do not depend on another multiple dependent claim (审查指南, claims) | Allowed, but a multiple dependent claim must not depend on another multiple dependent claim (37 CFR 1.75(c)); extra fees apply | Follow Rule 6 and the receiving office's forms |
| Antecedent | First mention 一种 / 一个; later 所述 | First mention "a"/"an"; later "the" or "said" | Same discipline in English |
| Support | Every feature must be in the description (专利法 Art. 26, paragraph 4). The description must enable a person skilled in the art (本领域技术人员) to carry out the invention | 35 U.S.C. § 112(a) written description and enablement; § 112(b) definiteness | PCT Article 5 (disclosure) and Article 6 (support) |

Do not put 其特征在于 into a US claim. Do not translate a Chinese two-part
claim word-for-word into English and call it a US claim.

Product, method (方法), system, and use (用途) claims are all available when
the facts support them. CN excludes methods of diagnosis and treatment of
diseases as subject matter (专利法 Art. 25). A compound-for-use style that
the Guidelines allow is a drafting question for `claims-drafter` and counsel,
not a conclusion of the screen.

## 4. Description shape

CN, five parts used by the Implementing Regulations and 审查指南 Part II
(names, not a guessed article number):

1. 技术领域 (technical field)
2. 背景技术 (background art)
3. 发明内容 (summary of the invention)
4. 附图说明 (brief description of the drawings) — omit only when there are no drawings
5. 具体实施方式 (detailed description of embodiments)

US, the usual 37 CFR 1.77 headings: background, brief summary, brief
description of the drawings, detailed description. Do not add a "best mode"
heading that asserts a best mode the inventor never identified. PCT Rule 5
does ask for the best mode contemplated by the applicant; if the inventor
has not stated one, mark `[INVENTOR TO CONFIRM]`.

## 5. Abstract limits

| Jurisdiction | Limit | What to count |
|---|---|---|
| CN | 300 characters maximum for the abstract body | Count characters, including punctuation. 审查指南 forbids advertising language. The title is a separate field and is not a substitute for the abstract. One 摘要附图 when drawings exist |
| US | 150 words | 37 CFR 1.72(b): as concise as the disclosure permits, preferably not exceeding 150 words. MPEP 608.01(b) generally uses one paragraph of 50 to 150 words. This suite's checker fails a longer abstract. Do not copy a claim into the abstract |
| PCT | Preferably 50 to 150 words in English | PCT Rule 8 |

`abstract-writer` and its checker own the count. Do not "summarize" by
inventing an advantage.

## 6. Drawing rules

Shared rule of this suite: every reference sign (附图标记) in the description
and in the figures matches one-to-one. One sign, one name.

CN (审查指南 drawing requirements, applied at preliminary examination):

- Black lines on a white ground. Clear enough to reproduce.
- Figure numbers as 图1, 图2, in order of citation.
- Words on drawings only when a flowchart or similar figure cannot be understood without a short label.
- Photographs are exceptional, not the default.
- The abstract figure is a single selected figure, not a new drawing and not a collage.

US (37 CFR 1.84):

- Black ink, durable, uniformly thick lines. Color only if the rule's petition path is actually used.
- Paper size and margins as stated in 37 CFR 1.84. Cite the section rather than retyping millimeters from memory in the draft.
- Reference characters at least 3.2 mm (1/8 inch) high, not placed on lines, and consistent with the description.
- Photographs only when they are the practical way to show the subject (37 CFR 1.84(b)).

PCT (Rule 11):

- Black, well-defined lines; no coloring as a design choice.
- Sheet size and margins as in Rule 11. The international phase is strict about physical form; a figure that looks fine in a slide can fail.

Figures are original. Do not trace a figure from a paper or from another
person's patent.

## 7. Patentability, in one screen

This is the vocabulary the later skills use. It is not a freedom-to-operate
opinion and not a grant prediction.

### CN — 专利法 Art. 22

- 新颖性 (novelty): the invention is not prior art, and there is no conflicting application (抵触申请) filed earlier by anyone and published on or after the filing date. Prior art is technology known to the public in China or abroad before the filing date (absolute novelty).
- 创造性 (inventive step): compared with the prior art, the invention has prominent substantive features and represents notable progress (突出的实质性特点和显著的进步). A utility model uses a lower standard (实质性特点和进步).
- 实用性 (practical applicability): the invention can be made or used and can produce a positive effect (积极效果).

The examination of inventive step uses the three-step approach (三步法) in
审查指南 Part II Chapter 4: closest prior art (最接近的现有技术),
distinguishing features (区别技术特征) and the technical problem actually
solved, then whether the invention would have been obvious to the skilled
person. See `shared/glossary_cn_en.md` and the worksheet in
`inventive-point-finder`.

Subject matter that is not an invention: 专利法 Art. 2 (a technical solution).
Excluded matter: Art. 5 (law, morality, public interest, illegal genetic
resources) and Art. 25 (scientific discoveries, rules and methods for mental
activities, diagnostic and therapeutic methods, animal and plant varieties,
nuclear transformation processes and substances obtained that way, and designs
of patterns, colors, or both on printed matter that serve mainly as
indicators). Production methods of animal and plant varieties can be patented
(Art. 25, second paragraph). Computer-program
inventions are examined under 审查指南 Part II Chapter 9: a technical problem,
technical means, and technical effect can be eligible even though a pure
algorithm or business rule is not.

### US

- § 101: a new and useful process, machine, manufacture, or composition of matter, or an improvement. Judicial exceptions (laws of nature, natural phenomena, abstract ideas) are analyzed with the Alice/Mayo steps in MPEP 2106. Utility must be specific, substantial, and credible (MPEP 2107).
- § 102: prior art before the effective filing date, including a prior patent, printed publication, public use, on sale, or otherwise available to the public, plus earlier-filed later-published US applications naming another inventor. The one-year inventor grace is § 102(b)(1), not a Chinese-style grace.
- § 103: obviousness to a person of ordinary skill before the effective filing date. Graham factors and KSR rationales (MPEP 2141 and 2143). Do not replace this test with the Chinese 三步法 when the file is US-only. The worksheet has a US column so the facts still line up.
- § 112: written description, enablement, and definite claims.

Duty of disclosure: 37 CFR 1.56. Material prior art the inventor knows belongs
in an information disclosure statement. Do not bury the closest reference.

### PCT

The international search and preliminary examination use novelty, inventive
step, and industrial applicability (PCT Article 33). Each designated state
applies its own law again at national phase. A favorable written opinion is
not a US or CN allowance.

## 8. Grace periods (宽限期)

Public disclosure before filing can destroy novelty. Read this before any
paper, preprint, poster, thesis, talk, website, sale, or public code release.

| | CN | US | PCT |
|---|----|----|-----|
| Default | Disclosure before the filing date is prior art against the application | Disclosure before the effective filing date is prior art, subject to § 102(b) | The Treaty does not create a grace period. Each national law applies in its phase |
| Exception | 专利法 Art. 24, as amended in 2020: within six months before the filing date, novelty is not lost only for (1) a first disclosure for the public interest when the state is in an emergency or an extraordinary situation (国家出现紧急状态或者非常情况时，为公共利益目的首次公开), (2) first display at an international exhibition sponsored or recognized by the Chinese government, (3) first publication at a prescribed academic or technological meeting, or (4) disclosure by another person without the applicant's consent | § 102(b)(1): a disclosure one year or less before the effective filing date, made by the inventor or by someone who obtained the subject matter from the inventor (and certain later disclosures of the same subject matter) | Depends on the national phase. China does not inherit the US year. The US does not inherit Art. 24 |
| What researchers get wrong | An inventor's own journal article, preprint, or thesis is usually fatal in China. Art. 24 is not a general six-month cushion for the inventor's own papers | A paper by the inventor can be graced if it is inside one year and the exception is properly invoked. Do not assume every co-author's independent paper qualifies | Filing a PCT application does not repair a disclosure that already destroyed CN novelty |

If a grace-period ground might apply in China, the applicant must declare it
and file evidence within the time the Implementing Regulations set. Confirm
that time limit in the current text before filing. Mark the file
`【待发明人确认】` until the inventor lists dates and venues.

## 9. Fees

Do not hard-code amounts. They change, and entity status changes them.

- CN: official fee schedule published by CNIPA, from [cnipa.gov.cn](https://www.cnipa.gov.cn).
- US: USPTO fee schedule, from [uspto.gov](https://www.uspto.gov).
- PCT: current international fee tables linked from [patentscope.wipo.int](https://patentscope.wipo.int).

Official search and document sites used by `prior-art-search`:

- [pss-system.cponline.cnipa.gov.cn](https://pss-system.cponline.cnipa.gov.cn)
- [patents.google.com](https://patents.google.com)
- [worldwide.espacenet.com](https://worldwide.espacenet.com)
- [lens.org](https://www.lens.org)
- [patentscope.wipo.int](https://patentscope.wipo.int)
- [ppubs.uspto.gov](https://ppubs.uspto.gov)

## 10. Switching mode

Switching CN ↔ US ↔ PCT after drafting has started is a human decision.
The orchestrator reopens the gates that depend on language and legal tests
(claim form, abstract length, grace-period analysis, inventive-step write-up).
It does not auto-translate a locked claim set.
