import os
import smtplib
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from agents import function_tool
from email.message import EmailMessage
from sheet_utils import get_sheet, append_row


class EmailInput(BaseModel):
    to: str
    subject: str
    body: str
    patient_id: Optional[str] = None
    appointment_id: Optional[str] = None

@function_tool
async def send_email_tool(input: EmailInput) -> dict:
    """Send email confirmation for appointments.
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email content
        patient_id: Optional patient ID for tracking
        appointment_id: Optional appointment ID for tracking
        
    Returns:
        dict: {
            "status": "success" | "error",
            "message": str
        }
    """
    try:
        msg = EmailMessage()
        msg.set_content(input.body)
        msg["Subject"] = input.subject
        msg["From"] = os.getenv("SMTP_FROM", "noreply@nazcare.com")
        msg["To"] = input.to
        
        with smtplib.SMTP(os.getenv("SMTP_HOST", "smtp.gmail.com"), 
                         int(os.getenv("SMTP_PORT", "587"))) as server:
            server.starttls()
            server.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASS"))
            server.send_message(msg)
        
        # Log the email in the sheet if we have patient info
        if input.patient_id:
            try:
                sheet = get_sheet()
                email_data = {
                    "Pat Num": input.patient_id,
                    "Timestamp": datetime.now().isoformat(),
                    "Chat Summary": f"Email sent: {input.subject}",
                    "App Num": input.appointment_id or ""
                }
                append_row(sheet, email_data)
            except Exception:
                pass  # Don't fail if logging fails
        
        return {
            "status": "success",
            "message": "Email sent successfully"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error sending email: {str(e)}"
        }