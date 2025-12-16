from .llm import ask_llm

async def classify_intent(text: str):
    prompt = f"""
Classify the user's request into ONE of these categories:
task, schedule, research, browse, contact, notifications, energy, report

User request:
{text}

Respond with ONLY the category name.
"""
    intent = await ask_llm(prompt)
    return intent.lower().strip()
