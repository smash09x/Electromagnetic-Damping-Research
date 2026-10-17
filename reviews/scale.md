# Scale audit

Data lattice (21 files, 2761 distinct values, 2773 codes): step = 23.64726 +/- 0.00001 uV; all values fit k*step + offset within 0.01 uV. Fractional offset V_ref*D/V_s = n + 0.834, so V_ref/V_s is not exactly 1/2 in the flashed code.

Excluded: repo set 3.3/4095/35 (23.025 uV); gain 34 with 3.3 (23.70 uV). Oversample_Factor 50 only truncates onto the integer lattice; it does not change the step.

No round set matches exactly. Closest: gain 35, sourceVoltage 3.39, divisor 4096 = 23.6468 uV (21 ppm low; residuals to 0.7 uV versus 0.01 observed), so treat as effective, not exact.

True scale (LSB = 3.3/4096, G = 35): 23.019 uV/code. Multiply reported EMF by 0.973 (damping coefficient c by 0.947). With G = 36: 0.946. Verify G and the 3V3 rail with a DMM.
