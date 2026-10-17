# Referee report: data analysis and statistics

Scripts and outputs are in `/root/paper/reviews/stats_work/`: `refit.py`, `physfit.py`, `extra.py`, `cfit.py`, `corr.py`, `extra2.py`, and `out/*.json`. The authors' `make_figs.py` was re-run unchanged into `stats_work/out/`.

## Verification of quoted numbers (item 5)

Almost all of the numbers reproduce exactly from the raw CSVs. This covers every gamma, Q and eps_rms in Table 1, every entry in Table 2, the means and s.d. (17.8±0.6 and 20.9±1.9), Q = 465±15 and 353±33, b = 3.74±0.12 and 4.40±0.41 g/s, c = −0.0094±0.0077 and 0.015±0.026, c_pred = 0.0190, gamma_em = 1.25e-3 (7.0% of the total, 2.1 times the scatter), 1.9e-8 s^-1, the divider values 0.245 / 0.3125 / 6.1%, R^2 (19 of 21 above 0.97), r = 0.98 / −0.06, and the 4% / 21% retake differences. Mismatches and imprecisions:

- **(MINOR) Frequencies.** 2.633 Hz and 2.333 Hz are FFT bins (79/30 s and 70/30 s), with a resolution of 0.033 Hz. Zero crossings of the fundamental give **2.626 Hz** (spring 1, 9 runs, range 2.625–2.628) and **2.349 Hz** (spring 2, range 2.348–2.349). *Fix:* quote f = 2.626(2) and 2.349(1) Hz, and recompute Q.
- **(MINOR) Sec. 4.4, "coil 2 ≈ one third … same pattern on both springs".** On spring 2, coil 2 gives 6.7/14.9 = **0.45** of coil 1, not one third. *Fix:* "≈1/3 (spring 1) and ≈1/2 (spring 2); coil 3 ≈1/9 on both".
- **(MINOR)** The ±0.02 on 0.25 is really ±0.015. That is acceptable, but say it is propagated from the 6% scatter.

## 1. Alternative gamma estimators (MAJOR)

I re-fitted every run in four further ways:

- **(a) Hilbert envelope** of the fundamental band (0.6–1.4 f).
- **(b) Per-cycle rms** in sliding one-cycle windows.
- **(c) NLS harmonic fit.** A nonlinear least-squares fit of a three-harmonic damped series to the full waveform, with a separate decay rate for each harmonic.
- **(d) Physical-transduction NLS.** eps = (k0 + k1 z + k2 z^2 + k3 z^3) z-dot, with z = A0 e^{−gamma t} cos(theta).

| Spring (n=8), 10^-3 s^-1 | Table 1 (peak) | Hilbert fund. | per-cycle rms | NLS fund. | phys. model |
|---|---|---|---|---|---|
| 1 | 17.81 ± 0.58 | 15.05 ± 0.65 | 16.20 ± 0.60 | 15.17 ± 0.66 | 14.18 ± 0.66 |
| 2 | 20.95 ± 1.95 | 17.19 ± 1.18 | 18.80 ± 1.55 | 17.30 ± 1.22 | 15.35 ± 0.80 |

**The methods do not agree within errors.** The peak method is 15–20% higher in every run, an offset 10–15 times larger than the quoted fit SE. The run-to-run ranking is preserved (r = 0.88–1.00 with Table 1), so the null result is unaffected.

The cause is that the EMF is strongly anharmonic. The second-to-first harmonic ratio A2/A1 is 0.30–0.35 on spring 1 and 0.33–0.49 on spring 2. The second harmonic decays at about twice the fundamental rate (NLS ratio 1.92–1.97 on spring 1, 1.83–1.91 on spring 2), as expected for a term in kappa(z) linear in z, which contributes ∝ A^2. The peak of |eps| therefore falls faster than A. The statement in Sec. 3.4 that "the EMF envelope decays at the same rate as the displacement" is true only for constant kappa. This bias is also a plausible part of why gamma_track is "systematically lower": the spring-1 tracked mean is 13.6, which is close to the fundamental-band ≈15.

