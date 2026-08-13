"""

The interview flow. The agent shows you what you built this week and asks
what actually happened. Your answer - not the commits alone - becomes the
post.

The questions are designed to set exactly the flags that strategy.py routes
on:

    completed a milestone   -> is_first_party + has_real_completion -> BUILD_ANNOUNCE
    ongoing progress        -> is_first_party                       -> SHIP_LOG
    something broke         -> has_real_failure (first_party False) -> FAILURE_LESSON
    measured something      -> has_real_measurement                 -> BENCHMARK_COMPARISON

Note the quirk in strategy.py: is_first_party is checked FIRST, so to reach
FAILURE_LESSON we must set has_real_failure=True and is_first_party=False.
This module handles that mapping so you don't have to think about it.
"""

from dataclasses import dataclass
from datetime import datetime, timezone

from core.models import Finding
from sources.github_source import WorkItem, fetch_my_work


@dataclass
class InterviewResult:
    """A first-party Finding plus the strategy flags its story implies."""
    finding: Finding
    is_first_party: bool
    has_real_completion: bool
    has_real_failure: bool
    has_real_measurement: bool


# maps the menu choice -> (flags), matching strategy.py's routing
_CHOICES = {
    "1": {  # shipped / completed  -> BUILD_ANNOUNCE
        "label": "I shipped / completed something",
        "is_first_party": True, "has_real_completion": True,
        "has_real_failure": False, "has_real_measurement": False,
        "followup": "What did you complete, and what's one non-obvious detail a builder would notice?",
    },
    "2": {  # ongoing progress  -> SHIP_LOG
        "label": "Made progress, still building",
        "is_first_party": True, "has_real_completion": False,
        "has_real_failure": False, "has_real_measurement": False,
        "followup": "What did you move forward, and what's the mechanism (A -> B -> C)?",
    },
    "3": {  # something broke  -> FAILURE_LESSON  (note: first_party False)
        "label": "Something broke / I got something wrong",
        "is_first_party": False, "has_real_completion": False,
        "has_real_failure": True, "has_real_measurement": False,
        "followup": "What broke, what was the actual cause, and what did you change?",
    },
    "4": {  # measured something  -> BENCHMARK_COMPARISON
        "label": "I measured something (real numbers)",
        "is_first_party": False, "has_real_completion": False,
        "has_real_failure": False, "has_real_measurement": True,
        "followup": "What did you measure - setup, metric, and the numbers you got?",
    },
}


def _pick_workitem(items: list[WorkItem]) -> WorkItem | None:
    if not items:
        return None
    if len(items) == 1:
        return items[0]

    print("\nWhich work do you want to post about?")
    for i, item in enumerate(items, 1):
        print(f"  {i}. {item.repo} ({item.commit_count} commits)")
    choice = input("> ").strip()
    try:
        return items[int(choice) - 1]
    except (ValueError, IndexError):
        return items[0]


def run_interview(days: int = 7) -> InterviewResult | None:
    """
    Interactive. Returns an InterviewResult, or None if there is nothing
    to post about (no work, or you opt out). None is a valid outcome.
    """
    items = fetch_my_work(days=days)
    item = _pick_workitem(items)

    if item is None:
        print(f"\nNo pushed work in the last {days} days. Nothing to post.")
        return None

    print("\n" + "=" * 70)
    print("YOUR WORK THIS WEEK")
    print("=" * 70)
    print(item.summary())

    print("\n" + "=" * 70)
    print("What happened with this work?")
    print("=" * 70)
    for key, c in _CHOICES.items():
        print(f"  {key}. {c['label']}")
    print("  q. nothing worth posting - skip")

    choice = input("\n> ").strip().lower()
    if choice == "q" or choice not in _CHOICES:
        print("Skipped. Nothing to post.")
        return None

    selected = _CHOICES[choice]

    print(f"\n{selected['followup']}")
    story = input("> ").strip()

    if not story:
        print("No story given. Nothing to post.")
        return None

    # build the first-party finding: commits give the WHAT, your answer gives the WHY
    content = (
        f"WORK CONTEXT (from commits):\n{item.summary()}\n\n"
        f"WHAT ACTUALLY HAPPENED (author's own account):\n{story}"
    )

    finding = Finding(
        title=f"{item.repo}: {selected['label']}",
        content=content,
        source_url=f"https://github.com/12PrashantKumar/{item.repo}",  # <-- edit username
        source_type="own_work",
        fetched_at=datetime.now(timezone.utc),
        source_id=item.repo,
    )

    return InterviewResult(
        finding=finding,
        is_first_party=selected["is_first_party"],
        has_real_completion=selected["has_real_completion"],
        has_real_failure=selected["has_real_failure"],
        has_real_measurement=selected["has_real_measurement"],
    )