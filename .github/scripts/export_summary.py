"""Read sync-report.json and export GitHub Actions step summary + outputs.

Kept as a plain script (not part of the package) so the workflow can call it
without importing the project. It tolerates a missing report (e.g. when the
pipeline crashed before writing one) and still emits a failure signal.
"""

from __future__ import annotations

import json
import os


def _clean(value) -> str:
    return str(value if value is not None else "unknown").replace("\n", " ").replace("\r", " ")


def main() -> None:
    report: dict = {}
    try:
        with open("sync-report.json", encoding="utf-8") as handle:
            report = json.load(handle)
    except FileNotFoundError:
        print("sync-report.json not found; nothing to export")

    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as handle:
            handle.write(f"status={_clean(report.get('status', 'failure'))}\n")
            handle.write(f"failure_reason={_clean(report.get('failure_reason'))}\n")
            handle.write(f"domains_total={report.get('domains_total', 0)}\n")
            handle.write(f"domains_added={report.get('domains_added', 0)}\n")
            handle.write(f"domains_removed={report.get('domains_removed', 0)}\n")

    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        status = _clean(report.get("status", "failure"))
        with open(summary_path, "a", encoding="utf-8") as handle:
            handle.write("\n## Cloudflare DNS list sync\n")
            handle.write(f"- **Status**: `{status}`\n")
            handle.write(f"- **Domains total**: {report.get('domains_total', 0):,}\n")
            handle.write(f"- **Added**: +{report.get('domains_added', 0):,}\n")
            handle.write(f"- **Removed**: -{report.get('domains_removed', 0):,}\n")
            reason = report.get("failure_reason")
            if reason:
                handle.write(f"- **Reason**: {_clean(reason)}\n")


if __name__ == "__main__":
    main()
