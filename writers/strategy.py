from dataclasses import dataclass


@dataclass(frozen=True)
class StrategyDecision:
    archetype: str
    reason: str


# These are the archetypes we can safely select automatically
# at this stage.
#
# More sophisticated routing will come with the ranker/synthesis
# layer in the next stages of ContentForge.

def choose_archetype(
    source_type: str,
    *,
    is_first_party: bool = False,
    has_real_failure: bool = False,
    has_real_measurement: bool = False,
    has_real_completion: bool = False,
) -> StrategyDecision:

    # First-party completed work
    if is_first_party and has_real_completion:
        return StrategyDecision(
            archetype="BUILD_ANNOUNCE",
            reason=(
                "First-party work has a real completed milestone."
            ),
        )

    # First-party work that is actively being built
    if is_first_party:
        return StrategyDecision(
            archetype="SHIP_LOG",
            reason=(
                "First-party work is available for a build/ship update."
            ),
        )

    # Real failure
    if has_real_failure:
        return StrategyDecision(
            archetype="FAILURE_LESSON",
            reason=(
                "A real failure is available in the source context."
            ),
        )

    # Real measurement
    if has_real_measurement:
        return StrategyDecision(
            archetype="BENCHMARK_COMPARISON",
            reason=(
                "A real measured comparison is available."
            ),
        )

    # External sources cannot automatically become a personal
    # TIL or ship log. We intentionally fail closed here.
    if source_type in {"news", "paper"}:
        raise ValueError(
            "No safe automatic archetype exists for this "
            "external source yet. The source needs synthesis "
            "or a manually selected format."
        )

    raise ValueError(
        "Insufficient information to select a safe archetype."
    )