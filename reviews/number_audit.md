# Number audit: /root/paper2/main.tex

Scripts: `/root/paper2/audit/audit.py` (all derived values). Ground truth: final_stats.json, final_table.csv, clock.json, round2 reviews, raw CSVs.

| # | claim | value in paper | verified value | status |
|---|---|---|---|---|
| 1 | US\$43 DAQ | 43 | README BOM total 42.57 | OK |
| 2 | resistances 15 Ω to 2.2 MΩ | 15, 2.2 | R_c = 15.2 Ω; 2.2M run | OK |
| 3 | decay rate γ, n = 8 (abstract, results) | 11.9 ± 0.5, n=8 | 11.886 ± 0.493, n=8 | OK |
| 4 | braking current about 16 nA | 16 nA | 16.24 mV / 1 MΩ = 16.2 nA | OK |
| 5 | EM damping about 10^-6 of total | 1e-6 | 3.03e-8 / 11.9e-3 = 2.6e-6 | OK (order) |
| 6 | would have added about 17% | 17% | 0.168 | OK |
| 7 | excluded at about 3σ | 3σ | 2.3-3.6σ, perm p = .003 | OK |
| 8 | hum at 63 Hz, not 50 Hz | 63 | 63.07 Hz | OK |
| 9 | sampling ran 26% slower (abstract, conclusion) | 26% slower | interval 26% longer; rate only 20.7% lower | WRONG |
| 10 | γ/ω ≈ 10^-3 | 1e-3 | 0.91e-3 / 1.15e-3 | OK |
| 11 | κ largest at z = ±a/2 | a/2 | analytic: z² = a²/4 | OK |
| 12 | total mass 105 g; R_c 15.2 Ω | 105 g | m = 0.105 in all scripts | OK |
| 13 | spring constants 16.578, 19.438 N/m | as stated | round2_brief.md | OK |
| 14 | gain 35, R5 1 MΩ, 1.65 V, 1.6 kHz | as stated | firmware, BOM, electronics.md | OK |
| 15 | averages blocks of 50 readings | 50 | data spacing 500 µs (repo firmware says 100) | OK |
| 16 | stores up to 60 s in RAM | 60 s | 60000 points x 631 µs = 37.8 s | WRONG |
| 17 | recorded step 23.65 µV | 23.65 | 23.650 | OK |
| 18 | 2.7% larger than firmware constants | 2.7% | 23.65/23.025 = 1.0272 | OK |
| 19 | noise 29-94 µV rms, median 48 | 29, 94, 48 | min 29.4, median 47.4-47.5; max recomputes to 80-88 | UNSOURCED (max only) |
| 20 | noise about 3e-3 of signal | 3e-3 | 48 µV / 16 mV = 3.0e-3 | OK |
| 21 | timestamps sample number x 500 µs | 500 µs | dt = 500 µs | OK |
| 22 | R_ext values; coils 2, 3 once each | as listed | final_table.csv | OK |
| 23 | each run about 38 s | 38 s | 37.84 s true | OK |
| 24 | about 80 cycles | 80 | 78.8 (spring 1), 70.5 (spring 2) | WRONG |
| 25 | Butterworth 4th order, 20 Hz; band 0.6-1.4 f | as stated | common.py, final.py | OK |
| 26 | peaks overestimate γ by 15-20% | 15-20% | 19% (S1), 23% (S2); per-run 16-28% | WRONG |
| 27 | fit starts 1 s after peak, ends 1 s before end | 1 s | code uses 1 s nominal = 1.26 s true | WRONG |
| 28 | other estimators agree within 7% | 7% | spring 1: 6.6%; spring 2: 11.5% | WRONG |
| 29 | scatter / method error (spring 1) | 0.5 / 0.4 | 0.493 / 0.39 | OK |
| 30 | clock error on γ_1 | 0.15 | 1.03% x 11.89 = 0.12 | WRONG |
| 31 | Q_1 = 551 ± 24; Q_2 = 436 ± 32 | as stated | 551.2 ± 24.0; 435.6 ± 31.7 | OK |
| 32 | γ_2 = 13.5 ± 1.0; 2.2 MΩ run 11.5 | as stated | 13.49 ± 0.95; 11.53 | OK |
| 33 | ε_rms about 16 mV; A about 2.2 cm | 16, 2.2 | 16.24 mV; A = 0.022 in code | OK |
| 34 | c = 0.030 Ω/s; γ_em about 2.0e-3 | 0.030, 2.0 | 0.0303; 1.995 | OK |
| 35 | 9-25% for A = 3.0-1.8 cm | 9-25% | 0.09-0.25 | OK |
| 36 | c = -0.011 ± 0.006; p = .003; 2.3σ at 20% | as stated | -0.01077 ± 0.00554; .003; 2.30 | OK |
| 37 | R_loop 1.000 to at most 1.010 MΩ | 1.010 | 1 + 0.0096 + 0.0152 kΩ = 1.0096 | OK |
| 38 | dissipating about 0.3 nW | 0.3 | 0.264 nW | OK |
| 39 | mechanical loss about 0.25 mW | 0.25 mW | 2γE = 0.103 mW (0.25 only on nominal clock) | WRONG |
| 40 | γ_em about 3e-8 s^-1 | 3e-8 | 3.03e-8 | OK |
| 41 | divider 0.31; corrected 0.30; 15% smaller release | 0.31, 0.30, 15% | 0.3125; 0.303; 14.2% | OK |
| 42 | hum 63.07 ± 0.23 Hz | as stated | 63.067 ± 0.233 | OK |
| 43 | harmonic at 126.2 Hz | 126.2 | 126.12 (measured); 2 x 63.07 = 126.13 | WRONG |
| 44 | s = 1.261 ± 0.013; 12.6 µs; 631 µs | as stated | 1.2613; 12.61; 630.7 | OK |
| 45 | video ratio 1.06 ± 0.06; s = 1.23 ± 0.07 | as stated | 1.059 (SEM 0.058); 1.23 ± 0.067 | OK |
| 46 | frequencies 2.08, 1.86 Hz; ratio 1.118 | as stated | 2.0821, 1.8622; 1.1181 | OK |
| 47 | swapped-k prediction 1.083 | 1.083 | sqrt(19.438/16.578) = 1.0828 | OK |
| 48 | 4-8% below static-k | 4-8% | 3.8% and 6.9% | WRONG |
| 49 | early vs late faster by 18% / 25% | 18, 25 | 1.183, 1.252 | OK |
| 50 | r = .97 (spring 2) | .97 | 0.967 | OK |
| 51 | air drag about 2% of damping | 2% | physics.md M5: 2% of b | OK |
| 52 | coil 2 EMF 0.37 / 0.45; coil 3 0.11 | as stated | 0.365 / 0.450; 0.119, 0.105 (mean 0.11) | OK |
| 53 | suppression 10^6-fold | 1e6 | 1 MΩ vs 15 Ω-ish loop: 1e6 | OK |
| 54 | ±15 V rails | ±15 | electronics.md | OK |

