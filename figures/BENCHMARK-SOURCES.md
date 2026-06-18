# Security-parameter benchmark figures

The report-native performance figures are the annotated triptychs:

- `benchmark_hiding_poseidon_triptych_extra_x.pdf`
- `benchmark_hiding_bytewise_triptych_extra_x.pdf`
- `benchmark_binding_poseidon_triptych_extra_x.pdf`
- `benchmark_binding_bytewise_triptych_extra_x.pdf`

They are converted from the corresponding `*_triptych.svg` outputs in:

- `ark-vc/crates/ark-mt/benches/plots/with_level_transitions/`

The source plots derive from the `ark-mt` `security_parameters` Criterion
benchmark and deterministic observation CSVs. The fixed regime is a binary
Merkle tree with 4,096 leaves and 32 openings. Red `x` markers identify the
first point requiring another Poseidon2 permutation or Blake3 compression.
Field-coloured vertical lines mark the first measured configurations reaching
the displayed security targets.
