import csv
import re
import json
from pathlib import Path
from typing import Dict, Any, Optional

from app.core.config import settings
from app.evaluation.confusion_matrix_engine import ConfusionMatrixEngine


def evaluate_historical_dataset(csv_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Parses the 1,005-specimen execution results from the separate test device
    and constructs publication-grade forensic confusion matrices and performance metrics.
    """
    if csv_path is None:
        csv_path = settings.ROOT_DIR / "results.csv"

    if not csv_path.exists():
        raise FileNotFoundError(f"Historical results file not found at {csv_path}")

    engine = ConfusionMatrixEngine()

    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            path_str = row["path"]
            if "authentic" in path_str:
                ground_truth = "AUTHENTIC"
                manip_type = "AUTHENTIC"
            else:
                ground_truth = "TAMPERED"
                m = re.search(r"morph_\d+_(\w+)\.jpg", path_str)
                manip_type = m.group(1).upper() if m else "TAMPERED_OTHER"

            system_dec = row["overall_assessment"]  # 'requires_human_review' in historical run

            # Parse indicators string: method1=val1;method2=val2...
            detector_obs: Dict[str, str] = {}
            for item in row["indicators"].split(";"):
                if "=" in item:
                    k, v = item.strip().split("=", 1)
                    detector_obs[k] = v

            engine.record_sample(
                ground_truth=ground_truth,
                system_decision=system_dec,
                detector_observations=detector_obs,
                manipulation_type=manip_type,
                image_class="PHOTOGRAPH",
            )

    summary = engine.compute_summary()
    md_report = engine.format_markdown_report()

    # Save to storage/reports
    reports_dir = settings.STORAGE_DIR / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    json_out = reports_dir / "historical_1005_evaluation.json"
    with open(json_out, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    md_out = reports_dir / "historical_1005_evaluation.md"
    with open(md_out, "w", encoding="utf-8") as f:
        f.write(md_report)

    return summary


if __name__ == "__main__":
    print("Evaluating historical 1,005 examination run...")
    results = evaluate_historical_dataset()
    print("Done. System Confusion Matrix:")
    print(json.dumps(results["overall_system_confusion_matrix"], indent=2))
