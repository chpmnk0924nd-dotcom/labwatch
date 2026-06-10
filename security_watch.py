from pathlib import Path


SECURITY_REPORT_PATH = Path("security_reports/latest_security_report.txt")


def get_latest_security_report():
    """
    Read the latest Security Watch report from the local LabWatch security_reports folder.
    """

    if not SECURITY_REPORT_PATH.exists():
        return {
            "found": False,
            "content": "No Security Watch report found yet.",
            "path": str(SECURITY_REPORT_PATH),
        }

    try:
        content = SECURITY_REPORT_PATH.read_text(encoding="utf-8", errors="replace")

        return {
            "found": True,
            "content": content,
            "path": str(SECURITY_REPORT_PATH),
        }

    except Exception as e:
        return {
            "found": False,
            "content": f"Could not read Security Watch report: {e}",
            "path": str(SECURITY_REPORT_PATH),
        }