# Referee report: instrumentation and electronics

**Scope.** I checked the KiCad schematic (DAQ_electric_damp.pdf, rev v1.0), main.cpp, claw.cpp, serial_plotter.py, the README/BOM and all 21 CSV files against Methods and Discussion.

## 1. The coil loop (central claim): correct, with quantification to add

From the schematic: COIL_REF is the U5A buffer output (1.65 V). COIL_SIG goes only to U2B pin 5 (+IN), and R5 (1 MΩ) runs from pin 5 back to the 1.65 V node. R4 (1 kΩ) returns to the same 1.65 V node, so G = 1 + R3/R4 = 1 + 34k/1k = 35, referenced to 1.65 V. R6, C5, D1/D2 and R7 all sit **downstream of the U2B output**. The op-amp output isolates them, so they carry no coil current. The other parallel paths are negligible:
- OPA2134 input impedance is 10^13 Ω || 2 pF. With roughly 10–20 pF of breadboard capacitance, the input is about 3–6 GΩ at 2.6 Hz.
- I_B ≈ 5 pA, which gives about 5 µV of DC across R5.
- U5A's closed-loop output impedance is below 1 Ω.

The loop resistance is therefore R_c + R_ext + 1 MΩ, and the manuscript's explanation is **correct**. I suggest adding to Discussion: *"I = ε/(R_c+R_ext+R5) ≈ 16.2 mV/1.00 MΩ = 16 nA rms (23 nA peak), so P_J ≈ ε²/R5 ≈ 0.26 nW. The mechanical loss is 2γE ≈ 2(0.0178)(7.0 mJ) ≈ 0.25 mW, so P_J is 10⁻⁶ of it. Op-amp input impedance (>1 GΩ at 2.6 Hz), bias current (5 pA), the clamp diodes and C5 lie outside the coil loop or are negligible."*

**MINOR, 2.2 MΩ run.** That run sits at a high-impedance node (≈690 kΩ). Its pre-release baseline is offset by ≈10 mV, compared with ≈0.6 mV in the other runs, and its noise is 1.4 mV rms, compared with 30–90 µV elsewhere. The table's ε_rms = 4.0 mV is therefore noise-contaminated. The 20% shortfall from 0.31 is more likely due to resistor tolerance, leakage on the breadboard, or the run-to-run variation in release amplitude (±6%) than to "input loading". Measure R5 and the 2.2 MΩ resistor with a DMM, and subtract the noise power in quadrature.

## 2. Specification claims

**MAJOR: the timebase is assumed, not measured.** The firmware writes `t = i*Output_Interval` and comments out the actual timestamps. The polling loop (`micros()`, `digitalRead`, `analogRead`, plus USB interrupts) must complete within 10 µs. If it cannot, `previousMicros` falls permanently behind and the true block period exceeds the nominal value. That scales f and γ by the same factor, while Q stays invariant. The paper's own "unresolved inconsistency" fits this pattern for spring 1: the measured f is 1.32× the f predicted from k, and the video γ values are about 30% lower than the DAQ values. Spring 2 does not fit as neatly, so this is not proven. It must be checked anyway:
- Log `micros()` at the start and end of each capture, or toggle a GPIO and time it with a scope or a reference generator.
- Compare cycle counts against the video over the same interval.

The preferred fix is the RP2040's free-running ADC with DMA (`adc_set_clkdiv`), which gives sample timing locked to the crystal. Until the timebase is verified, absolute γ and b should be called provisional.

**MAJOR: firmware does not match the data.** The repository has Output_Interval = 1000 µs, but the data are spaced 500 µs, so N = 50 for these runs. The data also sit on a grid of exactly **23.647 µV**. The repository constants (3.3/4095/35) give 23.025 µV, so there is a 2.7% scale difference. That implies different G, V_s or V_ref constants, and it biases ε by 2.7% and c by 5.4%. Publish the firmware that was actually used. Also resolve R3: the schematic says 34 kΩ and the BOM says 35 kΩ (G = 36). Measure G with a known 10 mV input.

**MAJOR: "oversampling and decimation" gives no added resolution.** `tempStorage/Oversample_Factor` is integer division, so every stored value is truncated back onto the raw 1-LSB grid. All the data confirm this. Averaging reduces white noise, but the output resolution stays at 23.6 µV, with a −0.5 LSB bias. Replacement text: *"Blocks of 50 samples were averaged (boxcar filter, nulls at multiples of 2 kHz). The firmware truncates the mean to an integer code, so the output resolution remains one ADC LSB (23.6 µV input-referred)."* The fix is to store the 32-bit sum, or divide in floating point.

**MINOR: noise floor and SNR.** Across the 16 coil-1 runs, the pre-release rms ranges from 29 to 94 µV (median ≈48 µV). The 34 µV figure is the best case. State the statistic (rms over a stated window and bandwidth), and give the median and range. The 63 dB SNR ratio mixes peak full scale with rms noise:
- The sine-wave dynamic range is 20 log(33.3 mV/34 µV) ≈ 60 dB, or ≈9.7 effective bits in 0–1 kHz.
- The actual signal-to-noise ratio at 16 mV rms is ≈54 dB.

The front end is not the limit. OPA2134 noise of 8 nV/√Hz over 1.6 kHz is ≈0.3 µV, and the coil's 15 Ω source shunts R5's Johnson noise. The floor is set by the ADC (ENOB ≈8.7 bits, so ≈65 µV rms input-referred per raw sample), by Pico 3V3 ripple and by low-frequency pickup.

