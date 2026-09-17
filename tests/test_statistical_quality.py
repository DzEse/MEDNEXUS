import numpy as np
import pytest

from mednexus.analytics import production_kpis
from mednexus.statistical_quality import (
    capacity_waterfall,
    methodology_gates,
    p_chart_by_plant,
    six_big_losses,
    value_leakage,
)
from mednexus.synthetic import generate


@pytest.fixture(scope='module')
def frames():
    return generate(seed=42)


def test_fpy_has_first_pass_semantics(frames):
    out = production_kpis(frames['fact_production'])
    expected = (out['total_count'] - out['defect_units']) / out['total_count']
    assert np.allclose(out['fpy'], expected)
    assert np.allclose(out['fpy_proxy'], out['fpy'])


def test_methodology_gates_fail_closed_for_unsupported_metrics():
    gates = methodology_gates().set_index('method')
    assert gates.loc['First Pass Yield (FPY)', 'status'] == 'IMPLEMENTED'
    assert gates.loc['p chart', 'status'] == 'IMPLEMENTED'
    assert gates.loc['Rolled Throughput Yield (RTY)', 'status'] == 'NOT_CALCULABLE'
    assert gates.loc['DPMO', 'status'] == 'NOT_CALCULABLE'
    assert gates.loc['Cp/Cpk/Pp/Ppk', 'status'] == 'NOT_CALCULABLE'
    assert gates.loc['Full COPQ', 'status'] == 'NOT_CALCULABLE'


def test_p_chart_limits_are_valid_and_observations_classified(frames):
    chart = p_chart_by_plant(frames['fact_production'])

    assert chart['defect_rate'].between(0, 1).all()
    assert chart['center_line'].between(0, 1).all()
    assert chart['lcl'].between(0, 1).all()
    assert chart['ucl'].between(0, 1).all()
    assert (chart['lcl'] <= chart['ucl']).all()
    assert chart['out_of_control'].isin([0, 1]).all()


def test_capacity_waterfall_reconciles_to_good_output(frames):
    flow = capacity_waterfall(frames['fact_production'])
    pivot = flow.pivot(index='month', columns='stage', values='units_equivalent')

    reconstructed = (
        pivot['Theoretical Capacity']
        + pivot['Planned Downtime']
        + pivot['Unplanned Downtime']
        + pivot['Speed Loss']
        + pivot['Quality Loss']
    )
    assert np.allclose(reconstructed, pivot['Good Production'], atol=1e-6)


def test_six_big_losses_keeps_startup_rejects_gated(frames):
    losses = six_big_losses(frames)

    startup = losses[losses['loss_category'] == 'Startup Rejects']
    supported = losses[losses['loss_category'] != 'Startup Rejects']

    assert not startup.empty
    assert startup['status'].eq('NOT_CALCULABLE').all()
    assert supported['status'].eq('CALCULATED').all()


def test_value_leakage_does_not_fabricate_full_copq(frames):
    leakage = value_leakage(frames)

    assert leakage['scrap_cost'].ge(0).all()
    assert leakage['downtime_cost'].ge(0).all()
    assert leakage['rework_cost'].isna().all()
    assert leakage['full_copq'].isna().all()
    assert leakage['copq_status'].eq('NOT_CALCULABLE').all()
