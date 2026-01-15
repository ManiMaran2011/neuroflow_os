from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import openai
import tempfile

router = APIRouter(
    prefix="/voice",
    tags=["voice"]
)

openai.api_key = os.getenv("OPENAI_API_KEY")


@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    if not openai.api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key missing")

    try:
        # Save uploaded audio to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # Whisper / GPT-4o mini transcribe
        with open(tmp_path, "rb") as audio:
            transcript = openai.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",
                file=audio
            )

        os.unlink(tmp_path)

        return {
            "text": transcript.text
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
