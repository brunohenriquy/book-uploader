import os
import smtplib
import time
from abc import ABC, abstractmethod
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

CONTROL_FILES_DIR = "control_files"
SENT_FILES_FILE = f"{CONTROL_FILES_DIR}/sent_files.txt"
FAILED_FILES_FILE = f"{CONTROL_FILES_DIR}/failed_files.txt"


class EmailSender(ABC):
    def __init__(self, sender_email, sender_password):
        self.sender_email = sender_email
        self.sender_password = sender_password

    @abstractmethod
    def send_email(self, recipient_email, email_content):
        pass


class GmailSender(EmailSender):
    def __init__(self, sender_email, sender_password):
        super().__init__(sender_email, sender_password)
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587

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


def prepare_email_with_attachment(sender_email, recipient_email, subject, message, attachment_path):
    msg = MIMEMultipart()
    msg["From"] = sender_email
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

    return msg.as_string()


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


def send_epub_emails_from_directory(directory_path, sender_email, sender_password, recipient_email, subject, message):
    sent_files = read_sent_files()
    failed_files = read_failed_files()
    skipped_files = 0

    file_list = sorted(os.listdir(directory_path))
    total_files = len(file_list)
    files_sent = 0

    email_sender = GmailSender(sender_email, sender_password)

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
                email_content = prepare_email_with_attachment(sender_email, recipient_email, subject, message,
                                                              file_path)
                if email_sender.send_email(recipient_email, email_content):
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


if __name__ == '__main__':
    sender_email = "your_email@gmail.com"
    sender_password = "your_password"
    recipient_email = "recipient_email@gmail.com"
    subject = "Email with EPUB Attachment"
    message = "Hello, please find the EPUB attachment."
    directory_path = "/path/to/directory"

    send_epub_emails_from_directory(directory_path, sender_email, sender_password, recipient_email, subject, message)
