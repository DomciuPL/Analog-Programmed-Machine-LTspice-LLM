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
├─ examples/
│  └─ dzielnik.cir       # Divider example (C = A/B via feedback)
├─ README.md
└─ LICENSE
```

---

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

## Example: `examples/dzielnik.cir` — Divider by closed loop

Computes `C = A / B` using the canonical error-driven integrator. The product node is normalized using `VL`.

```spice
* APM1_DIVIDER_DIRECT — C = A / B   (feedback, VL-normalized product)
* --- LIBRARY AND MACHINE SCALE ---
.include apm1_lib.txt
.param VL=10

* --- TASK PARAMETERS ---
.param A0=6      B0=3
.param k=150     leak=1e-3
.param L=-100    H=100

* --- NUMERICS FOR FEEDBACK LOOPS ---
.options method=gear maxord=2 trtol=5 reltol=1e-6 abstol=1e-9 vntol=1e-9 plotwinsize=0

* --- CONSTANTS VIA INTEGRATORS (no ideal DC sources) ---
XA  A   0 0   INT     IC={A0}  SIGN=+1  leak=0
XB  B   0 0   INT     IC={B0}  SIGN=+1  leak=0

* --- CORE LOOP: e = A - (B*C) ---
* MUL outputs (·)/VL, so pre-scale B by VL to realize physical product B*C at node BC
XBV  BV  B 0  GAIN  K={VL}
XMUL BC  BV C 0  MUL
XERR e   A  BC 0  SUM   Ku=1  Kd=-1

* Loop gain and state integrator with clamps and small leak
XK   es  e  0   GAIN  K={k}
XC   C   es 0  INTV  SIGN=+1  IC=0  L={L} H={H} leak={leak}

* --- TRANSIENT SETUP ---
.param Tstop=0.30  maxstep={Tstop/30000}
.tran 0 {Tstop} 0 {maxstep}

* --- RESULTS (mandatory) ---
*=== RESULTS_BEGIN ===
.meas tran C_avg     AVG  V(C) FROM=0.20 TO=0.30
.meas tran C_at25    AT   time=0.25
.meas tran C_val25   FIND V(C) AT=C_at25
; Ideal: C = A0/B0 = {A0/B0}
*=== RESULTS_END ===
```

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