Word count (not stated in paper): `wc -w` = 3000 including LaTeX markup; detex prose is 2693 (title to end), 2519 (abstract to data availability), 2290 (introduction to conclusion). "~2.9k" is not supported; ~2.5-2.7k.

## Replacements for WRONG items (old -> new)

1. `sampling ran 26\% slower than the firmware assumed` -> `each stored sample took 26\% longer than the firmware assumed`
2. `the DAQ's clock ran 26\% slow` -> `the DAQ's sample spacing was 26\% longer than assumed`
3. `stores up to \SI{60}{s} in RAM` -> `stores up to 60\,000 points in RAM (about \SI{38}{s} at the true spacing)`
4. `or about 80 cycles` -> `or about 70--80 cycles`
5. `overestimates $\gamma$ by 15--20\%` -> `overestimates $\gamma$ by about 19--23\%`
6. `The fit started \SI{1}{s} after the first large peak and ended \SI{1}{s} before the end of the record` -> `The fit started \SI{1.26}{s} after the first large peak and ended \SI{1.26}{s} before the end of the record` (1 s nominal)
7. `agree within 7\%` -> `agree within 7\% (spring 1) and 12\% (spring 2)`
8. `\pm 0.15_{\rm clock}` -> `\pm 0.12_{\rm clock}`
9. `The mechanical loss is about \SI{0.25}{mW}` -> `The mechanical loss is about \SI{0.10}{mW}`
10. `harmonic at \SI{126.2}{Hz}` -> `harmonic at \SI{126.1}{Hz}`
11. `lie 4--8\% below the static-$k$ predictions` -> `lie 4--7\% below the static-$k$ predictions`

Note for #19: the 94 µV maximum is from electronics.md only; recomputation from raw data gives 80-88 µV. Authors should confirm the window or write `29--88`.
