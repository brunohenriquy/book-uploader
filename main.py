import os
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

SENT_FILES_FILE = "sent_files.txt"
FAILED_FILES_FILE = "failed_files.txt"

def send_email_with_attachment(sender_email, sender_password, recipient_email, subject, message, attachment_path):
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
    email_content = msg.as_string()

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, email_content)

        return True
    except Exception as e:
        print(f"Error sending email for file '{attachment_path}': {str(e)}")
        return False

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
                if send_email_with_attachment(sender_email, sender_password, recipient_email, subject, message, file_path):
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
