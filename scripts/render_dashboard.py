"""Render a dependency-light runtime dashboard from the lab JSONL logs.

The YAML dashboard contract remains the source of truth for panel names,
units, aggregations and thresholds. This renderer turns that contract and the
same ``data/logs.jsonl`` source into a shareable HTML dashboard.
"""

from __future__ import annotations

import argparse
import html
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import mean

import yaml


def percentile(values: list[float], percentile_value: int) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, math.ceil(percentile_value / 100 * len(ordered)) - 1))
    return ordered[index]


def load_records(path: Path, minutes: int) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"Log source not found: {path}")
    records = [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    timestamps = [datetime.fromisoformat(record["ts"].replace("Z", "+00:00")) for record in records if record.get("ts")]
    if not timestamps:
        return []
    cutoff = max(timestamps) - timedelta(minutes=minutes)
    return [
        record
        for record in records
        if record.get("ts")
        and datetime.fromisoformat(record["ts"].replace("Z", "+00:00")) >= cutoff
    ]


def calculate(records: list[dict]) -> dict[str, object]:
    responses = [record for record in records if record.get("event") == "response_sent"]
    requests = [record for record in records if record.get("event") == "request_received"]
    failures = [record for record in records if record.get("event") == "request_failed"]
    latencies = [float(record["latency_ms"]) for record in responses if record.get("latency_ms") is not None]
    costs = [float(record["cost_usd"]) for record in responses if record.get("cost_usd") is not None]
    tokens_in = sum(int(record.get("tokens_in", 0)) for record in responses)
    tokens_out = sum(int(record.get("tokens_out", 0)) for record in responses)
    quality = [float(record["quality_score"]) for record in responses if record.get("quality_score") is not None]
    errors = len(failures) / len(requests) * 100 if requests else 0.0
    return {
        "latency": f"P50 {percentile(latencies, 50):.0f} ms · P95 {percentile(latencies, 95):.0f} ms · P99 {percentile(latencies, 99):.0f} ms",
        "traffic": f"{len(requests)} requests",
        "errors": f"{errors:.2f}% ({len(failures)} failures)",
        "cost": f"${sum(costs):.4f}",
        "tokens": f"{tokens_in:,} in · {tokens_out:,} out",
        "quality": f"{mean(quality):.3f}" if quality else "0.000",
    }


def render(records: list[dict], contract: dict, generated_at: datetime) -> str:
    dashboard = contract["dashboard"]
    values = calculate(records)
    cards = []
    for panel in dashboard["panels"]:
        panel_id = panel["id"]
        threshold = panel["threshold"]
        threshold_text = f"{threshold['aggregation']} {threshold['operator']} {threshold['value']} {panel['unit']}"
        cards.append(
            f"<article class='card'><h2>{html.escape(panel['title'])}</h2>"
            f"<div class='value'>{html.escape(str(values[panel_id]))}</div>"
            f"<div class='unit'>Unit: {html.escape(panel['unit'])}</div>"
            f"<div class='threshold'>Threshold: {html.escape(threshold_text)}</div></article>"
        )
    return f"""<!doctype html>
<html lang='en'><head><meta charset='utf-8'><meta http-equiv='refresh' content='{dashboard['refresh_seconds']}'>
<title>{html.escape(dashboard['title'])}</title>
<style>body{{font-family:system-ui,sans-serif;background:#f4f7fb;color:#172033;max-width:1200px;margin:2rem auto;padding:0 1rem}}.meta{{color:#536176}}.grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1rem}}.card{{background:#fff;border:1px solid #dce3ed;border-radius:12px;padding:1.25rem;box-shadow:0 2px 8px #17203312}}h2{{font-size:1.05rem;margin-top:0}}.value{{font-size:1.55rem;font-weight:700;margin:1rem 0}}.unit,.threshold{{font-size:.85rem;color:#536176;margin-top:.4rem}}@media(max-width:700px){{.grid{{grid-template-columns:1fr}}}}</style></head>
<body><h1>{html.escape(dashboard['title'])}</h1>
<p class='meta'>Source: data/logs.jsonl · Time range: last {dashboard['time_range_minutes']} minutes · Refresh: {dashboard['refresh_seconds']} seconds · Generated: {generated_at.isoformat()}</p>
<section class='grid'>{''.join(cards)}</section></body></html>"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Render the Day 13 observability dashboard")
    parser.add_argument("--logs", type=Path, default=Path("data/logs.jsonl"))
    parser.add_argument("--config", type=Path, default=Path("config/dashboard.yaml"))
    parser.add_argument("--output", type=Path, default=Path("submission/evidence/dashboard.html"))
    args = parser.parse_args()
    contract = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    records = load_records(args.logs, int(contract["dashboard"]["time_range_minutes"]))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(records, contract, datetime.now(timezone.utc)), encoding="utf-8")
    print(f"Dashboard rendered: {args.output} ({len(records)} records, 6 panels)")


if __name__ == "__main__":
    main()
