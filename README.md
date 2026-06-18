# Security Contracts for `ark-vc` and `ark-mt`

The default single-element digest configurations shipped with `ark-mt` do not
achieve λ=128 binding or hiding for small fields. A one-element BabyBear digest
carries roughly 30 conservative bits; a birthday attack finds a binding break in
44 seconds. No single parameter choice is correct across fields: BabyBear and
BN254 require nine and two digest elements respectively at the same λ=128 target.

This report defines a security-requirements spine for `ark-vc` and `ark-mt` that
corrects this. A protocol designer provides a field `F`, a security level `λ`, a
hash function `H`, and a choice of standard or hiding interface. The spine
derives conservative parameters, encodes the corresponding obligations, measures
their cost, and publishes the evidence. A Lean 4 formalisation gives the
parameter derivation machine-checked standing for any compliant instantiation.

The formal parameter derivation for digest width `D`, field salt length `k`, and
byte salt length `S` is:

$$D = \lceil(\lambda+1+2h)/\lfloor\log_2|\mathbb{F}|\rfloor\rceil, \quad
  k = \lceil\lambda/\lfloor\log_2|\mathbb{F}|\rfloor\rceil, \quad
  S = \lceil\lambda/8\rceil$$

For BabyBear at λ=128, h=64: D=9, κ=270, k=5, S=16. The ROM binding
certificate for this instantiation is fully machine-checked.

## Build

```bash
latexmk -pdf main.tex
```

The PDF is written to `build/main.pdf`.

## Structure

The body is organised by security property rather than by the generic
motivation/method/results shape: the vector-commitment object is stated once in
the spine, and binding and hiding each carry their own definition, failure,
derived parameter, and validation status.

Active build (`main.tex` inputs, in order):

- `main.tex`: title, abstract, contributions, and the evidence-register reference
- `sections/motivation.tex`: the commitment layer as the rung every IOP compiles through, and why the small-field defaults fail both properties
- `sections/spine.tex`: the security-requirements spine — the VC/Merkle object, the four designer inputs, and the arity-independent `(D,k,S)` rule
- `sections/binding.tex`: position binding, sized and machine-checked end to end (generic over the Merkle shape)
- `sections/hiding.tex`: the hiding contract — machine-checked salt cardinality, with the ROM composition named as the open obligation
- `sections/cost.tex`: the measured Poseidon2 cost and the Bytewise Blake3 contrast
- `sections/conclusion.tex`: the priced, validated contract, the evidence register, and the `Next` roadmap
- `tables/claim-register.tex`: honest status of each security axis (the credibility anchor, referenced from contributions and conclusion)
- `figures/make-performance-plots.py`: binding/hiding performance plot generator
- `preamble/style.tex`, `preamble/macros.tex`: short-paper visual system and notation

Retained but no longer built (superseded by the property-organised structure;
kept as companion material so nothing is lost): `sections/attack.tex`,
`sections/approach.tex`, `sections/results.tex`, `sections/phase1.tex`,
`sections/implications.tex`, `tables/parameter-example.tex`,
`tables/results-summary.tex`, `tables/method-summary.tex`.

## What this report does NOT claim

- A completed hiding theorem or Merkle `HasROMHiding` instance (the interface,
  cardinality prerequisites, and structural foundation are in place; the
  selective-opening composition is the next development step)
- A completed ROM extraction certificate (`cacheExtract_sound` is sorry)
- A Lean-to-Rust refinement theorem
- Programmable-ROM simulation or equivocation (out of scope)
- Protocol-level security for every system using a Merkle tree
