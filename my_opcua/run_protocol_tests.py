from __future__ import annotations

import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

AGENT_ROOT = Path(__file__).resolve().parents[2]
if str(AGENT_ROOT) not in sys.path:
    sys.path.insert(0, str(AGENT_ROOT))

from tools_requirements import _load_spec, build_evidence_document, record_acceptance_result, traceability_report
from execution_policy import authorization_scope
from runtime_support import atomic_write, redact_data

for _stream in (sys.stdout, sys.stderr):
    if not _stream.isatty() and hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            pass


class EvidenceResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cases = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.cases.append({"test": test.id(), "status": "pass"})

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.cases.append({"test": test.id(), "status": "fail", "error": self._exc_info_to_string(err, test)})

    def addError(self, test, err):
        super().addError(test, err)
        self.cases.append({"test": test.id(), "status": "error", "error": self._exc_info_to_string(err, test)})

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.cases.append({"test": test.id(), "status": "skipped", "reason": reason})


def main() -> int:
    root = Path(__file__).resolve().parent
    suite = unittest.defaultTestLoader.discover(str(root), pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2, resultclass=EvidenceResult)
    result = runner.run(suite)
    passed = result.wasSuccessful() and result.testsRun >= 6 and not result.skipped
    output = root / "evidence" / "local_protocol_tests.json"
    spec_path, spec = _load_spec(str(root / "requirements.yaml"))
    covered = [rid for rid in ("FR-001", "IF-001", "SAFE-001") if any(req["id"] == rid for req in spec["requirements"])]
    report = build_evidence_document(spec_path, spec, covered, scope="local_simulation",
                                     reporter="my-opcua-local-protocol-runner",
                                     run_id=datetime.now(timezone.utc).strftime("protocol-%Y%m%dT%H%M%S%fZ"),
                                     checks=[{"name": case["test"], "status": "PASS" if case["status"] == "pass" else "FAIL"} for case in result.cases],
                                     status="PASS" if passed else "FAIL", evidence_paths=[str(output)])
    report.update({
        "boundary": "LOCAL_SIMULATION_NOT_DEVICE_OR_CUSTOMER_ACCEPTANCE",
        "security": "ANONYMOUS_LOOPBACK_ONLY",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if passed else "FAIL",
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "cases": result.cases,
    })
    atomic_write(output, json.dumps(redact_data(report), ensure_ascii=False, indent=2))
    # This runner can attest only its own loopback tests, never physical acceptance.
    def allow_local_record(operation):
        args = operation["arguments"]
        return operation["tool"] == "record_acceptance_result" and args["spec_path"] == str(spec_path) and args["requirement_id"] in covered
    with authorization_scope(allow_local_record):
        for rid in covered:
            print(record_acceptance_result(str(spec_path), rid, "pass" if passed else "fail", evidence="evidence/local_protocol_tests.json", notes="本地环回协议测试，不代表真实 PLC 或客户验收", tester="local-protocol-runner"))
    print(traceability_report(str(spec_path)))
    print(f"本地协议测试证据: {output}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
