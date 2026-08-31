import json

import pytest

from ayus.config import PlannerConfig, load_config


def test_config_rejects_invalid_canny_order():
    with pytest.raises(ValueError):
        PlannerConfig(canny_low=200, canny_high=100).validate()


def test_config_round_trip(tmp_path):
    path = tmp_path / "config.json"
    config = PlannerConfig(seed=123, algorithm="aco")
    config.save(path)
    assert load_config(path) == config
    assert json.loads(path.read_text(encoding="utf-8"))["seed"] == 123
