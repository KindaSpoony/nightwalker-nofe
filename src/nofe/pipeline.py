import yaml
import os
from datetime import datetime, timezone
from pathlib import Path
from jinja2 import Template
from collections import Counter
from itertools import combinations

from nofe.ingestion import fetch_rss
from nofe.analysis import NightwalkerAgentStack, evaluate_truth_vector
from nofe.ai_analysis import generate_ai_analysis  # assumes you’ve implemented this
                                                   # as described earlier

# Paths relative to this file; BASE points to src/nofe, ROOT is the repo root
BASE = os.path.dirname(os.path.dirname(__file__))
ROOT = os.path.dirname(BASE)


def load_config() -> dict:
    """Load configuration from YAML file located at src/nofe/config.yaml."""
    cfg_path = os.path.join(BASE, "config.yaml")
    if not os.path.isfile(cfg_path):
        return {}  # fallback to defaults if config is missing
    with open(cfg_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_template() -> Template:
    """Load the report template from the prompts directory."""
    template_path = os.path.join(ROOT, "prompts", "chaos_template.md")
    with open(template_path, "r", encoding="utf-8") as f:
        return Template(f.read())


def main() -> None:
    """Main entry point for generating the CHAOS report (and optional AI analysis)."""
    cfg = load_config()
    feeds = cfg.get("feeds", [])
    max_items = cfg.get("max_items_per_feed", 8)
    tz = cfg.get("report_timezone", "UTC")

    items = fetch_rss(feeds, max_items)

    stack = NightwalkerAgentStack()
    rendered_items = []
    co_occurrence_counter: Counter = Counter()

    for it in items:
        summary = it.get("summary", "")

        # Support both return shapes from evaluate_truth_vector
        res = evaluate_truth_vector(summary)
        if isinstance(res, tuple):
            tv, tv_score, tv_pass = res
        else:
            tv, tv_score, tv_pass = res, None, None

        entities = stack.extract_entities(summary) or []

        # Deduplicate while preserving order
        unique_entities = list(dict.fromkeys(entities))
        # Count co-occurrences of entity pairs
        for a, b in combinations(unique_entities, 2):
            pair = tuple(sorted((a, b)))
            co_occurrence_counter[pair] += 1

        item_row = {
            "title": it.get("title"),
            "link": it.get("link"),
            "published": it.get("published"),
            "source": it.get("source"),
            "summary": summary,
            "thinker": stack.thinker(summary),
            "doer": stack.doer(summary),
            "controller": stack.controller(summary),
            "pulse": stack.pulse(summary),
            "truth_vector": tv.to_dict(),
            "entities": ", ".join(entities),
        }
        # Add score/pass only if provided so templates don’t break
        if tv_score is not None:
            item_row["truth_score"] = round(tv_score, 4)
            item_row["truth_pass"] = tv_pass

        rendered_items.append(item_row)

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
    report_text = template.render(
        timestamp=ts,
        top_signals=top_signals,
        pulse_summary=pulse_summary,
        confidence_summary=confidence_summary,
        items=rendered_items,
        entity_co_occurrences=co_occurrences_summary
    )

    # Write the standard CHAOS report
    out_dir = os.path.join(ROOT, "reports")
    os.makedirs(out_dir, exist_ok=True)
    date_stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    report_path = os.path.join(out_dir, f"CHAOS_{date_stamp}.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    print(report_path)  # for logging/debugging

    # Optionally run AI analysis
    if cfg.get("enable_ai_analysis"):
        ai_summary = generate_ai_analysis(report_text, cfg=cfg)
        inline = cfg.get("ai_analysis_inline", False)
        if inline:
            # Append AI analysis to the same report
            with open(report_path, "a", encoding="utf-8") as f:
                f.write("\n\n## AI Analysis\n\n")
                f.write(ai_summary)
                f.write("\n")
        else:
            # Write AI analysis to a separate file
            ai_path = os.path.join(out_dir, f"AI_CHAOS_{date_stamp}.md")
            Path(ai_path).write_text("# AI Analysis\n\n" + ai_summary)
            print(ai_path)  # for logging/debugging


if __name__ == "__main__":
    main()
