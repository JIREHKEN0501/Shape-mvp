from pathlib import Path


TEST_PATH = Path(
    "scripts/test_governance_validation.py"
)


content = TEST_PATH.read_text()


OLD = '''
    pprint({
        "governance_status": report.governance_status,
        "total_assertions": report.total_assertions,
        "passed_assertions": report.passed_assertions,
        "failed_assertions": report.failed_assertions,
        "severity_counts": report.severity_counts,
    })
'''


NEW = '''
    pprint(report.to_dict())
'''


content = content.replace(OLD, NEW)


TEST_PATH.write_text(content)

print(
    "Test suite updated to use report serialization."
)
