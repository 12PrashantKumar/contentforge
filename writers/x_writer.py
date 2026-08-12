import json
from pathlib import Path

from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)

from core.llm import invoke_llm
from core.models import (
    Draft,
    DraftVariant,
    Finding,
)
from services.validators import (
    validate_generation,
)
from writers.prompt_loader import (
    build_system_prompt,
)


EXAMPLES_DIR = (
    Path(__file__).parent / "examples"
)


def load_examples() -> list[str]:
    """
    Load only real examples supplied by the user.
    """

    examples = []

    for path in sorted(
        EXAMPLES_DIR.glob("*.txt")
    ):

        text = path.read_text(
            encoding="utf-8"
        ).strip()

        if text:
            examples.append(text)

    return examples


def build_examples_text(
    examples: list[str],
) -> str:

    if not examples:
        return (
            "No real X examples are currently available."
        )

    return "\n\n".join(
        (
            f"REAL USER POST {index}:\n"
            f"{example}"
        )
        for index, example in enumerate(
            examples,
            start=1,
        )
    )


def extract_json(
    content: str,
) -> dict:
    """
    Parse JSON returned by the LLM.

    The prompt asks for raw JSON only.
    This function also handles accidental ```json fences
    defensively.
    """

    content = content.strip()

    if content.startswith(
        "```json"
    ):
        content = content[
            len("```json"):
        ]

    elif content.startswith(
        "```"
    ):
        content = content[
            len("```"):
        ]

    if content.endswith(
        "```"
    ):
        content = content[:-3]

    content = content.strip()

    try:
        return json.loads(content)

    except json.JSONDecodeError as error:

        raise ValueError(
            "LLM did not return valid JSON."
        ) from error


def build_generation_prompt(
    finding: Finding,
    archetype: str,
) -> tuple[
    SystemMessage,
    HumanMessage,
]:

    system_prompt = (
        build_system_prompt(
            archetype
        )
    )

    examples = load_examples()

    examples_text = (
        build_examples_text(
            examples
        )
    )

    user_prompt = f"""
# REAL USER WRITING EXAMPLES

{examples_text}


# SOURCE

TITLE:
{finding.title}

SOURCE TYPE:
{finding.source_type}

SOURCE URL:
{finding.source_url}

SOURCE CONTENT:
{finding.content}


# GENERATION TASK

Generate content using the selected archetype:

{archetype}

The source content is the factual boundary.

Do not invent personal experience.

Do not turn external information into first-person
experience.

If the selected archetype requires information that
the source does not contain, return:

{{
  "status": "insufficient_input",
  "missing": "describe the missing evidence"
}}

Otherwise return exactly three variants.

The three variants MUST have genuinely different
angles.

They must not be three rewrites of the same idea.

Return ONLY valid JSON.
"""

    return (
        SystemMessage(
            content=system_prompt
        ),
        HumanMessage(
            content=user_prompt
        ),
    )


def write(
    finding: Finding,
    archetype: str,
    max_attempts: int = 2,
) -> Draft:

    messages = list(
        build_generation_prompt(
            finding,
            archetype,
        )
    )

    for attempt in range(
        max_attempts
    ):

        response = invoke_llm(
            messages
        )

        result = extract_json(
            response.content
        )

        # If the model honestly says the source
        # is insufficient, return that instead of
        # fabricating a post.
        if (
            result.get("status")
            == "insufficient_input"
        ):

            return Draft(
                status="insufficient_input",
                archetype=archetype,
                variants=[],
                source_url=finding.source_url,
                notes=result.get(
                    "missing"
                ),
            )

        try:

            validate_generation(
                result,
                finding.source_url,
            )

            variants = [
                DraftVariant(
                    id=variant["id"],
                    post=variant["post"],
                    thread=variant["thread"],
                    first_reply=variant[
                        "first_reply"
                    ],
                    media_suggestion=variant[
                        "media_suggestion"
                    ],
                    alt_text=variant[
                        "alt_text"
                    ],
                    char_count=len(
                        variant["post"]
                    ),
                    reply_surface=variant[
                        "reply_surface"
                    ],
                )
                for variant in result[
                    "variants"
                ]
            ]

            return Draft(
                status="ok",
                archetype=result[
                    "archetype"
                ],
                variants=variants,
                source_url=finding.source_url,
                rejected_angle=result.get(
                    "rejected_angle"
                ),
                notes=result.get(
                    "notes"
                ),
            )

        except ValueError as error:

            if (
                attempt
                == max_attempts - 1
            ):
                raise

            # Ask for correction rather than
            # silently accepting invalid output.
            messages.append(
                HumanMessage(
                    content=f"""
The previous JSON failed application validation.

Validation error:
{error}

Regenerate the complete JSON.

Do not merely rephrase the same failed variant.

Return exactly three valid variants with
different angles.

Return JSON only.
"""
                )
            )

    raise RuntimeError(
        "Failed to generate valid X content."
    )