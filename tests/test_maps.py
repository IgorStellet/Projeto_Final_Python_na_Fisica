import numpy as np


from gcm.maps import (
    bistable_map,
    bistable_intervals,
    lyapunov_local,
    sync_boundaries,
    escape_boundaries,
)




def test_bistable_map_is_odd():
    mu = 1.9
    xs = np.array([-1.0, -0.8, -1/3, -0.2, 0.0, 0.2, 1/3, 0.8, 1.0], dtype=float)
    f = bistable_map(xs, mu)
    f_minus = bistable_map(-xs, mu)
    assert np.allclose(f + f_minus, 0.0)

test_bistable_map_is_odd()


def test_bistable_map_piecewise_boundaries():
    mu = 1.9
    xs = np.array([-1.0, -1/3, 0.0, 1/3, 1.0], dtype=float)
    f = bistable_map(xs, mu)
    # valores esperados via fórmula
    exp = np.empty_like(xs)
    for i, x in enumerate(xs):
        if x <= -1/3:
            exp[i] = -2*mu/3 - mu*x
        elif x < 1/3:
            exp[i] = mu*x
        else:
            exp[i] = 2*mu/3 - mu*x
    assert np.allclose(f, exp)

test_bistable_map_piecewise_boundaries()


def test_bistable_intervals_symmetry_and_order():
    for mu in [1.3, 1.9]:
        i_minus, i_plus = bistable_intervals(mu)
        # ordenados
        assert i_minus[0] <= i_minus[1]
        assert i_plus[0] <= i_plus[1]
        # simetria I_- = - I_+
        assert np.allclose(i_minus, (-i_plus[1], -i_plus[0]))

test_bistable_intervals_symmetry_and_order()


def test_lyapunov_local_and_boundaries():
    mu = 1.9
    lam = lyapunov_local(mu)
    assert np.isclose(lam, np.log(abs(mu)))

    eps_inf, eps_sup = sync_boundaries(mu)
    assert eps_inf < eps_sup

    esc_lo, esc_hi = escape_boundaries(mu)
    assert esc_lo < esc_hi

test_lyapunov_local_and_boundaries()