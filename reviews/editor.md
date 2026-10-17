# Editor's report: "Why changing the load resistance did not change the damping..."

**Decision: publishable after major revision. The physics is sound. The packaging is not ready yet.**

## 1. Venue check (October 2026)

| Venue | Fit | Type / length | Fees | Student authors |
|---|---|---|---|---|
| **Physics Education (IOP)** | Best fit. Audience is school and intro-undergraduate teachers, and a classroom-relevant "why your demo fails" is exactly their kind of paper | Paper, max 3000 words (about 5 pp). Frontline, max 1000 words | No submission fee. Subscription route is free. Gold OA APC is £2655/$3665, with LMIC discounts | No restriction. Ethics statement only if there are human participants. Circuit diagrams must follow BS 3939. Journal warns against papers that simply swap an Arduino or microcontroller in for a standard sensor |
| **European Journal of Physics (IOP)** | Good. Welcomes "student projects" and "new laboratory exercises... relatively inexpensive equipment", aimed at university level | Paper, typically up to 4000 words. Cover letter mandatory | Same as Physics Education (free on subscription route, $3665 for OA) | No restriction. Same Arduino caveat |
| **Journal of Emerging Investigators** | Acceptable fallback. Scope since March 2026 covers hypothesis-driven experimental physical sciences | Must be hypothesis-driven, on the JEI Word template. Mentor must be last author and an adult submits | Reported as free to publish. A $35 submission fee was introduced in Feb 2024, so check current status | Grades 6-12 at first submission. Typical time to publication is 7-8 months |
| AJP / The Physics Teacher | AJP: "Instructional Laboratories" fits, but it is a stretch because the paper's main result is a design error, not a technique. TPT: max 3000 words with each figure counting as 200, no abstract, endnotes | No fees listed | -- |
| Journal of Student Research | Low selectivity. Has an APC and service fee, a separate high-school portal, advisor required, title max 100 characters | -- | -- |
| HardwareX / J. Open Hardware | Only for a separate DAQ paper. HardwareX APC up to $500, open hardware licence required. JOH is diamond OA (free) | -- | -- |
| arXiv physics.ed-ph | Since 21 Jan 2026, an institutional email no longer qualifies a new author for endorsement. A personal endorser is needed: ask Dr Hoodbhoy or Dr Manzoor if they have recent arXiv papers, or have them submit | -- | -- |

IOP-wide rules that apply to both IOP journals:
- **AI disclosure:** required when AI use materially contributed. It must be a separate statement inside the Acknowledgements, plus a description in Methods if AI was used in the analysis.
- **Data availability:** strongly encouraged. Use one of five standard wordings in its own section between the Acknowledgements and the References, with a DOI.

