# Round 2: handling editor

## (a) Outline (Physics Education, 3000 words)

Two lessons: the loop was never closed, and the clock was never checked. The headline is the 10⁶ suppression; the c-test only supports it.

| Section | Words |
|---|---|
| 1. Introduction | 280 |
| 2. Theory: γ_em from the measured EMF | 280 |
| 3. Apparatus and DAQ, plus limitations | 420 |
| 4. Result: damping ignores R | 380 |
| 5. Lesson 1: open loop | 300 |
| 6. Lesson 2: clock | 320 |
| 7. Mechanical damping | 200 |
| 8. Corrected circuit | 200 |
| Instructor box | 110 |
| 9. Conclusion | 110 |
| Captions | 220 |
| **Total** | **2820** |

**APA 7** is allowed but gains nothing. IOP accepts any format ("format your paper in the way that you choose"; [article format](https://publishingsupport.iopscience.iop.org/questions/article-format/)) and restyles references into Harvard or Vancouver "whatever format you submit them in" ([references](https://publishingsupport.iopscience.iop.org/questions/references/)). If APA stays, use `floatsintext`: `man` mode moves figures to the end, but IOP wants them in the text.

## (b) Title and abstract

**Title:** *No current, no braking: two instrument lessons from a magnet–coil damping experiment*

> A magnet oscillating on a spring above a coil is a standard demonstration of electromagnetic braking, usually checked by showing that damping scales as 1/R with coil-circuit resistance. We attempted this test with a US$43 Raspberry Pi Pico data-acquisition system. Across series resistances from 15 Ω to 2.2 MΩ the decay rate did not change: γ = [γ₁] s⁻¹ (n = 8). The coil was closed only through the amplifier's 1 MΩ bias resistor, so the braking current was about 16 nA and electromagnetic damping about 10⁻⁶ of the total. A loop closed through the coil would have given a [7]% effect, which the data disfavour at about [2.5]σ. A second hidden error was the clock: mains hum recorded at 63 Hz rather than 50 Hz showed that sampling ran [26]% slow. The correction agrees with independent video timing and resolves an apparent conflict with the spring constants. The remaining damping is mechanical and amplitude-dependent. We give a corrected circuit and five checks for instructors.

## (c) Conflicts

**Conflict 8 (cuts).**
- **Video tracking: I concede; keep it.** On the phone's own clock it gives 11.6–11.8 against the corrected 11.9, so it independently confirms Lesson 2. Keep one column and one sentence, and drop the internship report.
- **Coil table: cut.** Replace it with one sentence: coil 2 gives ≈1/3 (spring 1) and ≈1/2 (spring 2), coil 3 gives ≈1/9.
- **Dipole equation: cut.**

**Conflict 7 (DAQ flaws).**
- **In the paper:** the timebase, the 2.7% scale mismatch (it moves c by 5%), the integer truncation (delete "oversampling"), the median noise (≈48 µV, range 29–94 µV), and one sentence on the ±15 V clamp risk.
- **In the README:** the clamp analysis, the DNL erratum, R3 (34k vs 35k), the power tree, and the transimpedance details.

Stating the flaws openly is the contribution, not a weakness.

## (d) Lessons for instructors

- Before blaming the physics, compute the allowed current I = ε/R_loop.
- A high-impedance input on a coil measures the EMF but brakes nothing, so give the braking current a known low-resistance path.
- Do not trust a microcontroller's assumed sample rate: the 50 Hz hum already in your data is a free clock.
- Run an on/off control (open versus shorted coil), and check that the predicted effect exceeds your run-to-run scatter before collecting a full data set.
- Compare the early and late halves of each decay, because one exponential fit hides amplitude-dependent loss.

## (e) Where I disagree

1. **Electronics (clock).** I accept the mains calibration, but before submission the authors should also do one direct timing check (a GPIO toggle against a scope) and re-measure k. The label swap is then a fact, not a hypothesis.
2. **Physics.** Do not quote the range "2.5–4.9σ". Use the Stats figure (≈2.5σ, t-distribution with 6 dof, uncertainty in A included).
3. **Estimator.** The headline value should be the clock-corrected Hilbert fundamental envelope; the physical-model and per-cycle rms values bound the systematic. A reference-amplitude γ is overkill here.
4. **Electronics (figure).** Show R_load across the coil, which teachers can build; give the transimpedance input one paragraph.
5. **Physics (amplitude mechanism).** Name no single cause: the nearby steel rod joins cradle modes and string friction as candidates. Claim "mechanical, amplitude-dependent, unidentified."
6. **Myself.** Wrong to cut video in round 1.
