# Round 2: statistics referee

## (b) Headline estimator, with the clock correction applied

**Recommendation:** use the Hilbert envelope of the fundamental band (0.6–1.4 f). Fit ln(envelope) from the first peak above 50% of the maximum plus 1 s, to the end minus 1 s, with one point per cycle. Quote errors from a 6-cycle block bootstrap.

**Systematic band:** the half-range of the three estimators of displacement decay (Hilbert, NLLS fundamental, transduction model), plus ±1% for the clock. Exclude peak-picking and rms, because harmonics bias both.

| Quantity (×10⁻³ s⁻¹, true time) | Spring 1 | Spring 2 |
|---|---|---|
| Hilbert envelope (headline) | **11.9 ± 0.5** | **13.5 ± 1.0** |
| NLLS / transduction model | 12.0 / 11.2 | 13.7 / 12.2 |
| Q | 551 ± 24 | 436 ± 32 |
| f_true (Hz) | 2.082 | 1.862 |

The ± values are the s.d. over 8 runs.

**γ at a reference amplitude:** report it as secondary. Its spread is larger (s.d. 0.79 against 0.50 for spring 1), and its value moves from 10.3 to 11.4 depending on the chosen amplitude.

*Sentence:* "γ is the decay rate of the fundamental-band envelope: γ₁ = (11.9 ± 0.5_scatter ± 0.4_method ± 0.15_clock)×10⁻³ s⁻¹; the first half of each run decays 18% (spring 1) and 25% (spring 2) faster than the second."

## (a) Final positions

**Conflict 2.** The clock correction *does* change the significance. The predicted c ∝ 1/ω² rises by s², while the measured c falls by 1/s.

- Measured: c = −0.011 ± 0.006 Ω s⁻¹. Predicted: c = +0.030 Ω s⁻¹, with A = 2.2 cm.
- Under a t-distribution with 6 dof: 3.6σ with A exact, 3.0σ for σ_A = 10%, 2.3σ for σ_A = 20%.
- Permutation test p = 0.003 (2.75σ). Pairs bootstrap 2.6σ. Dropping either 0 Ω retake gives 3.2 or 3.6σ.
- Predicted γ_em/γ is **17%** (9–25% over A = 3.0–1.8 cm), not 7%.

*Sentence:* "A fit gives c = (−0.011 ± 0.006) Ω s⁻¹ against +0.030 Ω s⁻¹ expected for a loop closed through R_c + R_ext, excluded at about 3σ (permutation p = 0.003; 2.3σ if A is uncertain by 20%). The decisive argument is independent of this fit: the loop closed through 1 MΩ, suppressing γ_em by 10⁶."

**Conflict 3.** Keep the divider check.
- The 1.4 mV rms noise is mostly hum (SNR 802), which the 20 Hz filter removes.
- After filtering, the noise is 0.042 mV, a negligible correction in quadrature.
- Corrected for amplitude using H2/H1 (r = 0.999), the ratio is **0.303 ± 0.006**. The prediction is 0.3125, or 0.29–0.33 allowing 5% resistor tolerance.
- Caveat: extrapolated (H2/H1 0.285 vs 0.32–0.36).

*Sentence:* "After correcting for this run's ≈15% smaller release, the EMF is 0.30 of the low-R value, against 0.31 from the R5/(R5+R_ext) divider."

**Conflict 5.** I accept the correction. Evidence: hum harmonics at 126/189 Hz; video implies s = 1.23 ± 0.07 (s = 1 ruled out at 3.5σ); swapped k labels fit. f is stable to 0.06% within runs. The 52–55 Hz peaks in three runs come from a second interferer, and the SNR > 50 cut correctly excludes them.

*Sentence:* "The timebase was calibrated against the 50 Hz mains line (s = 1.261 ± 0.013) and checked against the video record." For the springs, write only "consistent with the k labels being swapped; k is being re-measured". Require a direct timing check (GPIO toggle or micros() log).

## (c) Video check

γ_video/γ_EMF,true = **1.06 ± 0.20 (s.d.), standard error of the mean 0.06, n = 12**. By spring it is 1.15 ± 0.20 (spring 1) and 0.97 ± 0.17 (spring 2), consistent with 1 (p = 0.33). On the nominal clock with the peak estimator it was 0.76. The per-run correlation is nil (r = 0.26 and −0.16), so the video confirms the scale only.

## (d) Disagreements

- **Brief, "significance does not change":** it does. z goes from 2.6 to 3.6 at fixed A. My Round-1 value of 2.6σ is superseded, and σ_A now dominates.
- **Physics M2:** reference-amplitude γ should be secondary, not the headline. Quote the divider as "0.29–0.30", which covers both Physics' 0.287 and my 0.303.
- **Electronics:** the 2.2 MΩ noise is out of band and does not bias ε_rms.
- **Editor:** keep two sentences on video tracking as the clock check, and drop only its table column. The proposed abstract's "17.8" and "7%" are now wrong; they become 11.9 and ≈17%.
