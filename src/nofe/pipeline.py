import yaml, os
from datetime import datetime, timezone
from jinja2 import Template
from nofe.ingestion import fetch_rss
from nofe.analysis import NightwalkerAgentStack, evaluate_truth_vector

BASE = os.path.dirname(os.path.dirname(__file__))
ROOT = os.path.dirname(BASE)

def load_config():
    with open(os.path.join(BASE, "config.yaml"), "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_template():
    with open(os.path.join(ROOT, "prompts", "chaos_template.md"), "r", encoding="utf-8") as f:
        return Template(f.read())

def main():
    cfg = load_config()
    feeds = cfg.get("feeds", [])
    max_items = cfg.get("max_items_per_feed", 5)

    items = fetch_rss(feeds, max_items)
    stack = NightwalkerAgentStack()
    rendered_items = []
    for it in items:
        tv = evaluate_truth_vector(it.get("summary", ""))
        rendered_items.append({
            "title": it["title"],
            "link": it["link"],
            "published": it["published"],
            "source": it["source"],
            "summary": it["summary"],
            "thinker": stack.thinker(it["summary"]),
            "doer": stack.doer(it["summary"]),
            "controller": stack.controller(it["summary"]),
            "pulse": stack.pulse(it["summary"]),
            "truth_vector": tv.to_dict()
        })

    top_signals = ", ".join([x["title"] for x in rendered_items[:3]])
    pulse_summary = "Automated sentiment drift proxy."
    confidence_summary = "MVP auto-scored; requires human review."

    template = load_template()
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    report = template.render(
        timestamp=ts,
        top_signals=top_signals,
        pulse_summary=pulse_summary,
        confidence_summary=confidence_summary,
        items=rendered_items
    )

    out_dir = os.path.join(ROOT, "reports")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"CHAOS_{datetime.now(timezone.utc).strftime('%Y%m%d')}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Report generated: {out_path}")

if __name__ == "__main__":
    main()
