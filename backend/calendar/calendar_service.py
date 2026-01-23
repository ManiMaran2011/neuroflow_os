from datetime import datetime, timedelta
from backend.utils.llm import ask_llm

EVENT_EXTRACTION_PROMPT = """
You are a scheduling assistant.

From the user input, extract a calendar event.

Rules:
- Use ISO 8601 format
- Assume user's timezone is Asia/Kolkata
- If duration is missing, assume 30 minutes
- If date is "tomorrow", calculate correctly

Return ONLY valid JSON in this format:

{
  "title": "...",
  "description": "...",
  "start_time": "YYYY-MM-DDTHH:MM:SS",
  "end_time": "YYYY-MM-DDTHH:MM:SS"
}

User input:
"{user_input}"
"""

def extract_calendar_event(user_input: str):
    response = call_llm(
        prompt=EVENT_EXTRACTION_PROMPT.format(user_input=user_input)
    )

    return response  
