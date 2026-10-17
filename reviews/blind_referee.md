# Blind referee report: "No Current, No Braking" (Physics Education)

Recommendation: **major revision**. The physics diagnosis (Lesson 1) is sound and the 2.2 MΩ divider test is persuasive. The issues below are the ones that block acceptance.

1. **The 10^6 suppression figure is wrong (l.217, l.221).** The current is suppressed by R5/Rc = 1 MΩ/15.2 Ω ≈ 6.6×10^4, not 10^6. Only γ_em/γ ≈ 2.5×10^-6 is of order 10^-6.
   - Limitations: `a $10^6$-fold suppression of the current` -> `a roughly $7\times10^4$-fold ($R_5/R_c$) suppression of the current`
   - Conclusion: `suppressed by about $10^6$` -> `suppressed by a factor of about $7\times10^4$, to about $10^{-6}$ of the total damping`

2. **"Excluded at about 3σ" overstates the evidence (abstract, l.140).** The text's own amplitude range (1.8–3.0 cm, about ±25%) gives 2.3σ, and the permutation test gives about 2.75σ. The text never says what was permuted. The fitted c is negative at about 2σ, which is unphysical and points to unmodelled systematics. Abstract: `which the data exclude at about $3\sigma$` -> `which the data disfavour at 2.3--3$\sigma$, depending on the uncertainty in amplitude`. The abstract should also say "spring 1" and that ±0.5 is a standard deviation.

3. **The clock direction is inverted (l.173).** The assumed spacing is too *short*, so the assumed clock runs slow and frequencies appear too high. `the firmware's assumed timebase runs fast by` -> `the firmware underestimates the sample spacing by a factor`

4. **Lesson 2: the cause is asserted, and alternatives are not ruled out.** The 12.6 µs per read is inferred from s, not measured (see the TODO). `The cause is in the firmware.` -> `The most likely cause is in the firmware.` Add one sentence on why the line is mains-derived and not a servo PWM or lighting line, a supply ripple, or an alias: the exact 2:1 harmonic, a pickup amplitude that scales with input impedance, and stability across runs. Add the cheapest direct check: 60 000 points should span 37.9 s, not 30 s, and an 8 s difference can be timed from the phone video.

5. **The video check is internally inconsistent (l.185).** A ratio of 1.06 implies s = 1.261/1.06 = 1.19 (or 1.34), not 1.23. Explain the derivation. Also explain why the decay rates (±6%) are used rather than the video oscillation frequency, which over 70 cycles would give s to better than 1%.

6. **The spring-constant check is post hoc, not independent.** It works only after an unverified label swap, leaves gaps of 4% and 7% that differ in size, and taken at face value would imply s ≈ 1.31–1.35. The pre-correction conflict (+17–21%) is never stated. The Discussion says the clock error was found through the spring constants, while Lesson 2 says it was found through the hum. Abstract: `and removes an apparent conflict with the measured spring constants` -> `and brings the frequencies closer to static-$k$ predictions, if two spring labels were swapped`. Soften the Conclusion in the same way.

7. **The amplitude-dependence claim is weaker than stated.** The legend of Figure 7 shows r = −0.40 for spring 1, the opposite sign to spring 2, and the text omits it. In final_stats.json, the early (15.6) and late (13.2) rates both exceed the full-run γ (11.9). That suggests a different estimator, likely a peak-based one, which the paper says is biased by faster-decaying harmonics that are larger early in each run. Recompute the two halves with the fundamental-envelope estimator, report r for spring 1, and soften the abstract.

8. **Unresolved red TODOs** cover the magnet size, coil turns and radius, equilibrium height, the uncertainty in k, ORCID, DOI and author contributions. Teachers cannot reproduce the experiment without the geometry. Resolve all of them before submission.

9. **APA and journal-style problems.**
   - Figure 4 is cited in Theory before Figures 1–3, so the figures are not numbered in order of first mention. Delete `, as seen in Figure~\ref{fig:trace}` and place the trace float before Figure 3.
   - Author Contributions, Acknowledgments and Data Availability belong in the author note, not in Level 1 sections.
   - Check whether Physics Education requires IOP Harvard style instead of APA.

10. **Readability for teachers.**
    - Gloss "Hilbert envelope", "block bootstrap", "permutation test" and "transimpedance" in one clause each.
    - Define s on first use.
    - The "low resistances" bullet (l.157, "but not for a parallel one") is unclear, and it is weak as evidence. Explain it or delete it.
