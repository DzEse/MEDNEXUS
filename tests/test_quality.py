from mednexus.synthetic import generate
from mednexus.quality import evaluate, data_trust_score


def test_generated_data_quality():
    frames=generate(seed=42)
    tq,bq=evaluate(frames)
    assert (tq['status']=='PASS').all()
    assert (bq['status']=='PASS').all()
    score,_=data_trust_score(tq,bq)
    assert 0 <= score <= 100
