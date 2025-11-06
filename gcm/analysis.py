"""
gcm.analysis
============
Pipelines reprodutíveis para varreduras em ε, comparação com fronteiras analíticas,
salvamento de CSVs e geração de figuras.

Foco da Semana 1:
- Reproduzir/verificar fronteiras de sincronização (teóricas) e detectar escape.
- Varredura 1D em ε para um μ fixo (ex.: μ = 1.9), medindo <σ>.

Observação: as funções aqui NÃO escondem o custo computacional. Parâmetros como
T_burn e T_meas devem ser ajustados conscientemente.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import numpy as np
import matplotlib.pyplot as plt

from .core import Config, GloballyCoupledMaps
from .maps import sync_boundaries, escape_boundaries
from .metrics import sigma as sigma_metric

__all__ = [
    "ScanResult",
    "theory_boundaries",
    "scan_eps",
    "save_scan_to_csv",
    "plot_sigma_vs_eps",
]


@dataclass
class ScanResult:
    """Resultado de uma varredura 1D em ε para μ fixo.

    Atributos
    ---------
    mu : float
    eps_grid : np.ndarray, shape (K,)
    sigma_mean : np.ndarray, shape (K,)
        Média temporal de σ_t após burn-in.
    escaped_frac : np.ndarray, shape (K,)
        Fração de passos (no período de medição) em que ocorreu escape (|x|>1)
        em pelo menos um sítio. Útil como indicador de regime turbulento/escape.
    is_synced : np.ndarray, shape (K,), dtype=bool
        Marcador de sincronização via limiar numérico (σ̄ < tol_sync).
    meta : dict
        Metadados do experimento (N, T_burn, T_meas, seed_base, init, tol_sync).
    """

    mu: float
    eps_grid: np.ndarray
    sigma_mean: np.ndarray
    escaped_frac: np.ndarray
    is_synced: np.ndarray
    meta: Dict[str, Any]


def theory_boundaries(mu: float) -> dict:
    """Coleta as fronteiras teóricas úteis para sobreposição em gráficos.

    Parâmetros
    ----------
    mu : float

    Retorna
    -------
    dict
        {
          "mu": mu,
          "eps_sync": (eps_sync_inf, eps_sync_sup),
          "eps_escape": (eps_esc_low, eps_esc_high),
        }
    """
    eps_sync = sync_boundaries(mu)
    eps_esc = escape_boundaries(mu)
    return {"mu": mu, "eps_sync": eps_sync, "eps_escape": eps_esc}


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def scan_eps(
    mu: float,
    eps_grid: np.ndarray,
    N: int,
    *,
    T_burn: int = 2_000,
    T_meas: int = 2_000,
    init: str = "half_half",
    seed_base: int | None = 12345,
    tol_sync: float = 1e-7,
) -> ScanResult:
    """Varre ε e mede <σ>, escape e sincronização para μ fixo.

    Procedimento (para cada ε):
    - Cria sistema GCM(N, ε, μ).
    - reset(init="half_half") (exige 1 < |μ| < 2) ou "uniform".
    - Roda T_burn passos sem registrar.
    - Roda T_meas passos medindo σ_t e se houve escape.
    - σ̄ = mean(σ_t); marcamos `is_synced = (σ̄ < tol_sync)`.

    Parâmetros
    ----------
    mu : float
    eps_grid : np.ndarray, shape (K,)
        Valores de ε a varrer.
    N : int
        Tamanho do sistema.
    T_burn : int, padrão 2000
        Passos de transiente a descartar.
    T_meas : int, padrão 2000
        Passos de medição.
    init : {"half_half", "uniform"}, padrão "half_half"
        Modo de ICs.
    seed_base : int | None, padrão 12345
        Semente base; variamos por índice de ε para reprodutibilidade.
    tol_sync : float, padrão 1e-7
        Limiar para marcar sincronização via σ̄.

    Retorna
    -------
    ScanResult
        Estrutura com arrays por ε e metadados.
    """
    eps_grid = np.asarray(eps_grid, dtype=float)
    K = eps_grid.size

    sigma_mean_arr = np.empty(K, dtype=float)
    escaped_frac_arr = np.empty(K, dtype=float)
    is_synced_arr = np.empty(K, dtype=bool)

    for k, eps in enumerate(eps_grid):
        seed = None if seed_base is None else (int(seed_base) + k)
        cfg = Config(N=N, eps=float(eps), mu=float(mu), seed=seed)
        sys = GloballyCoupledMaps(cfg)
        sys.reset(init="half_half" if init == "half_half" else "uniform")

        # Burn-in
        sys.run(T_burn, track=False)

        # Medição
        escaped_count = 0
        sigmas = np.empty(T_meas, dtype=float)
        for t in range(T_meas):
            sys.step()
            sigmas[t] = sigma_metric(sys.x)
            if sys.last_escaped_mask is not None and sys.last_escaped_mask.any():
                escaped_count += 1

        sigma_mean_arr[k] = float(sigmas.mean())
        escaped_frac_arr[k] = escaped_count / float(T_meas)
        is_synced_arr[k] = sigma_mean_arr[k] < tol_sync

    meta = dict(
        N=N,
        T_burn=T_burn,
        T_meas=T_meas,
        init=init,
        seed_base=seed_base,
        tol_sync=tol_sync,
    )
    return ScanResult(
        mu=float(mu),
        eps_grid=eps_grid,
        sigma_mean=sigma_mean_arr,
        escaped_frac=escaped_frac_arr,
        is_synced=is_synced_arr,
        meta=meta,
    )


def save_scan_to_csv(result: ScanResult, path: str | Path) -> Path:
    """Salva o resultado de `scan_eps` em CSV com colunas amigáveis.

    Colunas:
      eps, sigma_mean, escaped_frac, is_synced (0/1), mu, N, T_burn, T_meas, init, seed_base, tol_sync

    Parâmetros
    ----------
    result : ScanResult
    path : str | Path
        Caminho do CSV (será criado; diretórios pais serão gerados).

    Retorna
    -------
    Path
        Caminho final salvo.
    """
    path = Path(path)
    _ensure_parent(path)
    data = np.column_stack(
        [
            result.eps_grid,
            result.sigma_mean,
            result.escaped_frac,
            result.is_synced.astype(int),
        ]
    )
    header = (
        "eps,sigma_mean,escaped_frac,is_synced,"
        f"mu,N,T_burn,T_meas,init,seed_base,tol_sync\n"
    )
    # Cabeçalho de metadados na primeira linha + dados
    meta = result.meta
    meta_line = (
        f"# mu={result.mu}, N={meta['N']}, T_burn={meta['T_burn']}, T_meas={meta['T_meas']}, "
        f"init={meta['init']}, seed_base={meta['seed_base']}, tol_sync={meta['tol_sync']}\n"
    )
    with path.open("w", encoding="utf-8") as f:
        f.write(meta_line)
        f.write(header)
        np.savetxt(f, data, delimiter=",", fmt="%.10g")
    return path


def plot_sigma_vs_eps(
    result: ScanResult,
    *,
    outpath: str | Path | None = None,
    show: bool = False,
) -> Path | None:
    """Gera o gráfico σ̄(ε) com linhas verticais nas fronteiras teóricas.

    Parâmetros
    ----------
    result : ScanResult
    outpath : str | Path | None, padrão None
        Se fornecido, salva a figura em `outpath`. Diretórios pais serão criados.
    show : bool, padrão False
        Se True, exibe a figura (bloqueante em alguns ambientes locais).

    Retorna
    -------
    Path | None
        Caminho salvo, se `outpath` não for None.
    """
    bounds = theory_boundaries(result.mu)
    eps_sync_inf, eps_sync_sup = bounds["eps_sync"]
    eps_esc_low, eps_esc_high = bounds["eps_escape"]

    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    ax.plot(result.eps_grid, result.sigma_mean, marker="o", lw=1.5, ms=4, label=r"$\overline{\sigma}$")
    ax.set_xlabel(r"$\varepsilon$")
    ax.set_ylabel(r"$\overline{\sigma}$")
    ax.grid(True, alpha=0.25)

    # Linhas de referência (sincronização e escape)
    for x, ls, lab in [
        (eps_sync_inf, "--", "sync (inf)"),
        (eps_sync_sup, "--", "sync (sup)"),
        (eps_esc_low, ":", "escape (low)"),
        (eps_esc_high, ":", "escape (high)"),
    ]:
        if np.isfinite(x):
            ax.axvline(x, linestyle=ls, alpha=0.7, label=lab)

    ax.legend(loc="best", frameon=True)

    saved_path: Path | None = None
    if outpath is not None:
        saved_path = Path(outpath)
        _ensure_parent(saved_path)
        fig.tight_layout()
        fig.savefig(saved_path, dpi=200)
    if show:
        plt.show()
    plt.close(fig)
    return saved_path

