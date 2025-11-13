import numpy as np
from pathlib import Path


from gcm.analysis import scan_eps, save_scan_to_csv, plot_sigma_vs_eps, theory_boundaries




def test_scan_eps_and_io(tmp_path: Path):
    mu = 1.9
    eps_grid = np.array([0.2, 0.7, 1.1]) # desordenado → ordenado dessinc. → ordenado sinc.


    res = scan_eps(
        mu=mu,
        eps_grid=eps_grid,
        N=256,
        T_burn=500,
        T_meas=500,
        init="half_half",
        seed_base=2025,
        tol_sync=1e-6,
    )

    assert res.eps_grid.shape == eps_grid.shape
    assert res.sigma_mean.shape == eps_grid.shape
    assert res.escaped_frac.shape == eps_grid.shape
    assert res.is_synced.shape == eps_grid.shape

    # Expectativa qualitativa: sigma média em 1.1 < sigma média em 0.2
    assert res.sigma_mean[-1] < res.sigma_mean[0]


    # salvar CSV
    csv_path = tmp_path / "data" / "scan_eps_quick.csv"
    out_csv = save_scan_to_csv(res, csv_path)
    assert out_csv.exists()
    txt = out_csv.read_text(encoding="utf-8")
    assert txt.startswith("# mu=")

    # figura
    fig_path = tmp_path / "figs" / "sigma_vs_eps_quick.png"
    out_fig = plot_sigma_vs_eps(res, outpath=fig_path, show=False)
    assert out_fig.exists()

    # fronteiras teóricas (sanidade)
    bounds = theory_boundaries(mu)
    eps_sync_inf, eps_sync_sup = bounds["eps_sync"]
    assert eps_sync_inf < eps_sync_sup


data_path = Path("test_analysis")
test_scan_eps_and_io(data_path)