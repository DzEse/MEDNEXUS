from __future__ import annotations

import json

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import kruskal, spearmanr
from sklearn.tree import DecisionTreeRegressor, export_text
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.proportion import proportion_confint


NUMERIC_DRIVERS = [
    'unplanned_downtime_min',
    'machine_age_years',
    'capacity_gap_pct',
    'absence_rate',
    'overtime_hours_per_employee',
]

SEGMENT_DIMENSIONS = [
    'plant_id',
    'line_id',
    'product_id',
    'machine_age_band',
]


def build_diagnostic_frame(frames) -> pd.DataFrame:
    p = frames['fact_production'].copy()
    p['date'] = pd.to_datetime(p['date'])
    p['month'] = p['date'].dt.to_period('M').astype(str)
    p['defect_rate'] = p['defect_units'] / p['total_count'].replace(0, np.nan)
    p['fpy'] = (p['total_count'] - p['defect_units']) / p['total_count'].replace(0, np.nan)

    machine = frames['dim_machine'][['machine_id', 'machine_age_years']].copy()
    p = p.merge(machine, on='machine_id', how='left', validate='many_to_one')

    workforce = frames['fact_workforce'].copy()
    workforce['month'] = pd.to_datetime(workforce['month']).dt.to_period('M').astype(str)
    workforce = workforce[
        [
            'month',
            'plant_id',
            'capacity_gap_pct',
            'absence_rate',
            'overtime_hours_per_employee',
        ]
    ]
    p = p.merge(
        workforce,
        on=['month', 'plant_id'],
        how='left',
        validate='many_to_one',
    )

    p['machine_age_band'] = pd.cut(
        p['machine_age_years'],
        bins=[-np.inf, 3, 6, 9, np.inf],
        labels=['0-3 years', '4-6 years', '7-9 years', '10+ years'],
    ).astype(str)

    required = [
        'production_order_id',
        'defect_rate',
        'total_count',
        'defect_units',
        *NUMERIC_DRIVERS,
        *SEGMENT_DIMENSIONS,
    ]
    if p[required].isna().any().any():
        missing = p[required].isna().sum()
        missing = missing[missing > 0].to_dict()
        raise RuntimeError(f'Root-cause diagnostic frame contains missing required values: {missing}')

    if p['production_order_id'].duplicated().any():
        raise RuntimeError('Root-cause diagnostic grain is not unique by production_order_id.')

    return p


def _effect_label(value: float, thresholds=(0.10, 0.30, 0.50)) -> str:
    magnitude = abs(float(value))
    if magnitude < thresholds[0]:
        return 'negligible'
    if magnitude < thresholds[1]:
        return 'small'
    if magnitude < thresholds[2]:
        return 'moderate'
    return 'large'


