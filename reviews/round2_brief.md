# Round 2: cross-examination brief

There are four referee reports from round 1 in this folder: `physics.md`, `stats.md`, `electronics.md` and `editor.md`. Read all four before you respond. Below are the points where the reports conflict, plus one new result from the corresponding author.

## New result: the DAQ timebase is slow by s = 1.261 ± 0.005

- **Firmware timing.** The firmware writes timestamps as i × 500 µs. It schedules each ADC read with `previousMicros += 10`. When one read plus the loop overhead takes longer than 10 µs, the loop runs at its maximum speed instead, so the real sample period is longer than assumed.
- **Mains hum.** Every run contains a narrow line at 63.07 ± 0.23 Hz, with its second harmonic at 126.2 Hz. The values come from the 11 runs where the line's SNR is above 50; the strongest is the 2.2 MΩ run, at SNR 821. Pakistan's grid runs at 50 Hz, so s = 63.07/50 = 1.261. Including the grid's tolerance of about ±1%, that is s = 1.26 ± 0.013, which means about 12.6 µs per ADC read. The script is `/root/paper/analysis/clock_cal.py` and the results are in `/root/paper/figs/clock.json`.

**Consequences, if the line really is 50 Hz mains:**
- **True frequencies:** 2.633/1.261 = 2.09 Hz for spring 1, and 2.333/1.261 = 1.85 Hz for spring 2.
- **The k–f contradiction is resolved if the two k labels are swapped.** The static k values predict 2.17 Hz (k = 19.438) and 2.00 Hz (k = 16.578). The measured 2.09 and 1.85 Hz are then 4% and 7.5% low, which is the expected direction for spring mass.
- **Decay rates and Q.** γ_true = γ_nominal / s, and Q is unchanged. The fundamental-band γ for spring 1 is about 15.0 ×10⁻³ s⁻¹, which becomes 11.9 after dividing by s. The phone-video decay rates (on the phone's own clock) were about 11.6–11.8 at R = 0 and at 3.18 and 9.61 kΩ. That is independent agreement.
- **The predicted c** in γ_em = c/R_loop picks up a factor 1/s through ω² (and γ is also divided by s), so the significance test does not change.
- **An alternative to rule out:** a 50 Hz servo PWM on the ESP32 release board would land at the same 63 Hz. Either way, the reference is 50 Hz.

## Conflicts to settle, answering only those relevant to your expertise

1. **Headline estimator.** Candidates: the Hilbert envelope of the fundamental band, the per-cycle rms, the NLLS harmonic fit, and the physical transduction model, which gave 14.2. Which one should the paper report as γ, and which go in a systematic band? Should γ be quoted at a reference amplitude, given that the decay is non-exponential on both springs?
2. **Significance of the excluded 1/R term.** The original claim was 3.7σ. Stats gives about 2.6σ under a t-distribution, and 1.8–2.4σ under bootstrap or leave-one-out. Physics gives 2.5–4.9σ depending on A. What exact sentence should the paper use? Should the paper rest instead on the argument that the current is suppressed by a factor of 10⁶?
3. **The 2.2 MΩ divider check.** Physics gets 0.287 and Stats gets 0.30 after amplitude correction, against 0.31 predicted. Electronics says this run is noise-contaminated: its offset is 10 mV and its noise is 1.4 mV rms. Should the paper keep it as supporting evidence, and with what wording?
4. **The amplitude-dependent mechanism.** Physics rejects quadratic air drag (about 2% of b) and suggests coupling to the cradle's pendulum or torsion mode, or friction. The photos show the magnet cradle a few cm from a steel retort rod (`/root/paper/figs/setup.jpg`), and the magnet hangs above the coil rather than passing through it. What should the paper claim?
5. **The clock correction itself.** Do you accept it, and how strongly should the paper state it? Should the paper assert that the k labels were swapped, or only say that the swap makes the data consistent and ask for a re-measurement?
6. **Corrected circuit for a teaching journal.** The options are a load resistor across the coil (simple, but it cannot test a shorted coil) or a transimpedance input (current measured directly, and the original series-R protocol works). Which goes in the figure, and which in the text?
7. **The DAQ design flaws:** the ±15 V rails and clamp risk, the truncating average, the per-run noise floor, and the 2.7% scale mismatch. How much of this belongs in a Physics Education paper (3000-word limit), and how much in the repository README? Does presenting the flaws honestly weaken the paper?
8. **The editor's proposed cuts.** These are the video-tracking material, the coil-comparison table and the dipole equation. Note that the video tracking is now valuable as an independent clock check. Do you agree with each cut?

Also note: the paper is being reformatted to APA 7 (apa7 class, biblatex-apa) at the authors' request.