**Fit SE.** The residuals of the log-peak fit have lag-1 autocorrelation of 0.1–0.6. A block bootstrap (blocks of about 6 cycles) inflates the SE by a factor of 0.9–1.4 on spring 1 and 1.1–1.65 on spring 2. Both effects are small compared with the run-to-run scatter (3–9%) and the method systematic (≈17%).

*Fix:* adopt a fundamental-band estimator as primary, or report "gamma_peak", define it, and state the ≈17% model systematic. Recompute Q, which becomes ≈550 (spring 1) and ≈430 (spring 2). Replace "resolves the decay rate … to about 1%" with "statistical precision ≈1–2% per run; the systematic dependence on the envelope definition is ≈15–20%". Quote bootstrap errors in Table 1.

## 2. Non-exponential decay (MAJOR)

A quadratic term in the log-peak envelope is significant in 15 of the 16 coil-1 runs: curvature/sigma is 4–6 on spring 1 (7 of 8 runs) and 5–10 on spring 2. Its sign is always "decay slows as the amplitude falls".

Part of this is the harmonic artefact above, but it survives in the fundamental-only Hilbert envelope:

| Fundamental band | gamma early − gamma late (10^-3 s^-1) | Runs with early > late | Typical per-run significance |
|---|---|---|---|
| Spring 1 | 1.6 ± 1.7 | 7 of 8 | 2–4 sigma |
| Spring 2 | 2.9 ± 0.9 | 8 of 8 | 2–4 sigma |

The physical model with dA/dt = −(g0 + beta A)A prefers beta > 0 in every run on **both** springs, with similar beta.

Amplitude-dependent damping is therefore **not specific to spring 2**. Spring 1 simply lacks the across-run lever arm: the CV of eps_rms is 6% on spring 1 against 15% on spring 2. *Fix:* in the abstract and Sec. 4.5, replace "For spring 2 these losses were strongly amplitude-dependent" with "The decay is non-exponential on both springs (the rate falls by ≈10–20% between the first and second halves of each run); for spring 2, where release amplitude varied most, gamma also correlates with initial amplitude across runs." Rephrase "Spring 1 shows no such correlation" as "spring 1's amplitude range was too small to test this across runs". Note also that a single exponential fitted over a fixed fractional amplitude window is a model-dependent summary.

## 3. Significance of the c-test (MAJOR)

The authors' fit reproduces exactly (z = 3.67). That number is not robust:

| Variant (Table 1 gamma) | c (Ohm/s) | One-sided p | Gaussian-equivalent |
|---|---|---|---|
| Paper: sigma = s.d., Gaussian | −0.0094 ± 0.0077 | — | 3.7 sigma |
| Same, Student-t, 6 dof (sigma is *estimated* from the same 8 points) | | 0.0052 | **2.6 sigma** |
| Unweighted OLS (residual-scaled) | −0.0094 ± 0.0074 | 0.0043 | 2.6 sigma |
| Include 2.2 MOhm run | −0.0063 ± 0.0078 | 0.0073 | 2.4 sigma |
| 0-Ohm retakes averaged (n=7) | −0.0086 ± 0.0095 | 0.017 | 2.1 sigma |
| Drop retake 1 / drop retake 2 | −0.003 / −0.014 | 0.03 / 0.01 | 1.9 / 2.3 sigma |
| Permutation test (H0: c = c_pred) | | 0.014 | 2.2 sigma |
| Pairs bootstrap over runs | | 0.04 | 1.8 sigma |
| Fit-SE weights, absolute (inappropriate: chi^2/dof ≈ 7.6) | −0.0074 ± 0.0029 | | 9 sigma |

The other estimators give the same picture: z(t) is 2.5–2.8 sigma for Hilbert, rms and NLS.

