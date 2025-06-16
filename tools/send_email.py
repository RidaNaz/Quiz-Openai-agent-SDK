import smtplib
from email.message import EmailMessage

class EmailInput(BaseModel):
    to: str
    subject: str
    body: str

@function_tool
def send_email_tool(input: EmailInput) -> str:
    """Send email via SMTP"""
    
    msg = EmailMessage()
    msg.set_content(input.body)
    msg["Subject"] = input.subject
    msg["From"] = "clinic@example.com"
    msg["To"] = input.to
    
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASS"))
        server.send_message(msg)
    
    return "Email sent successfully"