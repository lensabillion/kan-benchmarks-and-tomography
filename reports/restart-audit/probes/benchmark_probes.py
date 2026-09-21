"""Read-only, bounded implementation probes; no fitting or checkpoint loading."""

from __future__ import annotations
import ast
import argparse
import json
from pathlib import Path
from types import SimpleNamespace
import sys
import numpy as np
import torch
from scipy.interpolate import BSpline
from kan.spline import B_batch, coef2curve, curve2coef, extend_grid

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("repository", type=Path)
ROOT = parser.parse_args().repository.resolve()


def definitions(path, cell, env):
    source = "".join(json.loads((ROOT / path).read_text())["cells"][cell]["source"])
    nodes = ast.parse(source).body
    module = ast.Module(
        body=[n for n in nodes if isinstance(n, (ast.FunctionDef, ast.ClassDef))],
        type_ignores=[],
    )
    exec(compile(module, path, "exec"), env)


def probes():
    env = {"np": np, "sigmoid": lambda x: 1 / (1 + np.exp(-x))}
    definitions("KAN vs MLP /MLP_vs_KAN_Research_Demo.ipynb", 11, env)
    net = env["KAN"](2)
    net.layer1.coeff *= 5
    net.layer2.coeff *= 5
    x = np.array([[-0.3, 0.2, 0.5, -0.7], [0.1, -0.5, 0.9, 0.6]])
    y = np.array([[0.0, 1.0, 0.0, 1.0]])
    a = net.forward(x)
    old, scale = net.layer2.coeff.copy(), net.layer2.scale.copy()
    net.layer2.backward((a - y) / 4, 1.0)
    analytic = old - net.layer2.coeff
    net.layer2.coeff[:] = old
    net.layer2.scale[:] = scale
    ix = np.unravel_index(abs(analytic).argmax(), analytic.shape)
    eps = 1e-5
    net.layer2.coeff[ix] += eps
    plus = net.compute_cost(net.forward(x), y)
    net.layer2.coeff[ix] -= 2 * eps
    minus = net.compute_cost(net.forward(x), y)
    print(
        "gradient numerical/implemented (4 samples):",
        (plus - minus) / (2 * eps) / analytic[ix],
    )
    knots = env["build_knots"](-2, 2, 5, 3)
    x = np.array([[3.0]])
    _, deriv = env["eval_bspline"](x, knots, 3)
    bp = env["eval_bspline"](x + eps, knots, 3)[0]
    bm = env["eval_bspline"](x - eps, knots, 3)[0]
    print(
        "outside-domain derivative reported/numerical:",
        abs(deriv).max(),
        abs((bp - bm) / (2 * eps)).max(),
    )
    x = np.linspace(-2, 2, 37)[None, :]
    b, _ = env["eval_bspline"](x, knots, 3)
    ref = BSpline.design_matrix(x[0], knots, 3).toarray()
    print("basis max difference versus SciPy:", abs(b[0] - ref).max())
    print("partition-unity max error:", abs(b.sum(2) - 1).max())
    env = {
        "torch": torch,
        "nn": torch.nn,
        "B_batch": B_batch,
        "coef2curve": coef2curve,
        "curve2coef": curve2coef,
        "extend_grid": extend_grid,
    }
    definitions(
        "KAN vs BSpline_MLP/Example_1_function_fitting_MLP + BSpline.ipynb", 2, env
    )
    torch.manual_seed(0)
    act = env["BSplineActivation"](2).double()
    x = torch.linspace(-0.3, 0.6, 100, dtype=torch.float64)[:, None].repeat(1, 2)
    before = act(x).detach()
    act.update_grid_from_samples(x)
    print(
        "grid-update max forward discontinuity:",
        (act(x).detach() - before).abs().max().item(),
    )
    sys.path.insert(0, str(ROOT / "KAN vs BSpline_MLP/KANbeFair/src"))
    from models.bspline_mlp import BSpline_MLP
    from models.kanbefair import KANbeFair

    args = SimpleNamespace(
        input_size=2,
        output_size=1,
        layers_width=[3],
        batch_norm=False,
        kan_bspline_grid=3,
        kan_grid_range=[-1, 1],
        kan_bspline_order=3,
        kan_shortcut_function=torch.nn.SiLU(),
        kan_shortcut_name="silu",
    )
    for cls in (BSpline_MLP, KANbeFair):
        m = cls(args)
        m(torch.rand(4, 2)).square().mean().backward()
        print(
            cls.__name__,
            "formula/trainable/active/all:",
            m.total_parameters(),
            sum(p.numel() for p in m.parameters() if p.requires_grad),
            sum(p.numel() for p in m.parameters() if p.grad is not None),
            sum(p.numel() for p in m.parameters()),
        )
    args.layers_width, args.kan_bspline_grid = [5], 20
    torch.manual_seed(17)
    m1 = KANbeFair(args)
    torch.manual_seed(99)
    m2 = KANbeFair(args)
    print(
        "distinct caller seeds give identical KAN parameters:",
        all(torch.equal(p, q) for p, q in zip(m1.parameters(), m2.parameters())),
    )
    m1(torch.rand(4, 2)).square().mean().backward()
    print(
        "Feynman anchor trainable/active:",
        sum(p.numel() for p in m1.parameters() if p.requires_grad),
        sum(p.numel() for p in m1.parameters() if p.grad is not None),
    )
    import importlib.metadata

    print(
        "runtime:",
        sys.version.split()[0],
        "numpy",
        np.__version__,
        "torch",
        torch.__version__,
        "pykan",
        importlib.metadata.version("pykan"),
    )


probes()
