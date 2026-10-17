# Referee report: theory and physical interpretation

**Manuscript:** "Why changing the load resistance did not change the damping…" (main.tex)
**Focus:** derivations, the physical interpretation and the alternative explanations
**Checks:** I reran the paper's own pipeline (`fit_decay.py`, `make_figs.py`) on the raw DAQ files and added these checks: positive and negative peaks fitted separately, a lock-in (demodulated) envelope of the fundamental, early-half versus late-half decay rates, and harmonic ratios. My numbers for every quoted value in Table 1 and stats.json agree with the paper's.

## Summary
The central result is sound and useful for teaching. The coil was terminated only by R5 (1 MΩ), so no measurable braking current flowed, and the data rule out a loop closed through R_c+R_ext. The energy-method formula is correct. The weak points are these:
- the decay-rate estimator is biased by the shape of the EMF waveform;
- the quoted significance ignores the uncertainty in A;
- the 2.2 MΩ run is under-analysed;
- the physical story for the amplitude-dependent damping is not supported quantitatively.

## MAJOR

**M1. Peak-picking γ is not the displacement decay rate (Sec. 3.4, Analysis paragraph).** The paper says that "because ε ∝ ż for a fixed coupling profile, the EMF envelope decays at the same rate as the displacement". The profile is not fixed in the sense the paper needs. Because κ(z) varies along the stroke, ε = κ(z)ż contains a strong second harmonic. In the first 4 s, H2/H1 = 0.36–0.41 for spring 1 and 0.36–0.50 for spring 2. That ratio scales with amplitude: across runs it correlates with ε_rms at r = 0.99 (spring 1) and r = 0.996 (spring 2), and within each run it falls from about 0.38 to about 0.27.

The peak of |sin θ + r sin 2θ| grows with r, with d ln(peak)/d ln r ≈ 0.27 at r = 0.4. The peak envelope therefore decays roughly 20–25% faster than A. Demodulating the fundamental gives:
- spring 1: γ = (15.0 ± 0.7)×10⁻³ s⁻¹, against the reported 17.8;
- spring 2: γ = (17.0 ± 1.1)×10⁻³ s⁻¹, against the reported 20.9.

The video-tracking rates in Table 1 (mostly 11–17) are systematically lower than the peak-based values in the same way. The null result survives, because the bias is the same at every R. However, the absolute γ, Q and b, and the "7%" figure, are all affected.

*Fix:* Fit the envelope of the fundamental, either by lock-in demodulation at f or by fitting a + b cos + c sin to each cycle. Alternatively, fit positive and negative peaks after correcting for the harmonic content. Replace the sentence with: "Because κ varies along the stroke, the EMF contains harmonics whose relative size scales with amplitude, so the peak envelope of |ε| does not decay at exactly the rate of z. We therefore fit the envelope of the fundamental component." Then recompute Table 1, Q, b and γ_em/γ.

**M2. The envelope is not exponential, in either spring (Secs. 2.1 and 3.2).** With the fundamental-envelope estimator, the early half of each run decays 8–15% faster than the late half, for spring 1 as well as spring 2. Binned local rates for spring 2 rise from about 17×10⁻³ s⁻¹ at 12 mV to about 28×10⁻³ s⁻¹ at 24 mV. A single γ per run is therefore an amplitude-weighted average. The statement "Spring 1 shows no such correlation" is true only across runs, because spring 1's release amplitudes span just ±8%. It is not true within runs.

*Fix:* Report γ at a fixed reference amplitude, either interpolated or taken from a fit of γ(A) = γ₀ + γ₁A. Base the R-test (Sec. 3.3) on that. State that both springs show amplitude-dependent loss.

**M3. The 3.7σ significance omits the uncertainty in A (Sec. 3.3).** The prediction scales as c_pred ∝ 1/A², and A = 2.2 cm comes from blurred video ("[uncertainty in A]" is still a todo). Varying A from 1.8 to 3.0 cm moves c_pred from 0.028 to 0.010 Ω s⁻¹, so the exclusion moves from 4.9σ to 2.5σ.

The energy formula itself, γ_em = ⟨ε²⟩/(R m ω²A²), is correct. It follows from ⟨P⟩ = ⟨ε²⟩/R and E = ½mω²A² = m⟨ż²⟩, and it already averages the asymmetric κ(z)² correctly. It needs A at the same epoch as ⟨ε²⟩, however, and the paper pairs a run-averaged ε_rms (which varies by ±8%) with a single A.

*Fix:* Propagate δA into c_pred and quote the range ("2.5–4.9σ for A = 1.8–3.0 cm"). Better, measure A per run (for example a ruler in frame, or the release height). Note that A cancels in γ_em × R/⟨ε²⟩ only if κ is calibrated, which could be done in a single run by measuring ε at a known ż.

**M4. The 2.2 MΩ divider test is under-analysed (Sec. 5, para 2).** The observed ratio 0.245 against the predicted 0.3125 is a 3.5σ discrepancy, given the 6% scatter of the other runs. The paper calls this "order of magnitude agreement", which undersells the test.

This run's H2/H1 is 0.324, against 0.380 ± 0.018 for the other spring-1 runs. Since H2/H1 tracks amplitude, this release was about 15% smaller. Correcting for that gives a ratio of about 0.287, within about 1.4σ of the prediction. The remainder could come from R5 and R_ext tolerances. An uncorrected 0.245 would instead imply a shunt of about 0.71 MΩ.

The low-R runs also settle the wiring question raised for review. If R_ext had been placed across the coil, the 33.6 Ω run would read about 0.69 of normal. It reads 0.96. So R_ext was in series, as stated.

