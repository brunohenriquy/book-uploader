# Book Uploader

The Book Uploader is a Python script that allows you to send Book files via email. This script provides two options for running the code: using a local Python installation or using Docker.

It automates the process of sending Book files to a specified recipient via email for example to `Kindle` service. It reads the configuration from either a `config.json` file or environment variables, depending on the chosen method of execution. The script supports sending multiple Book files in a directory, skipping files that have already been sent, and keeping track of failed attempts.

## Prerequisites

- Python 3.9 or higher (only required if running the script locally)
- Docker (only required if running the script using Docker)

## Running with a Local Python Installation

To run the Book Uploader using a local Python installation, follow these steps:

1. Clone the repository:

   ```shell
   git clone https://github.com/bruno.henriquy/book-uploader.git

2. Navigate to the project directory:

   ```shell
    cd book-uploader

3. Install the required dependencies:

    ```shell
    pip install -r requirements.txt

4. Set up the configuration.

    - Create a file named config.json inside the config_files directory, there is an example there.
    - Open config.json and update the following fields with your email server and account details:
      - "SMTP_SERVER": SMTP server address.
      - "SMTP_PORT": SMTP server port.
      - "SENDER_EMAIL": Email address of the sender.
      - "SENDER_PASSWORD": Password for the sender's email account.
      - "RECIPIENT_EMAIL": Email address of the recipient.
      - "SUBJECT": Subject of the email (optional).
      - "MESSAGE": Body of the email (optional).
      - "DIRECTORY_PATH": Path to the directory containing the Book files.
      - "ALLOWED_EXTENSIONS": Array with the allowed book extensions.

5. Run the script:

    ```shell
    python main.py
    ```
   
    The script will start sending Book files via email based on the configuration provided.

## Running with Docker

To run the Book Uploader using Docker, follow these steps:

1. Clone the repository:

   ```shell
   git clone https://github.com/bruno.henriquy/book-uploader.git

2. Navigate to the project directory:

   ```shell
    cd book-uploader
   
3. Open the docker-compose.yaml file and update the environment variables under the app service with your email server and account details:

    ```yaml
    environment:
   - SMTP_SERVER=smtp.gmail.com
   - SMTP_PORT=587
   - SENDER_EMAIL=your-email@gmail.com
   - SENDER_PASSWORD=your-email-password
   - RECIPIENT_EMAIL=recipient-email@example.com
   - SUBJECT=Subject (optional)
   - MESSAGE=Message (optional)
   - ALLOWED_EXTENSIONS=[".epub", ".pdf", ".mobi"]
   
4. If your Book files are located in a specific directory on your host machine, update the volumes section under the app service in the docker-compose.yaml file. Replace /path/to/book/files with the absolute path to your Book files directory on your host machine:

    ```yaml
    volumes:
   - /path/to/book/files:/app/books


5. Build and run the Docker containers:

   ```shell
    docker-compose up