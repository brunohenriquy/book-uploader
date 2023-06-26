import json
import os
import smtplib
import time
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from colorama import init, Fore

init(autoreset=True)  # Initialize colorama

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
            return True
        except Exception as e:
            print(f"{Fore.RED}Error sending email: {str(e)}")
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


class ConfigManager:
    CONFIG_FILES_DIR = "config_files"
    CONFIG_FILE = f"{CONFIG_FILES_DIR}/config.json"
    SENT_FILES_FILE = f"{CONFIG_FILES_DIR}/sent_files.txt"
    FAILED_FILES_FILE = f"{CONFIG_FILES_DIR}/failed_files.txt"

    @staticmethod
    def read_config():
        config_file_path = ConfigManager.CONFIG_FILE
        if not os.path.isfile(config_file_path):
            raise FileNotFoundError(f"Config file '{config_file_path}' not found.")

        with open(config_file_path, "r") as config_file:
            config = json.load(config_file)

        return config

    @staticmethod
    def read_file(file_path):
        file_set = set()

        if os.path.isfile(file_path):
            with open(file_path, "r") as file:
                for line in file:
                    file_set.add(line.strip())

        return file_set

    @staticmethod
    def save_file(file_path, file_name):
        with open(file_path, "a") as file:
            file.write(file_name + "\n")

    @staticmethod
    def read_sent_files():
        return ConfigManager.read_file(ConfigManager.SENT_FILES_FILE)

    @staticmethod
    def read_failed_files():
        return ConfigManager.read_file(ConfigManager.FAILED_FILES_FILE)

    @staticmethod
    def save_sent_file(file_name):
        ConfigManager.save_file(ConfigManager.SENT_FILES_FILE, file_name)

    @staticmethod
    def save_failed_file(file_name):
        ConfigManager.save_file(ConfigManager.FAILED_FILES_FILE, file_name)


def print_statistics(failed_files_count, sent_files_count, skipped_files_count):
    print(f"{Fore.GREEN}Emails sent: {sent_files_count}")
    print(f"{Fore.YELLOW}Files skipped: {skipped_files_count}")
    print(f"{Fore.RED}Files failed: {failed_files_count}")


def send_epub_emails_from_directory():
    import pydevd_pycharm;
    pydevd_pycharm.settrace('host.docker.internal', port=8787, stdoutToServer=True, stderrToServer=True)
    config = ConfigManager.read_config()

    smtp_server = config["smtp_server"]
    smtp_port = config["smtp_port"]
    sender_email = config["sender_email"]
    sender_password = config["sender_password"]
    recipient_email = config["recipient_email"]
    subject = config["subject"]
    message = config["message"]
    directory_path = config["directory_path"]

    sent_files = ConfigManager.read_sent_files()
    failed_files = ConfigManager.read_failed_files()

    file_list = sorted(os.listdir(directory_path))
    total_files = len(file_list)

    sent_files_count = 0
    skipped_files_count = 0
    failed_files_count = 0

    email_service = EmailService(smtp_server, smtp_port, sender_email, sender_password)

    for file_name in file_list:
        file_path = os.path.join(directory_path, file_name)

        if os.path.isfile(file_path) and file_name.lower().endswith(".epub"):
            if file_name in sent_files:
                print(f"{Fore.YELLOW}File '{file_name}' has already been sent. Skipping...")
                skipped_files_count += 1
            elif file_name in failed_files:
                print(f"{Fore.YELLOW}File '{file_name}' has previously failed to send. Skipping...")
                skipped_files_count += 1
            else:
                print(f"{Fore.GREEN}Sending book: {file_name}")
                email_content = email_service.prepare_email_with_attachment(recipient_email, subject, message, file_path)

                if email_service.send_email(recipient_email, email_content):
                    ConfigManager.save_sent_file(file_name)
                    sent_files_count += 1
                    processed_files_count = sent_files_count + skipped_files_count + failed_files_count
                    progress = processed_files_count / total_files * 100
                    print(f"{Fore.GREEN}Progress: {progress:.2f}%")
                else:
                    ConfigManager.save_failed_file(file_name)
                    failed_files_count += 1

                time.sleep(20)

    print_statistics(failed_files_count, sent_files_count, skipped_files_count)


if __name__ == '__main__':
    send_epub_emails_from_directory()
