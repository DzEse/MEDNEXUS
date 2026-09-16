from mednexus.synthetic import generate
from mednexus.analytics import monthly_enterprise_mart
from mednexus.risk import build_mori


def test_mori_bounds():
    frames=generate(seed=42)
    mart=monthly_enterprise_mart(frames)
    w={'quality':.16,'equipment':.16,'downtime':.12,'capacity':.12,'supply':.12,'logistics':.10,'workforce':.10,'technology':.12}
    r=build_mori(mart,w)
    assert r['mori_score'].between(0,100).all()
