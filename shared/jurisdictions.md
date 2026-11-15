# Jurisdictions: US and PCT

This file compares the two filings this suite drafts in English: a US
utility non-provisional and a PCT international application. A Chinese
invention patent (CNIPA, written in Chinese) is out of scope here; use
[patent-skills-private](https://github.com/Xuzhen-Li/patent-skills-private)
for that. For a later China national phase, counsel checks the Chinese
rules separately.

This file is drafting orientation, not legal advice. Confirm every fee, form, and
time limit on the office site before you rely on it.

Choose one mode in `patent.yaml` (`US` or `PCT`) and keep it until a
human switches it. All outputs are English.

## 1. What each mode is

| | US | PCT |
|---|----|-----|
| Right you are drafting | Utility patent, non-provisional | International application |
| Office | USPTO | Receiving Office, then an International Searching Authority; patents are granted only in the national/regional phase |
| Language of this suite | English | English |
| Term | 20 years under 35 U.S.C. § 154, generally from the earliest related non-provisional filing date, plus any patent term adjustment the Office applies | No international grant. National terms follow each office |
| Publication | 18 months from the earliest filing date, with exceptions | International publication, normally 18 months from the priority date |

US design patents and plant patents are out of scope.

## 2. Document set

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

| | US | PCT |
|---|----|-----|
| Independent claim shape | Open-ended claim, usually "comprising". A Jepson (two-part) claim is optional, not the default (37 CFR 1.75(e)) | Two-part form where appropriate (Rule 6.3); otherwise a one-part claim |
| Dependent claims | Further limitations; proper antecedent basis | Rule 6 |
| Multiple dependent claims | Allowed, but a multiple dependent claim must not depend on another multiple dependent claim (37 CFR 1.75(c)); extra fees apply | Follow Rule 6 and the receiving office's forms |
| Antecedent | First mention "a"/"an"; later "the" or "said" | Same discipline in English |
| Support | 35 U.S.C. § 112(a) written description and enablement; § 112(b) definiteness | PCT Article 5 (disclosure) and Article 6 (support) |

Do not translate a Chinese two-part claim word-for-word into English and
call it a US claim.

Unity is separate from claim form. US: restriction of independent and
distinct inventions under 35 U.S.C. § 121. PCT: Rule 13.1 and Rule 13.2.
`inventive-point-finder` records the split. `claims-drafter` does not
write one claim set across groups that do not share that feature unless
the inventor accepts a documented combination.

Product, method, system, and use claims are all available when the facts
support them.

## 4. Description shape

US, the usual 37 CFR 1.77 headings: background, brief summary, brief
description of the drawings, detailed description. Do not add a "best mode"
heading that asserts a best mode the inventor never identified. PCT Rule 5
does ask for the best mode contemplated by the applicant; if the inventor
has not stated one, mark `[INVENTOR TO CONFIRM]`.

## 5. Abstract limits

| Jurisdiction | Limit | What to count |
|---|---|---|
| US | 150 words | 37 CFR 1.72(b): as concise as the disclosure permits, preferably not exceeding 150 words. MPEP 608.01(b) generally uses one paragraph of 50 to 150 words. This suite's checker fails a longer abstract. Do not copy a claim into the abstract |
| PCT | Preferably 50 to 150 words in English | PCT Rule 8 |

`abstract-writer` and its checker own the count. Do not "summarize" by
inventing an advantage.

## 6. Drawing rules

Shared rule of this suite: every reference sign in the description
and in the figures matches one-to-one. One sign, one name.

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

### US

- § 101: a new and useful process, machine, manufacture, or composition of matter, or an improvement. Judicial exceptions (laws of nature, natural phenomena, abstract ideas) are analyzed with the Alice/Mayo steps in MPEP 2106. Utility must be specific, substantial, and credible (MPEP 2107).
- § 102: prior art before the effective filing date, including a prior patent, printed publication, public use, on sale, or otherwise available to the public, plus earlier-filed later-published US applications naming another inventor. The one-year inventor grace is § 102(b)(1).
- § 103: obviousness to a person of ordinary skill before the effective filing date. Graham factors and KSR rationales (MPEP 2141 and 2143).
- § 112: written description, enablement, and definite claims.

Duty of disclosure: 37 CFR 1.56. Material prior art the inventor knows belongs
in an information disclosure statement. Do not bury the closest reference.

### PCT

The international search and preliminary examination use novelty, inventive
step, and industrial applicability (PCT Article 33). Each designated state
applies its own law again at national phase. A favorable written opinion is
not a national allowance.

## 8. Grace periods

Public disclosure before filing can destroy novelty. Read this before any
paper, preprint, poster, thesis, talk, website, sale, or public code release.

| | US | PCT |
|---|----|-----|
| Default | Disclosure before the effective filing date is prior art, subject to § 102(b) | The Treaty does not create a grace period. Each national law applies in its phase |
| Exception | § 102(b)(1): a disclosure one year or less before the effective filing date, made by the inventor or by someone who obtained the subject matter from the inventor (and certain later disclosures of the same subject matter) | Depends on the national phase. Another country does not inherit the US year |
| What researchers get wrong | A paper by the inventor can be graced if it is inside one year and the exception is properly invoked. Do not assume every co-author's independent paper qualifies | Filing a PCT application does not repair a disclosure that already destroyed novelty in a national phase |

## 9. Fees

Do not hard-code amounts. They change, and entity status changes them.

- US: [USPTO fee schedule](https://www.uspto.gov/learning-and-resources/fees-and-payment/uspto-fee-schedule), with excess-claim items under 37 CFR 1.16.
- PCT: [WIPO PCT fee tables](https://www.wipo.int/en/web/pct-system/fees).

`claims-drafter` warns when the claim count may add an excess fee and lists optional fallbacks. It does not impose a claim ceiling.

Official search and document sites used by `prior-art-search`:

- [pss-system.cponline.cnipa.gov.cn](https://pss-system.cponline.cnipa.gov.cn) (Chinese-language prior art)
- [patents.google.com](https://patents.google.com)
- [worldwide.espacenet.com](https://worldwide.espacenet.com)
- [lens.org](https://www.lens.org)
- [patentscope.wipo.int](https://patentscope.wipo.int)
- [ppubs.uspto.gov/pubwebapp](https://ppubs.uspto.gov/pubwebapp/)

## 10. Switching mode

Switching US ↔ PCT after drafting has started is a human decision.
The orchestrator reopens the gates that depend on language and legal tests
(claim form, grace-period analysis, inventive-step write-up).
It does not auto-translate a locked claim set.
