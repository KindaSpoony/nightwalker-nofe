import yaml, os
from datetime import datetime, timezone
from jinja2 import Template
from nofe.ingestion import fetch_rss
from nofe.analysis import NightwalkerAgentStack, evaluate_truth_vector
from collections import Counter
from itertools import combinations

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

    stack = NightwalkerAgentStack()
    rendered_items = []
    co_occurrence_counter: Counter = Counter()

    for it in items:
        summary = it.get("summary", "")
        tv = evaluate_truth_vector(summary)
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
            "entities": ", ".join(entities)
        })

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
    # Print the path for debugging/logging
    print(out_path)


if __name__ == "__main__":
    main()
