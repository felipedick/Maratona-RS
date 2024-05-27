import logging
import os

# Create a logger
logger = logging.getLogger("whatsapp bot")
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def load_env(env_file: str = ".env") -> None:
    with open(env_file) as file:
        env_file_content = file.readlines()
        for row in env_file_content:
            key, value = row.split("=", 1)
            os.environ[key] = value.strip()


def convert_number(phone: str) -> str:
    if len(phone) == 12 and phone[4] == "9":
        phone = phone[:4] + "9" + phone[4:]
    return phone
