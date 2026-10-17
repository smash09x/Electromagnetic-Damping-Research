# Internal review record

The manuscript was stress-tested before submission by independent AI referee agents (Claude, Anthropic), each given one specialty. The authors made the final decisions.

| File | Stage | What it checked |
|---|---|---|
| `physics.md`, `stats.md`, `electronics.md`, `editor.md` | Round 1 | Theory, statistics and re-analysis of the raw data, instrumentation, journal fit |
| `round2_brief.md` and `round2_*.md` | Round 2 | Cross-examination: each referee rebutted the others after the clock finding |
| `number_audit.md`, `audit.py`, `scale.md` | Audit | Every number in the manuscript recomputed from data; ADC scale lattice |
| `blind_referee.md` | Final | A referee who had seen none of the above |

Main changes these reviews produced:
- the peak-based decay fit was replaced by a fundamental-band estimator (the old one was biased high by about 20%);
- the mains-hum clock calibration (s = 1.261) was added;
- the 1/R exclusion was softened from 3.7σ to 2.3–3σ;
- the suppression factor was corrected to R5/Rc ≈ 7 × 10⁴.
