from mednexus.synthetic import generate


def test_seed_reproducibility():
    a=generate(seed=7)['fact_finance']
    b=generate(seed=7)['fact_finance']
    assert a.equals(b)