def segment_defect_rates(diagnostic: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for dimension in SEGMENT_DIMENSIONS + ['machine_id']:
        grouped = (
            diagnostic.groupby(dimension, observed=True)
            .agg(
                production_orders=('production_order_id', 'count'),
                total_units=('total_count', 'sum'),
                defect_units=('defect_units', 'sum'),
                unplanned_downtime_min=('unplanned_downtime_min', 'sum'),
            )
            .reset_index()
            .rename(columns={dimension: 'segment_value'})
        )
        grouped['segment_dimension'] = dimension
        grouped['defect_rate'] = grouped['defect_units'] / grouped['total_units'].replace(0, np.nan)
        low, high = proportion_confint(
            grouped['defect_units'].to_numpy(),
            grouped['total_units'].to_numpy(),
            alpha=0.05,
            method='wilson',
        )
        grouped['defect_rate_ci95_low'] = low
        grouped['defect_rate_ci95_high'] = high
        grouped['fpy'] = 1 - grouped['defect_rate']
        grouped['rank_high_defect_rate'] = grouped['defect_rate'].rank(
            method='dense', ascending=False
        ).astype(int)
        rows.append(grouped)

    out = pd.concat(rows, ignore_index=True)
    global_rate = diagnostic['defect_units'].sum() / diagnostic['total_count'].sum()
    out['enterprise_defect_rate'] = global_rate
    out['defect_rate_lift_pp'] = (out['defect_rate'] - global_rate) * 100
    out['interpretation'] = (
        'Descriptive segment signal with Wilson interval; association/investigation priority, not causation.'
    )
    return out[
        [
            'segment_dimension',
            'segment_value',
            'production_orders',
            'total_units',
            'defect_units',
            'defect_rate',
            'defect_rate_ci95_low',
            'defect_rate_ci95_high',
            'fpy',
            'unplanned_downtime_min',
            'enterprise_defect_rate',
            'defect_rate_lift_pp',
            'rank_high_defect_rate',
            'interpretation',
        ]
    ]


def numeric_associations(diagnostic: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for feature in NUMERIC_DRIVERS:
        x = diagnostic[feature].astype(float)
        y = diagnostic['defect_rate'].astype(float)
        rho, p_value = spearmanr(x, y, nan_policy='omit')

        q1 = x.quantile(0.25)
        q3 = x.quantile(0.75)
        low = diagnostic[x <= q1]
        high = diagnostic[x >= q3]
        low_rate = low['defect_units'].sum() / low['total_count'].sum()
        high_rate = high['defect_units'].sum() / high['total_count'].sum()

        rows.append(
            {
                'feature': feature,
                'analysis_grain': 'production_order_machine_day',
                'n': int(len(diagnostic)),
                'spearman_rho': float(rho),
                'p_value': float(p_value),
                'rho_magnitude': _effect_label(rho),
                'q1_cutoff': float(q1),
                'q3_cutoff': float(q3),
                'low_quartile_defect_rate': float(low_rate),
                'high_quartile_defect_rate': float(high_rate),
                'high_minus_low_defect_rate_pp': float((high_rate - low_rate) * 100),
                'direction': 'positive' if rho > 0 else ('negative' if rho < 0 else 'flat'),
                'interpretation': (
                    'Spearman association plus exposure-weighted quartile contrast; not causal evidence.'
                ),
            }
        )

    out = pd.DataFrame(rows)
    rejected, adjusted, _, _ = multipletests(out['p_value'], method='fdr_bh')
    out['p_value_fdr_bh'] = adjusted
    out['statistically_detected_fdr_0_05'] = rejected
    return out.sort_values(
        ['statistically_detected_fdr_0_05', 'spearman_rho'],
        ascending=[False, False],
    ).reset_index(drop=True)


def categorical_group_tests(diagnostic: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for dimension in SEGMENT_DIMENSIONS:
        groups = [
            group['defect_rate'].dropna().to_numpy()
            for _, group in diagnostic.groupby(dimension, observed=True)
            if len(group) >= 20
        ]
        if len(groups) < 2:
            continue
        stat, p_value = kruskal(*groups)
        n = int(sum(len(group) for group in groups))
        k = int(len(groups))
        epsilon_sq = max(0.0, float((stat - k + 1) / max(n - k, 1)))
        rows.append(
            {
                'dimension': dimension,
                'test': 'Kruskal-Wallis',
                'groups': k,
                'n': n,
                'statistic': float(stat),
                'p_value': float(p_value),
                'epsilon_squared': epsilon_sq,
                'effect_magnitude': _effect_label(
                    epsilon_sq,
                    thresholds=(0.01, 0.06, 0.14),
                ),
                'assumption_note': (
                    'Independent production-order observations assumed; nonparametric test used for bounded/skewed defect rates.'
                ),
                'interpretation': (
                    'Group-distribution difference signal; statistical significance does not establish causation or business materiality.'
                ),
            }
        )

    out = pd.DataFrame(rows)
    if not out.empty:
        rejected, adjusted, _, _ = multipletests(out['p_value'], method='fdr_bh')
        out['p_value_fdr_bh'] = adjusted
        out['statistically_detected_fdr_0_05'] = rejected
    return out.sort_values('epsilon_squared', ascending=False).reset_index(drop=True)


def binomial_regression(diagnostic: pd.DataFrame):
    x = diagnostic[NUMERIC_DRIVERS].astype(float).copy()
    means = x.mean()
    stds = x.std(ddof=0).replace(0, np.nan)
    if stds.isna().any():
        raise RuntimeError('Root-cause regression contains a zero-variance predictor.')

    x_std = (x - means) / stds
    exog = sm.add_constant(x_std, has_constant='add')
    endog = np.column_stack(
        [
            diagnostic['defect_units'].astype(float).to_numpy(),
            (diagnostic['total_count'] - diagnostic['defect_units']).astype(float).to_numpy(),
        ]
    )

    model = sm.GLM(endog, exog, family=sm.families.Binomial())
    fit = model.fit(cov_type='HC0', maxiter=200)

    ci = fit.conf_int()
    rows = []
    for term in exog.columns:
        coefficient = float(fit.params[term])
        lower = float(ci.loc[term, 0])
        upper = float(ci.loc[term, 1])
        rows.append(
            {
                'term': term,
                'standardized_predictor': term != 'const',
                'coefficient_log_odds': coefficient,
                'std_error_robust': float(fit.bse[term]),
                'z_value': float(fit.tvalues[term]),
                'p_value': float(fit.pvalues[term]),
                'ci95_log_odds_low': lower,
                'ci95_log_odds_high': upper,
                'odds_ratio_per_1sd': float(np.exp(coefficient)),
                'odds_ratio_ci95_low': float(np.exp(lower)),
                'odds_ratio_ci95_high': float(np.exp(upper)),
                'interpretation': (
                    'Adjusted association in grouped-binomial GLM with HC0 robust covariance; not a causal effect.'
                ),
            }
        )

    coefficients = pd.DataFrame(rows)
    non_const = coefficients['term'] != 'const'
    if non_const.any():
        rejected, adjusted, _, _ = multipletests(
            coefficients.loc[non_const, 'p_value'],
            method='fdr_bh',
        )
        coefficients.loc[non_const, 'p_value_fdr_bh'] = adjusted
        coefficients.loc[non_const, 'statistically_detected_fdr_0_05'] = rejected
    coefficients.loc[~non_const, 'p_value_fdr_bh'] = np.nan
    coefficients.loc[~non_const, 'statistically_detected_fdr_0_05'] = False

    vif_rows = []
    vif_x = sm.add_constant(x_std, has_constant='add')
    for i, column in enumerate(vif_x.columns):
        if column == 'const':
            continue
        vif_rows.append(
            {
                'feature': column,
                'vif': float(variance_inflation_factor(vif_x.to_numpy(), i)),
            }
        )
    vif = pd.DataFrame(vif_rows)

    diagnostics = {
        'model': 'Grouped-binomial GLM',
        'covariance': 'HC0 robust',
        'analysis_grain': 'production_order_machine_day',
        'rows': int(len(diagnostic)),
        'total_units': int(diagnostic['total_count'].sum()),
        'total_defects': int(diagnostic['defect_units'].sum()),
        'predictor_count': int(len(NUMERIC_DRIVERS)),
        'deviance': float(fit.deviance),
        'df_resid': float(fit.df_resid),
        'deviance_per_df_resid': float(fit.deviance / max(fit.df_resid, 1)),
        'max_vif': float(vif['vif'].max()),
        'converged': bool(fit.converged),
        'adequacy_notes': [
            'Grouped-binomial form respects defect counts and production exposure.',
            'Predictors are standardized before fitting.',
            'HC0 robust covariance is used for inferential uncertainty.',
            'VIF is reported to expose multicollinearity.',
            'Association estimates are not causal effects.',
            'Synthetic-data relationships may not generalize to real operations.',
        ],
    }
    return coefficients, vif, diagnostics


def diagnostic_tree(diagnostic: pd.DataFrame):
    x = diagnostic[NUMERIC_DRIVERS].astype(float)
    y = diagnostic['defect_rate'].astype(float)
    weights = diagnostic['total_count'].astype(float)

    min_leaf = max(50, int(len(diagnostic) * 0.03))
    tree = DecisionTreeRegressor(
        max_depth=3,
        min_samples_leaf=min_leaf,
        random_state=42,
    )
    tree.fit(x, y, sample_weight=weights)

    importance = pd.DataFrame(
        {
            'feature': NUMERIC_DRIVERS,
            'tree_importance': tree.feature_importances_,
        }
    ).sort_values('tree_importance', ascending=False)
    importance['interpretation'] = (
        'Shallow diagnostic-tree split importance for investigation prioritization; not causal evidence.'
    )

    rules = export_text(tree, feature_names=NUMERIC_DRIVERS, decimals=4)
    diagnostics = {
        'model': 'DecisionTreeRegressor diagnostic segmentation',
        'max_depth': 3,
        'min_samples_leaf': min_leaf,
        'weighted_r2_in_sample': float(tree.score(x, y, sample_weight=weights)),
        'purpose': 'Exploratory segmentation / investigation prioritization only',
        'causal_status': 'NOT_CAUSAL',
    }
    return importance, rules, diagnostics


def investigation_priorities(
    segments: pd.DataFrame,
    associations: pd.DataFrame,
    regression: pd.DataFrame,
    tree_importance: pd.DataFrame,
) -> pd.DataFrame:
    rows = []

    for row in associations.head(5).itertuples(index=False):
        rows.append(
            {
                'evidence_type': 'numeric_association',
                'factor_or_entity': row.feature,
                'signal_strength': abs(float(row.spearman_rho)),
                'evidence': (
                    f'Spearman rho={row.spearman_rho:.3f}; FDR p={row.p_value_fdr_bh:.3g}; '
                    f'high-vs-low quartile defect difference={row.high_minus_low_defect_rate_pp:.3f} pp.'
                ),
                'next_validation_step': (
                    'Review operational context and time ordering; validate with controlled/pre-post evidence before intervention claims.'
                ),
                'causal_status': 'ASSOCIATION_ONLY',
            }
        )

    eligible = segments[
        (segments['production_orders'] >= 100)
        & (segments['defect_rate_lift_pp'] > 0)
    ].copy()
    eligible = eligible.sort_values(
        ['defect_rate_lift_pp', 'total_units'],
        ascending=[False, False],
    )
    for row in eligible.head(5).itertuples(index=False):
        rows.append(
            {
                'evidence_type': 'high_defect_segment',
                'factor_or_entity': f'{row.segment_dimension}={row.segment_value}',
                'signal_strength': float(row.defect_rate_lift_pp),
                'evidence': (
                    f'Defect rate={row.defect_rate:.3%} '
                    f'(95% CI {row.defect_rate_ci95_low:.3%}-{row.defect_rate_ci95_high:.3%}); '
                    f'{row.defect_rate_lift_pp:.3f} pp above enterprise.'
                ),
                'next_validation_step': (
                    'Inspect linked downtime/workforce/quality events and confirm the segment pattern with business owners.'
                ),
                'causal_status': 'DESCRIPTIVE_ONLY',
            }
        )

    reg = regression[
        (regression['term'] != 'const')
        & (regression['statistically_detected_fdr_0_05'].eq(True))
    ].copy()
    reg['distance_from_one'] = (reg['odds_ratio_per_1sd'] - 1).abs()
    for row in reg.sort_values('distance_from_one', ascending=False).head(5).itertuples(index=False):
        rows.append(
            {
                'evidence_type': 'adjusted_regression_association',
                'factor_or_entity': row.term,
                'signal_strength': float(row.distance_from_one),
                'evidence': (
                    f'Adjusted OR per 1 SD={row.odds_ratio_per_1sd:.3f} '
                    f'(95% CI {row.odds_ratio_ci95_low:.3f}-{row.odds_ratio_ci95_high:.3f}); '
                    f'FDR p={row.p_value_fdr_bh:.3g}.'
                ),
                'next_validation_step': (
                    'Treat as an adjusted association; investigate omitted variables and prospective validation before action attribution.'
                ),
                'causal_status': 'ASSOCIATION_ONLY',
            }
        )

    for row in tree_importance.head(3).itertuples(index=False):
        if row.tree_importance <= 0:
            continue
        rows.append(
            {
                'evidence_type': 'diagnostic_tree',
                'factor_or_entity': row.feature,
                'signal_strength': float(row.tree_importance),
                'evidence': f'Shallow-tree split importance={row.tree_importance:.3f}.',
                'next_validation_step': (
                    'Use tree splits to guide drill-down only; confirm with independent statistical and business evidence.'
                ),
                'causal_status': 'EXPLORATORY_ONLY',
            }
        )

    out = pd.DataFrame(rows)
    if out.empty:
        return pd.DataFrame(
            columns=[
                'priority',
                'evidence_type',
                'factor_or_entity',
                'signal_strength',
                'evidence',
                'next_validation_step',
                'causal_status',
            ]
        )
    out = out.sort_values('signal_strength', ascending=False).reset_index(drop=True)
    out.insert(0, 'priority', np.arange(1, len(out) + 1))
    return out


def run_root_cause_analysis(frames):
    diagnostic = build_diagnostic_frame(frames)
    segments = segment_defect_rates(diagnostic)
    associations = numeric_associations(diagnostic)
    group_tests = categorical_group_tests(diagnostic)
    regression, vif, regression_diagnostics = binomial_regression(diagnostic)
    tree_importance, tree_rules, tree_diagnostics = diagnostic_tree(diagnostic)
    priorities = investigation_priorities(
        segments,
        associations,
        regression,
        tree_importance,
    )
    methodology = {
        'analysis_target': 'first-pass defect rate',
        'evidence_hierarchy': [
            'Pareto',
            'trend',
            'segmentation with Wilson intervals',
            'Spearman association with FDR correction and quartile contrast',
            'Kruskal-Wallis group comparison with epsilon-squared',
            'grouped-binomial GLM with robust covariance and VIF',
            'shallow diagnostic tree',
            'business validation',
        ],
        'causal_claim': False,
        'required_interpretation': (
            'Outputs identify association and investigation priority only. They do not establish root cause causally.'
        ),
        'regression_diagnostics': regression_diagnostics,
        'tree_diagnostics': tree_diagnostics,
    }
    return {
        'diagnostic_frame': diagnostic,
        'segments': segments,
        'associations': associations,
        'group_tests': group_tests,
        'regression': regression,
        'vif': vif,
        'tree_importance': tree_importance,
        'tree_rules': tree_rules,
        'priorities': priorities,
        'methodology': methodology,
    }
