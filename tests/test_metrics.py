import numpy as np
from gcm.metrics import (
    sigma,
    spins,
    magnetization,
    order_param_M,
    persistence_curve,
)




def test_sigma_and_spins_and_magnetization():
    x = np.zeros(10)
    assert sigma(x) == 0.0

    x = np.array([-2, -0.1, 0, 0.1, 2], dtype=float)
    s = spins(x)
    assert s.tolist() == [-1, -1, 1, 1, 1] # 0 → +1 por convenção
    assert np.isclose(magnetization(x), s.mean())

test_sigma_and_spins_and_magnetization()



def test_persistence_curve_and_order_param():
    # série sintética de spins (T=4, N=6)
    S = np.array([
        [ 1, 1, 1, -1, -1, -1], # t=0
        [ 1, -1, 1, -1, 1, -1], # em t=1 mudam: col 2 e 5
        [ 1, -1, 1, -1, 1, -1],
        [ 1, -1, 1, -1, 1, -1],
    ])
    p = persistence_curve(S)
    # t=0: 100% não mudou; t>=1: 4 de 6 nunca mudaram
    assert np.allclose(p, [1.0, 4/6, 4/6, 4/6])

    Ms = S.mean(axis=1)
    m_ord = order_param_M(Ms)
    assert np.isclose(m_ord, abs(Ms.mean()))

test_persistence_curve_and_order_param()