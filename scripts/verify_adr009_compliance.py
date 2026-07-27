#!/usr/bin/env python3

import json
from pathlib import Path


ROUTING_TRACE_LOG = Path("logs/routing_trace_log.jsonl")


def load_routing_traces():
    """
    Load all routing traces from the routing trace log.
    """

    if not ROUTING_TRACE_LOG.exists():
        raise FileNotFoundError(
            f"Routing trace log not found: {ROUTING_TRACE_LOG}"
        )

    traces = []

    with ROUTING_TRACE_LOG.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            traces.append(json.loads(line))

    return traces


def add_failure(failures, index, message):
    """
    Add a consistently formatted failure message.
    """

    failures.append(f"Trace {index}: {message}")


def print_check_result(name, failures):
    """
    Print verification result for a single compliance check.
    """

    if failures:
        print(f"\n{name} : FAILED ({len(failures)} issue(s))")

        for failure in failures:
            print(f" - {failure}")

    else:
        print(f"\n{name} : PASSED")


def verify_trace_structure(traces):
    """
    Verify every routing trace contains the minimum
    ADR-009 structural requirements.
    """

    required_top_level = {
        "event_type",
        "participant_id",
        "timestamp",
        "trace",
    }

    required_trace_fields = {
        "routing_status",
        "signals_considered",
        "dominant_signals",
        "routing_directives",
        "conflict_detected",
        "reasoning",
        "transparency_note",
    }

    failures = []

    for index, record in enumerate(traces, start=1):

        missing = required_top_level - record.keys()

        if missing:
            add_failure(
                failures,
                index,
                f"Missing top-level fields: {sorted(missing)}",
            )
            continue

        trace = record["trace"]

        if not isinstance(trace, dict):
            add_failure(
                failures,
                index,
                "'trace' is not a JSON object.",
            )
            continue

        missing = required_trace_fields - trace.keys()

        if missing:
            add_failure(
                failures,
                index,
                f"Missing trace fields: {sorted(missing)}",
            )

    return failures
def verify_routing_directives(traces):
    """
    Verify every routing trace contains a valid
    routing_directives object.
    """

    required_directives = {
        "stabilize",
        "reduce_difficulty",
        "increase_difficulty",
    }

    failures = []

    for index, record in enumerate(traces, start=1):

        directives = record["trace"].get("routing_directives")

        if not isinstance(directives, dict):
            add_failure(
                failures,
                index,
                "routing_directives is missing or invalid.",
            )
            continue

        missing = required_directives - directives.keys()

        if missing:
            add_failure(
                failures,
                index,
                f"Missing directives: {sorted(missing)}",
            )
            continue

        for key in required_directives:
            if not isinstance(directives[key], bool):
                add_failure(
                    failures,
                    index,
                    f"'{key}' is not boolean.",
                )

    return failures


def verify_reasoning_and_transparency(traces):
    """
    Verify that every routing decision is accompanied by
    human-readable reasoning and transparency metadata.
    """

    failures = []

    for index, record in enumerate(traces, start=1):

        trace = record["trace"]

        reasoning = trace.get("reasoning")
        transparency = trace.get("transparency_note")

        if not isinstance(reasoning, list):
            add_failure(
                failures,
                index,
                "reasoning is not a list.",
            )

        elif not reasoning:
            add_failure(
                failures,
                index,
                "reasoning is empty.",
            )

        if not isinstance(transparency, str):
            add_failure(
                failures,
                index,
                "transparency_note is not a string.",
            )

        elif not transparency.strip():
            add_failure(
                failures,
                index,
                "transparency_note is empty.",
            )

    return failures


def verify_signal_integrity(traces):
    """
    Verify every routing signal satisfies the
    ADR-009 evidence contract.
    """

    required_fields = {
        "signal_type",
        "value",
        "confidence",
        "priority",
        "source",
    }

    failures = []

    for index, record in enumerate(traces, start=1):

        signals = record["trace"].get("signals_considered")

        if not isinstance(signals, list):
            add_failure(
                failures,
                index,
                "signals_considered is not a list.",
            )
            continue

        for signal_number, signal in enumerate(signals, start=1):

            if not isinstance(signal, dict):
                add_failure(
                    failures,
                    index,
                    f"Signal {signal_number} is not an object.",
                )
                continue

            missing = required_fields - signal.keys()

            if missing:
                add_failure(
                    failures,
                    index,
                    f"Signal {signal_number} missing fields: {sorted(missing)}",
                )
                continue

            if not isinstance(signal["confidence"], (int, float)):
                add_failure(
                    failures,
                    index,
                    f"Signal {signal_number}: confidence is not numeric.",
                )

            if not isinstance(signal["priority"], int):
                add_failure(
                    failures,
                    index,
                    f"Signal {signal_number}: priority is not an integer.",
                )

            if (
                not isinstance(signal["source"], str)
                or not signal["source"].strip()
            ):
                add_failure(
                    failures,
                    index,
                    f"Signal {signal_number}: source is empty.",
                )

    return failures

def verify_dominant_signals(traces):
    """
    Verify every dominant signal originates from the
    signals considered during routing.
    """

    failures = []

    for index, record in enumerate(traces, start=1):

        trace = record["trace"]

        considered = trace.get("signals_considered")
        dominant = trace.get("dominant_signals")

        if not isinstance(considered, list):
            add_failure(
                failures,
                index,
                "signals_considered is not a list.",
            )
            continue

        if not isinstance(dominant, list):
            add_failure(
                failures,
                index,
                "dominant_signals is not a list.",
            )
            continue

        for signal_number, signal in enumerate(dominant, start=1):

            if signal not in considered:
                add_failure(
                    failures,
                    index,
                    f"Dominant signal {signal_number} does not exist in signals_considered.",
                )

    return failures


def main():
    traces = load_routing_traces()

    # Run Verification Checks
    structure_failures = verify_trace_structure(traces)
    directive_failures = verify_routing_directives(traces)
    reasoning_failures = verify_reasoning_and_transparency(traces)
    signal_failures = verify_signal_integrity(traces)
    dominant_signal_failures = verify_dominant_signals(traces)

    # Report Checks
    print("=" * 50)
    print("ADR-009 Compliance Verification")
    print("=" * 50)
    print(f"Routing traces loaded : {len(traces)}")

    print_check_result("Structure Check", structure_failures)
    print_check_result("Directive Check", directive_failures)
    print_check_result("Reasoning Check", reasoning_failures)
    print_check_result("Signal Integrity Check", signal_failures)
    print_check_result("Dominant Signal Check", dominant_signal_failures)

    # Overall Compliance Summary
    all_failures = (
        structure_failures
        + directive_failures
        + reasoning_failures
        + signal_failures
        + dominant_signal_failures
    )

    print("\n" + "=" * 50)

    if all_failures:
        print("ADR-009 COMPLIANCE : FAILED")
        print(f"Total Issues : {len(all_failures)}")
    else:
        print("ADR-009 COMPLIANCE : PASSED")
        print("All architectural verification checks succeeded.")

    print("=" * 50)


if __name__ == "__main__":
    main()
