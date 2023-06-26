import os
import time

from colorama import Fore, Style

from config_manager import ConfigManager
from email_service import EmailService


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
                email_content = email_service.prepare_email_with_attachment(
                    recipient_email,
                    subject,
                    message,
                    file_path
                )

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

                print(
                    f"{Fore.BLUE}Sleeping for {sleep_seconds} seconds before trying to send another book!{Style.RESET_ALL}")
                time.sleep(sleep_seconds)

    print_statistics(failed_book_count, sent_book_count, skipped_book_count)


if __name__ == '__main__':
    send_book_emails_from_directory()
