import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# SMTP Configuration (Replace with real credentials)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "harshal2495@gmail.com"  # Your real email
SMTP_PASSWORD = "xlwf xdaz erkf gpmn"  # Use an App Password if using Gmail

def send_invite_email(email: str, password: str):
    """
    Sends an email invitation with login credentials.
    """
    subject = "Welcome to Task Management System"
    login_url = "http://127.0.0.1:8000/login"

    body = f"""
    <html>
    <body>
        <h2>Welcome to the Task Management System!</h2>
        <p>Hello,</p>
        <p>Your account has been created. Below are your login credentials:</p>
        <ul>
            <li><strong>Email:</strong> {email}</li>
            <li><strong>Password:</strong> {password}</li>
        </ul>
        <p><a href=http://127.0.0.1:8000/login style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Click Here to Login</a></p>
        <br>
        <p>Best Regards,<br>Admin Team</p>
    </body>
    </html>
    """

    # Create Email Message
    msg = MIMEMultipart()
    msg["From"] = SMTP_USERNAME
    msg["To"] = email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))  # Sending as HTML

    try:
        # Establish SMTP Connection
        smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        smtp.starttls()  # Secure the connection
        smtp.login(SMTP_USERNAME, SMTP_PASSWORD)  # Login to SMTP server
        smtp.sendmail(SMTP_USERNAME, email, msg.as_string())  # Send email
        smtp.quit()  # Close connection
        print(f"Email sent successfully to {email}")
    except Exception as e:
        print(f"Failed to send email: {e}")
