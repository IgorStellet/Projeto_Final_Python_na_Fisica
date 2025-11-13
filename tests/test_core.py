import numpy as np
from gcm.core import Config, GloballyCoupledMaps
from gcm.maps import bistable_intervals

def test_reset_half_half_and_uniform():
    mu = 1.9
    N = 400
    cfg = Config(N=N, eps=0.6, mu=mu, seed=42)
    sys = GloballyCoupledMaps(cfg)

    # half_half
    sys.reset(init="half_half")
    i_minus, i_plus = bistable_intervals(mu)
    # checa que valores estão dentro de I_- ∪ I_+
    assert np.all(((sys.x >= i_minus[0]) & (sys.x <= i_minus[1])) |
                  ((sys.x >= i_plus[0]) & (sys.x <= i_plus[1])))

    # fração próxima de 1/2
    frac_plus = (sys.x > 0).mean()
    assert 0.45 <= frac_plus <= 0.55

    # uniform
    sys.reset(init="uniform")
    assert np.all(sys.x >= -1.0) and np.all(sys.x <= 1.0)

test_reset_half_half_and_uniform()




def test_step_broadcast_equivalence():
    mu = 1.9
    N = 256
    cfg = Config(N=N, eps=0.7, mu=mu, seed=7)
    sys = GloballyCoupledMaps(cfg)
    sys.reset(init="half_half")

    # passo 1 (via metodo)
    x0 = sys.x.copy()
    sys.step()
    x1 = sys.x.copy()

    # reconstroi manualmente
    from gcm.maps import bistable_map
    y = bistable_map(x0, mu)
    m = y.mean()
    x1_manual = (1.0 - cfg.eps) * y + cfg.eps * m
    assert np.allclose(x1, x1_manual)

test_step_broadcast_equivalence()


def test_run_shapes_and_escaped_mask():
    mu = 1.9
    N = 128
    cfg = Config(N=N, eps=0.2, mu=mu, seed=123)
    sys = GloballyCoupledMaps(cfg)
    sys.reset(init="half_half")

    traj = sys.run(T=50, discard=10, track=True)
    assert traj.shape == (40, N)
    assert sys.last_escaped_mask.shape == (N,)

test_run_shapes_and_escaped_mask()