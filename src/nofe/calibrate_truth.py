3) Pipe config into scoring + log rows
Edit src/nofe/pipeline.py where we currently call evaluate_truth_vector. Load weights/threshold from config, and log outputs for calibration.

Add near your config load:

python
Copy
Edit
tv_cfg = cfg.get("truth_vector", {}) if isinstance(cfg, dict) else {}
tv_weights = (tv_cfg.get("weights") or {})
tv_threshold = tv_cfg.get("threshold")
log_path = tv_cfg.get("log_path", "reports/calibration_log.csv")
Replace the current call site:

python
Copy
Edit
tv, tv_score, tv_pass = evaluate_truth_vector(it.get("summary",""), tv_weights, tv_threshold)
When building rendered_items, include:

python
Copy
Edit
"truth_vector": asdict(tv),
"truth_score": round(tv_score, 4),
"truth_pass": tv_pass,
After the loop (before rendering), append a CSV row for each item so you get a running dataset. Add this helper up top:

python
Copy
Edit
import csv, pathlib
Then after you finish rendered_items, write:

python
Copy
Edit
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
        tv = r["truth_vector"]
        w.writerow([
            now, r["source"], r["title"],
            tv["empirical"], tv["logical"], tv["emotional"], tv["historical"],
            r["truth_score"], int(r["truth_pass"]),
            ""  # label to be filled in later: 1=good,0=bad
        ])
You’ll add labels later (manually: open CSV, fill label column for a sample of rows).
