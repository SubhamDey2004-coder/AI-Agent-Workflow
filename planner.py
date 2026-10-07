import ollama
import json


PLANNER_SYSTEM_PROMPT = """
You are a planning component for an AI agent.

Your job is to break the user's goal into a small number of
clear, ordered steps.

Rules:

1. Return ONLY valid JSON.
2. Return a JSON object with a single key: "steps".
3. "steps" must be a list of strings.
4. Steps must be ordered logically.
5. Include all actions required to complete the user's goal.
6. Do not execute any tools.
7. Do not answer the user's question.
8. Do not add unnecessary steps.
9. If the task requires verification, include a verification step.
10. Preserve all filenames explicitly provided by the user exactly.
11. Do not invent or rename filenames when the user has specified one.
12. If a later step depends on information from an earlier step,
    place the earlier step first.

Example:

User goal:
Read ml_notes.txt and create ml_summary.txt, then verify it.

Output:
{
    "steps": [
        "Read ml_notes.txt",
        "Create ml_summary.txt using the contents of ml_notes.txt",
        "Verify that ml_summary.txt was created successfully"
    ]
}
"""


def create_plan(goal):

    response = ollama.chat(
        model="qwen3:4b",
        messages=[
            {
                "role": "system",
                "content": PLANNER_SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": goal
            }
        ]
    )

    content = response.message.content.strip()

    try:

        plan = json.loads(content)

        if not isinstance(plan, dict):
            raise ValueError("Planner output is not a JSON object.")

        if "steps" not in plan:
            raise ValueError("Planner output does not contain 'steps'.")

        if not isinstance(plan["steps"], list):
            raise ValueError("'steps' must be a list.")

        return plan["steps"]

    except Exception as e:

        print("Planner error:", e)
        print("Raw planner output:", content)

        return []