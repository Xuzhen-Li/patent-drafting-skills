# Claim template (US utility and PCT)

Write the filed text in `04-claims/claims.md`. One claim is one sentence, ending with a period. US output is English. PCT claims follow this template and PCT Rule 6. Mark missing facts `[INVENTOR TO CONFIRM]`.

Statutory frame to apply while drafting:

- 35 U.S.C. §112(a): the description must enable the claim and show possession of the invention.
- 35 U.S.C. §112(b): the claim must particularly point out and distinctly claim the subject matter.
- 35 U.S.C. §112(d) and 37 CFR 1.75: a dependent claim refers to an earlier claim and further limits it.
- 35 U.S.C. §112(e) and 37 CFR 1.75(c); PCT Rule 6.4: a multiple-dependent claim refers to other claims in the alternative only, and it must not serve as a basis for any other multiple-dependent claim.
- Antecedent basis: MPEP 2173.05(e). Introduce with `a`/`an` (or `at least one`, `one or more`, `a plurality of`). Repeat with `the` or `said`.

## Preamble, transition, body

Every claim has three parts.

1. Preamble: names the category (`A sensor device`, `A method`, `A system`).
2. Transition:
   - `comprising` — open. Listed elements are required; unlisted elements are not excluded. Default.
   - `consisting of` — closed. Unlisted elements are excluded. Use only when the inventor wants that scope.
   - `consisting essentially of` — excludes elements that would materially affect the basic and novel characteristics. Use only with an explicit inventor instruction, because the boundary is easy to under-describe.
3. Body: the elements and how they are connected, arranged, or performed.

```
1. A sensor device comprising:
a housing; and
a sensor disposed in the housing.

2. The sensor device of claim 1, wherein the sensor is a temperature sensor.

3. The sensor device of any one of claims 1 or 2, wherein the housing is metal.
```

`of claim 1`, `according to claim 1`, and `as claimed in claim 1` are all acceptable single dependencies. For more than one parent, write `any one of claims 1 to 3` or `claim 1 or claim 2`. Do not write `claims 1 and 2`.

A claim that depends from only one multiple-dependent claim is allowed. This is not allowed:

```
4. The sensor device of claim 1 or 2, wherein the housing is closed.
5. The sensor device of claim 3 or 4, wherein the housing is sealed.
```

Claim 5 is multiple-dependent and uses claim 4, which is itself multiple-dependent.

## Method

```
1. A method comprising:
measuring a signal with a sensor; and
adjusting an output based on the signal.
```

Name the actor's act and the object. Do not add temperatures, times, or yields the inventor did not supply.

## System

```
1. A system comprising:
a processor; and
a memory storing instructions that, when executed by the processor, cause the processor to [act the inventor described].
```

If the invention is not a programmed computer, do not force this skeleton.

## Means-plus-function (35 U.S.C. §112(f))

`means for` or `step for` plus a function, without structure, material, or acts in the claim, invokes §112(f). The claim is then limited to the corresponding structure, material, or acts in the specification and equivalents (MPEP 2181).

Nonce words can be treated the same way when they have no structural meaning: `module for`, `unit for`, `mechanism for`, `device for`, `element for`.

Default: recite the structure.

```
a latch biased against the housing
```

Use §112(f) only when the inventor chooses it. Then the detailed description must name the structure that performs each function, not only the function.

```
a fastening means for holding the housing closed
```

is acceptable only together with a description that identifies the actual fastener (clip, screw, weld) and its arrangement.

## Reference signs

Parenthetical reference signs are optional (37 CFR 1.84 practice; PCT Rule 6). They must match the drawing numerals and are not a second naming system.

```
a housing (10); and
a sensor (12) disposed in the housing (10).
```

## After drafting

```bash
python3 skills/claims-drafter/scripts/check_antecedent.py 04-claims/claims.md --lang en
```

PCT: same command. Keep the claim count and multiple-dependent fees in view for the US filing; the script does not compute fees.