**MINOR: RP2040 DNL.** Erratum RP2040-E11 describes DNL spikes at codes 512, 1536, 2560 and 3584. Peak envelopes cross codes 1536 and 2560 (≈±12 mV input) inside the fit window. Check the code histograms, or exclude those codes. Driving GPIO23 high (PWM mode on the Pico SMPS) or adding an external reference on ADC_VREF also lowers the noise.

**MINOR: RC filter.** R6/C5 is 1 kΩ/0.1 µF, which gives f_c = 1.6 kHz. That is adequate anti-aliasing for 100 kS/s, but it should be stated.

## 3. The ±15 V rail and ADC protection (MAJOR design error)

A 0–3.3 V ADC does not need ±15 V. The OPA2134 output can swing to about ±13.5 V on any overload: an input above 47 mV, a magnet strike, or an open input. Through R6 = 1 kΩ that drives ≈10 mA. D1/D2 are ordinary silicon diodes (Vf ≈0.7 V), so they let the pin reach ≈4.0 V and −0.7 V, beyond the RP2040's absolute limits of IOVDD+0.5 and −0.5 V. The internal ESD diodes then conduct, and D2 back-feeds the Pico's 3.3 V rail, which cannot sink current. The BOM also lists a single diode, but the schematic has two.

The converter's "isolation" is moot, because its 0 V is tied to GND and the Pico's GND reaches the PC through USB. A switching DC–DC converter is also an added noise source.

Replacement text: *"The op-amps run from ±15 V. Because this lets the output exceed the ADC range, a rail-to-rail op-amp on a single 3.3–5 V supply (e.g. OPA2350/MCP6022), with Schottky clamps (BAT54S) and R6 ≥ 4.7 kΩ, is preferable."* Also correct "battery power": the BOM and schematic use a 9 V adapter and a 7805.

## 4. Corrected topology

The proposed fix (R_load across the coil terminals, read in parallel with the high-Z input, V = εR_load/(R_c+R_load)) is **correct**. It is incomplete in three ways:
1. It cannot reach a short circuit.
2. ε must then be inferred through R_c, which drifts by 0.39%/K.
3. Breadboard lead resistance of about 0.1–0.5 Ω matters at small R_load, so connect R_load at the coil terminals (Kelvin connection).

**Recommended addition: a transimpedance (current) input.** Connect the coil and R_ext between COIL_REF and the inverting input of an op-amp, with R_f in feedback and +IN at 1.65 V. The loop then sees R_c + R_ext (plus a few mΩ), so the authors' **original series-resistor protocol works unchanged**, and V_out − 1.65 = −εR_f/(R_c+R_ext). With I_peak ≈ 1.5 mA at R_ext = 0, R_f = 1 kΩ gives ±1.5 V. Switch R_f in decades as R_ext grows, and add C_f for stability. This measures I directly, so P = I²R_loop can be checked independently.

An alternative is a **second, open-circuit sense coil** read by the existing high-Z amplifier, which lets the damping coil be shorted or opened freely. The open-versus-shorted Δγ then gives γ_em(R_c) directly. An instrumentation amplifier (e.g. INA333, single 3.3 V supply, one gain resistor, CMRR > 90 dB) could replace U2B, R3, R4 and the ±15 V converter, but it still needs one coil end returned to V_ref.

Separately, ε ∝ κ(z)ż with a nonlinear κ, so the ε envelope is not strictly proportional to amplitude at large swings. This could contribute to the r = 0.98 correlation for spring 2.

## 5. Figure request

Replace the cropped full schematic with a block diagram, left to right:
1. **Coil** (R_c, ε source) and **R_ext** in series, with the two terminals labelled COIL_SIG and COIL_REF.
2. **R5 1 MΩ** drawn as the *only* return path, shaded and labelled "loop closes here: I ≈ 16 nA".
3. **U2B** non-inverting amplifier, G = 1 + 34k/1k = 35, with R4 returning to V_ref.
4. A **V_ref block**: 3.3 V → 100k/100k divider → U5A buffer → 1.65 V, feeding both COIL_REF and R4.
5. **RC filter** (1 kΩ/100 nF, f_c = 1.6 kHz) and **clamps** to GND/3.3 V.
6. **RP2040 ADC** (12-bit, 100 kS/s) → 50-sample boxcar → 2 kS/s → RAM (60 000 samples) → USB → PC (20 Hz Butterworth, fit).
7. A **power** sub-block: 9 V → 7805 → 5 V → NMA0515 (±15 V to the op-amps) and Pico VBUS.

Add an inset of the corrected topology (TIA, or R_load across the coil), annotated with the R_loop formula.

## 6. Safety

- The ±15 V output can damage the ADC pin (Section 3).
- NdFeB magnets and the servo claw are pinch hazards.
- The mains adapter should be a certified unit.

## The three most important changes

1. Verify the timebase: measure the real block period, publish the firmware actually used, and fix the 2.7% scale mismatch. Until then, f and γ are provisional, and this may explain the f-versus-k inconsistency.
2. Add the coil-loop quantification (16 nA, 10⁻⁶ power ratio, no other paths) and the transimpedance or sense-coil topology that permits the series-R and shorted-coil protocols.
3. Correct the Methods: integer-truncated "oversampling", the noise and SNR definitions, the ±15 V and clamp design flaw, R3 34k vs 35k, and battery vs adapter.
