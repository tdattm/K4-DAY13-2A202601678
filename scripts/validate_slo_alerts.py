from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.cli import configure_utf8_stdio


REQUIRED_SLIS = {
    "latency_p95_ms",
    "error_rate_pct",
    "daily_cost_usd",
    "quality_score_avg",
}
REQUIRED_SLO_FIELDS = {
    "description",
    "objective",
    "operator",
    "unit",
    "target",
    "evaluation_window",
    "minimum_requests",
    "error_budget",
    "note",
}
REQUIRED_ALERT_FIELDS = {
    "name",
    "severity",
    "sli",
    "condition",
    "operator",
    "threshold",
    "evaluation_window",
    "duration",
    "type",
    "owner",
    "runbook",
    "summary",
    "recovery_condition",
}
DURATION_PATTERN = re.compile(r"^[1-9]\d*[mhd]$")


class SreConfigError(ValueError):
    pass


def _load_yaml(path: Path) -> dict:
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SreConfigError(f"Không tìm thấy config: {path}") from exc
    except yaml.YAMLError as exc:
        raise SreConfigError(f"YAML không hợp lệ tại {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SreConfigError(f"Config phải là YAML object: {path}")
    return payload


def _require_duration(value: object, location: str) -> None:
    if not isinstance(value, str) or not DURATION_PATTERN.fullmatch(value):
        raise SreConfigError(f"'{location}' phải có dạng số + m/h/d, ví dụ 5m hoặc 1d")


def _heading_anchors(markdown: str) -> set[str]:
    anchors: set[str] = set()
    for line in markdown.splitlines():
        if not line.startswith("#"):
            continue
        heading = line.lstrip("#").strip().lower()
        anchor = re.sub(r"[^\w\s-]", "", heading, flags=re.UNICODE)
        anchors.add(re.sub(r"[\s_-]+", "-", anchor).strip("-"))
    return anchors


def validate_slo_payload(payload: dict) -> dict[str, dict]:
    if payload.get("schema_version") != 1:
        raise SreConfigError("'slo.schema_version' phải bằng 1")
    if payload.get("window") != "28d":
        raise SreConfigError("SLO reporting window phải là 28d")
    if not payload.get("service") or not payload.get("owner") or not payload.get("data_source"):
        raise SreConfigError("SLO phải khai báo service, owner và data_source")

    slis = payload.get("slis")
    if not isinstance(slis, dict) or set(slis) != REQUIRED_SLIS:
        missing = ", ".join(sorted(REQUIRED_SLIS - set(slis or {})))
        extra = ", ".join(sorted(set(slis or {}) - REQUIRED_SLIS))
        raise SreConfigError(f"Danh sách SLI không đúng; thiếu: {missing or 'không'}; thừa: {extra or 'không'}")

    for name, slo in slis.items():
        if not isinstance(slo, dict):
            raise SreConfigError(f"SLI '{name}' phải là YAML object")
        missing = REQUIRED_SLO_FIELDS - set(slo)
        if missing:
            raise SreConfigError(f"SLI '{name}' thiếu: {', '.join(sorted(missing))}")
        if slo["operator"] not in {"lte", "gte"}:
            raise SreConfigError(f"SLI '{name}' dùng operator không hỗ trợ")
        if not isinstance(slo["objective"], (int, float)):
            raise SreConfigError(f"SLI '{name}'.objective phải là số")
        if not isinstance(slo["target"], (int, float)) or not 0 < slo["target"] <= 100:
            raise SreConfigError(f"SLI '{name}'.target phải nằm trong (0, 100]")
        if not isinstance(slo["minimum_requests"], int) or slo["minimum_requests"] < 1:
            raise SreConfigError(f"SLI '{name}'.minimum_requests phải là số nguyên dương")
        if not isinstance(slo["error_budget"], dict) or not slo["error_budget"]:
            raise SreConfigError(f"SLI '{name}'.error_budget không được rỗng")
        _require_duration(slo["evaluation_window"], f"slis.{name}.evaluation_window")
    return slis


def validate_alert_payload(payload: dict, slis: dict[str, dict], repo_root: Path) -> list[dict]:
    if payload.get("schema_version") != 1:
        raise SreConfigError("'alert_rules.schema_version' phải bằng 1")
    defaults = payload.get("defaults")
    if not isinstance(defaults, dict) or defaults.get("no_data_state") != "no_data":
        raise SreConfigError("Alert defaults phải đặt no_data_state: no_data")

    alerts = payload.get("alerts")
    if not isinstance(alerts, list) or not alerts:
        raise SreConfigError("'alerts' phải là danh sách không rỗng")
    names: set[str] = set()
    covered_slis: set[str] = set()
    expected_alert_operator = {"lte": "gt", "gte": "lt"}

    for index, alert in enumerate(alerts, start=1):
        if not isinstance(alert, dict):
            raise SreConfigError(f"Alert #{index} phải là YAML object")
        missing = REQUIRED_ALERT_FIELDS - set(alert)
        if missing:
            raise SreConfigError(f"Alert #{index} thiếu: {', '.join(sorted(missing))}")
        name = alert["name"]
        if name in names:
            raise SreConfigError(f"Tên alert bị trùng: {name}")
        names.add(name)
        if alert["severity"] not in {"warning", "critical"}:
            raise SreConfigError(f"Alert '{name}' có severity không hỗ trợ")
        if alert["type"] != "symptom-based":
            raise SreConfigError(f"Alert '{name}' phải là symptom-based")

        sli_name = alert["sli"]
        if sli_name not in slis:
            raise SreConfigError(f"Alert '{name}' tham chiếu SLI không tồn tại: {sli_name}")
        covered_slis.add(sli_name)
        slo = slis[sli_name]
        if alert["operator"] != expected_alert_operator[slo["operator"]]:
            raise SreConfigError(f"Alert '{name}' phải đảo chiều operator của SLO '{sli_name}'")
        if alert["threshold"] != slo["objective"]:
            raise SreConfigError(f"Alert '{name}' threshold không khớp objective của '{sli_name}'")
        if alert["evaluation_window"] != slo["evaluation_window"]:
            raise SreConfigError(f"Alert '{name}' evaluation_window không khớp SLO")
        if alert.get("minimum_requests", slo["minimum_requests"]) != slo["minimum_requests"]:
            raise SreConfigError(f"Alert '{name}' minimum_requests không khớp SLO")
        _require_duration(alert["duration"], f"alerts.{name}.duration")

        runbook = alert["runbook"]
        if not isinstance(runbook, str) or "#" not in runbook:
            raise SreConfigError(f"Alert '{name}' phải trỏ tới một runbook anchor")
        relative_path, anchor = runbook.split("#", 1)
        runbook_path = repo_root / relative_path
        try:
            markdown = runbook_path.read_text(encoding="utf-8")
        except FileNotFoundError as exc:
            raise SreConfigError(f"Không tìm thấy runbook của alert '{name}': {relative_path}") from exc
        if anchor not in _heading_anchors(markdown):
            raise SreConfigError(f"Runbook anchor của alert '{name}' không tồn tại: #{anchor}")

    uncovered = REQUIRED_SLIS - covered_slis
    if uncovered:
        raise SreConfigError(f"Các SLI chưa có alert: {', '.join(sorted(uncovered))}")
    return alerts


def validate_configs(slo_path: Path, alert_path: Path, repo_root: Path = REPO_ROOT) -> tuple[dict, dict]:
    slo_payload = _load_yaml(slo_path)
    alert_payload = _load_yaml(alert_path)
    slis = validate_slo_payload(slo_payload)
    validate_alert_payload(alert_payload, slis, repo_root)
    if alert_payload.get("service") != slo_payload.get("service"):
        raise SreConfigError("Service trong SLO và alert rules phải giống nhau")
    return slo_payload, alert_payload


def main() -> int:
    configure_utf8_stdio()
    parser = argparse.ArgumentParser(description="Kiểm tra SLO, alert rules và runbook")
    parser.add_argument("--slo", type=Path, default=REPO_ROOT / "config" / "slo.yaml")
    parser.add_argument("--alerts", type=Path, default=REPO_ROOT / "config" / "alert_rules.yaml")
    args = parser.parse_args()
    try:
        slo_payload, alert_payload = validate_configs(args.slo, args.alerts)
    except SreConfigError as exc:
        print(f"KHÔNG HỢP LỆ: {exc}")
        return 1
    print(
        f"HỢP LỆ: {len(slo_payload['slis'])} SLO/SLI, "
        f"{len(alert_payload['alerts'])} alert rules và tất cả runbook links tồn tại."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
