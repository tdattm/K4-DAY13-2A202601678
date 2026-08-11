from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from scripts.validate_slo_alerts import (
    REPO_ROOT,
    SreConfigError,
    validate_alert_payload,
    validate_configs,
    validate_slo_payload,
)


SLO_PATH = REPO_ROOT / "config" / "slo.yaml"
ALERT_PATH = REPO_ROOT / "config" / "alert_rules.yaml"


def _payload(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_repository_slo_alerts_and_runbook_are_consistent() -> None:
    slo_payload, alert_payload = validate_configs(SLO_PATH, ALERT_PATH)

    assert len(slo_payload["slis"]) == 4
    assert {alert["sli"] for alert in alert_payload["alerts"]} == set(slo_payload["slis"])


def test_alert_threshold_must_match_slo_objective() -> None:
    slis = validate_slo_payload(_payload(SLO_PATH))
    alert_payload = deepcopy(_payload(ALERT_PATH))
    alert_payload["alerts"][0]["threshold"] = 9999

    with pytest.raises(SreConfigError, match="threshold không khớp"):
        validate_alert_payload(alert_payload, slis, REPO_ROOT)


def test_every_sli_must_have_an_alert() -> None:
    slis = validate_slo_payload(_payload(SLO_PATH))
    alert_payload = deepcopy(_payload(ALERT_PATH))
    alert_payload["alerts"] = [
        alert for alert in alert_payload["alerts"] if alert["sli"] != "quality_score_avg"
    ]

    with pytest.raises(SreConfigError, match="quality_score_avg"):
        validate_alert_payload(alert_payload, slis, REPO_ROOT)
