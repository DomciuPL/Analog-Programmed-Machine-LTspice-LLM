# APM-1 — Analog Programmed Machine (LTspice Library)

Deterministic, reproducible analog-computing library for LTspice. The library implements canonical building blocks for continuous-time computation with explicit **machine voltage** `VL` and **computational ground** `GDN=0`. Designs follow the analog computer hierarchy: **integrators**, **summers**, **multipliers/dividers (via feedback)**, **limiters**, and **hybrid timing** elements.

---

## Scope

- Core blocks: `INT`, `INTV`, `SUM`, `GAIN`, `MUL`, `LIM`, `ABS`, `SGN`, `LP1`, `HP1`.
- Hybrid helpers: `CLK`, `MONO`, `EDGE_R/F`, `MUX`, `PWM`, `RSTINT`, `S_H`.
- Pin order is fixed and ends with `GDN`. All examples assume `GDN → 0`.
- Product normalization: `MUL` returns `(a*b)/VL`. Scale accordingly.

---

## Requirements

- LTspice 24.x or newer.
- `apm1_lib.txt` available in the project or LTspice search path.

---

## Installation

1. Copy `apm1_lib.txt` to your project folder.
2. In each `.cir`, include and set the machine scale:
   ```spice
   .include apm1_lib.txt
   .param VL=10
   ```

---

## Numerical settings for feedback loops

Use Gear integration with tight tolerances for stable convergence in closed loops:
```spice
.options method=gear maxord=2 trtol=5 reltol=1e-6 abstol=1e-9 vntol=1e-9 plotwinsize=0
```

---

## Directory layout

```
apm1-lib/
├─ apm1_lib.txt          # Library of APM-1 subcircuits
├─ apm1_lib_rag_v12_pl.md # RULES & GUIDELINES
├─ examples/ 
│  └─ division.cir       # Divider example (C = A/B via feedback)
├─ README.md
└─ LICENSE
```

---
```spice
## Engineering conventions

- **Scaling:** Keep physical variables within ±VL to avoid limiter action unless intended.
- **Products:** `MUL` returns `(a*b)/VL`. Pre- or post-scale with `GAIN K={VL}` when a physical product is required.
- **Division:** Implement as a feedback loop solving `A ≈ B·C`. Add clamps and a small integrator leak.
- **Grounding:** Always connect the last pin of every subcircuit to node `0` (computational ground).
- **RESULTS block:** Each example ends with `.meas` statements (AVG/AT/FROM/TO) for automated validation.

---

## Quick start

1. Duplicate any example from `examples/`.
2. Run `.tran` and inspect `RESULTS` in the LTspice Error Log.
3. Plot state variables and verify steady-state against analytical values.

---

* APM1_DIVISION_NOM_ONLY_APM1.cir — C = A / B (pętla, normalizacja do nominalnej)
* —–– BIBLIOTEKA I SKALA MASZYNOWA —––
.include apm1_lib.txt
.param VL=10

* —–– PARAMETRY ZADANIA —––
.param NOM_A0=6  NOM_B0=3
.param NOM_k=150 NOM_leak=1e-3  NOM_L=-100 NOM_H=100

* —–– OPCJE NUMERYCZNE (sprzężenie zwrotne) —––
.options method=gear maxord=2 trtol=5 reltol=1e-6 abstol=1e-9 vntol=1e-9 plotwinsize=0

* —–– GENERACJA STAŁYCH (integratory z IC; brak źródeł zewn.) —––
XNOM_A   NOM_A   0 0  INT    IC={NOM_A0}  SIGN=+1  leak=0
XNOM_B   NOM_B   0 0  INT    IC={NOM_B0}  SIGN=+1  leak=0

* —–– MULTIPLIKATOR Z KOMPENSACJĄ SKALI VL —––
XNOM_bVL NOM_BVL NOM_B 0 GAIN K={VL}
XNOM_MUL NOM_BC  NOM_BVL NOM_C 0 MUL

* —–– PĘTLA SPRZĘŻENIA: e = A  B*C;  dC/dt = NOM_k·e —––
XNOM_SUM NOM_E   NOM_A   NOM_BC 0 SUM  Ku=1 Kd=-1
XNOM_K   NOM_Es  NOM_E   0       GAIN K={NOM_k}
XNOM_INT NOM_C   NOM_Es  0       INTV SIGN=+1 IC=0 L={NOM_L} H={NOM_H} leak={NOM_leak}

* —–– TRANZJENT I POMIARY —––
.tran 0 0.06 0 1u

*=== RESULTS_BEGIN ===
.meas tran NOM_C_nom        PARAM {NOM_A0/NOM_B0}
.meas tran NOM_C_avg        AVG   V(NOM_C) FROM=0.04 TO=0.06
.meas tran NOM_C_norm_avg   AVG   ( V(NOM_C) / ({NOM_A0}/{NOM_B0}) ) FROM=0.04 TO=0.06
.meas tran NOM_C_rel_err    AVG   ( (V(NOM_C)-({NOM_A0}/{NOM_B0})) / ({NOM_A0}/{NOM_B0}) ) FROM=0.04 TO=0.06
.meas tran NOM_C_rel_err_pc AVG   ( 100*(V(NOM_C)-({NOM_A0}/{NOM_B0})) / ({NOM_A0}/{NOM_B0}) ) FROM=0.04 TO=0.06

.meas tran NOM_t_tau   WHEN V(NOM_E)={NOM_A0}/exp(1)  FALL=1
.meas tran NOM_t_1pct  WHEN V(NOM_E)=0.01*{NOM_A0}    FALL=1
*=== RESULTS_END ===


**Why it converges:** The integrator drives the error `e = A − B·C` toward zero through the gain `k`. With `MUL` normalization handled by `XBV`, steady state satisfies `A ≈ B·C`, hence `C ≈ A/B`. Clamp limits (`L`, `H`) and `leak` prevent wind-up.

---

## Validation checklist

- `[ ]` `.include apm1_lib.txt` present and `.param VL=10` set.
- `[ ]` All subcircuits connect their last pin to node `0`.
- `[ ]` Gear method and tolerances set as above.
- `[ ]` `RESULTS_BEGIN/END` block with `.meas` is present.
- `[ ]` Signals remain within ±VL under nominal parameters.

---

## Troubleshooting

- **Singular matrix or timestep too small:** Add small `leak` to integrators, verify ground pin, reduce loop gain `k`, or relax `maxstep`.
- **Saturation:** Increase `VL` consistently or widen limiter bounds `L/H`.
- **Slow settling:** Reduce `k` oscillations by lowering `maxord` or adding first-order `LP1` in the loop.

---

## Contributing

Open an issue with: LTspice version, minimal failing `.cir`, expected vs. measured behavior, and the Error Log. Match pin order and scaling rules when adding new blocks.

---

## License

MIT recommended for netlists and library code. Add source attributions in comments when reproducing historical examples.

---

## Citation

When using APM-1 in research or teaching, cite the library and specify `VL`, loop topology, and measurement window in your methods section to ensure reproducibility.