Weighting by the run-to-run scatter is appropriate, because the fit SEs underestimate the scatter by about 2.8 times. However, with sigma estimated from n=8 the reference distribution is t with 6 dof, not Gaussian.

The leverage of 1/(Rc+R) lies almost entirely in the two 0-Ohm runs (0.066, against ≤0.02 elsewhere). The test is therefore effectively "the 0-Ohm mean against the rest", and the two 0-Ohm retakes themselves differ by 0.76e-3.

c_pred also has no uncertainty. It scales as 1/A^2, and A = 2.2 cm comes from blurred video. A 10% (20%) uncertainty in A lowers the result to 2.4 (2.1) sigma.

**Robust statement:** the data disfavour the closed-loop prediction at about 2–2.5 sigma (p ≈ 0.005–0.04 depending on choices). *Fix:* in the abstract, Sec. 4.3 and the Conclusion, replace "excludes … at the 3.7sigma level" with "is disfavoured (one-sided p ≈ 0.005, about 2.5sigma, for a t-distribution with 6 degrees of freedom; 2–2.5sigma under alternative weightings, resampling and a 10% uncertainty on A)". Add the uncertainty in A to c_pred. Note that the authors' own central argument is the 10^6 suppression. The c-test is a consistency check of a hypothesis that, by their own analysis, did not apply, so it should not be the headline significance.

## 4. Spring-2 correlation r = 0.98 (MINOR)

The correlation is robust:

- Spearman rho = 0.98.
- Leave-one-out r is 0.96–0.99.
- It survives every gamma estimator: r is 0.97–0.99, including the fundamental-only and physical-model fits.

Shared noise cannot drive it, because the SNR is about 60 dB. There is a systematic circularity, however. The peak bias in Sec. 1 grows with harmonic content, which grows with amplitude. That inflates the slope of gamma_peak against amplitude: the across-run s.d. is 1.95 for the peak method against 1.2 for the fundamental. A partly decoupled test, with amplitude from cycles 1–3 and gamma from the late half only, gives r = 0.80.

*Fix:* replace "almost perfectly" with "strongly". State that the correlation persists (r = 0.98) for a fundamental-band envelope, and r = 0.80 when gamma is fitted only to the second half of each run.

## 6. The 2.2 MOhm divider (MINOR, but it improves the paper)

The observed ratio is 0.245 ± 0.015, against 0.3125 predicted. The shortfall of 4.5 sigma would imply an input resistance of 0.71 MOhm. But the 2.2 MOhm run was released at a smaller amplitude: its harmonic ratio A2/A1 is 0.285, while all other runs lie in 0.32–0.35. A resistive divider leaves this ratio unchanged.

Over the 8 low-R runs, eps_rms is linearly related to A2/A1 with **r = 1.00**. Extrapolating to 0.285 predicts 13.1 mV before division, giving an amplitude-corrected ratio of **0.30**, consistent with 0.31. *Fix:* replace "plausibly due to additional loading … not characterised" with this amplitude correction, noting that it is a mild extrapolation. Also note that this run's lower amplitude is a caveat to calling its gamma "indistinguishable": given Sec. 2, a smaller release lowers gamma_peak.

## The 3 most important changes

1. **Soften "3.7 sigma" to about 2.5 sigma** (t-distribution with 6 dof, with A uncertainty propagated). Report the sensitivity to the treatment of the 0-Ohm retakes, and stop presenting this test as the headline result.
2. **Fix the decay-rate estimator.** The |eps|-peak envelope is biased high by 15–20% by harmonics that decay at twice the rate. Use a fundamental-band envelope, recompute gamma, Q and b throughout, and quote bootstrap errors plus the method systematic. Correct the claim that the EMF envelope decays at the displacement rate.
3. **Reframe the amplitude-dependence claim.** The decay is non-exponential on both springs; spring 2 differs only in having a wider spread of release amplitudes. Use the harmonic-ratio amplitude proxy to explain the 0.25 vs 0.31 divider result.
