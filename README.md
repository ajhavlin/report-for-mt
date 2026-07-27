# Security Contracts for `ark-vc` and `ark-mt`

The default single-element digest configurations shipped with `ark-mt` do not
achieve λ=128 binding or hiding for small fields. A one-element BabyBear digest
carries roughly 30 conservative bits; a birthday attack finds a binding break in
44 seconds. No single parameter choice is correct across fields: BabyBear and
BN254 require nine and two digest elements respectively at the same λ=128 target.

This report defines a security-requirements rule for `ark-vc` and `ark-mt` that
corrects this. A protocol designer provides a field `F`, a security level `λ`, a
hash function `H`, a standard or hiding interface, and a declared query budget.
The rule derives conservative parameters, encodes the corresponding obligations,
measures their cost, and publishes the evidence. The binding analysis and the
salt-cardinality prerequisite carry machine-checked Lean 4 backing; the full
hiding composition remains explicitly scoped as an open obligation.

The formal parameter derivation for digest width `D`, field salt length `k`, and
byte salt length `S` is:

$$D = \lceil(\lambda+1+2h)/\lfloor\log_2|\mathbb{F}|\rfloor\rceil, \quad
  k = \lceil\lambda/\lfloor\log_2|\mathbb{F}|\rfloor\rceil, \quad
  S = \lceil\lambda/8\rceil$$

For BabyBear at λ=128, h=64: D=9, κ=270, k=5, S=16. The binding chain for
this instantiation carries fully machine-checked backing.

## Build

```bash
latexmk -pdf main.tex
```

The build output is written to `build/main.pdf`; `main.pdf` is the compiled
snapshot included with the report sources.

## Structure

The body is organised by security property rather than by the generic
motivation/method/results shape. Binding and hiding each carry their own
definition, failure mode, derived parameter, and validation status; the appendix
holds the supporting definitions, benchmarks, and engineering history.

Active build (`main.tex` inputs, in order):

- `main.tex`: title, abstract, and section arc
- `sections/contributions.tex`: scope and contributions
- `sections/background.tex`, `sections/rule-box.tex`: protocol context, definitions, failure, and the derive-or-refuse rule
- `sections/binding.tex`: position binding and its security reduction
- `sections/hiding.tex`: the hiding contract and salt-cardinality prerequisite
- `sections/cost.tex`: the measured Poseidon2 cost and the Bytewise Blake3 contrast
- `tables/cost-at-128.tex`: absolute measurements at the λ=128 crossings
- `sections/conclusion.tex`: the priced contract, formal status, and the `Next` roadmap
- `sections/appendix.tex`: supporting definitions, engineering history, and benchmark details
- `figures/make-performance-plots.py`: binding/hiding performance plot generator
- `preamble/style.tex`, `preamble/macros.tex`: short-paper visual system and notation

## What this report does NOT claim

- A completed hiding theorem or Merkle `HasROMHiding` instance (the interface,
  cardinality prerequisites, and structural foundation are in place; the
  selective-opening composition is the next development step)
- A completed ROM extraction certificate (`cacheExtract_sound` is sorry)
- A Lean-to-Rust refinement theorem
- Programmable-ROM simulation or equivocation (out of scope)
- Protocol-level security for every system using a Merkle tree
