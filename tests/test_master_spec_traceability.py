from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / 'docs' / 'specification' / 'MEDNEXUS_MASTER_BUILD_SPECIFICATION.md'
TRACE = ROOT / 'docs' / 'specification' / 'REQUIREMENTS_TRACEABILITY_MATRIX.md'
POLICY = ROOT / 'docs' / 'specification' / 'SCOPE_PRESERVATION_POLICY.md'
BLUEPRINT = ROOT / 'docs' / 'MASTER_IMPLEMENTATION_BLUEPRINT.md'
DATASET_ENHANCEMENT = ROOT / 'docs' / 'specification' / 'MEDNEXUS_ENTERPRISE_DATASET_DIGITAL_TWIN_ENHANCEMENT.md'
COMMAND_CENTER_ENHANCEMENT = ROOT / 'docs' / 'specification' / 'MEDNEXUS_EXECUTIVE_COMMAND_CENTER_ENHANCEMENT.md'
ENHANCEMENT_TRACE = ROOT / 'docs' / 'specification' / 'ENHANCEMENT_TRACEABILITY_MATRIX.md'


def _text(path: Path) -> str:
    assert path.exists(), f'Missing required governance artifact: {path.relative_to(ROOT)}'
    return path.read_text(encoding='utf-8')


def test_canonical_specification_preserves_all_57_sections():
    text = _text(SPEC)
    found = {int(n) for n in re.findall(r'^#\s+(\d+)\.', text, flags=re.MULTILINE)}
    expected = set(range(1, 58))
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
    expected = set(range(1, 58))
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


def test_dataset_twin_enhancement_preserves_all_32_requirements():
    text = _text(DATASET_ENHANCEMENT)
    found = {int(n) for n in re.findall(r'^#\s+(\d+)\.', text, flags=re.MULTILINE)}
    expected = set(range(1, 33))
    assert expected.issubset(found), f'Missing dataset/twin enhancement requirements: {sorted(expected - found)}'


def test_command_center_enhancement_preserves_all_28_requirements():
    text = _text(COMMAND_CENTER_ENHANCEMENT)
    found = {int(n) for n in re.findall(r'^#\s+(\d+)\.', text, flags=re.MULTILINE)}
    expected = set(range(1, 29))
    assert expected.issubset(found), f'Missing Command Center enhancement requirements: {sorted(expected - found)}'


def test_master_blueprint_preserves_all_enhancement_ids():
    text = _text(BLUEPRINT)
    for prefix, count in (('A', 32), ('B', 28)):
        missing = [f'{prefix}{i:02d}' for i in range(1, count + 1) if f'{prefix}{i:02d}' not in text]
        assert not missing, f'Missing enhancement blueprint IDs: {missing}'


def test_enhancement_traceability_covers_all_60_new_requirements():
    text = _text(ENHANCEMENT_TRACE)
    for prefix, count in (('A', 32), ('B', 28)):
        missing = [f'{prefix}{i:02d}' for i in range(1, count + 1) if re.search(rf'^\|\s*{prefix}{i:02d}\s*\|', text, flags=re.MULTILINE) is None]
        assert not missing, f'Missing enhancement traceability IDs: {missing}'


def test_enhancement_docs_are_binding_in_master_spec():
    text = _text(SPEC)
    assert 'MEDNEXUS_ENTERPRISE_DATASET_DIGITAL_TWIN_ENHANCEMENT.md' in text
    assert 'MEDNEXUS_EXECUTIVE_COMMAND_CENTER_ENHANCEMENT.md' in text
    assert '32 additive requirements' in text
    assert '28 additive requirements' in text
