from typing import List, Dict, Any, Optional
from collections import defaultdict
from app.evaluation.metrics import BinaryMetrics


class ConfusionMatrixEngine:
    """
    Forensic Confusion Matrix & Defensible Evaluation Engine (SATYA v2).
    Generates:
      1. Overall System Confusion Matrix (Preserving INCONCLUSIVE/REVIEW category)
      2. Detector-Level Confusion Matrices & Forensic Metrics
      3. Manipulation-Type Breakdown Matrix
      4. Image-Class Breakdown Matrix
    """
    VERSION = "2.0.0"

    def __init__(self):
        # Overall System Confusion Matrix: Ground Truth -> System Decision -> Count
        # Ground truth: 'AUTHENTIC', 'TAMPERED'
        # System decision: 'AUTHENTIC', 'TAMPERED', 'REVIEW'
        self.system_matrix: Dict[str, Dict[str, int]] = {
            "AUTHENTIC": {"AUTHENTIC": 0, "TAMPERED": 0, "REVIEW": 0},
            "TAMPERED": {"AUTHENTIC": 0, "TAMPERED": 0, "REVIEW": 0},
        }

        # Detector-level metrics: detector_name -> BinaryMetrics
        self.detector_metrics: Dict[str, BinaryMetrics] = defaultdict(BinaryMetrics)

        # Manipulation-type breakdown: manipulation_type -> detector_name -> {positive, negative, inconclusive}
        self.manipulation_breakdown: Dict[str, Dict[str, Dict[str, int]]] = defaultdict(
            lambda: defaultdict(lambda: {"positive": 0, "negative": 0, "inconclusive": 0, "total": 0})
        )

        # Image-class breakdown: image_class -> {AUTHENTIC, TAMPERED, REVIEW}
        self.image_class_breakdown: Dict[str, Dict[str, int]] = defaultdict(
            lambda: {"AUTHENTIC": 0, "TAMPERED": 0, "REVIEW": 0, "total": 0}
        )

    def record_sample(
        self,
        ground_truth: str,  # 'AUTHENTIC' or 'TAMPERED'
        system_decision: str,  # 'LIKELY_AUTHENTIC', 'LIKELY_TAMPERED', 'INCONCLUSIVE', 'requires_human_review'
        detector_observations: Dict[str, str],  # detector_name -> 'positive' | 'negative' | 'inconclusive' | 'not_applicable'
        manipulation_type: str = "UNKNOWN",
        image_class: str = "PHOTOGRAPH",
    ) -> None:
        """
        Records a single forensic specimen observation across all evaluation dimensions.
        """
        gt = ground_truth.upper()
        if gt not in self.system_matrix:
            self.system_matrix[gt] = {"AUTHENTIC": 0, "TAMPERED": 0, "REVIEW": 0}

        # Map system decision
        dec = system_decision.upper()
        if "TAMPER" in dec:
            pred_col = "TAMPERED"
        elif "AUTH" in dec and "NOT" not in dec:
            pred_col = "AUTHENTIC"
        else:
            pred_col = "REVIEW"

        self.system_matrix[gt][pred_col] += 1
        self.image_class_breakdown[image_class][pred_col] += 1
        self.image_class_breakdown[image_class]["total"] += 1

        # Record detector-level metrics
        for det_name, obs_status in detector_observations.items():
            obs = obs_status.lower().strip()
            bm = self.detector_metrics[det_name]
            bm.total += 1

            is_positive = (obs == "indicator_detected" or obs == "positive")
            is_negative = (obs == "no_indicator_detected" or obs == "negative")

            if is_positive:
                if gt == "TAMPERED":
                    bm.tp += 1
                else:
                    bm.fp += 1
                self.manipulation_breakdown[manipulation_type][det_name]["positive"] += 1
            elif is_negative:
                if gt == "AUTHENTIC":
                    bm.tn += 1
                else:
                    bm.fn += 1
                self.manipulation_breakdown[manipulation_type][det_name]["negative"] += 1
            else:
                bm.inconclusive += 1
                self.manipulation_breakdown[manipulation_type][det_name]["inconclusive"] += 1
            self.manipulation_breakdown[manipulation_type][det_name]["total"] += 1

    def compute_summary(self) -> Dict[str, Any]:
        """
        Calculates all summary matrices and performance metrics.
        """
        det_summary = {
            det_name: bm.summary_dict()
            for det_name, bm in self.detector_metrics.items()
        }

        # Format manipulation type summary table
        manip_summary: Dict[str, Dict[str, Any]] = {}
        for m_type, dets in self.manipulation_breakdown.items():
            manip_summary[m_type] = {}
            for d_name, counts in dets.items():
                tot = max(1, counts["total"])
                manip_summary[m_type][d_name] = {
                    "positive_count": counts["positive"],
                    "positive_rate_pct": round(counts["positive"] / tot * 100.0, 1),
                    "inconclusive_rate_pct": round(counts["inconclusive"] / tot * 100.0, 1),
                    "total": counts["total"],
                }

        return {
            "overall_system_confusion_matrix": self.system_matrix,
            "detector_level_confusion_matrices": det_summary,
            "manipulation_type_matrix": manip_summary,
            "image_class_matrix": dict(self.image_class_breakdown),
        }

    def format_markdown_report(self) -> str:
        """
        Generates a publication-grade GitHub Flavored Markdown report.
        """
        md = []
        md.append("## SCSS SATYA v2 — Forensic Evaluation & Confusion Matrix Report\n")

        # 1. Overall System Matrix
        md.append("### 1. Overall System Decision Matrix")
        md.append("| Ground Truth | System: Authentic | System: Tampered | System: Review / Inconclusive | Total |")
        md.append("|---|---|---|---|---|")
        for gt, cols in sorted(self.system_matrix.items()):
            tot = sum(cols.values())
            md.append(f"| **{gt}** | {cols.get('AUTHENTIC', 0)} | {cols.get('TAMPERED', 0)} | {cols.get('REVIEW', 0)} | **{tot}** |")

        # 2. Detector Performance Table
        md.append("\n### 2. Detector-Level Forensic Metrics")
        md.append("| Detector | Sensitivity | Specificity | Precision | F1 | Balanced Acc | MCC | Inconclusive Rate | Decisive Total |")
        md.append("|---|---|---|---|---|---|---|---|---|")
        for det_name, bm in sorted(self.detector_metrics.items()):
            sens = f"{bm.sensitivity * 100:.1f}%" if bm.sensitivity is not None else "N/A"
            spec = f"{bm.specificity * 100:.1f}%" if bm.specificity is not None else "N/A"
            prec = f"{bm.precision * 100:.1f}%" if bm.precision is not None else "N/A"
            f1 = f"{bm.f1:.3f}" if bm.f1 is not None else "N/A"
            bacc = f"{bm.balanced_accuracy * 100:.1f}%" if bm.balanced_accuracy is not None else "N/A"
            mcc = f"{bm.mcc:.3f}" if bm.mcc is not None else "N/A"
            inconcl = f"{bm.inconclusive_rate * 100:.1f}%"
            md.append(f"| `{det_name}` | {sens} | {spec} | {prec} | {f1} | {bacc} | {mcc} | {inconcl} | {bm.decisive_total} |")

        # 3. Manipulation Type Table
        md.append("\n### 3. Manipulation-Type Detection Sensitivity Breakdown")
        m_types = sorted(self.manipulation_breakdown.keys())
        key_dets = [
            "copy_move_forgery_detection",
            "image_splicing_detector",
            "noise_residual_analysis",
            "ai_generative_classifier",
            "error_level_analysis",
            "document_typography_and_alignment",
        ]
        md.append("| Manipulation Type | " + " | ".join(f"`{d[:12]}`" for d in key_dets) + " |")
        md.append("|---" * (len(key_dets) + 1) + "|")
        for mt in m_types:
            row = [f"**{mt}**"]
            for d in key_dets:
                stats = self.manipulation_breakdown[mt].get(d, {"positive": 0, "total": 0})
                tot = max(1, stats["total"])
                rate = (stats["positive"] / tot) * 100.0
                row.append(f"{rate:.1f}% ({stats['positive']}/{tot})")
            md.append("| " + " | ".join(row) + " |")

        return "\n".join(md)
