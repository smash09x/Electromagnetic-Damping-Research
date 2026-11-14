# Coil-circuit impedance and sampling-clock errors in a microcontroller-based electromagnetic damping experiment

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23448903.svg)](https://doi.org/10.5281/zenodo.23448903)

Data and code for a study of electromagnetic damping in a magnet–spring oscillator. It set out to test whether
the damping falls as 1/R when resistance is added to the coil circuit, using a low-cost Raspberry Pi Pico
data-acquisition system (DAQ). The coil circuit turned out to be closed only through the amplifier's 1 MΩ bias
resistor, so the 1/R hypothesis could not be tested; the repository documents that diagnosis, a second error in the
DAQ's timebase, and the mechanical damping that was actually measured.

Author: Hassan Tariq Malik ([ORCID 0009-0001-3749-090X](https://orcid.org/0009-0001-3749-090X))  
Contributors: Umer Farooq (DAQ hardware, firmware and schematics; data collection), Hardaysh Kumar (video tracking, live serial plotter)  
The Black Hole Science Lab, Islamabad  
Research supervisors: M. Sanan Qureshi, Dr Sadia Manzoor (COMSATS University Islamabad), Dr Pervez Hoodbhoy

## Quick start

Requires Python ≥ 3.11 (tested on 3.13).

```bash
pip install -r Code/requirements.txt
cd Code/Analysis
python run_all.py        # or python3, depending on your system
```

`run_all.py` runs every analysis script in order on the raw DAQ dumps in `Data/Raw/`. It writes the
results, the figures, a combined workbook (`Overall_Results.xlsx`) and each script's printed output to
`Data/Results/`. Later scripts read intermediate files from `Code/Analysis/out/`, so run
`run_all.py` rather than single scripts. The only step it does not run is `check_video_clocks.py`, which
needs the original videos and FFmpeg; its outputs (`Data/Video/frame_times/`) are committed.

## What is measured

A plated NdFeB cup magnet with a disc on its face (105 g oscillating mass) hangs on a spring and oscillates about 6 cm above a hand-wound coil.
The DAQ amplifies the coil's EMF 35× and records it at a nominal 2 kS/s.

- **Outcome:** the decay rate γ of the oscillation. It is fitted to the Hilbert envelope of the
  fundamental-frequency band of the EMF, with block-bootstrap errors. Q = πf/γ.
- **Manipulation:** the external resistance R_ext in series with the coil (0 Ω to 2.2 MΩ), two springs,
  and three coils.
- **Clock correction:** the firmware's sampling loop could not keep its 10 µs schedule. The 50 Hz mains
  line appears at 63.07 Hz on the firmware's timebase, so all times are multiplied by
  s = 1.2613 (± 0.013, grid tolerance), read by every script from `clock_calibration.json`. The phone
  videos give s = 1.2618 ± 0.0003 independently. Every value below is clock-corrected.
- **Prediction:** the energy method gives γ_em = ⟨ε²⟩ / (R_loop m ω² A²) = c / R_loop from the measured
  EMF alone.

| Set | Runs | R_ext values | Use |
|---|---|---|---|
| Spring 1, coil 1 | 9 | 0 (×2), 33.6, 81.4, 324, 1051, 3180, 9610 Ω, 2.2 MΩ | main test |
| Spring 2, coil 1 | 8 | 0 (×2), 33.3, 84.1, 327, 997, 3190, 9670 Ω | replication |
| Springs 1–2, coils 2–3 | 4 | 0 Ω | coil geometry |

## Repository layout

```
Data/
  Raw/                         one folder per run; each holds the DAQ dump (.csv) and a screenshot
    spring_1/coil_1/Resistance/<R_ext>/
    spring_1/coil_2/, spring_1/coil_3/
    spring_2/coil_1/Resistance/<R_ext>/
    spring_2/coil_2/, spring_2/coil_3/
  Video/                       phone-video tracks: VID-*.csv (time_s, vertical_distance_m)
    frame_times/               true time of every video frame (ffprobe); the tracks assume even spacing
  Results/                     everything run_all.py produces
    final_table.csv            per-run γ, SE, Q, f and initial EMF (Table A1)
    final_stats.json           means, estimator comparison, 1/R fit, divider check
    clock_calibration.json     mains-hum frequency per run, clock factor s
    decay_halves.json          early- vs late-half decay rates
    video_analysis.json        video frequencies, clock factor from video, decay of the motion (Table A2)
    supporting_numbers.json    ADC step, noise, dipole moment and turns, air drag, time per ADC read
    video_clock_check.json     per-video frame-clock check (from check_video_clocks.py)
    Overall_Results.xlsx       the same results as one workbook
    figures/                   Figures 3, 4, 6 and 7 (PDF and PNG)
    logs/                      printed output of every script
Code/
  requirements.txt             pinned dependencies
  Firmware/
    main.cpp                   DAQ firmware (Raspberry Pi Pico, Arduino core)
    claw.cpp                   servo release mechanism (ESP32)
  Live Plotter/
    serial_plotter.py          live serial plot used during the experiment
  Analysis/
    run_all.py                 runs everything below and writes Data/Results/
    common.py                  paths, run list and shared helpers (not run directly)
    fit_decay.py               loader and the original peak-based fit (not run directly)
    clock_calibration.py       mains-hum clock factor
    alternative_estimators.py  peak, per-cycle rms and nonlinear least-squares estimators
    transduction_model.py      physical model of the coil's response
    final_table.py             headline estimator, clock-corrected table
    significance_tests.py      1/R fit (t, permutation, bootstrap), divider check
    video_analysis.py          video tracks timed with true frame times: clock check, decay of the motion
    decay_halves.py            early- vs late-half decay
    supporting_numbers.py      smaller numbers quoted in the paper (step, noise, turns, drag, 12.6 us/read)
    figures.py                 figures
    check_video_clocks.py      ffprobe frame-clock check; needs the original .mp4 files (not run by run_all.py)
    extended/                  v2: forward model, simulated DAQ, coupling function, damping law, ADC error
      run_extended.py          runs everything in this folder and writes Data/Results/extended/
Hardware/
  Schematics/                  KiCad schematic exports (PDF: DAQ, claw); as-built vs corrected circuit; signal-chain diagram
  Photos/                      apparatus, coils and DAQ board
  DAQ_Build_Guide.md           build notes and bill of materials (US$45.56)
```

## Expected headline output

Running `run_all.py` on the data in this repository should give these values.

| Result | Value |
|---|---|
| Clock factor s from mains hum (11 runs, SNR > 50) | 1.2613 ± 0.0047 (run scatter), ± 0.013 (grid) |
| Clock factor s from video (spring 1, spring 2) | 1.2618 ± 0.0003, 1.2618 ± 0.0001 |
| Decay of the motion, spring 1 videos (7) | (11.31 ± 0.30) × 10⁻³ s⁻¹, Q ≈ 580, early/late (video) 1.08 ± 0.04 |
| Spring 1 decay rate γ, 8 runs below 10 kΩ | (11.9 ± 0.5) × 10⁻³ s⁻¹ |
| Spring 1 Q, f | 551 ± 24, 2.082 Hz |
| Spring 2 decay rate γ | (13.5 ± 1.0) × 10⁻³ s⁻¹ |
| Spring 2 Q, f | 436 ± 32, 1.862 Hz |
| 1/R coefficient c, spring 1 (fit) | (-0.011 ± 0.006) Ω s⁻¹, consistent with the as-built prediction c = 0 (two-sided p = 0.10) |
| 1/R coefficient c at a common EMF amplitude (14.7 mV) | (+0.011 ± 0.010) Ω s⁻¹ |
| c predicted if the loop had been closed through R_c + R_ext | +0.030 Ω s⁻¹ (γ_em ≈ 2.0 × 10⁻³ s⁻¹, ≈ 18% of the video damping) |
| 2.2 MΩ divider, EMF ratio to the low-R runs | raw 0.245 ± 0.015; 0.30 after correcting for the smaller release (extrapolated); predicted 0.31 (0.29–0.33) |
| Early/late decay ratio (EMF envelope) | 1.11 (spring 1), 1.19 (spring 2) |
| γ vs initial EMF, Pearson r | -0.40 (spring 1), 0.97 (spring 2) |

`final_stats.json` also contains t, permutation and leave-one-out tests of the fit against the closed-loop
prediction. Those compare the data with a circuit that was not built, so they do not by themselves show that the
loop was open; the paper reports them only in an appendix.

## Extended analysis (v2)

`Code/Analysis/extended/run_extended.py` adds a forward model of the experiment, a simulated copy of the
as-built DAQ, and three analyses that use only the recordings already in this repository plus one earlier
session (23 July). Run it after `run_all.py`; it takes about half a minute and writes to
`Data/Results/extended/`.

```bash
cd Code/Analysis/extended
python run_extended.py
```

| Result | Value | File |
|---|---|---|
| Coupling function κ(z) = EMF / velocity at rest, spring 1 | 0.072 V s m⁻¹; shape repeats to 1.5% run to run; up and down strokes agree to 0.5% | `kappa_recon.json` |
| κ(z), spring 2 against spring 1 (one height offset, 0.72 cm) | curves agree to 3.0% rms over the overlap | `kappa_measured.png` |
| κ(z), 23 July session (12 runs) against 24 July | agree to 6.3% rms after a −0.55 cm offset | `kappa_recon.json` |
| Predicted added decay rate with coil 1 shorted, spring 1 | 2.05 × 10⁻³ s⁻¹ at release, falling to 1.63 at small amplitude (18% to 14% of the video damping) | `kappa_recon.json` |
| Point dipole at the stated 6 cm, second and third harmonic | predicted 0.52 and 0.15 of the fundamental; measured 0.33 and 0.054 | `validate.json` |
| Effective coupling (two fitted numbers), EMF-envelope rate | predicted 12.08 (spring 1) and 13.26 (spring 2); measured 11.89 ± 0.50 and 13.49 ± 0.95 | `validate.json` |
| Spring-2 run-to-run SD of the EMF-envelope rate | 0.95 raw, 0.23 after the modelled amplitude dependence | `sim_validation.png` |
| Injection-recovery: quantisation, integer division, read noise | change the recovered rate by less than 0.01% | `inject.json` |
| Injection-recovery: nominal timestamps | frequency 2.626 Hz (measured 2.6261); the hum correction recovers s to 2 parts in 10⁵ | `inject.json` |
| Clock factor, 23 July session (100-read blocks, video against DAQ) | 1.2614 ± 0.0007 | `session_0723.json` |
| The 52–55 Hz feature | the 20th and 21st harmonics of the oscillation (22nd and 23rd for spring 2) | `adc_nonlinearity.json` |
| Level-dependent ADC error (RP2040-E11) | steps of −7.3 and −7.1 LSB, 516 and 510 codes either side of a +1.7 LSB step; independent halves correlate at r = 1.00 | `adc_inl.png` |
| Decay law of the motion (spring-1 videos) | amplitude-dependent term 5.4 ± 1.7 (SE) × 10⁻³ s⁻¹ at release; dry friction has the wrong sign | `damping_law.json` |

Three points change how the earlier numbers should be read.

- **Geometry.** A point dipole 6 cm above the coil centre does not reproduce the recorded waveform, and no
  dipole or finite-loop magnet model at any distance between 2.5 and 6 cm does. A rough reading of frames from the run videos puts
  the magnet nearer than 6 cm and shows it reaching the mouth of the coil at the bottom of each swing. The
  dipole-based turns estimate in `supporting_numbers.json` should therefore not be relied on. The prediction
  of the shorted-coil effect never used the geometry: it comes from the measured EMF and the video amplitude,
  and the amplitude was checked against the metre rule in the frames (4.8 cm peak to peak on the first swing).
- **Mechanical damping is set by the apparatus.** On 23 July the same oscillator decayed at
  (49.4 ± 0.9) × 10⁻³ s⁻¹, more than four times the 24 July rate, at a frequency 2.5% lower. The run videos
  appear to show the joint between spring and cradle before and after it was reinforced with hot glue, which
  is a candidate cause but not a tested one. The 23 July
  series is used here for κ(z) and for the clock, not for damping.
- **The DAQ's remaining flaws are measurable but harmless.** The ADC's step error produces a comb of high
  harmonics a few µV high and shifts the fitted decay rate by 0.3%.

`Data/Raw/session_2026-07-23/` holds the twelve DAQ dumps of that session (nominal spacing 1000 µs, 100-read
blocks) and `Data/Video/session_2026-07-23/` the seven usable displacement tracks. The track labels 0 to 150
are the values written on the original files; the coil loop was open in this session as well.

## Data dictionary

**Raw DAQ dumps (`Data/Raw/**/YYYY-MM-DD-muino-data_dump.csv`).** These are plain text. A file may contain
several captures, each opened by `STARTING CAPTURE...` and `BUTTON RELEASED, DUMPING DATA...` and
closed by `DONE.`. The analysis uses the longest capture. Each data line is `time_us,emf_uV`:

- `time_us`: nominal time, computed by the firmware as sample index × 500 µs. Multiply by s = 1.2613 for
  true time.
- `emf_uV`: coil EMF referred to the amplifier input, in µV. Values sit on a 23.647 µV lattice, which is
  2.7% coarser than the published firmware constants give (see Known issues).

**Video tracks (`Data/Video/VID-*.csv`).** `time_s` assumes evenly spaced frames at the file's average
frame rate; the videos actually have a variable frame rate (intervals of about 33 and 36 ms), so
`video_analysis.py` re-times each track with `frame_times/VID-*.csv`. The ~10 MB videos are not included
(available from the corresponding author).

**Folder names** give the external series resistance in ohms (`0.0`, `33.6`, `3.18k`, `2.2M`, …).
`Retake` folders are repeated runs at the same setting. The screenshot in each folder was taken from
the live plotter at the time.

**`final_table.csv`** has one row per run, with these columns:

- `run`
- `R_ext` (Ω)
- `gamma_true` (10⁻³ s⁻¹)
- `gamma_err` (block-bootstrap SE)
- `Q`
- `f_true` (Hz)
- `eps_rms_init_mV`: the rms EMF over the first three cycles

## Apparatus constants

| Quantity | Value |
|---|---|
| Oscillating mass | 105 g (NdFeB cup magnet ≈ Ø41 × 7 mm with a Ø30 mm disc, string cradle) |
| Field at the coil (Hall probe) | 11 G |
| Magnet–coil centre distance at rest | 6 cm (nominal; the recorded waveform is not consistent with it, see Extended analysis) |
| Coil 1 | R_c = 15.2 Ω, inner diameter ≈ 5.6 cm, winding height ≈ 4 cm, ≈ 550 turns (estimated from the EMF; 430–810 from the resistance) |
| Spring constants (force–extension slope) | 16.578 N/m and 19.438 N/m. The measured frequency ratio (2.08/1.86 Hz = 1.118) is closer to the prediction if the two labels were swapped (spring 1 ≈ 19.438, spring 2 ≈ 16.578; predicted ratio 1.083, vs 0.924 unswapped); even then both frequencies are 4–7% below the static-k prediction |
| DAQ gain, input range, input step | 35, ±47 mV, 23.647 µV |
| Amplifier input bias resistor R5 | 1 MΩ (the only path closing the coil loop) |

## Known issues and recommended fixes

- **Open-loop coil.** The coil returns only through R5 (1 MΩ) to the 1.65 V node, so the loop current is about 16 nA and a series R_ext does nothing. Fix: put R_load across the coil terminals (Kelvin connection), or feed the coil into a transimpedance input (coil and R_ext between 1.65 V and the inverting input, R_f in feedback).
- **Timebase.** The loop cannot sustain 10 µs, so the real block period is about 1.26× the nominal 500 µs. Do not write `t = i*Output_Interval`. Record `micros()` per block, or use RP2040 free-running ADC with DMA at a fixed `adc_set_clkdiv`. Check with mains hum (50 Hz should appear at 50 Hz).
- **Truncating average.** `tempStorage/Oversample_Factor` is integer division, so resolution stays at 1 LSB with a −0.5 LSB bias. Store the 32-bit sum, or divide in float.
- **Rails and clamps.** The ±15 V op-amp output can reach about ±13.5 V and drive the ADC pin through R6 = 1 kΩ and silicon diodes. Use a single-supply rail-to-rail op-amp (3.3 V), BAT54S Schottky clamps and R6 ≥ 4.7 kΩ.
- **R3.** The schematic says 34 kΩ (G = 35); the BOM says 35 kΩ (G = 36). Measure G with a known 10 mV input.
- **Scale constants.** Logged data sit on a 23.647 µV/code lattice; the repo constants (3.3, 4095, 35) give 23.025 µV. Commit the flashed firmware. Using LSB = 3.3/4096/35 = 23.019 µV, published EMF is about 2.7% high.
- **Committed vs flashed firmware.** The original flashed `.cpp` was not kept. `main.cpp` has been set to the `Output_Interval = 500` µs (2 kS/s nominal) used for the data, as the raw `time_us` column shows; its ADC scale constants still differ from the flashed build (see Scale constants).
- **ADC DNL.** RP2040-E11 gives DNL spikes near codes 512, 1536, 2560 and 3584. Check code histograms or exclude those codes.

### Corrected sampling loop

```cpp
// RAM: 8 B/sample -> keep Max_Samples <= 25000 on the RP2040
uint32_t sumStore[Max_Samples], tStore[Max_Samples];
uint32_t acc = 0, n = 0, count = 0, t0 = micros(), next = t0;
while (digitalRead(BUTTON_PIN) == LOW && count < Max_Samples) {
  if ((int32_t)(micros() - next) >= 0) {
    next += Sample_Interval;
    acc += analogRead(ADC_PIN);
    if (++n == Oversample_Factor) {
      sumStore[count] = acc;            // full-precision sum
      tStore[count++] = micros() - t0;  // real time
      acc = n = 0;
    }
  }
}
// output: code = sumStore[i] / (float)Oversample_Factor;
// V = (code / 4096.0f * VS - VREF) / GAIN
```

All of these were found after the data were taken. The analysis uses the logged data as-is and treats these issues as uncertainties.

## Licence and citation

- Code and hardware: MIT licence (see `LICENSE`).
- Data: CC BY 4.0.

Releases are archived on Zenodo (all versions: https://doi.org/10.5281/zenodo.23448903), including v1.0 (https://doi.org/10.5281/zenodo.23448904), v1.1 (https://doi.org/10.5281/zenodo.23455570) and v1.2 (https://doi.org/10.5281/zenodo.23614958). Cite as: Malik, H. T. (2026). *Electromagnetic-Damping-Research: Data, firmware, hardware and analysis code* [Computer software]. Zenodo.

If you use this repository, please also cite the paper:

> Malik, H. T. (2026). *Coil-circuit impedance and sampling-clock errors in a microcontroller-based electromagnetic damping experiment* [Manuscript submitted for publication].

An earlier version of the paper, titled *Electromagnetic damping: A closer look at a contactless braking system*, is available as a preprint at https://doi.org/10.5281/zenodo.23449036.

Contact: Hassan Tariq Malik, hassantariq102938@gmail.com
