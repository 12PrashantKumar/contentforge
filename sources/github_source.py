"""

Reads YOUR recent commits. This is raw material, NOT finished findings.

Commits tell you WHAT you touched ("fix ingest bug") but never WHY it
mattered - and "why it mattered" is what makes a good post. So this
source deliberately produces a lightweight WorkItem, and the interview
flow (interview.py) turns it into a real Finding by asking you about it.

Needs a GitHub personal access token (read-only) in .env as GITHUB_TOKEN.
Create one at: GitHub -> Settings -> Developer settings -> Personal access
tokens -> Fine-grained -> read-only, "Contents" + "Metadata" on your repos.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from github import Github

from core.config import GITHUB_TOKEN


@dataclass
class WorkItem:
    """
    One repo's worth of recent activity. Raw input for the interview flow.
    Not a Finding - it has no story yet, only facts about what changed.
    """
    repo: str
    commit_messages: list[str] = field(default_factory=list)
    files_touched: list[str] = field(default_factory=list)
    commit_count: int = 0
    since: datetime = None

    def summary(self) -> str:
        files = ", ".join(sorted(set(self.files_touched))[:8])
        msgs = "\n  - ".join(self.commit_messages[:10])
        return (
            f"repo: {self.repo}\n"
            f"commits: {self.commit_count}\n"
            f"files: {files}\n"
            f"messages:\n  - {msgs}"
        )


def fetch_my_work(days: int = 7, username: str = None) -> list[WorkItem]:
    """
    Recent commits across your repos, grouped by repo.

    Returns [] if nothing was pushed in the window - which is a valid
    state, not an error. No work, no post.
    """
    gh = Github(GITHUB_TOKEN)
    user = gh.get_user(username) if username else gh.get_user()

    since = datetime.now(timezone.utc) - timedelta(days=days)
    items: list[WorkItem] = []

    for repo in user.get_repos():
        if repo.fork:
            continue

        try:
            commits = list(repo.get_commits(since=since))
        except Exception:
            # empty repo or no access to commits - skip quietly
            continue

        if not commits:
            continue

        messages, files = [], []
        for c in commits:
            msg = (c.commit.message or "").splitlines()[0].strip()
            if msg:
                messages.append(msg)
            try:
                files.extend(f.filename for f in c.files)
            except Exception:
                pass

        items.append(WorkItem(
            repo=repo.name,
            commit_messages=messages,
            files_touched=files,
            commit_count=len(commits),
            since=since,
        ))

    return items