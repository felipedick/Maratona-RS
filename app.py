import os
from typing import Any, Dict

import uvicorn
from fastapi import FastAPI, HTTPException, Request

from db_handler import update_user_data
from utils import convert_number
from wpp_conversation import WhatsAppConversation, WhatsAppMessage

app = FastAPI()


@app.get("/webhook")
async def webhook_auth(request: Request):
    params = dict(request.query_params)
    if not params.get("hub.verify_token") == os.environ["WEBHOOK_SECRET"]:
        raise HTTPException("Token does not match")
    if chlg := params.get("hub.challenge"):
        return int(chlg)


@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    changes = data.get("entry", [{}])[0].get("changes", [{}])

    for change in changes:
        if change.get("field") == "messages":
            messages = change.get("value", {}).get("messages", [])
            text_messages = [m for m in messages if m.get("type") == "text"]
            locations = [m for m in messages if m.get("type") == "location"]
            for message in text_messages:
                sender = convert_number(message.get("from", ""))
                body = message.get("text", {}).get("body")
                ts = int(message.get("timestamp"))
                conv = WhatsAppConversation(sender)
                message_obj = WhatsAppMessage(from_number=sender, body=body, ts=ts)
                conv.process_message(message_obj)
            for location in locations:
                sender = convert_number(location.get("from", ""))
                coords = location.get("location", {})
                update_user_data(sender, coords)

    return {"response": "OK"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
