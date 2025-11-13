"""Testes/figuras progressivos (leves) para guiar a intuição.

Gera 3 imagens em `figs/` (baixo custo):
  1) Série temporal de UM mapa (índice fixo) sob ε ∈ {0.2, 0.7, 1.1}.
  2) Raster de SPINS para N mapas (ε=0.7) mostrando ordenação sem sincronismo total.
  3) Histogramas finais de x para ε=0.2 vs 1.1.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")  # headless
import matplotlib.pyplot as plt
from pathlib import Path

from gcm.core import Config, GloballyCoupledMaps
from gcm.metrics import spins
from gcm.analysis import scan_eps, save_scan_to_csv, plot_sigma_vs_eps


FIGS_DIR = Path("figs")
FIGS_DIR.mkdir(parents=True, exist_ok=True)


def _time_series_single_index(mu: float, eps_list, N=256, T_burn=300, T_meas=300, seed=777):
    i_pick = 0
    ts = {}
    for eps in eps_list:
        cfg = Config(N=N, eps=eps, mu=mu, seed=seed)
        sys = GloballyCoupledMaps(cfg)
        sys.reset(init="half_half")
        sys.run(T_burn, track=False)
        traj = sys.run(T_meas, track=True)
        ts[eps] = traj[:, i_pick]
    return ts


def test_fig_time_series_single_map():
    mu = 1.9
    eps_list = [0.2, 0.7, 1.1]
    ts = _time_series_single_index(mu, eps_list)

    plt.figure(figsize=(7.2, 3.2))
    for eps, y in ts.items():
        plt.plot(y, lw=1.0, label=f"ε={eps}")
    plt.xlabel("t (após burn-in)")
    plt.ylabel("x_i(t)")
    plt.title("Série temporal de um mapa para ε distintos (μ=1.9)")
    plt.legend()
    plt.grid(alpha=0.25)
    out = FIGS_DIR / "TS_single_index_eps_0.2_0.7_1.1.png"
    plt.tight_layout(); plt.savefig(out, dpi=160); plt.close()
    assert out.exists()

test_fig_time_series_single_map()

def test_fig_raster_spins_ordered_desync():
    mu = 1.9
    eps = 0.7  # janela ordenada dessíncrona esperada
    cfg = Config(N=256, eps=eps, mu=mu, seed=1234)
    sys = GloballyCoupledMaps(cfg)
    sys.reset(init="half_half")
    T_burn, T_meas = 300, 300
    sys.run(T_burn, track=False)
    traj = sys.run(T_meas, track=True)

    S = spins(traj)
    plt.figure(figsize=(7.2, 3.2))
    plt.imshow(S.T, aspect="auto", origin="lower", interpolation="nearest")
    plt.xlabel("t (após burn-in)")
    plt.ylabel("índice i")
    plt.title("Raster de spins (ε=0.7, μ=1.9)")
    out = FIGS_DIR / "Raster_spins_eps_0.7.png"
    plt.tight_layout(); plt.savefig(out, dpi=160); plt.close()
    assert out.exists()

test_fig_raster_spins_ordered_desync()

def test_fig_histograms_eps_compare():
    mu = 1.9
    N = 512
    T_burn, T_meas = 300, 300
    hist_data = {}
    for eps in [0.2, 1.1]:
        cfg = Config(N=N, eps=eps, mu=mu, seed=987)
        sys = GloballyCoupledMaps(cfg)
        sys.reset(init="half_half")
        sys.run(T_burn + T_meas, track=False)
        hist_data[eps] = sys.x.copy()

    plt.figure(figsize=(7.2, 3.2))
    for eps, x in hist_data.items():
        plt.hist(x, bins=50, histtype="step", density=True, label=f"ε={eps}")
    plt.xlabel("x")
    plt.ylabel("densidade")
    plt.title("Distribuições finais de x (μ=1.9)")
    plt.legend()
    plt.grid(alpha=0.25)
    out = FIGS_DIR / "Hist_x_eps_0.2_vs_1.1.png"
    plt.tight_layout(); plt.savefig(out, dpi=160); plt.close()
    assert out.exists()

test_fig_histograms_eps_compare()

def test_quick_scan_and_outputs_repo_paths():
    mu = 1.9
    eps_grid = np.linspace(0.2, 1.2, 6)
    res = scan_eps(mu=mu, eps_grid=eps_grid, N=256, T_burn=400, T_meas=400, seed_base=314)

    data_path = Path("data") / "scan_eps_quick_repo.csv"
    fig_path = Path("figs") / "sigma_vs_eps_quick_repo.png"

    save_scan_to_csv(res, data_path)
    out_fig = plot_sigma_vs_eps(res, outpath=fig_path, show=False)

    assert data_path.exists()
    assert out_fig.exists()

test_quick_scan_and_outputs_repo_paths()