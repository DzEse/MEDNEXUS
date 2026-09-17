from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / 'docs' / 'specification' / 'MEDNEXUS_MASTER_BUILD_SPECIFICATION.md'
TRACE = ROOT / 'docs' / 'specification' / 'REQUIREMENTS_TRACEABILITY_MATRIX.md'
POLICY = ROOT / 'docs' / 'specification' / 'SCOPE_PRESERVATION_POLICY.md'
BLUEPRINT = ROOT / 'docs' / 'MASTER_IMPLEMENTATION_BLUEPRINT.md'


def _text(path: Path) -> str:
    assert path.exists(), f'Missing required governance artifact: {path.relative_to(ROOT)}'
    return path.read_text(encoding='utf-8')


def test_canonical_specification_preserves_all_55_sections():
    text = _text(SPEC)
    found = {int(n) for n in re.findall(r'^#\s+(\d+)\.', text, flags=re.MULTILINE)}
    expected = set(range(1, 56))
    assert expected.issubset(found), f'Missing canonical specification sections: {sorted(expected - found)}'


def test_master_blueprint_preserves_all_60_required_areas():
    text = _text(BLUEPRINT)
    found = {int(n) for n in re.findall(r'^#\s+(\d+)\.', text, flags=re.MULTILINE)}
    expected = set(range(1, 61))
    assert expected.issubset(found), f'Missing master blueprint areas: {sorted(expected - found)}'


def test_traceability_matrix_covers_every_spec_section():
    text = _text(TRACE)
    found = {
        int(n)
        for n in re.findall(r'^\|\s*(\d+)\s*\|', text, flags=re.MULTILINE)
    }
    expected = set(range(1, 56))
    assert expected.issubset(found), f'Missing traceability rows: {sorted(expected - found)}'


def test_scope_preservation_policy_contains_non_dropping_rule():
    text = _text(POLICY).lower()
    assert 'no future implementation step may silently delete, weaken, narrow, or supersede' in text
    assert 'silence is not a valid disposition' in text


def test_master_governance_priority_hierarchy_is_preserved():
    required = (
        'ACCURACY',
        'BUSINESS LOGIC',
        'DATA INTEGRITY',
        'ANALYTICAL VALIDITY',
        'REPRODUCIBILITY',
        'DECISION VALUE',
        'TECHNICAL DEPTH',
        'VISUAL POLISH',
    )
    spec = _text(SPEC)
    blueprint = _text(BLUEPRINT)
    for item in required:
        assert item in spec, f'Priority hierarchy item missing from canonical specification: {item}'
        assert item.title() in blueprint or item in blueprint, f'Priority hierarchy item missing from blueprint: {item}'