*Fix:* Add the amplitude correction and state both arguments. Measure R5 and the 2.2 MΩ resistor in situ. Ideally, add runs at 470 kΩ and 1 MΩ to show the divider curve V/ε = R5/(R5+R_c+R_ext).

**M5. The interpretation of the amplitude-dependent damping (Sec. 3.5).** The correlation is not a peak-picking artifact: the fundamental-envelope γ still gives r = 0.97 for spring 2. But "quadratic air drag" is quantitatively implausible. For a disc of area about 5 cm², C_d ≈ 1 and v_max ≈ ωA ≈ 0.36 m s⁻¹, the equivalent linear coefficient is (8/3π)·½ρC_dSv_max ≈ 1×10⁻⁴ kg s⁻¹. That is about 2% of b = 3.7×10⁻³ kg s⁻¹, far too small to change γ by 50%. The reported beating instead points to a Wilberforce-type pendulum or torsional exchange in the string cradle (Berg & Marshall, Am. J. Phys. 59, 32 (1991)). Such an exchange produces apparent extra decay over a 30 s window, with a size that depends on initial conditions.

*Fix:* Change the text to "consistent with transfer of energy to a swinging or torsional mode of the cradle, or with amplitude-dependent friction at the string attachments; quadratic air drag on the magnet is estimated to be ≲ few % of b." Fit longer records (60 s) to look for the beat period, and quote the cradle dimensions.

## MINOR

**m1. Sec. 5, "unresolved inconsistency".** With m = 105 g, the measured frequencies imply k_eff = 28.6 and 22.9 N m⁻¹. Going the other way, the stated k values imply m_eff = 61 and 89 g, or 71 and 76 g if the spring labels are swapped. Possible explanations:
- **Spring mass:** it adds about m_s/3 and lowers f, so it makes the discrepancy worse.
- **Dynamic versus static k:** for a helical spring far below its surge frequency the two are equal, so this cannot explain a 70% difference.
- **Pendulum mode:** a 2.63 Hz pendulum would need L ≈ 3.6 cm, which is implausible.
- **Remaining candidates:** a label swap combined with an error in k or m. For example, k may have been computed as mg/x using a length that includes initial tension, a mass in the wrong unit, or a different hanging configuration.

*Fix:* Re-weigh the oscillating mass and remeasure k from the slope of a load–extension plot with ≥ 5 loads. Cross-check f against the video tracks. Until this is done, state: "The measured frequencies are inconsistent with the stated k and m by ~30% in effective mass; b = 2mγ values carry this uncertainty." No conclusion about the null result depends on this.

**m2. Eq. (4) and below.** Write "Φ is the flux of a point dipole through a single coaxial loop; for a multilayer coil κ = Σᵢ dΦᵢ/dz over turns." The point-dipole model is poor for stacked discs at z ~ a. The extremum at z = ±a/2 is correct.

**m3. Eq. (5).** The force is F = −κI = −κ²ż/R_loop, so b_em(z) is a position-dependent coefficient. State that the effective rate is γ_em = ⟨κ²ż²⟩/(2mR⟨ż²⟩), which is what Eq. (6) measures. State the self-inductance (L of order mH, so ωL/R ≲ 10⁻² even for harmonics) rather than assuming it.

**m4. Alternative loss channels.** These should be discussed briefly, and none affects the conclusion:
- **Eddy currents in the aluminium claw, clamps and stand:** these are independent of R and belong in γ_mech. The 2.2 MΩ run cannot separate them. A run with the claw removed or retracted, or with the coil absent, would.
- **Coil self-capacitance:** at 10–100 pF it has an impedance of about 10⁹ Ω at 2.6 Hz, so it is negligible.
- **OPA2134 input bias current:** pA level, negligible.
- **Ground loops:** the coil is floating and referenced to the U5A output, with an isolated supply, so there is no low-impedance return path.

**m5. Secs. 3.3 and 5.** "b_em ≈ 10⁻⁶ of total" is correct (c/1 MΩ ≈ 1.9×10⁻⁸ s⁻¹). Add that the coil-1 "7%" becomes about 8% with the corrected γ_mech (M1), and 5–10% over the range of A (M3).

**m6. Corrected circuit (Sec. 5).** Placing R_load across the coil is correct. Add that the R_load = 0 case can be measured as the voltage across a small sense resistor (≈ 1 Ω) with a higher gain.

**m7. Citations.** The cited AJP/EJP papers appear genuine. I suggest adding:
- Berg & Marshall (above), for mode coupling;
- W. M. Saslow, "Maxwell's theory of eddy currents in thin conducting sheets…", Am. J. Phys. 60, 693 (1992), for the eddy-current background.

For the spring-mass correction, a reference such as Galloni & Kohen, Am. J. Phys. 47, 1076 (1979) may be suitable, but I am not certain of its details and the authors must verify it before citing.

## Verdict: **Major revision**

The three changes that matter most:
1. **Replace the peak-picking γ with a fundamental-envelope (or harmonic-corrected) estimator**, report γ at a reference amplitude, and acknowledge the non-exponential decay in both springs (M1, M2).
2. **Propagate the uncertainty in A into c_pred and the 3.7σ claim**, and amplitude-correct the 2.2 MΩ divider test so it becomes quantitative evidence (M3, M4).
3. **Resolve the k/m/f inconsistency by remeasurement**, and replace the air-drag explanation with a quantitatively supported one (mode coupling or suspension friction) (m1, M5).
