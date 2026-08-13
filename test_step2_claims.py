from agents.verifier import extract_claims


TEXT = """
Anthropic's new model scores 82% on SWE-bench
and runs 3x faster than the previous version.

Honestly, this is a big deal for agent work.

I spent two days rewiring my pipeline around it.

I think this will completely change how
developers build agents.
"""


print(
    "Extracted claims:"
)

claims = extract_claims(
    TEXT
)

for index, claim in enumerate(
    claims,
    start=1,
):

    print(
        f"{index}. {claim}"
    )


print(
    "\nTotal claims:",
    len(claims)
)