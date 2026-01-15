# frontend/voice.py

import speech_recognition as sr


def listen_from_mic(timeout=5, phrase_time_limit=10):
    """
    Listen from local microphone and return recognized text.
    Returns empty string if nothing is understood.
    """

    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_time_limit
            )

        text = recognizer.recognize_google(audio)
        return text

    except sr.WaitTimeoutError:
        return ""

    except sr.UnknownValueError:
        return ""

    except sr.RequestError as e:
        raise RuntimeError(f"Speech recognition error: {e}")

