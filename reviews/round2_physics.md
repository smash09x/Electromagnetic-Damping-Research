# Round 2: physics referee

## (c) Stress test of s = 1.261

**Mains?** Probably. Across runs the hum scatters by 0.4% (62.6–63.5 Hz), while the spring frequency scatters by only 0.017%. The clock is stable and the source wanders: grid, not crystal-timed servo PWM. The uncertainty is the grid's: **s = 1.26 ± 0.01**.

**Swap holds; spring mass fails.**
- The ratio f₁/f₂ = 1.118 does not depend on s. Swapped labels predict 1.083, so the swap is needed regardless of the clock.
- With s = 1.261, the swapped effective masses are 113.5 g and 121.1 g, implying spring masses of **26 g and 48 g**.
- The springs in `setup.jpg` and the June photos (≈1 cm diameter, 30–40 thin turns) weigh roughly 3–8 g. Likelier: initial tension in close-wound springs makes mg/x overestimate k.

**Video agreement survives only loosely.**
- The spring-1 tracks span 11.6–17.3 (mean 13.6 ± 1.0); the brief quoted only the three lowest.
- Against the fundamental-band γ, the pooled best-fit s is **1.21 (95% CI 1.08–1.36)**. Consistent with 1.26, not a confirmation (against the peak estimator: 1.46).
- Counting video cycles would fix s to 0.1%.

## (a) Final positions

1. **Estimator.** Headline γ: fundamental-band Hilbert envelope over a fixed amplitude window (e.g. 20→10 mV), divided by s. NLS and physical model: ≈7% systematic band. *"Because κ(z) varies along the stroke, the EMF contains amplitude-dependent harmonics; we fit the fundamental-band envelope over a fixed amplitude window."*
2. **Significance.** The brief is wrong here: c_pred ∝ ω² gains s², while the fitted c falls by 1/s. Using the fundamental-band γ with t₆, 2.5σ at the nominal clock becomes 3.3σ (2.9–3.8σ for A ± 20%). *"With the coil closed only through R5, I ≈ 16 nA and γ_em ≈ 10⁻⁶γ. As a consistency check, a loop closed through R_c+R_ext is disfavoured (one-sided p ≈ 0.005, t-distribution, 6 dof, nominal timing)."*
3. **The 2.2 MΩ run.** Keep it. *"Corrected for its smaller release amplitude (from harmonic content), the attenuation is 0.29–0.30, consistent with the predicted 0.31 within resistor tolerances."*
4. **Mechanism.** *"The decay is non-exponential on both springs. Candidates are hysteresis/eddy losses in the steel stand a few cm from the magnet (Rayleigh hysteresis gives γ ≈ γ₀ + βA, as observed) and energy exchange with the cradle's pendulum mode; air drag (≈2% of b) is too small."* Control: move the rod.
5. **Clock.** Present it as inferred, and do not assert the swap. *"The mains line implies a timebase slow by s = 1.26 ± 0.01, consistent with the video; with swapped spring labels the frequencies then lie 4–8% below static-k predictions, more than spring mass explains. k and the timebase will be re-measured."*
8. **Editor's cuts.**
   - Video: keep it, in two sentences, as the clock-independent check.
   - Coil table: cut it.
   - Dipole equation: keep it, since it underpins the harmonic bias and the z ≈ a/2 advice.

## (b) Disagreements

- **Brief:** significance is not s-invariant; video "agreement" depends on track selection.
- **Electronics:** the 2.2 MΩ "noise" (1.25 mV raw) is 63 Hz hum, and only 8 µV rms after the 20 Hz filter. ε_rms = 4.0 mV is clean; the hum corroborates the high-impedance node.
- **Editor:** keep the video and the dipole equation (point 8).
- **Stats:** agreed; t₆ accepted.

## (d) Top 3

1. Measure the timebase directly (video cycle count or GPIO timing); re-measure k (slope, with initial tension) and spring masses.
2. Use the fundamental-band γ in a fixed amplitude window, and state that the decay is non-exponential on both springs, with the steel-stand and pendulum candidates.
3. Lead with the 10⁶ suppression; c-test with t₆, σ_A, s² scaling; amplitude-corrected divider.
