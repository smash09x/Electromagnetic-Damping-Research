# Electromagnetic Damping: A Closer Look at a Contactless Braking System

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23448904.svg)](https://doi.org/10.5281/zenodo.23448904)

Data and code for a study of electromagnetic damping in a magnet–spring oscillator. It tests whether the
damping falls as 1/R when resistance is added to the coil circuit, using a low-cost
Raspberry Pi Pico data-acquisition system (DAQ).

Author: Hassan Tariq Malik ([ORCID 0009-0001-3749-090X](https://orcid.org/0009-0001-3749-090X)) · Co-authors: Hardyesh Kumar, Muhammad Umer Farooq
The Black Hole Science Internship Programme 2026, Islamabad
Research supervisors: M. Sanan Qureshi, Dr Sadia Manzoor (COMSATS University Islamabad), Dr Pervez Hoodbhoy

## Quick start

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
    final_stats.json           means, estimator comparison, 1/R fit, divider check, video check
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
Hardware/
  Schematics/                  KiCad schematics (DAQ, claw); as-built vs corrected circuit; signal-chain diagram
  Photos/                      apparatus, coils and DAQ board
  DAQ_Build_Guide.md           build notes and bill of materials (US$42.57)
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
| 1/R coefficient c, spring 1 (fit) | (-0.011 ± 0.006) Ω s⁻¹ |
| c predicted for a loop closed through R_c + R_ext | +0.030 Ω s⁻¹ (≈ 17% of γ) |
| Exclusion of the prediction, t-distribution with 6 df | 3.6σ (A exact), 2.3σ (σ_A = 20%); permutation p = 0.003 |
| 2.2 MΩ divider, amplitude-corrected EMF ratio | 0.30 (predicted 0.31) |
| Early/late decay ratio (EMF envelope) | 1.11 (spring 1), 1.19 (spring 2) |
| γ vs initial EMF, Pearson r | -0.40 (spring 1), 0.97 (spring 2) |

## Data dictionary

**Raw DAQ dumps (`Data/Raw/**/YYYY-MM-DD-muino-data_dump.csv`).** These are plain text. A file may contain
several captures, each opened by `STARTING CAPTURE...` and `BUTTON RELEASED, DUMPING DATA...` and
closed by `DONE.`. The analysis uses the longest capture. Each data line is `time_us,emf_uV`:

- `time_us`: nominal time, computed by the firmware as sample index × 500 µs. Multiply by s = 1.261 for
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
| Magnet–coil centre distance at rest | 6 cm |
| Coil 1 | R_c = 15.2 Ω, inner diameter ≈ 5.6 cm, winding height ≈ 4 cm, ≈ 550 turns (estimated from the EMF; 430–810 from the resistance) |
| Spring constants (force–extension slope) | 16.578 N/m and 19.438 N/m |
| DAQ gain, input range, input step | 35, ±47 mV, 23.647 µV |
| Amplifier input bias resistor R5 | 1 MΩ (the only path closing the coil loop) |

## Known issues and recommended fixes

- **Open-loop coil.** The coil returns only through R5 (1 M) to the 1.65 V node, so the loop current is about 16 nA and a series R_ext does nothing. Fix: put R_load across the coil terminals (Kelvin connection), or feed the coil into a transimpedance input (coil and R_ext between 1.65 V and the inverting input, R_f in feedback).
- **Timebase.** The loop cannot sustain 10 us, so the real block period is about 1.26x the nominal 500 us. Do not write `t = i*Output_Interval`. Record `micros()` per block, or use RP2040 free-running ADC with DMA at a fixed `adc_set_clkdiv`. Check with mains hum (50 Hz should appear at 50 Hz).
- **Truncating average.** `tempStorage/Oversample_Factor` is integer division, so resolution stays at 1 LSB with a -0.5 LSB bias. Store the 32-bit sum, or divide in float.
- **Rails and clamps.** The +/-15 V op-amp output can reach about +/-13.5 V and drive the ADC pin through R6 = 1 k and silicon diodes. Use a single-supply rail-to-rail op-amp (3.3 V), BAT54S Schottky clamps and R6 >= 4.7 k.
- **R3.** The schematic says 34 k (G = 35); the BOM says 35 k (G = 36). Measure G with a known 10 mV input.
- **Scale constants.** Logged data sit on a 23.647 uV/code lattice; the repo constants (3.3, 4095, 35) give 23.025 uV. Commit the flashed firmware. Using LSB = 3.3/4096/35 = 23.019 uV, published EMF is about 2.7% high.
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

The data and code (v1.0) are archived on Zenodo: Malik, H. T., Kumar, H., & Farooq, M. U. (2026). *Electromagnetic-Damping-Research: Data, firmware, hardware and analysis code* (Version v1.0) [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.23448904

If you use this repository, please also cite the paper:

> Malik, H. T., Kumar, H., & Farooq, M. U. (2026). *Electromagnetic damping: A closer look at a contactless braking system* [Preprint].

Contact: Hassan Tariq Malik, hassantariq102938@gmail.com
