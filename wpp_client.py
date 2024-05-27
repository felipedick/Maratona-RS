import os

import requests

from utils import load_env

load_env()


class WhatsappAPI:

    api_key = os.environ["WPP_TOKEN"]
    number_id = os.environ["WPP_NUMBER_ID"]
    api_version = "v19.0"
    base_url = "https://graph.facebook.com/"

    @property
    def headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def send_message(self, number: str, message: str, message_type: str = "text"):
        url = f"{self.base_url}{self.api_version}/{self.number_id}/messages"
        body = {
            "messaging_product": "whatsapp",
            "to": number,
        }

        if message_type == "location":
            body.update(
                {
                    "type": "interactive",
                    "interactive": {
                        "type": "location_request_message",
                        "body": {"text": message},
                        "action": {"name": "send_location"},
                    },
                }
            )
        else:
            body.update({"text": {"body": message}})

        response = requests.post(url=url, headers=self.headers, json=body)
        response.raise_for_status()
