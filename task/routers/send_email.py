import smtplib
from email.message import EmailMessage

SMTP_SERVER = "smtp.gmail.com"  # Replace with your SMTP server
SMTP_PORT = 587  # Common SMTP port
EMAIL_SENDER = "harshal2495@gmail.com"
EMAIL_PASSWORD = "xlwf xdaz erkf gpmn"  # Use an app password instead of a real password

def send_email(to_email: str, subject: str, body: str):
    msg = EmailMessage()
    msg["From"] = EMAIL_SENDER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Secure the connection
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Email failed to send: {e}")