Sources: [Phys. Educ. about](https://publishingsupport.iopscience.iop.org/journals/physics-education/about-physics-education/), [EJP about](https://publishingsupport.iopscience.iop.org/journals/european-journal-of-physics/about-european-journal-physics/), [IOP AI policy](https://publishingsupport.iopscience.iop.org/questions/generative-ai-tools/), [IOP data statement](https://publishingsupport.iopscience.iop.org/?p=1907), [JEI checklist](https://www.emerginginvestigators.org/submissions/checklist), [JEI guide (Polygence)](https://www.polygence.org/blog/guide-publishing-research-journal-emerging-investigators), [JEI fee notice](https://emerginginvestigators.org/blog/new-35-submission-fee-starts-on-feb-19-2024), [AJP editorial policy](https://aapt.org/Publications/AJP/edpolicy.cfm), [TPT contributors](https://www.aapt.org/Publications/tptauthors.cfm), [JSR authors](https://jsr.org/index.php/path/authors), [HardwareX scope](https://shop.elsevier.com/journals/hardwarex/2468-0672), [HardwareX DOAJ](https://doaj.org/toc/2468-0672), [JOH](https://en.wikipedia.org/wiki/Journal_of_Open_Hardware), [arXiv endorsement](https://info.arxiv.org/help/endorsement.html), [2026 endorsement change](https://casrai.org/news/arxiv-2026-endorsement-english-ai-policy-changes).

## 2. Manuscript review

**Title.** At 33 words it is far too long, and it buries the lesson. Options:
1. *Measuring the voltage is not letting the current flow: a null result in electromagnetic damping*
2. *Why a coil connected to a voltmeter does not brake a magnet*
3. *An electromagnetic damping experiment that measured no electromagnetic damping, and how to fix it*

**Abstract.** It is 258 words and packed with numbers (gain, the c fit, r = 0.98). Proposed version (180 words):

> A magnet oscillating on a spring above a coil is a standard demonstration of electromagnetic braking, and the usual check that the braking is electromagnetic is to vary the coil-circuit resistance, since the damping should scale as 1/R. We attempted this check using a US$43 data-acquisition system built around a Raspberry Pi Pico (input noise ±34 µV). Across series resistances from 15 Ω to 2.2 MΩ the decay rate did not change: γ = (17.8 ± 0.6) × 10⁻³ s⁻¹ (Q ≈ 465, n = 8). From the measured EMF alone, a loop closed through the coil and resistor should have shown a 7% effect, which a fit excludes. The cause was the measurement circuit: the coil was closed only through the amplifier's 1 MΩ bias resistor, so almost no braking current flowed. A 2.2 MΩ run, which divides the recorded EMF as this explanation predicts, supports the diagnosis. The damping we measured was mechanical and, for one spring, strongly amplitude-dependent. We give a corrected circuit and a checklist for instructors: measuring a coil's voltage is not the same as letting current flow in it.

**Story and ordering.** The introduction already frames this well ("measuring the voltage on a coil is not the same as letting current flow in it"). However, the reader only learns why the result is null in Section 5, after three pages of results. For a teaching journal, the diagnosis should come before the details:
- Move the R5 explanation into the Results, straight after Fig. 3.
- Put the corrected circuit in its own short section.
- Cut the contributions list from five items to three: the diagnosis, the corrected design, and the DAQ.
- Present the DAQ as an enabler, not a headline, to avoid the IOP Arduino objection.

**Cut (needed to get under the 3000-word Physics Education limit):**
- The video-tracking column in Table 1 and the "Video tracking" paragraph. The authors themselves call this data qualitative.
- The "Spring comparison" paragraph that rebuts the internship report. A journal reader has never seen that report, so drop all references to it.
- The point-dipole flux equation. It is never used quantitatively.
- The Butterworth 1930 reference.
- The DAQ bullet details (supply converter, clamp diodes). Move these to supplementary material or the repository.
- Possibly the coil comparison (Table 2): coils 2 and 3 have unknown turns and resistances, so the table is not interpretable.

**Missing:**
1. **A simplified signal-chain block diagram** (coil, R5, buffer amplifier, ADC) to replace or sit beside the full KiCad sheet. At print size the KiCad sheet is unreadable (I checked p. 3 at 70 dpi). R5 must be visibly highlighted.
2. **A figure of the corrected circuit**: a side-by-side "as built vs. corrected" pair is the single most useful figure the paper could have. Physics Education requires BS 3939 symbols.
3. **A photo of the coil** and the magnet-coil geometry, with z₀ and a labelled. The current photo says "coil not shown".
4. **A boxed "Lessons for instructors"** with 3-4 bullets: check the loop is closed; estimate I = ε/R_loop before running; include a shorted-coil vs. open-coil control; check that the expected γ_em exceeds the run-to-run scatter.
5. **An uncertainty on the predicted c.** c ∝ 1/A², and A comes from motion-blurred video with no error bar, so a 15% error in A gives about 30% in c. The "3.7σ" claim currently ignores this. Either propagate σ_A or soften the claim to "excluded". The central conclusion does not depend on it, because it rests on the 10⁶ suppression.
6. **An honest statement on the 2.2 MΩ divider check.** The predicted ratio is 0.31 and the observed one is 0.25 ± 0.02, which is roughly 3σ apart. Calling this "order of magnitude agrees" understates the discrepancy. Either measure the input impedance or say plainly that it is unexplained.

**Consistency.**
- The k values give f = 2.00 and 2.17 Hz, but the measured frequencies are 2.63 and 2.33 Hz, in the opposite order. That points to swapped labels or a wrong k or mass. **This must be fixed, not flagged.** As it stands, a referee will distrust every other number.
- The firmware default sampling rate (1 kS/s) does not match the 0.5 ms data spacing.
- Coil table rows say "–" for predictions that the text describes.
- The author-contribution line credits H.T.M. with the "formal analysis", while the AI statement says Claude reanalysed the data. Make these two statements agree and describe the AI use in the Methods (IOP rule).

**Red [todo] items (10).** These are fatal if any survive submission: k method, magnet dimensions, coil specifications, block size, tracking tool, σ_A, coil-2/3 resistances, the k-f inconsistency, the Zenodo DOI, and the author contributions. Only switch `\showtodosfalse` once all of them are filled in.

**Figures.**
- Fig. 2: the envelope legend collides with the top envelope line. The bottom panel leaves white space. The raw (grey) trace is invisible under the filtered trace, so either drop it or offset it.
- Fig. 3: mention the log axis in the caption. Add a flat "as built" prediction line, so the reader sees both models.
- Fig. 4 is fine. Units on all axes are good.

**Tone.** Candid, careful and appropriately modest. That is the paper's main asset. Keep "no braking current ever flowed".

**References (11).** Thin for a teaching journal. Before submission, add:
- recent Physics Education / EJP / AJP papers on magnet-spring-coil damping, especially low-cost or microcontroller versions;
- a source on input impedance and loading in measurement (any electronics text, e.g. Horowitz & Hill);
- a source on nonlinear and air-drag damping in spring oscillators, to support Section 4.5.

Physics Education referees will expect a search of Physics Education's own back catalogue. Verify every citation yourselves, and do not cite from memory.

## 3. Recommendation

**Submit to Physics Education (IOP) as a Paper, using the free subscription route.** Fallback: EJP, which allows more words. For a guaranteed student venue, use JEI, recast around the hypothesis "γ ∝ 1/R_loop". Publish the DAQ separately later in the *Journal of Open Hardware* (free) once it has its own validation.

**The 3 changes that matter most:**
1. **Resolve every [todo]**, above all the k-f contradiction and σ_A, which affects the 3.7σ claim.
2. **Add the "as built vs. corrected" circuit figure and a "Lessons for instructors" box.** These are what turn a failure into a contribution.
3. **Shorten to under 3000 words with a short title and the abstract above**, and cut the video tracking and all internship-report material.
