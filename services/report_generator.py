import pandas as pd
from datetime import datetime
from pathlib import Path


class ReportGenerator:
    """Generate detection reports."""

    @staticmethod
    def generate_csv(results: list[dict], output_path: str) -> str:
        """Generate CSV report from detection results."""
        df = pd.DataFrame(results)

        # Ensure required columns
        columns = ["filename", "status", "violated_rules", "details", "checked_at"]
        for col in columns:
            if col not in df.columns:
                df[col] = ""

        df = df[columns]
        df.to_csv(output_path, index=False, encoding="utf-8-sig")
        return output_path

    @staticmethod
    def create_result(
        filepath: str,
        is_compliant: bool,
        violated_rules: list[str] = None,
        details: str = ""
    ) -> dict:
        """Create a single detection result entry."""
        return {
            "filename": Path(filepath).name,
            "status": "合规" if is_compliant else "不合规",
            "violated_rules": ", ".join(violated_rules or []),
            "details": details,
            "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
