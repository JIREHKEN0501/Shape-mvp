from pathlib import Path


TEST_PATH = Path(
    "scripts/test_governance_validation.py"
)


content = TEST_PATH.read_text()


IMPORT_BLOCK = '''
from project.governance.validation.reporting import (
    generate_validation_report,
)
'''


if "generate_validation_report" not in content:

    marker = '''
from project.governance.validation.telemetry import (
    telemetry_buffer,
)
'''

    content = content.replace(
        marker,
        marker + IMPORT_BLOCK,
    )


REPORT_BLOCK = '''

    report = generate_validation_report(results)

    print("\\n--- GOVERNANCE REPORT ---\\n")

    pprint({
        "governance_status": report.governance_status,
        "total_assertions": report.total_assertions,
        "passed_assertions": report.passed_assertions,
        "failed_assertions": report.failed_assertions,
        "severity_counts": report.severity_counts,
    })
'''


marker = '''
    print("\\n--- TELEMETRY EVENTS ---\\n")
'''


if "--- GOVERNANCE REPORT ---" not in content:

    content = content.replace(
        marker,
        REPORT_BLOCK + marker,
    )


TEST_PATH.write_text(content)

print("Governance reporting integrated into test suite.")
