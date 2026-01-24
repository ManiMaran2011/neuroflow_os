import os
import resend


resend.api_key = os.getenv("RESEND_API_KEY")


def send_email(
    to_email: str,
    subject: str,
    body: str,
):
    if not resend.api_key:
        raise Exception("RESEND_API_KEY not set")

    response = resend.Emails.send({
        "from": os.getenv(
            "EMAIL_FROM",
            "NeuroFlow Alerts <alerts@resend.dev>"
        ),
        "to": [to_email],
        "subject": subject,
        "html": f"<p>{body}</p>",
    })

    return response


