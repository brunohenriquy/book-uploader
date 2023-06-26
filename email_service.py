import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class EmailService:
    def __init__(self, smtp_server, smtp_port, sender_email, sender_password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password

    def send_email(self, recipient_email, email_content):
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, recipient_email, email_content)

        except Exception as e:
            raise e

    def prepare_email_with_attachment(self, recipient_email, subject, message, attachment_path):
        msg = MIMEMultipart()
        msg["From"] = self.sender_email
        msg["To"] = recipient_email
        msg["Subject"] = subject

        msg.attach(MIMEText(message, "plain"))

        with open(attachment_path, "rb") as attachment:
            attachment_data = MIMEBase("application", "octet-stream")
            attachment_data.set_payload(attachment.read())

        encoders.encode_base64(attachment_data)

        attachment_data.add_header(
            "Content-Disposition",
            f"attachment; filename={os.path.basename(attachment_path)}",
        )

        msg.attach(attachment_data)

        email_content = msg.as_string()

        return email_content
