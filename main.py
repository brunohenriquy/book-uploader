import json
import os
import smtplib
import time
from abc import ABC
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

CONFIG_FILES_DIR = "config_files"
SENT_FILES_FILE = f"{CONFIG_FILES_DIR}/sent_files.txt"
FAILED_FILES_FILE = f"{CONFIG_FILES_DIR}/failed_files.txt"
CONFIG_FILE = f"{CONFIG_FILES_DIR}/config.json"


class EmailService(ABC):
    def __init__(self, sender_email, sender_password):
        self.sender_email = sender_email
        self.sender_password = sender_password

    def send_email(self, recipient_email, email_content):
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, recipient_email, email_content)

            return True
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False

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


class GmailService(EmailService):
    def __init__(self, sender_email, sender_password):
        super().__init__(sender_email, sender_password)
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587


def read_sent_files():
    sent_files = set()

    if os.path.isfile(SENT_FILES_FILE):
        with open(SENT_FILES_FILE, "r") as file:
            for line in file:
                sent_files.add(line.strip())

    return sent_files


def read_failed_files():
    failed_files = set()

    if os.path.isfile(FAILED_FILES_FILE):
        with open(FAILED_FILES_FILE, "r") as file:
            for line in file:
                failed_files.add(line.strip())

    return failed_files


def save_sent_file(file_name):
    with open(SENT_FILES_FILE, "a") as file:
        file.write(file_name + "\n")


def save_failed_file(file_name):
    with open(FAILED_FILES_FILE, "a") as file:
        file.write(file_name + "\n")


def send_epub_emails_from_directory(directory_path, email_service, recipient_email, subject, message):
    sent_files = read_sent_files()
    failed_files = read_failed_files()
    skipped_files = 0

    file_list = sorted(os.listdir(directory_path))
    total_files = len(file_list)
    files_sent = 0

    for file_name in file_list:
        file_path = os.path.join(directory_path, file_name)

        if os.path.isfile(file_path) and file_name.lower().endswith(".epub"):
            if file_name in sent_files:
                print(f"File '{file_name}' has already been sent. Skipping...")
                skipped_files += 1
            elif file_name in failed_files:
                print(f"File '{file_name}' has previously failed to send. Skipping...")
                skipped_files += 1
            else:
                print(f"Sending book: {file_name}")
                email_content = email_service.prepare_email_with_attachment(recipient_email, subject, message,
                                                                            file_path)
                if email_service.send_email(recipient_email, email_content):
                    save_sent_file(file_name)
                    time.sleep(20)
                    files_sent += 1
                    progress = (files_sent + skipped_files) / total_files * 100
                    print(f"Progress: {progress:.2f}%")
                else:
                    save_failed_file(file_name)

    print(f"Emails sent: {files_sent}")
    print(f"Files skipped: {skipped_files}")
    print(f"Files failed: {len(failed_files)}")


def read_config():
    with open(CONFIG_FILE, "r") as config_file:
        config = json.load(config_file)
    return config


if __name__ == '__main__':
    config = read_config()

    sender_email = config["sender_email"]
    sender_password = config["sender_password"]
    recipient_email = config["recipient_email"]
    subject = config["subject"]
    message = config["message"]
    directory_path = config["directory_path"]

    email_service = GmailService(sender_email, sender_password)

    send_epub_emails_from_directory(directory_path, email_service, recipient_email, subject, message)
