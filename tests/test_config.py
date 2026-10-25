import pytest

from bbme.config import CONFIG_DIR, apply_overrides, load


@pytest.mark.parametrize("name", [p.stem for p in CONFIG_DIR.glob("*.yaml")])
def test_every_config_parses(name):
    assert isinstance(load(name), dict)


def test_overrides_parse_yaml_scalars():
    cfg = {"poi": {"kappa_E": 0.025}, "alpha": 1.0}
    apply_overrides(cfg, ["poi.kappa_E=0.03", "alpha=0.8"])
    assert cfg == {"poi": {"kappa_E": 0.03}, "alpha": 0.8}


def test_overrides_reject_unknown_keys():
    with pytest.raises(KeyError):
        apply_overrides({"alpha": 1.0}, ["alhpa=0.5"])
