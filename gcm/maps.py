"""
gcm.maps
========
Mapa local biestável (linear por partes e ímpar) e utilidades analíticas.

Referência principal:
- Alvarez-Llamoza & Cosenza (2014), "Synchronization and phase ordering in globally
  coupled chaotic maps".

Este módulo define:
- f(x; mu): mapa local `bistable_map` (vetorizado).
- Rotinas auxiliares para intervalos biestáveis I_±, expoente de Lyapunov local
  e fronteiras analíticas (sincronização e escape).
"""

from __future__ import annotations

from typing import Tuple

import numpy as np

__all__ = ["_validate_mu",
    "bistable_map",
    "bistable_intervals",
    "lyapunov_local",
    "sync_boundaries",
    "escape_boundaries",
]


def _validate_mu(mu: float) -> None:
    """Valida o parâmetro mu em um domínio físico razoável.

    Não impomos o domínio estrito do paper aqui (mu em [-3, 3]),
    mas avisamos se mu==0, pois algumas fórmulas (p.ex. escape) o utilizam no denominador.
    """
    if not np.isfinite(mu):
        raise ValueError("mu deve ser finito.")
    if abs(mu) < 1e-15:
        raise ValueError("mu não pode ser zero (|mu| ~ 0), pois certas fórmulas dividem por mu.")


def bistable_map(x: np.ndarray, mu: float, *, out: np.ndarray | None = None) -> np.ndarray:
    """Aplica o mapa local biestável (linear por partes e ímpar).

    Definição (x ∈ [-1, 1]):
        f(x; mu) =
          - 2*mu/3 - mu*x,   se x ∈ [-1, -1/3]
            mu*x,            se x ∈ (-1/3,  1/3)
            2*mu/3 - mu*x,   se x ∈ [ 1/3,  1]

    Observações
    ----------
    - O mapa é ímpar: f(-x; mu) = -f(x; mu).
    - Em (1 < |mu| < 2), o sistema exibe caos e biestabilidade (dois atratores caóticos simétricos).
    - Esta função é vetorizada e não realiza "clipping" para [-1, 1]. O escape (|x|>1)
      deve ser detectado no nível do integrador/sistema.

    Parâmetros
    ----------
    x : np.ndarray
        Vetor/array com estado(s) em [-1, 1] idealmente.
    mu : float
        Parâmetro do mapa.
    out : np.ndarray, opcional
        Buffer de saída (mesmo shape de x), se desejado.

    Retorna
    -------
    np.ndarray
        f(x; mu) com mesmo shape que `x`.
    """
    _validate_mu(mu)
    x = np.asarray(x, dtype=float)
    y = x if out is None else out  # pode sobrescrever em buffer externo

    # Máscaras das faixas
    m_left = x <= -1.0 / 3.0
    m_mid = (x > -1.0 / 3.0) & (x < 1.0 / 3.0)
    m_right = x >= 1.0 / 3.0

    # Aplicação por partes (vetorizada)
    if y is x:
        y = np.empty_like(x, dtype=float)
    y[m_left] = -2.0 * mu / 3.0 - mu * x[m_left]
    y[m_mid] = mu * x[m_mid]
    y[m_right] = 2.0 * mu / 3.0 - mu * x[m_right]
    return y


def bistable_intervals(mu: float) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    """Intervalos dos atratores caóticos I_- e I_+ para (1 < |mu| < 2).

    Fórmulas (para |mu| em (1, 2)):
        I_+ = [ mu*(2 - mu)/3 , mu/3 ]
        I_- = -I_+  = [ -mu/3 , -mu*(2 - mu)/3 ]

    Quando mu < 0, as expressões acima continuam válidas: I_+ terá limites com o mesmo sinal de mu.

    Parâmetros
    ----------
    mu : float
        Parâmetro local.

    Retorna
    -------
    ( (a_minus, b_minus), (a_plus, b_plus) ) : tupla de tuplas
        Intervalos I_- e I_+ (cada par ordenado a<=b).

    Levanta
    -------
    ValueError
        Se |mu| não pertencer ao regime biestável (1, 2).
    """
    _validate_mu(mu)
    if not (1.0 < abs(mu) < 2.0):
        raise ValueError("bistable_intervals: requer 1 < |mu| < 2 para biestabilidade.")

    a_plus = mu * (2.0 - mu) / 3.0
    b_plus = mu / 3.0
    a_minus = -b_plus
    b_minus = -a_plus

    # Ordena cada par para robustez (em caso de mu<0)
    i_minus = (min(a_minus, b_minus), max(a_minus, b_minus))
    i_plus = (min(a_plus, b_plus), max(a_plus, b_plus))
    return i_minus, i_plus


def lyapunov_local(mu: float) -> float:
    """Expoente de Lyapunov local do mapa por partes.

    Em regime linear por partes com derivada de módulo constante em cada ramo,
    temos λ_local = ln |mu| (para o mapa central e em regime caótico).

    Parâmetros
    ----------
    mu : float

    Retorna
    -------
    float
        λ_local = log(|mu|).
    """
    _validate_mu(mu)
    return float(np.log(abs(mu)))


def sync_boundaries(mu: float) -> tuple[float, float]:
    """Fronteiras analíticas de sincronização para o acoplamento global.

    Da análise linear do estado sincronizado:
        (1 - ε) * e^{λ_local} = ±1  ⇒  (1 - ε) * |mu| = ±1

    Assim:
        ε_sync_inf = 1 - 1/|mu|
        ε_sync_sup = 1 + 1/|mu|

    Parâmetros
    ----------
    mu : float

    Retorna
    -------
    (ε_sync_inf, ε_sync_sup) : tuple[float, float]
        Limites inferior e superior (o superior pode ultrapassar 1).
    """
    _validate_mu(mu)
    inv = 1.0 / abs(mu)
    return 1.0 - inv, 1.0 + inv


def escape_boundaries(mu: float) -> tuple[float, float]:
    """Fronteiras de escape aproximadas via (1 - ε) * mu = ±3.

    A condição de escape (fora de [-1, 1]) deriva das quebras de linearidade:
        (1 - ε) * mu = +3  ⇒  ε = 1 - 3/mu
        (1 - ε) * mu = -3  ⇒  ε = 1 + 3/mu

    Parâmetros
    ----------
    mu : float

    Retorna
    -------
    (ε_esc_low, ε_esc_high) : tuple[float, float]
        Dois valores ordenados (menor, maior). Podem estar fora de [0, 1].

    Observação
    ----------
    São fronteiras analíticas de referência; na prática, a ocorrência de escape
    depende do estado visitado e do regime de parâmetros.
    """
    _validate_mu(mu)
    eps1 = 1.0 - 3.0 / mu
    eps2 = 1.0 + 3.0 / mu
    eps_low, eps_high = (min(eps1, eps2), max(eps1, eps2))
    return float(eps_low), float(eps_high)

