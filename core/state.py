from typing import Optional, TypedDict

from core.models import Draft, Finding, VerificationResult


class SpineState(TypedDict, total=False):
    """
    State that flows through the linear spine graph.

    total=False so nodes can fill fields progressively; a node that
    fails sets `status` + `error` and later nodes short-circuit.
    """
    days: int                                  # input: how far back to fetch
    archetype: str                             # input: which archetype to write

    findings: list[Finding]                    # research node output
    finding: Optional[Finding]                 # the selected finding
    draft: Optional[Draft]                     # write node output
    verifications: dict[str, VerificationResult]   # {variant_id: result}

    status: str        # 'ok' | 'no_findings' | 'insufficient_input'
                       # | 'write_failed' | 'all_blocked' | 'error'
    error: str         # human-readable failure detail, '' when fine

     # first-party flags, set by the interview flow, read by strategy
    is_first_party: bool
    has_real_completion: bool
    has_real_failure: bool
    has_real_measurement: bool