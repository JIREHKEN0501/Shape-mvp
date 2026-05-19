from pathlib import Path


REPORTING_PATH = Path(
    "project/governance/validation/reporting.py"
)


content = REPORTING_PATH.read_text()


OLD = '''
    governance_status: str = "unknown"
'''


NEW = '''
    governance_status: str = "unknown"

    def to_dict(self) -> Dict[str, object]:
        """
        Serialize governance validation report.
        """

        return {
            "total_assertions": self.total_assertions,
            "passed_assertions": self.passed_assertions,
            "failed_assertions": self.failed_assertions,
            "governance_status": self.governance_status,
            "severity_counts": self.severity_counts,
            "violations": [
                violation.to_dict()
                for violation in self.violations
            ],
        }
'''


if "def to_dict" not in content:

    content = content.replace(OLD, NEW)


REPORTING_PATH.write_text(content)

print("Governance report serialization added.")
