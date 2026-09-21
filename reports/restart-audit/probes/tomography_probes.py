"""Read-only numerical checks for the tomography audit; never executes notebooks."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import scipy
import xlrd
from scipy.special import gammaln
from scipy.stats import poisson

parser = argparse.ArgumentParser()
parser.add_argument("repository", type=Path)
args = parser.parse_args()
data = args.repository / "KAN_assisted tomography" / "data"
print(f"numpy={np.__version__}, scipy={scipy.__version__}, xlrd={xlrd.__version__}")

for path in sorted(data.glob("*.xls")):
    sheet = xlrd.open_workbook(path).sheet_by_index(0)
    rows = np.array([sheet.row_values(i) for i in range(1, sheet.nrows)])
    print(f"\n{path.name}: rows={len(rows)}, columns={sheet.ncols}")
    print("headers:", sheet.row_values(0))
    print("brightness range:", rows[:, 0].min(), rows[:, 0].max())
    print("phase range:", rows[:, 1].min(), rows[:, 1].max())
    counts = rows[:, 2:]
    print(
        "integer nonnegative counts:",
        bool(np.all(counts >= 0) and np.all(counts == np.floor(counts))),
    )
    print("total count range:", counts.sum(axis=1).min(), counts.sum(axis=1).max())
    if sheet.ncols != 4:
        continue
    brightness, phase, count0, count1 = rows.T
    total = count0 + count1
    probability = count1 / total
    keys = np.round(brightness, 4)
    levels = np.unique(keys)
    print("brightness levels:", len(levels))
    print("probability range:", probability.min(), probability.max())
    print(
        "plug-in binomial RMS floor:",
        np.sqrt(np.mean(probability * (1 - probability) / total)),
    )
    print("tail at D=58:", poisson.sf(57, brightness.max()))
    print(
        "smallest D for Poisson tail <=1e-8:",
        int(poisson.isf(1e-8, brightness.max()) + 1),
    )
    gaps = []
    for level in levels:
        angles = np.sort(phase[keys == level] % (2 * np.pi))
        gaps.extend(np.diff(np.r_[angles, angles[0] + 2 * np.pi]))
    print("wrapped phase gap range:", min(gaps), max(gaps))
    if "MOESM4" not in path.name:
        continue
    moesm4_levels = levels
    for band in range(1, 5):
        means, integrals, dc_leakage = [], [], []
        for level in levels:
            mask = keys == level
            angles = phase[mask] % (2 * np.pi)
            order = np.argsort(angles)
            angles, response = angles[order], probability[mask][order]
            samples = response * np.exp(-1j * band * angles)
            means.append(samples.mean())
            integrals.append(
                np.trapezoid(
                    np.r_[samples, samples[0]], np.r_[angles, angles[0] + 2 * np.pi]
                )
                / (2 * np.pi)
            )
            dc_leakage.append(abs(np.exp(-1j * band * angles).mean()))
        print(
            f"band={band}, mean max imag={max(abs(np.imag(means))):.8f}, periodic trapezoid max imag={max(abs(np.imag(integrals))):.8f}, DC leakage max={max(dc_leakage):.8f}"
        )
    amplitudes = np.sqrt(levels)
    for band in range(5):
        j = np.arange(58 - band)
        kernel = np.exp(
            -amplitudes[:, None] ** 2
            + (2 * j + band) * np.log(amplitudes[:, None])
            - 0.5 * (gammaln(j + band + 1) + gammaln(j + 1))
        )
        singular = np.linalg.svd(kernel, compute_uv=False)
        print(
            f"band={band}, shape={kernel.shape}, condition={singular[0]/singular[-1]:.6e}, default numeric rank={np.linalg.matrix_rank(kernel)}"
        )

angles = 0.123 + 2 * np.pi * np.arange(40) / 40
print(
    "\nShifted uniform grid constant->band1 leakage:", abs(np.exp(-1j * angles).mean())
)
print(
    "Normalized fidelity counterexample F(.2 I,.8 I):",
    (2 * np.sqrt(0.2 * 0.8)) ** 2 / (0.4 * 1.6),
    "probability gap=0.6",
)
matrix = 0.5 * np.eye(6)
matrix[0, 5] = matrix[5, 0] = 0.2
coherent = np.exp(-1 + np.arange(6) * 0.5 * np.log(2) - 0.5 * gammaln(np.arange(6) + 1))
masked = matrix.copy()
masked[0, 5] = masked[5, 0] = 0
print("Full PSD matrix eigenvalues:", np.linalg.eigvalsh(matrix))
print(
    "Full-minus-L4 Born prediction:",
    coherent @ matrix @ coherent - coherent @ masked @ coherent,
)

print("\nSaved stress sweep split reproduction (same RNG call order):")
for seed in range(5):
    rng = np.random.default_rng(seed)
    for fraction in [1, 0.6, 0.4, 0.25]:
        train = np.sort(
            rng.choice(
                moesm4_levels, max(8, int(fraction * len(moesm4_levels))), replace=False
            )
        )
        test = moesm4_levels[~np.isin(moesm4_levels, train)]
        outside = (test < train.min()) | (test > train.max())
        print(
            f"seed={seed}, fraction={fraction:.2f}, train={len(train)}, heldout={len(test)}, outside-training-range={int(outside.sum())}"
        )
