import json
import os


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
