import os
from typing import Any, Dict

import folium
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse

from db_handler import get_all_user_data, update_user_data
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
            replies = [m for m in messages if m.get("type") == "interactive"]
            for message in text_messages:
                sender = convert_number(message.get("from", ""))
                body = message.get("text", {}).get("body")
                ts = int(message.get("timestamp"))
                message_obj = WhatsAppMessage(from_number=sender, body=body, ts=ts)
                conv = WhatsAppConversation(sender)
                conv.process_message(message_obj)
            for location in locations:
                sender = convert_number(location.get("from", ""))
                coords = location.get("location", {})
                coords = {
                    k: v for k, v in coords.items() if k in ["latitude", "longitude"]
                }
                update_user_data(sender, coords)
                ts = int(location.get("timestamp"))
                message_obj = WhatsAppMessage(from_number=sender, body="", ts=ts)
                conv = WhatsAppConversation(sender)
                conv.process_message(message_obj)
            for reply in replies:
                sender = convert_number(reply.get("from", ""))
                rep = reply.get("interactive", {}).get("button_reply")
                data = {rep.get("id").rsplit("_", 1)[0]: rep.get("title")}
                update_user_data(sender, data)
                ts = int(reply.get("timestamp"))
                message_obj = WhatsAppMessage(from_number=sender, body="", ts=ts)
                conv = WhatsAppConversation(sender)
                conv.process_message(message_obj)

    return {"response": "OK"}


@app.get("/", response_class=HTMLResponse)
def map_view():
    all_user_data = get_all_user_data()

    m = folium.Map(location=[-29, -53], zoom_start=5, tiles="cartodb positron")

    for user_data in all_user_data:
        info = ""
        for k, v in user_data.items():
            if k in ["latitude", "longitude"]:
                continue
            info += f"<b>{k}:</b> {v}<br>"
        folium.Marker(
            [user_data["latitude"], user_data["longitude"]],
            popup=folium.Popup(folium.IFrame(info), min_width=300, max_width=300),
        ).add_to(m)

    return m._repr_html_()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
