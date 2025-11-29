import csv
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from itertools import combinations
import pathlib

import yaml
from jinja2 import Template

# Ensure `src/` is on the import path so running the script directly works
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nofe.analysis import NightwalkerAgentStack, evaluate_truth_vector
from nofe.ingestion import fetch_rss

BASE = os.path.dirname(os.path.dirname(__file__))
ROOT = os.path.dirname(BASE)

def load_config():
    """Load configuration from YAML file located at src/config.yaml."""
    with open(os.path.join(BASE, "config.yaml"), "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_template():
    """Load the report template from the prompts directory."""
    with open(os.path.join(ROOT, "prompts", "chaos_template.md"), "r", encoding="utf-8") as f:
        return Template(f.read())

def main():
    cfg = load_config()
    feeds = cfg.get("feeds", [])
    max_items = cfg.get("max_items_per_feed", 8)
    tz = cfg.get("report_timezone", "UTC")
    items = fetch_rss(feeds, max_items)

    # Load truth vector config
    tv_cfg = cfg.get("truth_vector", {}) if isinstance(cfg, dict) else {}
    tv_weights = (tv_cfg.get("weights") or {})
    tv_threshold = tv_cfg.get("threshold")
    log_path = tv_cfg.get("log_path", "reports/calibration_log.csv")

    stack = NightwalkerAgentStack()
    rendered_items = []
    co_occurrence_counter: Counter = Counter()

    for it in items:
        summary = it.get("summary", "")
        tv, tv_score, tv_pass = evaluate_truth_vector(summary, tv_weights, tv_threshold)
        entities = stack.extract_entities(summary) or []

        # Deduplicate while preserving order
        unique_entities = list(dict.fromkeys(entities))
        # Count co-occurrences of entity pairs
        for a, b in combinations(unique_entities, 2):
            pair = tuple(sorted((a, b)))
            co_occurrence_counter[pair] += 1

        rendered_items.append({
            "title": it["title"],
            "link": it["link"],
            "published": it["published"],
            "source": it["source"],
            "summary": summary,
            "thinker": stack.thinker(summary),
            "doer": stack.doer(summary),
            "controller": stack.controller(summary),
            "pulse": stack.pulse(summary),
            "truth_vector": tv.to_dict(),
            "truth_score": round(tv_score, 4),
            "truth_pass": tv_pass,
            "entities": ", ".join(entities)
        })

    # Write calibration log
    pathlib.Path("reports").mkdir(parents=True, exist_ok=True)
    need_header = not pathlib.Path(log_path).exists()
    with open(log_path, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if need_header:
            w.writerow(["timestamp","source","title",
                        "empirical","logical","emotional","historical",
                        "truth_score","truth_pass","label"])
        now = datetime.now(timezone.utc).isoformat()
        for r in rendered_items:
            tv_dict = r["truth_vector"]
            w.writerow([
                now, r["source"], r["title"],
                tv_dict["empirical"], tv_dict["logical"], tv_dict["emotional"], tv_dict["historical"],
                r["truth_score"], int(r["truth_pass"]),
                ""
            ])

    # Build top co-occurrence summary
    co_occurrences_summary = ""
    if co_occurrence_counter:
        top_pairs = co_occurrence_counter.most_common(5)
        lines = []
        for (a, b), count in top_pairs:
            lines.append(f"{a} & {b} ({count})")
        co_occurrences_summary = "\n".join(lines)

    top_signals = ", ".join([x["title"] for x in rendered_items[:3]])
    pulse_summary = "Auto sentiment drift proxy across items."
    confidence_summary = "MVP auto-scored; requires human validation."

    template = load_template()
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    report = template.render(
        timestamp=ts,
        top_signals=top_signals,
        pulse_summary=pulse_summary,
        confidence_summary=confidence_summary,
        items=rendered_items,
        entity_co_occurrences=co_occurrences_summary
    )

    out_dir = os.path.join(ROOT, "reports")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"CHAOS_{datetime.now(timezone.utc).strftime('%Y%m%d')}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(out_path)

if __name__ == "__main__":
    main()
