from project.governance.validation.topology_validation import (
    is_transition_allowed,
    requires_reevaluation,
)


TEST_CASES = [

    (
        "suppression",
        "stabilization",
        True,
    ),

    (
        "suppression",
        "unrestricted",
        False,
    ),

    (
        "stabilization",
        "rehabilitation",
        True,
    ),

    (
        "rehabilitation",
        "unrestricted",
        False,
    ),

    (
        "low_authority",
        "unrestricted",
        True,
    ),
]


print("\n=== TOPOLOGY VALIDATION ===\n")


for source, target, expected in TEST_CASES:

    result = is_transition_allowed(
        source,
        target,
    )

    status = (
        "PASS"
        if result == expected
        else "FAIL"
    )

    print(
        f"{status} | "
        f"{source} -> {target} | "
        f"allowed={result}"
    )


print("\n=== REEVALUATION GATES ===\n")


REEVALUATION_CASES = [

    (
        "stabilization",
        "rehabilitation",
    ),

    (
        "low_authority",
        "unrestricted",
    ),

    (
        "suppression",
        "stabilization",
    ),
]


for source, target in REEVALUATION_CASES:

    gated = requires_reevaluation(
        source,
        target,
    )

    print(
        f"{source} -> {target} | "
        f"reevaluation_required={gated}"
    )
