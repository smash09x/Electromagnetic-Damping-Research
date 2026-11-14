"""Extended analysis (v2): forward model, DAQ injection-recovery, measured coupling function, damping law, ADC nonlinearity.

Usage:  python run_extended.py        (after run_all.py, which this does not replace)
Reads   Data/Raw/, Data/Video/, Data/Results/
Writes  Data/Results/extended/  (JSON results, figures, logs)
"""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.abspath(os.path.join(HERE, '..', '..', '..', 'Data', 'Results', 'extended')); LOGS = os.path.join(OUT, 'logs')
os.makedirs(LOGS, exist_ok=True)
STEPS = [
    ('check_real.py',       'Estimators reproduce final_table.csv; harmonic content of every run'),
    ('validate.py',         'Forward model: geometry-only test, effective coupling, unfitted predictions'),
    ('inject.py',           'Injection-recovery through the simulated as-built DAQ'),
    ('kappa_recon.py',      'Coupling function kappa(z) from the 24 July recordings; shorted-coil prediction'),
    ('kappa_extra.py',      '23 July session: third kappa(z) set, decay rate, independent clock factor'),
    ('damping_law.py',      'Decay law of the motion from the video tracks'),
    ('adc_nonlinearity.py', 'The 52-55 Hz feature: harmonic comb from the RP2040 ADC step error'),
    ('figs.py',             'Figure: simulation against measurement'),
    ('kappa_fig.py',        'Figure: measured coupling function and prediction'),
    ('inl_fig.py',          'Figure: level-dependent ADC error'),
]
env = dict(os.environ, PYTHONPATH=HERE + os.pathsep + os.path.join(HERE, '..'))
for i, (script, what) in enumerate(STEPS, 1):
    print(f'[{i}/{len(STEPS)}] {what}', flush=True)
    r = subprocess.run([sys.executable, os.path.join(HERE, script)], cwd=OUT, capture_output=True, text=True, env=env)
    open(os.path.join(LOGS, script.replace('.py', '.txt')), 'w').write(r.stdout + r.stderr)
    if r.returncode: sys.exit(f'{script} failed; see {LOGS}')
print('Done. Results in', OUT)
