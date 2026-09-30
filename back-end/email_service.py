import os
import resend

from config import email_from

resend.api_key = os.environ.get("RESEND_API_KEY")


def send_email(to_email, subject, html_body):
    if not resend.api_key:
        return {"success": False, "error": "RESEND_API_KEY is not set."}

    if not to_email:
        return {"success": False, "error": "No recipient email provided."}

    params = {
        "from": email_from,
        "to": [to_email],
        "subject": subject,
        "html": html_body
    }

    try:
        result = resend.Emails.send(params)
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}