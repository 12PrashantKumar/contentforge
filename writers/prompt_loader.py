from pathlib import Path
import re


WRITERS_DIR = Path(__file__).parent


def load_voice() -> str:
    """
    Load the provisional user voice profile.
    """

    path = WRITERS_DIR / "voice.md"

    return path.read_text(
        encoding="utf-8"
    )


def load_rules() -> str:
    """
    Load hard generation rules.

    rules.md is always loaded last.
    """

    path = WRITERS_DIR / "rules.md"

    return path.read_text(
        encoding="utf-8"
    )


def load_format(
    archetype: str,
) -> str:
    """
    Load ONLY the requested archetype from formats.md.

    The entire formats.md file must never be sent to the LLM.
    """

    path = WRITERS_DIR / "formats.md"

    text = path.read_text(
        encoding="utf-8"
    )

    pattern = re.compile(
        rf"^##\s+\d+\.\s+{re.escape(archetype)}\s*$"
        rf"(.*?)(?=^##\s+\d+\.|^##\s+Weekly composition|\Z)",
        re.MULTILINE | re.DOTALL,
    )

    match = pattern.search(text)

    if not match:
        raise ValueError(
            f"Archetype '{archetype}' "
            "was not found in formats.md."
        )

    heading = match.group(0)

    return heading.strip()


def build_system_prompt(
    archetype: str,
) -> str:
    """
    Assemble the generation prompt.

    Order matters:

    1. voice
    2. selected format
    3. hard rules

    rules.md is intentionally last.
    """

    voice = load_voice()

    selected_format = load_format(
        archetype
    )

    rules = load_rules()

    return f"""
# VOICE

{voice}

==================================================
# SELECTED FORMAT
==================================================

{selected_format}

==================================================
# HARD RULES
==================================================

{rules}
"""