import os
import subprocess
import sys

from mednexus.synthetic import generate


def test_seed_reproducibility():
    a = generate(seed=7)["fact_finance"]
    b = generate(seed=7)["fact_finance"]
    assert a.equals(b)


def test_stable_selection_is_independent_of_python_hash_seed():
    code = (
        "from mednexus.synthetic import _stable_index; "
        "print(_stable_index('PL0001-L1-M1', '2026-08-31', n=6))"
    )
    outputs = []
    for hash_seed in ("1", "999"):
        env = os.environ.copy()
        env["PYTHONHASHSEED"] = hash_seed
        outputs.append(
            subprocess.check_output(
                [sys.executable, "-c", code], env=env, text=True
            ).strip()
        )
    assert outputs[0] == outputs[1]