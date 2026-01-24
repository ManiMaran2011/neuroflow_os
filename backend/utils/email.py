import os
from resend import Resend

client = Resend(api_key=os.getenv("RESEND_API_KEY"))

def send_email(to_email: str, subject: str, body: str):
    response = client.emails.send({
        "from": os.getenv("EMAIL_FROM"),
        "to": [to_email],
        "subject": subject,
        "html": f"""
        <div style="font-family: Arial, sans-serif;">
            <h2>{subject}</h2>
            <p>{body}</p>
        </div>
        """
    })

    return response

