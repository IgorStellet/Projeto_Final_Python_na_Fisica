"""
gcm.metrics
===========
Métricas e estatísticas: sigma (sincronização), spins, magnetização,
parâmetro de ordem |<M>| e curva de persistência p_t.
"""

from __future__ import annotations

import numpy as np

__all__ = [
    "sigma",
    "spins",
    "magnetization",
    "order_param_M",
    "persistence_curve",
    "sigma_mean",
]


def sigma(x: np.ndarray) -> float:
    """Desvio-padrão instantâneo entre mapas.

    Parâmetros
    ----------
    x : np.ndarray, shape (N,)
        Estado no instante.

    Retorna
    -------
    float
        σ_t = std(x).
    """
    x = np.asarray(x, dtype=float)
    return float(np.std(x))


def spins(x: np.ndarray) -> np.ndarray:
    """Converte estado em spins s_i ∈ {-1, +1}.

    Convenção: valores exatamente 0 recebem +1.

    Parâmetros
    ----------
    x : np.ndarray, shape (N,)

    Retorna
    -------
    np.ndarray, shape (N,), dtype=int
        Vetor de spins.
    """
    x = np.asarray(x, dtype=float)
    s = np.ones_like(x, dtype=int)
    s[x < 0.0] = -1
    return s


def magnetization(x: np.ndarray) -> float:
    """Magnetização instantânea M_t = (1/N) * sum_i s_i.

    Parâmetros
    ----------
    x : np.ndarray, shape (N,)

    Retorna
    -------
    float
        Magnetização no instante.
    """
    s = spins(x)
    return float(np.mean(s))


def order_param_M(series_M: np.ndarray) -> float:
    """Parâmetro de ordem |<M>| (módulo da média temporal da magnetização).

    Parâmetros
    ----------
    series_M : np.ndarray, shape (T,)
        Série temporal de magnetização.

    Retorna
    -------
    float
        |<M>| = | mean(series_M) |.
    """
    series_M = np.asarray(series_M, dtype=float)
    return float(abs(series_M.mean()))


def persistence_curve(spin_series: np.ndarray) -> np.ndarray:
    """Curva de persistência p_t: fração que nunca mudou de sinal desde t=0.

    Implementação eficiente sem alocar matrizes gigantes:
    - Mantém um booleano `changed` por sítio.
    - Em cada t, atualiza `changed |= (s_t != s_0)` e computa p_t = mean(~changed).

    Parâmetros
    ----------
    spin_series : np.ndarray, shape (T, N), dtype=int
        Série de spins no tempo.

    Retorna
    -------
    np.ndarray, shape (T,)
        Vetor p_t.
    """
    S = np.asarray(spin_series)
    if S.ndim != 2:
        raise ValueError("spin_series deve ter shape (T, N).")

    T, N = S.shape
    s0 = S[0]
    changed = np.zeros(N, dtype=bool)
    p = np.empty(T, dtype=float)
    p[0] = 1.0  # no t=0 ninguém mudou

    for t in range(1, T):
        changed |= (S[t] != s0)
        p[t] = 1.0 - changed.mean()

    return p


def sigma_mean(sigmas: np.ndarray) -> float:
    """Média temporal de σ_t (após descarte já aplicado pelo chamador).

    Parâmetros
    ----------
    sigmas : np.ndarray, shape (T_meas,)

    Retorna
    -------
    float
        <σ> = mean(sigmas)
    """
    sigmas = np.asarray(sigmas, dtype=float)
    return float(sigmas.mean())

