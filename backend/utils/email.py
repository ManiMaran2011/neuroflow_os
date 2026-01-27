import os
import resend


def send_email(
    to_email: str,
    subject: str,
    body: str,
):
    api_key = os.getenv("RESEND_API_KEY")
    if not api_key:
        raise RuntimeError("RESEND_API_KEY not set in runtime environment")

    resend.api_key = api_key

    response = resend.Emails.send({
        "from": os.getenv(
            "EMAIL_FROM",
            "NeuroFlow Alerts <alerts@resend.dev>"
        ),
        "to": [to_email],
        "subject": subject,
        "html": f"<p>{body}</p>",
    })

    print("📧 Email sent via Resend:", response)
    return response


