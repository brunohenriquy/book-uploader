import json
import os
import smtplib
import time
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from colorama import Fore, Style


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


class ConfigManager:
    CONFIG_FILES_DIR = "config_files"
    CONFIG_FILE = f"{CONFIG_FILES_DIR}/config.json"
    SENT_BOOKS_FILE = f"{CONFIG_FILES_DIR}/sent_books.txt"
    FAILED_BOOKS_FILE = f"{CONFIG_FILES_DIR}/failed_books.txt"

    @staticmethod
    def read_config():
        config_file_path = ConfigManager.CONFIG_FILE
        if not os.path.isfile(config_file_path):
            return ConfigManager.get_config_from_env()

        with open(config_file_path, "r") as config_file:
            config = json.load(config_file)

        return config

    @staticmethod
    def get_config_from_env():
        config = {
            "SMTP_SERVER": os.environ.get("SMTP_SERVER"),
            "SMTP_PORT": int(os.environ.get("SMTP_PORT")),
            "SENDER_EMAIL": os.environ.get("SENDER_EMAIL"),
            "SENDER_PASSWORD": os.environ.get("SENDER_PASSWORD"),
            "RECIPIENT_EMAIL": os.environ.get("RECIPIENT_EMAIL"),
            "SUBJECT": os.environ.get("SUBJECT", ""),
            "MESSAGE": os.environ.get("MESSAGE", ""),
            "DIRECTORY_PATH": "books",
            "ALLOWED_EXTENSIONS": os.getenv('ALLOWED_EXTENSIONS').split(',')
        }
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
    def read_sent_books():
        return ConfigManager.read_file(ConfigManager.SENT_BOOKS_FILE)

    @staticmethod
    def read_failed_books():
        return ConfigManager.read_file(ConfigManager.FAILED_BOOKS_FILE)

    @staticmethod
    def save_sent_book(book_name):
        ConfigManager.save_file(ConfigManager.SENT_BOOKS_FILE, book_name)

    @staticmethod
    def save_failed_book(book_name):
        ConfigManager.save_file(ConfigManager.FAILED_BOOKS_FILE, book_name)


def print_statistics(failed_files_count, sent_files_count, skipped_files_count):
    print(f"{Fore.GREEN}Emails sent: {sent_files_count}")
    print(f"Files skipped: {skipped_files_count}")
    print(f"Files failed: {failed_files_count}{Style.RESET_ALL}")


def send_book_emails_from_directory():
    sleep_seconds = 20
    config = ConfigManager.read_config()

    smtp_server = config["SMTP_SERVER"]
    smtp_port = config["SMTP_PORT"]
    sender_email = config["SENDER_EMAIL"]
    sender_password = config["SENDER_PASSWORD"]
    recipient_email = config["RECIPIENT_EMAIL"]
    subject = config["SUBJECT"]
    message = config["MESSAGE"]
    directory_path = config["DIRECTORY_PATH"]
    allowed_extensions = config["ALLOWED_EXTENSIONS"]

    sent_books = ConfigManager.read_sent_books()
    failed_books = ConfigManager.read_failed_books()

    book_list = sorted(os.listdir(directory_path))
    book_count = len(book_list)

    sent_book_count = 0
    skipped_book_count = 0
    failed_book_count = 0

    email_service = EmailService(smtp_server, smtp_port, sender_email, sender_password)

    for book in book_list:
        file_path = os.path.join(directory_path, book)

        if os.path.isfile(file_path) and any(book.lower().endswith(f".{ext}") for ext in allowed_extensions):
            if book in sent_books:
                print(f"{Fore.YELLOW}Book '{book}' has already been sent. Skipping...{Style.RESET_ALL}")
                skipped_book_count += 1
            elif book in failed_books:
                print(f"{Fore.YELLOW}Book '{book}' has previously failed to send. Skipping...{Style.RESET_ALL}")
                skipped_book_count += 1
            else:
                print(f"{Fore.GREEN}Sending book: {book}{Style.RESET_ALL}")
                email_content = email_service.prepare_email_with_attachment(recipient_email, subject, message,
                                                                            file_path)

                try:
                    email_service.send_email(recipient_email, email_content)
                    ConfigManager.save_sent_book(book)
                    sent_book_count += 1
                    processed_files_count = sent_book_count + skipped_book_count + failed_book_count
                    progress = processed_files_count / book_count * 100
                    print(f"Progress: {progress:.2f}%")
                except Exception as e:
                    ConfigManager.save_failed_book(book)
                    failed_book_count += 1
                    print(f"{Fore.RED}Failed to send email for book '{book}': {str(e)}{Style.RESET_ALL}")

                print(f"{Fore.BLUE}Sleeping for {sleep_seconds} seconds before trying to send another book!{Style.RESET_ALL}")
                time.sleep(sleep_seconds)

    print_statistics(failed_book_count, sent_book_count, skipped_book_count)


if __name__ == '__main__':
    send_book_emails_from_directory()
