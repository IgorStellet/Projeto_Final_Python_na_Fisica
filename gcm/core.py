"""
gcm.core
========
Motor de evolução para mapas caóticos globalmente acoplados.

Atualização:
    x_i(t+1) = (1 - eps) * f(x_i(t); mu) + (eps / N) * sum_j f(x_j(t); mu)

Escolhas de projeto:
- API clara com `Config` imutável (dataclass frozen).
- Estado `x` em float64 para estabilidade numérica.
- `reset` com modos de ICs (meio-a-meio em I_± ou uniforme em [-1,1]).
- `step` e `run` vetorizados. `run` pode retornar a trajetória (track=True).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

import numpy as np

from .maps import bistable_map, bistable_intervals, _validate_mu

__all__ = ["Config", "GloballyCoupledMaps"]


@dataclass(frozen=True)
class Config:
    """Configuração imutável do sistema globalmente acoplado.

    Parâmetros
    ----------
    N : int
        Número de mapas (tamanho do sistema).
    eps : float
        Acoplamento global ε.
    mu : float
        Parâmetro local do mapa.
    seed : int | None, padrão None
        Semente para reprodutibilidade (usada em `reset`).
    """

    N: int
    eps: float
    mu: float
    seed: Optional[int] = None

    def __post_init__(self) -> None:
        if self.N <= 0:
            raise ValueError("N deve ser positivo.")
        if not np.isfinite(self.eps):
            raise ValueError("eps deve ser finito.")
        _validate_mu(self.mu)


class GloballyCoupledMaps:
    """Sistema de mapas globalmente acoplados.

    Métodos principais
    ------------------
    - reset(init): inicializa o estado `x`.
    - step(): executa 1 passo de tempo.
    - run(T, discard, track): executa T passos, com descarte opcional do transiente.

    Atributos
    ---------
    cfg : Config
        Configuração imutável do sistema.
    rng : np.random.Generator
        Gerador pseudoaleatório para ICs.
    x : np.ndarray, shape (N,)
        Estado atual do sistema.
    last_escaped_mask : np.ndarray[bool] | None
        Máscara de escape detectada no último `step` (|x| > 1). None antes do primeiro passo.
    """

    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.rng = np.random.default_rng(cfg.seed)
        self.x = np.zeros(cfg.N, dtype=float)
        self.last_escaped_mask: np.ndarray | None = None

    # ------------------------ inicialização / ICs ------------------------ #

    def reset(
        self,
        init: Literal["half_half", "uniform"] = "half_half",
        rng: np.random.Generator | None = None,
    ) -> None:
        """Reinicializa o estado `x` de acordo com o modo escolhido.

        Parâmetros
        ----------
        init : {"half_half", "uniform"}, padrão "half_half"
            - "half_half": amostra metade dos índices em I_+ e metade em I_-, com
              valores uniformes em cada intervalo e indices embaralhados.
              Requer 1 < |mu| < 2 (regime biestável) para que I_± existam.
            - "uniform": amostra uniforme em [-1, 1] (modo de depuração).
        rng : np.random.Generator, opcional
            Gerador a ser usado; por padrão utiliza `self.rng`.
        """
        _rng = self.rng if rng is None else rng
        N = self.cfg.N
        mu = self.cfg.mu

        if init == "uniform":
            self.x = _rng.uniform(-1.0, 1.0, size=N)
            self.last_escaped_mask = None
            return

        if init != "half_half":
            raise ValueError('init deve ser "half_half" ou "uniform".')

        # I_± apenas no regime biestável
        i_minus, i_plus = bistable_intervals(mu)  # pode levantar ValueError se fora do regime
        half = N // 2
        rest = N - half

        x_plus = _rng.uniform(i_plus[0], i_plus[1], size=half)
        x_minus = _rng.uniform(i_minus[0], i_minus[1], size=rest)
        x = np.concatenate([x_plus, x_minus])
        _rng.shuffle(x)
        self.x = x.astype(float, copy=False)
        self.last_escaped_mask = None

    # ----------------------------- dinâmica ----------------------------- #

    def step(self) -> None:
        """Executa um passo de tempo.

        Aplica y = f(x; mu) de forma vetorizada, calcula a média e atualiza:
            x <- (1 - eps) * y + eps * mean(y)

        Também atualiza `last_escaped_mask` (True onde |x| > 1 após o passo).
        """
        y = bistable_map(self.x, self.cfg.mu)
        mean_y = float(y.mean())
        self.x = (1.0 - self.cfg.eps) * y + self.cfg.eps * mean_y
        self.last_escaped_mask = np.abs(self.x) > 1.0

    def run(
        self,
        T: int,
        discard: int = 0,
        *,
        track: bool = False,
    ) -> np.ndarray | None:
        """Roda T passos de tempo.

        Parâmetros
        ----------
        T : int
            Número total de passos.
        discard : int, padrão 0
            Número de passos iniciais a descartar (transiente), caso `track=True`.
        track : bool, padrão False
            Se True, retorna a trajetória como array (T - discard, N). Caso False, retorna None.

        Retorna
        -------
        np.ndarray | None
            Trajetória (T - discard, N) se `track=True`; caso contrário None.

        Notas
        -----
        - Mesmo com track=False, `last_escaped_mask` é atualizado a cada `step`.
        - Este método não calcula métricas; use `gcm.metrics` para isso.
        """
        if T <= 0:
            raise ValueError("T deve ser positivo.")
        if discard < 0 or discard >= T:
            if track:
                raise ValueError("discard deve estar em [0, T-1] quando track=True.")

        if track:
            traj = np.empty((T, self.cfg.N), dtype=float)
            for t in range(T):
                self.step()
                traj[t] = self.x
            return traj[discard:]
        else:
            for _ in range(T):
                self.step()
            return None

